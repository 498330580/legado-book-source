from django.core.management.base import BaseCommand
from books.models import ScrapingTask
from books.scrapers.engine import ScrapingEngine


class Command(BaseCommand):
    help = '执行抓取任务'

    def add_arguments(self, parser):
        parser.add_argument('task_id', type=int, help='任务ID')

    def handle(self, *args, **options):
        task_id = options['task_id']

        self.stdout.write(f'开始执行任务 #{task_id}...')

        engine = ScrapingEngine()
        count = engine.run_task(task_id)

        if count > 0:
            self.stdout.write(self.style.SUCCESS(f'任务完成，导入 {count} 条数据'))
        else:
            self.stdout.write(self.style.WARNING(f'任务完成，未导入数据'))
