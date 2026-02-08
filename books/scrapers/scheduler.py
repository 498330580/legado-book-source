import os
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_source_site.settings')

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()
scheduler.start()


def run_scheduled_task(task_id):
    """执行定时任务"""
    import django
    django.setup()
    
    from books.models import ScheduledTask, ScheduledTaskLog
    
    try:
        task = ScheduledTask.objects.get(id=task_id)
    except ScheduledTask.DoesNotExist:
        return

    task.last_run_time = datetime.now()
    task.total_runs += 1
    task.save()

    log = ScheduledTaskLog.objects.create(
        scheduled_task=task,
        status='running'
    )

    try:
        from books.scrapers.engine import ScrapingEngine
        engine = ScrapingEngine()

        if task.task_type == 'search':
            count = engine.run_search_task_with_source(task)
        elif task.task_type == 'import':
            count = engine.run_import_task_with_source(task)
        else:
            count = 0

        log.status = 'success'
        log.result_count = count
        log.end_time = datetime.now()
        log.save()

        task.last_result_count = count
        task.save()

    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.end_time = datetime.now()
        log.save()


def add_task_to_scheduler(task):
    """将定时任务添加到调度器"""
    if task.status != 'active':
        return

    try:
        existing_job = scheduler.get_job(f'task_{task.id}')
        if existing_job:
            scheduler.remove_job(f'task_{task.id}')
    except:
        pass

    if task.interval_type == 'interval':
        trigger = IntervalTrigger(seconds=task.interval_seconds)
    elif task.interval_type == 'cron':
        try:
            parts = task.cron_expression.split()
            if len(parts) >= 5:
                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4]
                )
            else:
                return
        except:
            return
    else:
        return

    try:
        scheduler.add_job(
            run_scheduled_task,
            trigger=trigger,
            args=[task.id],
            id=f'task_{task.id}',
            name=task.name,
            replace_existing=True,
            max_instances=1
        )
        
        if task.interval_type == 'interval':
            next_time = datetime.now() + timedelta(seconds=task.interval_seconds)
            task.next_run_time = next_time
        else:
            job = scheduler.get_job(f'task_{task.id}')
            if job and job.next_run_time:
                task.next_run_time = job.next_run_time
        
        task.save()
    except Exception as e:
        print(f'添加任务到调度器失败: {e}')


def remove_task_from_scheduler(task_id):
    """从调度器移除任务"""
    try:
        scheduler.remove_job(f'task_{task_id}')
    except:
        pass


def load_all_tasks():
    """加载所有启用的定时任务"""
    import django
    django.setup()
    
    from books.models import ScheduledTask
    
    tasks = ScheduledTask.objects.filter(status='active')
    for task in tasks:
        add_task_to_scheduler(task)
    print(f'已加载 {tasks.count()} 个定时任务')


def pause_task(task_id):
    """暂停定时任务"""
    try:
        scheduler.pause_job(f'task_{task_id}')
        import django
        django.setup()
        from books.models import ScheduledTask
        task = ScheduledTask.objects.get(id=task_id)
        task.status = 'paused'
        task.save()
    except Exception as e:
        print(f'暂停任务失败: {e}')


def resume_task(task_id):
    """恢复定时任务"""
    try:
        scheduler.resume_job(f'task_{task_id}')
        import django
        django.setup()
        from books.models import ScheduledTask
        task = ScheduledTask.objects.get(id=task_id)
        task.status = 'active'
        task.save()
    except Exception as e:
        print(f'恢复任务失败: {e}')


def run_task_now(task_id):
    """立即执行定时任务"""
    import threading
    thread = threading.Thread(target=run_scheduled_task, args=(task_id,))
    thread.start()


if __name__ == '__main__':
    load_all_tasks()
    print('定时任务调度器已启动')
    print('按 Ctrl+C 退出')
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print('调度器已停止')
