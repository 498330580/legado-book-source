import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JsoupParser:
    def __init__(self, html: str, base_url: str = ''):
        self.html = html
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url

    def parse(self, rule: str) -> List[Any]:
        if not rule or not rule.strip():
            return []

        parts = rule.split('@')
        elements = [self.soup]

        for i, part in enumerate(parts):
            if not part or part.strip() == '':
                continue

            new_elements = []

            if part.startswith('css:'):
                selector = part[4:]
                for elem in elements:
                    if hasattr(elem, 'select'):
                        new_elements.extend(elem.select(selector))
                elements = new_elements

            elif part.startswith('XPath:') or part.startswith('//'):
                xpath = part[6:] if part.startswith('XPath:') else part
                for elem in elements:
                    new_elements.extend(self.xpath_query(elem, xpath))
                elements = new_elements

            elif part.startswith('json:'):
                json_path = part[5:]
                try:
                    data = json.loads(self.html if hasattr(self, 'html') and self.html.startswith('{') else str(elements[0]) if elements else '{}')
                    result = self.json_path_query(data, json_path)
                    if isinstance(result, list):
                        elements = [str(item) for item in result]
                    elif result is not None:
                        elements = [str(result)]
                    else:
                        elements = []
                except json.JSONDecodeError:
                    elements = []

            elif part.startswith('js:'):
                js_code = part[3:]
                try:
                    result = self.execute_js(js_code, elements)
                    if isinstance(result, list):
                        elements = [str(item) for item in result]
                    elif result is not None:
                        elements = [str(result)]
                    else:
                        elements = []
                except Exception as e:
                    logger.error(f"JS执行错误: {e}")
                    elements = []

            else:
                selector_info = part.split('.')
                selector_type = selector_info[0] if selector_info else 'tag'
                selector_name = selector_info[1] if len(selector_info) > 1 else ''
                selector_index = int(selector_info[2]) if len(selector_info) > 2 and selector_info[2] else 0
                selector_exclude = selector_info[3] if len(selector_info) > 3 else None

                if selector_type == 'class':
                    for elem in elements:
                        if hasattr(elem, 'find_all'):
                            found = elem.find_all(class_=selector_name)
                            if selector_exclude and selector_exclude.startswith('!'):
                                exclude_indices = [int(x) for x in selector_exclude[1:].split(':') if x]
                                found = [f for j, f in enumerate(found) if j not in exclude_indices]
                            if selector_index != 0 or selector_exclude:
                                found = [found[selector_index]] if 0 <= selector_index < len(found) else []
                            new_elements.extend(found)

                elif selector_type == 'id':
                    for elem in elements:
                        found = elem.find(id=selector_name)
                        if found:
                            new_elements.append(found)

                elif selector_type == 'tag':
                    for elem in elements:
                        if hasattr(elem, 'find_all'):
                            found = elem.find_all(selector_name)
                            if selector_exclude and selector_exclude.startswith('!'):
                                exclude_indices = [int(x) for x in selector_exclude[1:].split(':') if x]
                                found = [f for j, f in enumerate(found) if j not in exclude_indices]
                            if selector_index != 0 or selector_exclude:
                                found = [found[selector_index]] if 0 <= selector_index < len(found) else []
                            new_elements.extend(found)

                elif selector_type == 'text':
                    for elem in elements:
                        if hasattr(elem, 'find_all'):
                            found = elem.find_all(string=lambda t: selector_name and selector_name in str(t))
                            if selector_index != 0:
                                found = [found[selector_index]] if 0 <= selector_index < len(found) else []
                            new_elements.extend([BeautifulSoup(str(f), 'lxml') for f in found])

                elif selector_type == 'children':
                    for elem in elements:
                        if hasattr(elem, 'children'):
                            new_elements.extend([c for c in elem.children if hasattr(c, 'name')])

                elements = new_elements

        return elements

    def xpath_query(self, element, xpath):
        try:
            from lxml import etree
            html = str(element)
            parser = etree.HTMLParser()
            tree = etree.fromstring(html, parser)
            results = tree.xpath(xpath)
            return [etree.tostring(r, encoding='unicode') if hasattr(r, 'tag') else str(r) for r in results]
        except Exception as e:
            logger.error(f"XPath查询错误: {e}")
            return []

    def json_path_query(self, data, json_path):
        try:
            import jsonpath_rw
            matcher = jsonpath_rw.parse(json_path)
            results = [m.value for m in matcher.find(data)]
            return results[0] if len(results) == 1 else results
        except Exception as e:
            logger.error(f"JSONPath查询错误: {e}")
            return None

    def execute_js(self, js_code, elements):
        try:
            result = eval(js_code)
            return result
        except Exception as e:
            logger.error(f"JS执行错误: {e}")
            return None

    def get_text(self, elements):
        texts = []
        for elem in elements:
            if hasattr(elem, 'get_text'):
                text = elem.get_text(strip=True)
            elif hasattr(elem, 'text'):
                text = elem.text.strip()
            else:
                text = str(elem).strip()
            texts.append(text)
        return texts[0] if len(texts) == 1 else texts

    def get_html(self, elements):
        htmls = []
        for elem in elements:
            if hasattr(elem, 'prettify'):
                htmls.append(elem.prettify())
            else:
                htmls.append(str(elem))
        return htmls[0] if len(htmls) == 1 else htmls

    def get_attribute(self, elements, attr):
        values = []
        for elem in elements:
            if hasattr(elem, 'get'):
                value = elem.get(attr)
                if value:
                    values.append(value)
            elif hasattr(elem, 'attrs') and attr in elem.attrs:
                values.append(elem.attrs[attr])
        return values[0] if len(values) == 1 else values


