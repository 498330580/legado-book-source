from django.db import models


class Book(models.Model):
    name = models.CharField("书名", max_length=200)
    author = models.CharField("作者", max_length=100)
    cover_url = models.URLField("封面URL", max_length=500, blank=True)
    intro = models.TextField("简介", blank=True)
    kind = models.CharField("分类", max_length=50, blank=True)
    word_count = models.CharField("字数", max_length=20, blank=True)
    last_chapter = models.CharField("最新章节", max_length=200, blank=True)
    book_url = models.CharField("书籍URL", max_length=500, unique=True)
    toc_url = models.CharField("目录URL", max_length=500, blank=True)
    enabled = models.BooleanField("启用", default=True)
    is_local = models.BooleanField("本地书籍", default=True)
    from_source = models.CharField("来源书源", max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "书籍"
        verbose_name_plural = "书籍"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['author']),
            models.Index(fields=['book_url']),
        ]

    def __str__(self):
        return self.name

    def get_chapter_count(self):
        return self.chapters.count()
    get_chapter_count.short_description = "章节数"


class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField("章节标题", max_length=200)
    chapter_url = models.CharField("章节URL", max_length=500)
    chapter_index = models.IntegerField("章节序号")
    is_vip = models.BooleanField("VIP章节", default=False)
    content = models.TextField("正文内容", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = "章节"
        unique_together = [['book', 'chapter_url']]
        ordering = ['chapter_index']
        indexes = [
            models.Index(fields=['book', 'chapter_index']),
        ]

    def __str__(self):
        return f"{self.book.name} - {self.title}"


class BookSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        (0, "文本"),
        (1, "音频"),
        (2, "图片"),
        (3, "文件"),
    ]

    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '停用'),
        ('error', '错误'),
    ]

    name = models.CharField("书源名称", max_length=100)
    url = models.CharField("书源URL", max_length=500, unique=True)
    group = models.CharField("分组", max_length=50, blank=True)
    source_type = models.IntegerField("类型", choices=SOURCE_TYPE_CHOICES, default=0)
    enabled = models.BooleanField("启用", default=True)
    config_json = models.JSONField("书源配置", default=dict, blank=True)
    search_url = models.CharField("搜索URL模板", max_length=500, blank=True)
    book_list_rule = models.TextField("书籍列表规则", blank=True)
    name_rule = models.CharField("书名规则", max_length=200, blank=True)
    author_rule = models.CharField("作者规则", max_length=200, blank=True)
    kind_rule = models.CharField("分类规则", max_length=200, blank=True)
    cover_url_rule = models.CharField("封面规则", max_length=200, blank=True)
    intro_rule = models.CharField("简介规则", max_length=200, blank=True)
    last_chapter_rule = models.CharField("最新章节规则", max_length=200, blank=True)
    book_url_rule = models.CharField("书籍URL规则", max_length=200, blank=True)
    
    # 发现页面
    explore_url = models.TextField("发现URL", blank=True, help_text="格式：分类名::URL，每行一个")
    explore_rule = models.JSONField("发现规则", default=dict, blank=True)
    
    book_info_init = models.TextField("预处理规则", blank=True)
    toc_url_rule = models.CharField("目录URL规则", max_length=200, blank=True)
    chapter_list_rule = models.TextField("章节列表规则", blank=True)
    chapter_name_rule = models.CharField("章节名称规则", max_length=200, blank=True)
    chapter_url_rule = models.CharField("章节URL规则", max_length=200, blank=True)
    next_toc_url_rule = models.TextField("下一页规则", blank=True)
    content_rule = models.TextField("正文规则", blank=True)
    next_content_url_rule = models.TextField("正文下一页规则", blank=True)
    web_js = models.TextField("WebJs", blank=True)
    source_regex = models.TextField("资源正则", blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='active')
    error_message = models.TextField("错误信息", blank=True)
    last_check_time = models.DateTimeField("最后检查时间", null=True, blank=True)
    header = models.JSONField("请求头", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "书源配置"
        verbose_name_plural = "书源配置"

    def __str__(self):
        return self.name


class ScrapingTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('search', '搜索'),
        ('import', '导入'),
        ('sync', '同步'),
    ]

    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '进行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    source = models.ForeignKey(BookSource, on_delete=models.CASCADE, null=True, blank=True)
    task_type = models.CharField('任务类型', max_length=20, choices=TASK_TYPE_CHOICES)
    keyword = models.CharField('关键词', max_length=200, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    result_count = models.IntegerField('结果数量', default=0)
    error_message = models.TextField('错误信息', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        verbose_name = "抓取任务"
        verbose_name_plural = "抓取任务"

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.keyword or self.source}"


class ScheduledTask(models.Model):
    INTERVAL_TYPE_CHOICES = [
        ('interval', '间隔执行'),
        ('cron', 'Cron表达式'),
        ('date', '单次执行'),
    ]

    STATUS_CHOICES = [
        ('active', '启用'),
        ('paused', '暂停'),
        ('completed', '已完成'),
    ]

    name = models.CharField('任务名称', max_length=100)
    description = models.TextField('任务描述', blank=True)
    source = models.ForeignKey(BookSource, on_delete=models.CASCADE, null=True, blank=True, verbose_name='书源')
    task_type = models.CharField('任务类型', max_length=20, choices=ScrapingTask.TASK_TYPE_CHOICES)
    keyword = models.CharField('关键词', max_length=200, blank=True, help_text='搜索关键词或书籍URL')

    interval_type = models.CharField('执行类型', max_length=20, choices=INTERVAL_TYPE_CHOICES, default='interval')

    interval_seconds = models.IntegerField('间隔秒数', default=3600, help_text='间隔多少秒执行一次')
    cron_expression = models.CharField('Cron表达式', max_length=100, blank=True, help_text='分钟 小时 日期 月份 星期')

    start_time = models.DateTimeField('开始时间', null=True, blank=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)

    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    last_run_time = models.DateTimeField('上次执行时间', null=True, blank=True)
    next_run_time = models.DateTimeField('下次执行时间', null=True, blank=True)
    last_result_count = models.IntegerField('上次结果数', default=0)
    total_runs = models.IntegerField('总执行次数', default=0)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '定时任务'
        verbose_name_plural = '定时任务'

    def __str__(self):
        return self.name

    def get_interval_display(self):
        if self.interval_type == 'interval':
            hours = self.interval_seconds // 3600
            minutes = (self.interval_seconds % 3600) // 60
            if hours > 0:
                return f'每 {hours} 小时 {minutes} 分钟'
            elif minutes > 0:
                return f'每 {minutes} 分钟'
            else:
                return f'每 {self.interval_seconds} 秒'
        elif self.interval_type == 'cron':
            return f'Cron: {self.cron_expression}'
        else:
            return '单次执行'
    get_interval_display.short_description = '执行周期'


class ScheduledTaskLog(models.Model):
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('running', '运行中'),
    ]

    scheduled_task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='running')
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    result_count = models.IntegerField('结果数量', default=0)
    error_message = models.TextField('错误信息', blank=True)

    class Meta:
        verbose_name = '定时任务日志'
        verbose_name_plural = '定时任务日志'
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.scheduled_task.name} - {self.start_time.strftime("%Y-%m-%d %H:%M:%S")}'
