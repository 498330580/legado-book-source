from django.contrib import admin
from .models import Book, Chapter, BookSource, ScrapingTask, ScheduledTask, ScheduledTaskLog


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'kind', 'get_chapter_count', 'enabled', 'is_local', 'from_source', 'created_at']
    search_fields = ['name', 'author', 'book_url']
    list_filter = ['kind', 'enabled', 'is_local', 'from_source']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('基本信息', {'fields': ['name', 'author', 'kind', 'word_count']}),
        ('封面与简介', {'fields': ['cover_url', 'intro']}),
        ('URL信息', {'fields': ['book_url', 'toc_url']}),
        ('状态控制', {'fields': ['enabled', 'is_local', 'from_source']}),
        ('时间信息', {'fields': ['created_at', 'updated_at']}),
    ]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'book', 'chapter_index', 'is_vip', 'created_at']
    search_fields = ['title', 'book__name']
    list_filter = ['book', 'is_vip']
    readonly_fields = ['created_at', 'updated_at']


class BookSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'group', 'source_type', 'enabled', 'status', 'created_at']
    search_fields = ['name', 'url']
    list_filter = ['group', 'source_type', 'enabled', 'status']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('基本信息', {'fields': ['name', 'url', 'group', 'source_type', 'enabled']}),
        ('搜索规则', {'fields': ['search_url', 'book_list_rule', 'name_rule', 'author_rule', 'kind_rule', 'cover_url_rule', 'intro_rule', 'last_chapter_rule', 'book_url_rule']}),
        ('发现页面', {'fields': ['explore_url', 'explore_rule']}),
        ('详情页规则', {'fields': ['book_info_init', 'toc_url_rule']}),
        ('目录规则', {'fields': ['chapter_list_rule', 'chapter_name_rule', 'chapter_url_rule', 'next_toc_url_rule']}),
        ('正文规则', {'fields': ['content_rule', 'next_content_url_rule', 'web_js', 'source_regex']}),
        ('请求头', {'fields': ['header']}),
        ('状态信息', {'fields': ['status', 'error_message', 'last_check_time']}),
    ]


admin.site.register(BookSource, BookSourceAdmin)


class ScrapingTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_type', 'keyword', 'display_source', 'status', 'result_count', 'created_at']
    search_fields = ['keyword']
    list_filter = ['task_type', 'status', 'source']
    readonly_fields = ['created_at', 'completed_at']
    actions = ['run_tasks']
    
    def display_source(self, obj):
        return obj.source.name if obj.source else '-'
    
    def run_tasks(self, request, queryset):
        from books.scrapers.engine import ScrapingEngine
        engine = ScrapingEngine()
        
        count = 0
        for task in queryset:
            if task.status == 'pending':
                import threading
                thread = threading.Thread(target=engine.run_task, args=(task.id,))
                thread.start()
                count += 1
        
        self.message_user(request, f'已启动 {count} 个任务')
    
    display_source.short_description = '书源'
    display_source.admin_order_field = 'source__name'
    run_tasks.short_description = '运行选中任务'


admin.site.register(ScrapingTask, ScrapingTaskAdmin)


class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_source', 'task_type', 'keyword', 'get_interval_display', 'status', 'last_run_time', 'next_run_time', 'total_runs']
    search_fields = ['name', 'keyword']
    list_filter = ['task_type', 'status']
    readonly_fields = ['created_at', 'updated_at', 'last_run_time', 'next_run_time', 'total_runs']
    actions = ['enable_tasks', 'disable_tasks', 'run_now']
    fieldsets = [
        ('基本信息', {'fields': ['name', 'description', 'source', 'task_type', 'keyword']}),
        ('执行计划', {'fields': ['interval_type', 'interval_seconds', 'cron_expression', 'start_time', 'end_time']}),
        ('状态信息', {'fields': ['status', 'last_run_time', 'next_run_time', 'last_result_count', 'total_runs']}),
        ('时间信息', {'fields': ['created_at', 'updated_at']}),
    ]

    def display_source(self, obj):
        return obj.source.name if obj.source else '-'
    display_source.short_description = '书源'
    display_source.admin_order_field = 'source__name'

    def get_interval_display(self, obj):
        return obj.get_interval_display()
    get_interval_display.short_description = '执行周期'

    def enable_tasks(self, request, queryset):
        from books.scrapers.scheduler import add_task_to_scheduler
        for task in queryset:
            task.status = 'active'
            task.save()
            add_task_to_scheduler(task)
        self.message_user(request, f'已启用 {queryset.count()} 个定时任务')
    enable_tasks.short_description = '启用选中任务'

    def disable_tasks(self, request, queryset):
        from books.scrapers.scheduler import remove_task_from_scheduler
        for task in queryset:
            task.status = 'paused'
            task.save()
            remove_task_from_scheduler(task.id)
        self.message_user(request, f'已暂停 {queryset.count()} 个定时任务')
    disable_tasks.short_description = '暂停选中任务'

    def run_now(self, request, queryset):
        from books.scrapers.scheduler import run_task_now
        for task in queryset:
            run_task_now(task.id)
        self.message_user(request, f'已启动 {queryset.count()} 个任务')
    run_now.short_description = '立即执行'


admin.site.register(ScheduledTask, ScheduledTaskAdmin)


class ScheduledTaskLogAdmin(admin.ModelAdmin):
    list_display = ['scheduled_task', 'status', 'start_time', 'end_time', 'result_count']
    list_filter = ['status', 'scheduled_task']
    readonly_fields = ['start_time', 'end_time']
    date_hierarchy = 'start_time'


admin.site.register(ScheduledTaskLog, ScheduledTaskLogAdmin)
