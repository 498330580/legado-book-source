import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JsoupParser:
    def __init__(self, html: str, base_url: str = ''):
        self.html = html
        self.soup = BeautifulSoup(html, 'lxml')
        self.base_url = base_url
    
    def parse(self, rule: str) -> List[str]:
        if not rule:
            return []
        
        parts = rule.split('@')
        elements = [self.soup]
        
        for i, part in enumerate(parts):
            if not part:
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
                selector_index = int(selector_info[2]) if len(selector_info) > 2 else 0
                selector_exclude = selector_info[3] if len(selector_info) > 3 else None
                
                if selector_type == 'class':
                    for elem in elements:
                        if hasattr(elem, 'find_all'):
                            found = elem.find_all(class_=selector_name)
                            if selector_exclude and selector_exclude.startswith('!'):
                                exclude_indices = [int(x) for x in selector_exclude[1:].split(':')]
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
                                exclude_indices = [int(x) for x in selector_exclude[1:].split(':')]
                                found = [f for j, f in enumerate(found) if j not in exclude_indices]
                            if selector_index != 0 or selector_exclude:
                                found = [found[selector_index]] if 0 <= selector_index < len(found) else []
                            new_elements.extend(found)
                
                elif selector_type == 'text':
                    for elem in elements:
                        if hasattr(elem, 'find_all'):
                            found = elem.find_all(string=lambda t: selector_name in str(t))
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
            
            if self.config.book_info_init:
                try:
                    init_result = parser.parse(self.config.book_info_init)
                    if init_result:
                        info = {**info, **init_result}
                except:
                    pass
            
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
                    
                    if chapter['title']:
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
        if not rule:
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
