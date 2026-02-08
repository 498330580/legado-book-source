#!/usr/bin/env python
"""
启动脚本 - 同时启动Django服务和定时任务调度器
"""
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_source_site.settings')

import django
django.setup()

from django.core.management import call_command
from books.scrapers.scheduler import load_all_tasks, scheduler


def run_scheduler():
    """运行定时任务调度器"""
    print('定时任务调度器已启动...')
    try:
        import time
        while True:
            time.sleep(60)
            # 刷新任务状态
            from books.models import ScheduledTask
            from datetime import datetime, timedelta
            tasks = ScheduledTask.objects.filter(status='active', interval_type='interval')
            for task in tasks:
                if task.next_run_time and task.next_run_time < datetime.now():
                    pass  # APScheduler会自动处理
    except KeyboardInterrupt:
        scheduler.shutdown()
        print('调度器已停止')


def main():
    print('=' * 50)
    print('阅读3本地书源网站')
    print('=' * 50)
    
    # 加载定时任务
    print('加载定时任务...')
    load_all_tasks()
    
    # 启动定时任务调度器线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # 启动Django服务
    print('启动Django服务...')
    call_command('runserver', '0.0.0.0:8000', '--noreload')


if __name__ == '__main__':
    main()
