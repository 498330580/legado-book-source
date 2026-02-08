FROM python:3.12-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=novel_source_site.settings
ENV APP_HOME=/app

# ====================
# 环境变量说明：
# ADMIN_USERNAME - 管理员用户名（默认: admin）
# ADMIN_EMAIL    - 管理员邮箱（默认: admin@example.com）
# ADMIN_PASSWORD - 管理员密码（默认: admin123）
# ====================

# 设置工作目录
WORKDIR $APP_HOME

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录
RUN mkdir -p $APP_HOME

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /data

# 设置工作目录
WORKDIR $APP_HOME

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 启动命令
# 使用entrypoint.py脚本处理数据库迁移和启动
# 容器启动时会自动：
# 1. 执行数据库迁移
# 2. 收集静态文件
# 3. 创建管理员用户（根据环境变量）
# 4. 初始化测试数据（如果数据库为空）
ENTRYPOINT ["python", "entrypoint.py"]
