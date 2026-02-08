import re
import json
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models import Q
from .models import Book, Chapter, BookSource, ScrapingTask, ScheduledTask
from .serializers import (
    BookListSerializer, BookDetailSerializer, BookTocSerializer,
    ChapterContentSerializer, ChapterSerializer
)


def home(request):
    """首页"""
    return render(request, 'books/index.html')


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': '服务正常运行'
        })


class BookSearchView(APIView):
    def get(self, request):
        key = request.GET.get('key', '').strip()
        page = int(request.GET.get('page', 1))
        
        if not key:
            return Response({
                'code': -1,
                'msg': '搜索关键词不能为空',
                'data': []
            })
        
        books = Book.objects.filter(
            Q(name__icontains=key) | 
            Q(author__icontains=key)
        ).filter(enabled=True)
        
        start = (page - 1) * 20
        end = start + 20
        books = books[start:end]
        
        serializer = BookListSerializer(books, many=True)
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': serializer.data
        })


class BookDetailView(APIView):
    def get(self, request, book_id):
        try:
            if book_id.isdigit():
                book = Book.objects.get(id=book_id, enabled=True)
            else:
                book = Book.objects.get(book_url=book_id, enabled=True)
            
            serializer = BookDetailSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({
                'error': '书籍不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class BookTocView(APIView):
    def get(self, request, book_id):
        try:
            if book_id.isdigit():
                book = Book.objects.get(id=book_id, enabled=True)
            else:
                book = Book.objects.get(book_url=book_id, enabled=True)
            
            chapters = book.chapters.all()
            serializer = ChapterSerializer(chapters, many=True)
            
            return Response({
                'bookUrl': book.book_url,
                'chapters': serializer.data
            })
        except Book.DoesNotExist:
            return Response({
                'error': '书籍不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class ChapterContentView(APIView):
    def get(self, request, chapter_id):
        try:
            if chapter_id.isdigit():
                chapter = Chapter.objects.select_related('book').get(id=chapter_id)
            else:
                chapter = Chapter.objects.select_related('book').get(chapter_url=chapter_id)
            
            if not chapter.book.enabled:
                return Response({
                    'error': '书籍已禁用'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ChapterContentSerializer(chapter)
            return Response({
                'title': chapter.title,
                'content': chapter.content or '暂无内容',
                'chapterUrl': chapter.chapter_url,
                'bookUrl': chapter.book.book_url,
                'currentIndex': chapter.chapter_index,
                'total': chapter.book.chapters.count()
            })
        except Chapter.DoesNotExist:
            return Response({
                'error': '章节不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class ExploreView(APIView):
    def get(self, request):
        kind = request.GET.get('type', '').strip()
        page = int(request.GET.get('page', 1))
        
        books = Book.objects.filter(enabled=True)
        
        if kind:
            books = books.filter(kind__icontains=kind)
        
        start = (page - 1) * 20
        end = start + 20
        books = books[start:end]
        
        serializer = BookListSerializer(books, many=True)
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': serializer.data
        })


class BookSourceView(APIView):
    def get(self, request):
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        source_url = request.GET.get('url', '').strip()
        if source_url:
            try:
                source = BookSource.objects.get(url=source_url, enabled=True)
                config = source.config_json or {}
            except BookSource.DoesNotExist:
                config = {}
        else:
            config = {}
        
        book_source = {
            "bookSourceName": config.get('bookSourceName', '本地书源'),
            "bookSourceUrl": base_url,
            "bookSourceType": config.get('bookSourceType', 0),
            "bookSourceGroup": config.get('bookSourceGroup', '本地书源'),
            "enabled": True,
            "searchUrl": f"{base_url}/api/search?key={{key}}&page={{page}}",
            "ruleSearch": {
                "bookList": ".",
                "name": "name",
                "author": "author",
                "kind": "kind",
                "coverUrl": "coverUrl",
                "intro": "intro",
                "lastChapter": "lastChapter",
                "bookUrl": "bookUrl"
            },
            "ruleBookInfo": {
                "name": "name",
                "author": "author",
                "kind": "kind",
                "coverUrl": "coverUrl",
                "intro": "intro",
                "lastChapter": "lastChapter",
                "wordCount": "wordCount",
                "tocUrl": "tocUrl"
            },
            "ruleToc": {
                "chapterList": "chapters",
                "chapterName": "title",
                "chapterUrl": "url"
            },
            "ruleContent": {
                "content": "content"
            },
            "exploreUrl": f"{base_url}/api/explore?type={{type}}&page={{page}}",
            "ruleExplore": {
                "bookList": ".",
                "name": "name",
                "author": "author",
                "kind": "kind",
                "coverUrl": "coverUrl",
                "intro": "intro",
                "lastChapter": "lastChapter",
                "bookUrl": "bookUrl"
            }
        }
        
        return Response(book_source)


class BookSourcesView(APIView):
    def get(self, request):
        sources = BookSource.objects.filter(enabled=True)
        
        data = []
        for source in sources:
            base_url = request.build_absolute_uri('/').rstrip('/')
            data.append({
                "name": source.name,
                "url": f"{base_url}/api/source?url={source.url}",
                "type": source.source_type,
                "enabled": source.enabled
            })
        
        if not data:
            base_url = request.build_absolute_uri('/').rstrip('/')
            data.append({
                "name": "本地书源",
                "url": f"{base_url}/api/source",
                "type": 0,
                "enabled": True
            })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': data
        })


class ScrapingTaskView(APIView):
    def get(self, request):
        tasks = ScrapingTask.objects.all().order_by('-created_at')[:20]
        
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'task_type': task.task_type,
                'keyword': task.keyword,
                'source_name': task.source.name if task.source else '',
                'status': task.status,
                'result_count': task.result_count,
                'error_message': task.error_message,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else None,
            })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': data
        })
    
    def post(self, request):
        task_type = request.data.get('task_type', 'search')
        keyword = request.data.get('keyword', '')
        source_url = request.data.get('source_url', '')
        
        source = None
        if source_url:
            try:
                source = BookSource.objects.get(url=source_url, enabled=True)
            except BookSource.DoesNotExist:
                return Response({
                    'code': -1,
                    'msg': '书源不存在或已禁用'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        task = ScrapingTask.objects.create(
            source=source,
            task_type=task_type,
            keyword=keyword,
            status='pending'
        )
        
        return Response({
            'code': 0,
            'msg': '任务创建成功',
            'data': {
                'task_id': task.id
            }
        })


class RunScrapingTaskView(APIView):
    def post(self, request, task_id):
        try:
            task = ScrapingTask.objects.get(id=task_id)
        except ScrapingTask.DoesNotExist:
            return Response({
                'code': -1,
                'msg': '任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if task.status == 'running':
            return Response({
                'code': -1,
                'msg': '任务正在运行中'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from books.scrapers.engine import ScrapingEngine
        
        engine = ScrapingEngine()
        
        import threading
        thread = threading.Thread(target=engine.run_task, args=(task_id,))
        thread.start()
        
        return Response({
            'code': 0,
            'msg': '任务已开始执行',
            'data': {
                'task_id': task.id,
                'status': task.status
            }
        })


class ScheduledTaskView(APIView):
    def get(self, request):
        tasks = ScheduledTask.objects.all().order_by('-created_at')[:20]
        
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'task_type': task.task_type,
                'keyword': task.keyword,
                'source_name': task.source.name if task.source else '',
                'interval_type': task.interval_type,
                'interval_seconds': task.interval_seconds,
                'cron_expression': task.cron_expression,
                'status': task.status,
                'last_run_time': task.last_run_time.strftime('%Y-%m-%d %H:%M:%S') if task.last_run_time else None,
                'next_run_time': task.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if task.next_run_time else None,
                'last_result_count': task.last_result_count,
                'total_runs': task.total_runs,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': data
        })
    
    def post(self, request):
        from books.scrapers.scheduler import add_task_to_scheduler
        
        name = request.data.get('name', '定时任务')
        task_type = request.data.get('task_type', 'search')
        keyword = request.data.get('keyword', '')
        source_url = request.data.get('source_url', '')
        interval_type = request.data.get('interval_type', 'interval')
        interval_seconds = int(request.data.get('interval_seconds', 3600))
        cron_expression = request.data.get('cron_expression', '')
        
        source = None
        if source_url:
            try:
                source = BookSource.objects.get(url=source_url, enabled=True)
            except BookSource.DoesNotExist:
                return Response({
                    'code': -1,
                    'msg': '书源不存在或已禁用'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        task = ScheduledTask.objects.create(
            name=name,
            description=request.data.get('description', ''),
            source=source,
            task_type=task_type,
            keyword=keyword,
            interval_type=interval_type,
            interval_seconds=interval_seconds,
            cron_expression=cron_expression,
            status='active'
        )
        
        add_task_to_scheduler(task)
        
        return Response({
            'code': 0,
            'msg': '定时任务创建成功',
            'data': {
                'task_id': task.id
            }
        })


class RunScheduledTaskView(APIView):
    def post(self, request, task_id):
        try:
            task = ScheduledTask.objects.get(id=task_id)
        except ScheduledTask.DoesNotExist:
            return Response({
                'code': -1,
                'msg': '任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from books.scrapers.scheduler import run_task_now
        run_task_now(task_id)
        
        return Response({
            'code': 0,
            'msg': '任务已开始执行',
            'data': {
                'task_id': task.id
            }
        })
    
    def delete(self, request, task_id):
        try:
            task = ScheduledTask.objects.get(id=task_id)
        except ScheduledTask.DoesNotExist:
            return Response({
                'code': -1,
                'msg': '任务不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from books.scrapers.scheduler import remove_task_from_scheduler
        remove_task_from_scheduler(task_id)
        task.delete()
        
        return Response({
            'code': 0,
            'msg': '任务已删除'
        })


class CategoryListView(APIView):
    def get(self, request):
        categories = Book.objects.filter(
            enabled=True,
            kind__isnull=False
        ).exclude(
            kind=''
        ).values('kind').annotate(
            count=models.Count('id')
        ).order_by('kind')
        
        data = []
        for cat in categories:
            if cat['kind'] not in [d.get('name') for d in data]:
                data.append({
                    'name': cat['kind'],
                    'count': cat['count']
                })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'data': data
        })
