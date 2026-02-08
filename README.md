# 阅读3本地书源网站

## 项目简介

阅读3本地书源网站是一个基于Django + Django REST Framework搭建的本地书籍API服务网站。它为[阅读3APP](https://github.com/gedoor/legado)提供本地书籍数据支持，支持：

- 通过Django原生后台手动管理书籍
- 通过抓取器从其他网站导入书籍（完全本地化）
- 对外提供符合阅读3规范的API服务

## 功能特性

- 📖 **后台管理** - 通过Django原生后台轻松管理书籍、章节和书源配置
- 🔍 **全文搜索** - 支持按书名、作者搜索书籍
- 📚 **分类浏览** - 按分类浏览书籍，发现更多好书
- 🔗 **书源抓取** - 支持从其他网站抓取书籍，完全本地化存储
- 📱 **阅读3兼容** - 完全符合阅读3API规范，无缝对接
- 🌐 **局域网访问** - 专为局域网设计，支持多设备访问

## 安装步骤

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python manage.py migrate
```

### 4. 创建管理员账户

```bash
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码。

### 5. 初始化测试数据

```bash
python manage.py seed_data
```

这将创建3本测试书籍（斗破苍穹、凡人修仙传、全职高手），每本书10个章节。

### 6. 启动服务

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Docker 部署

### 使用Docker Hub镜像（推荐）

```bash
# 拉取镜像
docker pull 你的用户名/legado-book-source:latest

# 运行容器（使用默认管理员: admin / admin123）
docker run -d \
  --name legado-web \
  -p 8000:8000 \
  -v static_data:/app/static \
  你的用户名/legado-book-source:latest

# 运行容器（自定义管理员账户）
docker run -d \
  --name legado-web \
  -p 8000:8000 \
  -v static_data:/app/static \
  -e ADMIN_USERNAME=myadmin \
  -e ADMIN_EMAIL=admin@mysite.com \
  -e ADMIN_PASSWORD=mypassword123 \
  你的用户名/legado-book-source:latest
```

### 使用Docker Compose

```bash
# 克隆项目
git clone https://github.com/你的用户名/legado-book-source.git
cd legado-book-source

# 使用默认配置启动
docker-compose up -d

# 或者使用生产配置
docker-compose -f docker-compose.prod.yml up -d
```

### 环境变量配置

创建 `.env` 文件：

```env
# Docker Hub用户名
DOCKERHUB_USERNAME=你的用户名

# 镜像标签
TAG=latest

# 宿主机端口
HOST_PORT=8000

# 允许的域名
ALLOWED_HOSTS=*

# 调试模式
DEBUG=0

# ====================
# 管理员账户配置（可选）
# 不设置则使用默认值: admin / admin123
# ====================
# 管理员用户名
ADMIN_USERNAME=admin

# 管理员邮箱
ADMIN_EMAIL=admin@example.com

# 管理员密码
ADMIN_PASSWORD=admin123
```

### 自定义管理员账户

在 `.env` 文件中设置以下环境变量来自定义管理员账户：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `ADMIN_USERNAME` | admin | 管理员用户名 |
| `ADMIN_EMAIL` | admin@example.com | 管理员邮箱 |
| `ADMIN_PASSWORD` | admin123 | 管理员密码 |

示例：
```bash
# 自定义管理员账户
ADMIN_USERNAME=myadmin
ADMIN_EMAIL=admin@mysite.com
ADMIN_PASSWORD=mypassword123
```

### 使用Docker Compose + PostgreSQL

```bash
# 启动所有服务（包括PostgreSQL）
docker-compose -f docker-compose.yml --profile postgres up -d
```

### 端口和卷

| 映射 | 说明 |
|------|------|
| `8000:8000` | Web服务端口 |
| `static_data:/app/static` | 静态文件 |
| `media_data:/app/media` | 媒体文件 |

### 验证部署

```bash
# 检查容器状态
docker ps

# 检查健康状态
curl http://localhost:8000/api/health/

# 查看日志
docker-compose logs -f
```

### 数据持久化

- **数据库**：SQLite文件存储在容器内，升级时会自动迁移
- **静态文件**：挂载到 `static_data` 卷
- **备份**：挂载主机目录到 `/data`

### 更新部署

```bash
# 拉取最新镜像
docker pull 你的用户名/legado-book-source:latest

# 重新启动
docker-compose down
docker-compose up -d
```

### DockerHub自动构建

项目已配置GitHub Actions，当代码推送到master分支时，会自动：
1. 构建Docker镜像
2. 运行数据库迁移测试
3. 推送到Docker Hub

推送前需在GitHub仓库设置：
- `DOCKERHUB_USERNAME`：Docker Hub用户名
- `DOCKERHUB_TOKEN`：Docker Hub访问令牌

---

## 使用说明

### 后台管理

1. 访问 `http://localhost:8000/admin/`
2. 使用管理员账户登录
3. 可以管理以下内容：
   - **书籍**：添加、编辑、删除书籍
   - **章节**：管理书籍章节内容
   - **书源配置**：配置抓取规则
   - **抓取任务**：管理抓取任务

### 在阅读3APP中使用

1. 打开阅读3APP
2. 进入「书源管理」
3. 选择「导入书源」
4. 输入书源地址：`http://你的IP:8000/api/source`
5. 开始搜索和阅读！

### 添加本地书籍

1. 登录Django管理后台
2. 进入「书籍」管理页面
3. 点击「添加书籍」
4. 填写书籍信息：
   - 书名
   - 作者
   - 分类
   - 简介
   - 封面URL（可选）
   - 书籍URL（唯一标识）
5. 保存后，为书籍添加章节

### 抓取书籍

1. 在「书源配置」中添加书源（配置抓取规则）
2. 在「抓取任务」中创建抓取任务
3. 等待抓取完成后，可以在「书籍」中管理抓取的书籍

### 定时任务

网站支持设置定时自动抓取任务：

#### 启动方式

```bash
# 使用启动脚本（推荐）
python start.py
```

该脚本会同时启动Django服务和定时任务调度器。

#### 创建定时任务

1. 访问管理后台：http://localhost:8000/admin/
2. 进入「定时任务」管理页面
3. 点击「添加定时任务」
4. 配置任务参数：
   - 任务名称：给任务起个名字
   - 书源：选择已配置的书源
   - 任务类型：搜索 / 导入
   - 关键词：搜索关键词或书籍URL
   - 执行类型：
     - 间隔执行：设置秒数（如3600表示每小时执行一次）
     - Cron表达式：使用标准Cron格式（分 时 日 月 星期）
   - 状态：启用

#### API方式

```bash
# 创建定时任务
curl -X POST http://localhost:8000/api/scheduled-tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "每小时搜索",
    "task_type": "search",
    "keyword": "玄幻",
    "source_url": "https://example.com",
    "interval_type": "interval",
    "interval_seconds": 3600
  }'

# 查看任务列表
curl http://localhost:8000/api/scheduled-tasks/

# 立即执行
curl -X POST http://localhost:8000/api/scheduled-tasks/1/run/
```

详细说明请参考 [SCHEDULED_TASKS.md](./SCHEDULED_TASKS.md)

## 常见问题

### 1. 无法访问API？

确保服务已启动：检查`python manage.py runserver`是否在运行。

### 2. 阅读3无法连接？

- 确保手机和电脑在同一局域网
- 检查防火墙是否阻止了8000端口
- 使用电脑的局域网IP地址（如192.168.1.100）而非localhost

### 3. 如何备份数据？

数据库文件位于`db.sqlite3`，直接备份该文件即可。

### 4. 如何升级？

```bash
git pull
pip install -r requirements.txt
python manage.py migrate
```

## 项目结构

```
novel_source_site/
├── manage.py
├── requirements.txt           # 依赖列表
├── README.md                  # 使用说明
├── API.md                     # API文档
├── Dockerfile                 # Docker构建文件
├── docker-compose.yml         # 开发环境Docker Compose
├── docker-compose.prod.yml    # 生产环境Docker Compose
├── entrypoint.py             # Docker入口脚本
├── .dockerignore             # Docker忽略文件
├── .github/
│   └── workflows/
│       └── docker.yml       # GitHub Actions Docker构建
├── novel_source/              # Django项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/                     # 书籍应用
│   ├── models.py             # 数据库模型
│   ├── views.py              # API视图
│   ├── serializers.py         # API序列化
│   ├── urls.py               # API路由
│   ├── admin.py              # 后台管理配置
│   ├── scrapers/             # 抓取模块
│   │   ├── base.py          # 抓取器基类
│   │   ├── engine.py        # 抓取引擎
│   │   └── scheduler.py     # 定时任务调度器
│   └── management/           # 管理命令
│       └── commands/
│           ├── seed_data.py  # 初始化测试数据
│           └── run_scraping.py # 运行抓取任务
├── templates/                 # 模板文件
│   └── books/
│       └── index.html        # 首页
└── static/                   # 静态文件
    └── books/
        └── css/
            └── style.css
```

## 技术栈

- **后端框架**: Django 5.0+
- **API框架**: Django REST Framework
- **数据库**: SQLite（本地使用）
- **HTTP客户端**: requests + httpx
- **HTML解析**: BeautifulSoup4
- **定时任务**: APScheduler
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 许可证

MIT License

## 致谢

- [阅读3 (Legado)](https://github.com/gedoor/legado) - 优秀的开源阅读APP
- [Django](https://www.djangoproject.com/) - Python Web框架
- [Django REST Framework](https://www.django-rest-framework.org/) - REST API框架