class BookScraper:
    def __init__(self, source_config):
        self.config = source_config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        if source_config.header:
            self.session.headers.update(source_config.header)

    def search(self, keyword: str, page: int = 1) -> List[Dict[str, Any]]:
        search_url_template = self.config.search_url
        if not search_url_template:
            return []

        search_url = search_url_template.replace('{{key}}', keyword).replace('{{page}}', str(page))

        try:
            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()

            html = response.text

            if self.config.book_list_rule:
                parser = JsoupParser(html, search_url)
                book_elements = parser.parse(self.config.book_list_rule)

                books = []
                for elem in book_elements:
                    elem_html = str(elem)
                    elem_parser = JsoupParser(elem_html)

                    book = {
                        'name': self._extract_field(elem_parser, self.config.name_rule),
                        'author': self._extract_field(elem_parser, self.config.author_rule),
                        'kind': self._extract_field(elem_parser, self.config.kind_rule),
                        'cover_url': self._extract_field(elem_parser, self.config.cover_url_rule),
                        'intro': self._extract_field(elem_parser, self.config.intro_rule),
                        'last_chapter': self._extract_field(elem_parser, self.config.last_chapter_rule),
                        'book_url': self._extract_field(elem_parser, self.config.book_url_rule),
                    }

                    if book['name'] and book['book_url']:
                        if not book['book_url'].startswith('http'):
                            book['book_url'] = urljoin(self.config.url, book['book_url'])
                        books.append(book)

                return books

            return []

        except Exception as e:
            logger.error(f"搜索错误: {e}")
            return []

    def get_book_info(self, book_url: str) -> Dict[str, Any]:
        try:
            response = self.session.get(book_url, timeout=30)
            response.raise_for_status()

            parser = JsoupParser(response.text, book_url)

            info = {
                'name': '',
                'author': '',
                'kind': '',
                'cover_url': '',
                'intro': '',
                'last_chapter': '',
                'toc_url': '',
            }

            info['name'] = self._extract_field(parser, self.config.name_rule)
            info['author'] = self._extract_field(parser, self.config.author_rule)
            info['kind'] = self._extract_field(parser, self.config.kind_rule)
            info['cover_url'] = self._extract_field(parser, self.config.cover_url_rule)
            info['intro'] = self._extract_field(parser, self.config.intro_rule)
            info['last_chapter'] = self._extract_field(parser, self.config.last_chapter_rule)
            info['toc_url'] = self._extract_field(parser, self.config.toc_url_rule)

            if info['toc_url'] and not info['toc_url'].startswith('http'):
                info['toc_url'] = urljoin(book_url, info['toc_url'])

            return info

        except Exception as e:
            logger.error(f"获取书籍详情错误: {e}")
            return {}

    def get_chapters(self, toc_url: str) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(toc_url, timeout=30)
            response.raise_for_status()

            parser = JsoupParser(response.text, toc_url)

            if self.config.chapter_list_rule:
                chapter_elements = parser.parse(self.config.chapter_list_rule)

                chapters = []
                for i, elem in enumerate(chapter_elements):
                    elem_html = str(elem)
                    elem_parser = JsoupParser(elem_html)

                    chapter = {
                        'title': self._extract_field(elem_parser, self.config.chapter_name_rule),
                        'chapter_url': self._extract_field(elem_parser, self.config.chapter_url_rule),
                        'chapter_index': i + 1,
                        'is_vip': False,
                    }

                    if chapter['title'] and chapter['chapter_url']:
                        if not chapter['chapter_url'].startswith('http'):
                            chapter['chapter_url'] = urljoin(toc_url, chapter['chapter_url'])
                        chapters.append(chapter)

                return chapters

            return []

        except Exception as e:
            logger.error(f"获取章节列表错误: {e}")
            return []

    def get_chapter_content(self, chapter_url: str) -> str:
        try:
            response = self.session.get(chapter_url, timeout=30)
            response.raise_for_status()

            parser = JsoupParser(response.text, chapter_url)

            if self.config.content_rule:
                content_elements = parser.parse(self.config.content_rule)
                if content_elements:
                    content = parser.get_html(content_elements)
                    return content

            return ''

        except Exception as e:
            logger.error(f"获取章节内容错误: {e}")
            return ''

    def _extract_field(self, parser: JsoupParser, rule: str) -> str:
        if not rule or not rule.strip():
            return ''

        try:
            elements = parser.parse(rule)
            if elements:
                text = parser.get_text(elements)
                if isinstance(text, list):
                    return text[0] if text else ''
                return text
        except Exception as e:
            logger.error(f"字段提取错误: {e}")

        return ''


