from rest_framework import serializers
from .models import Book, Chapter, BookSource, ScrapingTask


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'url', 'index', 'vip', 'pay']
    
    url = serializers.CharField(source='chapter_url')
    index = serializers.IntegerField(source='chapter_index')
    vip = serializers.BooleanField()
    pay = serializers.SerializerMethodField()
    
    def get_pay(self, obj):
        return False


class ChapterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'content', 'chapterUrl', 'bookUrl', 'currentIndex', 'total']
    
    chapterUrl = serializers.CharField(source='chapter_url')
    bookUrl = serializers.CharField(source='book.book_url')
    currentIndex = serializers.IntegerField(source='chapter_index')
    
    def get_total(self, obj):
        return obj.book.chapters.count()


class ChapterContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'content', 'chapter_url', 'book_url', 'chapter_index']
    
    book_url = serializers.CharField(source='book.book_url')
    chapter_url = serializers.CharField()
    chapter_index = serializers.IntegerField(source='chapter_index')


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'author', 'kind', 'coverUrl', 'intro', 'lastChapter', 'bookUrl', 'tocUrl']
    
    coverUrl = serializers.CharField(source='cover_url')
    lastChapter = serializers.CharField(source='last_chapter')
    bookUrl = serializers.CharField(source='book_url')
    tocUrl = serializers.CharField(source='toc_url')


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'author', 'kind', 'coverUrl', 'intro', 'lastChapter', 'wordCount', 'tocUrl']
    
    coverUrl = serializers.CharField(source='cover_url')
    lastChapter = serializers.CharField(source='last_chapter')
    wordCount = serializers.CharField(source='word_count')
    tocUrl = serializers.CharField(source='toc_url')


class BookTocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['bookUrl', 'chapters']
    
    bookUrl = serializers.CharField(source='book_url')
    chapters = ChapterSerializer(many=True, read_only=True)


class BookSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSource
        fields = ['id', 'name', 'url', 'group', 'source_type', 'enabled', 'status']


class ScrapingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapingTask
        fields = ['id', 'task_type', 'keyword', 'source', 'status', 'result_count', 'created_at']
    
    source_name = serializers.CharField(source='source.name', read_only=True)
