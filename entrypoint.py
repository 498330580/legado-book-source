#!/usr/bin/env python
"""
Docker容器入口脚本
处理数据库迁移并启动Django服务
"""
import os
import sys
import subprocess


def run_migrations():
    """运行数据库迁移"""
    print("检查数据库迁移...")
    try:
        # 检查是否有未应用的迁移
        result = subprocess.run(
            [sys.executable, "manage.py", "showmigrations", "--plan"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode != 0:
            print(f"检查迁移失败: {result.stderr}")
            return False

        # 检查是否有未应用的迁移
        unapplied = "[ ]" in result.stdout
        if unapplied:
            print("发现未应用的迁移，正在执行...")
            migrate_result = subprocess.run(
                [sys.executable, "manage.py", "migrate", "--noinput"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            if migrate_result.returncode != 0:
                print(f"迁移失败: {migrate_result.stderr}")
                return False

            print("数据库迁移完成！")
        else:
            print("数据库已是最新的。")

        return True
    except Exception as e:
        print(f"迁移检查失败: {e}")
        return False


def collect_static_files():
    """收集静态文件"""
    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'novel_source_site.settings':
        if not os.path.exists('/app/static'):
            print("收集静态文件...")
            try:
                subprocess.run(
                    [sys.executable, "manage.py", "collectstatic", "--noinput"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                print("静态文件收集完成！")
            except Exception as e:
                print(f"静态文件收集失败（可选）: {e}")


def seed_data_if_needed():
    """如果数据库为空，初始化测试数据"""
    from django.conf import settings
    from django.db import connection

    try:
        # 检查是否需要初始化数据
        table_exists = False
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='books_book';"
            )
            table_exists = cursor.fetchone() is not None

        if table_exists:
            from books.models import Book
            if Book.objects.count() == 0:
                print("数据库为空，正在初始化测试数据...")
                subprocess.run(
                    [sys.executable, "manage.py", "seed_data"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                print("测试数据初始化完成！")
    except Exception as e:
        print(f"数据初始化检查失败（可选）: {e}")


def main():
    """主函数"""
    print("=" * 50)
    print("阅读3本地书源网站 - Docker启动")
    print("=" * 50)

    # 获取启动命令
    cmd = sys.argv[1:] if len(sys.argv) > 1 else ["manage.py", "runserver", "0.0.0.0:8000"]

    if cmd[0] == "manage.py" and cmd[1] == "runserver":
        # 如果是启动Django服务，先运行迁移
        run_migrations()
        collect_static_files()
        seed_data_if_needed()

    # 执行原始命令
    os.execv(sys.executable, [sys.executable] + [os.path.join(os.path.dirname(__file__), cmd[0])] + cmd[1:])


if __name__ == "__main__":
    main()
