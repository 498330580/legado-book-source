#!/bin/bash

echo "========================================="
echo "阅读3本地书源网站 - 安装脚本"
echo "========================================="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

# 创建虚拟环境
echo "[1/5] 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "[2/5] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[3/5] 安装Python依赖..."
pip install --upgrade pip
pip install django djangorestframework requests beautifulsoup4 lxml httpx python-dateutil markdown pygments django-filter

# 创建数据库
echo "[4/5] 初始化数据库..."
python manage.py migrate

# 创建管理员
echo "[5/5] 创建测试数据..."
python manage.py seed_data

echo ""
echo "========================================="
echo "安装完成！"
echo "========================================="
echo ""
echo "启动服务:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "访问地址:"
echo "  - 首页: http://localhost:8000/"
echo "  - API:  http://localhost:8000/api/source"
echo "  - 后台: http://localhost:8000/admin/"
echo ""
echo "在阅读3APP中导入书源:"
echo "  书源地址: http://你的IP:8000/api/source"
echo ""