class ScrapingEngine:
    def __init__(self):
        pass

    def run_search_task(self, task):
        from books.models import Book, Chapter, BookSource

        task.status = 'running'
        task.save()

        try:
            if not task.source:
                task.status = 'failed'
                task.error_message = '未指定书源'
                task.save()
                return 0

            scraper = BookScraper(task.source)
            books = scraper.search(task.keyword)

            imported_count = 0
            for book_data in books:
                book_url = book_data.get('book_url', '')
                if not book_url:
                    continue

                book, created = Book.objects.update_or_create(
                    book_url=book_url,
                    defaults={
                        'name': book_data.get('name', ''),
                        'author': book_data.get('author', ''),
                        'kind': book_data.get('kind', ''),
                        'cover_url': book_data.get('cover_url', ''),
                        'intro': book_data.get('intro', ''),
                        'last_chapter': book_data.get('last_chapter', ''),
                        'enabled': True,
                        'is_local': False,
                        'from_source': task.source.name,
                    }
                )

                if created:
                    imported_count += 1
                    task.result_count = imported_count
                    task.save()

            task.status = 'completed'
            task.save()
            return imported_count

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            return 0

    def run_import_task(self, task):
        from books.models import Book, Chapter, BookSource

        task.status = 'running'
        task.save()

        try:
            if not task.source:
                task.status = 'failed'
                task.error_message = '未指定书源'
                task.save()
                return 0

            scraper = BookScraper(task.source)

            if not task.keyword:
                task.status = 'failed'
                task.error_message = '未指定书籍URL'
                task.save()
                return 0

            book_info = scraper.get_book_info(task.keyword)
            if not book_info.get('name'):
                task.status = 'failed'
                task.error_message = '无法获取书籍信息'
                task.save()
                return 0

            toc_url = book_info.get('toc_url', task.keyword)
            book, created = Book.objects.update_or_create(
                book_url=task.keyword,
                defaults={
                    'name': book_info.get('name', ''),
                    'author': book_info.get('author', ''),
                    'kind': book_info.get('kind', ''),
                    'cover_url': book_info.get('cover_url', ''),
                    'intro': book_info.get('intro', ''),
                    'last_chapter': book_info.get('last_chapter', ''),
                    'toc_url': toc_url,
                    'enabled': True,
                    'is_local': False,
                    'from_source': task.source.name,
                }
            )

            chapters = scraper.get_chapters(toc_url)
            imported_chapters = 0

            for chapter_data in chapters:
                chapter_url = chapter_data.get('chapter_url', '')
                if not chapter_url:
                    continue

                content = scraper.get_chapter_content(chapter_url)

                chapter, chapter_created = Chapter.objects.update_or_create(
                    book=book,
                    chapter_url=chapter_url,
                    defaults={
                        'title': chapter_data.get('title', ''),
                        'chapter_index': chapter_data.get('chapter_index', 0),
                        'is_vip': chapter_data.get('is_vip', False),
                        'content': content,
                    }
                )

                if chapter_created:
                    imported_chapters += 1

            book.last_chapter = chapters[-1].get('title', '') if chapters else ''
            book.save()

            task.result_count = imported_chapters
            task.status = 'completed'
            task.save()
            return imported_chapters

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            return 0

    def run_search_task_with_source(self, scheduled_task):
        """带source的搜索任务（用于定时任务）"""
        from books.models import Book, BookSource
        from datetime import datetime

        if not scheduled_task.source:
            return 0

        scraper = BookScraper(scheduled_task.source)
        books = scraper.search(scheduled_task.keyword)

        imported_count = 0
        for book_data in books:
            book_url = book_data.get('book_url', '')
            if not book_url:
                continue

            book, created = Book.objects.update_or_create(
                book_url=book_url,
                defaults={
                    'name': book_data.get('name', ''),
                    'author': book_data.get('author', ''),
                    'kind': book_data.get('kind', ''),
                    'cover_url': book_data.get('cover_url', ''),
                    'intro': book_data.get('intro', ''),
                    'last_chapter': book_data.get('last_chapter', ''),
                    'enabled': True,
                    'is_local': False,
                    'from_source': scheduled_task.source.name,
                }
            )

            if created:
                imported_count += 1

        return imported_count

    def run_import_task_with_source(self, scheduled_task):
        """带source的导入任务（用于定时任务）"""
        from books.models import Book, Chapter
        from datetime import datetime

        if not scheduled_task.source or not scheduled_task.keyword:
            return 0

        scraper = BookScraper(scheduled_task.source)

        book_info = scraper.get_book_info(scheduled_task.keyword)
        if not book_info.get('name'):
            return 0

        toc_url = book_info.get('toc_url', scheduled_task.keyword)
        book, created = Book.objects.update_or_create(
            book_url=scheduled_task.keyword,
            defaults={
                'name': book_info.get('name', ''),
                'author': book_info.get('author', ''),
                'kind': book_info.get('kind', ''),
                'cover_url': book_info.get('cover_url', ''),
                'intro': book_info.get('intro', ''),
                'last_chapter': book_info.get('last_chapter', ''),
                'toc_url': toc_url,
                'enabled': True,
                'is_local': False,
                'from_source': scheduled_task.source.name,
            }
        )

        chapters = scraper.get_chapters(toc_url)
        imported_chapters = 0

        for chapter_data in chapters:
            chapter_url = chapter_data.get('chapter_url', '')
            if not chapter_url:
                continue

            content = scraper.get_chapter_content(chapter_url)

            chapter, chapter_created = Chapter.objects.update_or_create(
                book=book,
                chapter_url=chapter_url,
                defaults={
                    'title': chapter_data.get('title', ''),
                    'chapter_index': chapter_data.get('chapter_index', 0),
                    'is_vip': chapter_data.get('is_vip', False),
                    'content': content,
                }
            )

            if chapter_created:
                imported_chapters += 1

        book.last_chapter = chapters[-1].get('title', '') if chapters else ''
        book.save()

        return imported_chapters

    def run_task(self, task_id: int):
        from books.models import ScrapingTask

        try:
            task = ScrapingTask.objects.get(id=task_id)
        except ScrapingTask.DoesNotExist:
            return False

        if task.task_type == 'search':
            return self.run_search_task(task)
        elif task.task_type == 'import':
            return self.run_import_task(task)
        else:
            task.status = 'failed'
            task.error_message = f'未知任务类型: {task.task_type}'
            task.save()
            return 0
