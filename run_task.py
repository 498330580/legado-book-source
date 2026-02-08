#!/usr/bin/env python
"""
抓取任务运行脚本

使用方法:
    python run_task.py                    # 运行所有待执行的任务
    python run_task.py --task-id 1       # 运行指定任务
    python run_task.py --all              # 运行所有任务（包括已完成）
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_source_site.settings')
django.setup()

from books.models import ScrapingTask
from books.scrapers.engine import ScrapingEngine


def main():
    engine = ScrapingEngine()
    
    task_id = None
    run_all = False
    
    for arg in sys.argv[1:]:
        if arg == '--all':
            run_all = True
        elif arg.startswith('--task-id='):
            task_id = int(arg.split('=')[1])
    
    if task_id:
        print(f'运行任务 #{task_id}...')
        count = engine.run_task(task_id)
        print(f'任务完成，导入 {count} 条数据')
    elif run_all:
        tasks = ScrapingTask.objects.all()
        print(f'找到 {tasks.count()} 个任务')
        for task in tasks:
            if task.status in ['pending', 'failed']:
                print(f'运行任务 #{task.id}...')
                count = engine.run_task(task.id)
                print(f'  -> 导入 {count} 条数据')
    else:
        tasks = ScrapingTask.objects.filter(status='pending')
        print(f'找到 {tasks.count()} 个待执行任务')
        for task in tasks:
            print(f'运行任务 #{task.id} - {task.get_task_type_display()}: {task.keyword}')
            count = engine.run_task(task.id)
            print(f'  -> 导入 {count} 条数据')


if __name__ == '__main__':
    main()
