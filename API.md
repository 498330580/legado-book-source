# API文档

本文档详细描述了阅读3本地书源网站提供的所有API接口。

## 基础信息

- **Base URL**: `http://你的IP:8000`
- **API前缀**: `/api/`
- **响应格式**: JSON
- **编码**: UTF-8

## 通用响应格式

```json
{
    "code": 0,
    "msg": "success",
    "data": [...]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，0表示成功 |
| msg | string | 状态消息 |
| data | any | 响应数据 |

---

## 健康检查

### GET /api/health/

检查服务是否正常运行。

**请求示例**:
```bash
curl http://localhost:8000/api/health/
```

**响应示例**:
```json
{
    "status": "ok",
    "message": "服务正常运行"
}
```

---

## 搜索书籍

### GET /api/search/

搜索书籍。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 是 | 搜索关键词（书名或作者） |
| page | int | 否 | 页码，默认1 |

**请求示例**:
```bash
curl "http://localhost:8000/api/search?key=斗破&page=1"
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "name": "斗破苍穹",
            "author": "天蚕土豆",
            "kind": "玄幻",
            "coverUrl": "https://via.placeholder.com/150x200/FF6B6B/FFFFFF?text=斗破苍穹",
            "intro": "这里是属于斗气的世界，没有花俏艳丽的魔法，有的，仅仅是繁衍到巅峰的斗气！",
            "lastChapter": "第十章 迦南学院",
            "bookUrl": "/book/1",
            "tocUrl": "/book/1/toc"
        }
    ]
}
```

---

## 书籍详情

### GET /api/book/{book_id}/

获取书籍详情。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| book_id | int/string | 书籍ID或书籍URL |

**请求示例**:
```bash
curl http://localhost:8000/api/book/1/
```

**响应示例**:
```json
{
    "name": "斗破苍穹",
    "author": "天蚕土豆",
    "kind": "玄幻",
    "coverUrl": "https://via.placeholder.com/150x200/FF6B6B/FFFFFF?text=斗破苍穹",
    "intro": "这里是属于斗气的世界，没有花俏艳丽的魔法，有的，仅仅是繁衍到巅峰的斗气！",
    "lastChapter": "第十章 迦南学院",
    "wordCount": "500万字",
    "tocUrl": "/book/1/toc"
}
```

---

## 章节列表

### GET /api/book/{book_id}/toc/

获取书籍章节列表。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| book_id | int/string | 书籍ID或书籍URL |

**请求示例**:
```bash
curl http://localhost:8000/api/book/1/toc/
```

**响应示例**:
```json
{
    "bookUrl": "/book/1",
    "chapters": [
        {
            "title": "第一章 陨落的天才",
            "url": "/chapter/1",
            "index": 1,
            "vip": false,
            "pay": false
        },
        {
            "title": "第二章 神秘空间",
            "url": "/chapter/2",
            "index": 2,
            "vip": false,
            "pay": false
        }
    ]
}
```

---

## 章节内容

### GET /api/chapter/{chapter_id}/

获取章节正文内容。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| chapter_id | int/string | 章节ID或章节URL |

**请求示例**:
```bash
curl http://localhost:8000/api/chapter/1/
```

**响应示例**:
```json
{
    "title": "第一章 陨落的天才",
    "content": "<p>斗气大陆，炎盟，日。</p><p>天空之上，巨大的人口战粟着坐立...</p>",
    "chapterUrl": "/chapter/1",
    "bookUrl": "/book/1",
    "currentIndex": 1,
    "total": 10
}
```

---

## 发现/分类浏览

### GET /api/explore/

按分类浏览书籍。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 分类名称 |
| page | int | 否 | 页码，默认1 |

**请求示例**:
```bash
curl "http://localhost:8000/api/explore?type=玄幻&page=1"
```

**响应示例**: 同搜索API响应格式。

---

## 分类列表

### GET /api/categories/

获取所有书籍分类列表（自动去重）。

**请求示例**:
```bash
curl http://localhost:8000/api/categories/
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "name": "玄幻",
            "count": 5
        },
        {
            "name": "仙侠",
            "count": 3
        },
        {
            "name": "游戏",
            "count": 2
        }
    ]
}
```

---

## 获取书源

### GET /api/source/

获取书源配置（供阅读3APP导入）。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url | string | 否 | 指定书源URL |

**请求示例**:
```bash
curl http://localhost:8000/api/source/
```

**响应示例**:
```json
{
    "bookSourceName": "本地书源",
    "bookSourceUrl": "http://localhost:8000",
    "bookSourceType": 0,
    "bookSourceGroup": "本地书源",
    "enabled": true,
    "searchUrl": "http://localhost:8000/api/search?key={{key}}&page={{page}}",
    "ruleSearch": {
        "bookList": ".",
        "name": "name",
        "author": "author",
        "kind": "kind",
        "coverUrl": "coverUrl",
        "intro": "intro",
        "lastChapter": "lastChapter",
        "bookUrl": "bookUrl"
    },
    "ruleBookInfo": {
        "name": "name",
        "author": "author",
        "kind": "kind",
        "coverUrl": "coverUrl",
        "intro": "intro",
        "lastChapter": "lastChapter",
        "wordCount": "wordCount",
        "tocUrl": "tocUrl"
    },
    "ruleToc": {
        "chapterList": "chapters",
        "chapterName": "title",
        "chapterUrl": "url"
    },
    "ruleContent": {
        "content": "content"
    },
    "exploreUrl": "http://localhost:8000/api/explore?type={{type}}&page={{page}}",
    "ruleExplore": {
        "bookList": ".",
        "name": "name",
        "author": "author",
        "kind": "kind",
        "coverUrl": "coverUrl",
        "intro": "intro",
        "lastChapter": "lastChapter",
        "bookUrl": "bookUrl"
    }
}
```

---

## 获取书源列表

### GET /api/sources/

获取所有可用书源列表。

**请求示例**:
```bash
curl http://localhost:8000/api/sources/
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "name": "本地书源",
            "url": "http://localhost:8000/api/source",
            "type": 0,
            "enabled": true
        }
    ]
}
```

---

## 抓取任务

### GET /api/scraping-tasks/

获取抓取任务列表。

**请求示例**:
```bash
curl http://localhost:8000/api/scraping-tasks/
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "id": 1,
            "task_type": "search",
            "keyword": "斗破",
            "source_name": "笔趣阁",
            "status": "completed",
            "result_count": 5,
            "created_at": "2024-01-15 10:00:00"
        }
    ]
}
```

### POST /api/scraping-tasks/

创建抓取任务。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_type | string | 否 | 任务类型：search/import，默认search |
| keyword | string | 是 | 搜索关键词或书籍URL |
| source_url | string | 是 | 书源URL |

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/scraping-tasks/ \
  -H "Content-Type: application/json" \
  -d '{"task_type": "search", "keyword": "斗破", "source_url": "https://example.com"}'
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "任务创建成功",
    "data": {
        "task_id": 1
    }
}
```

### POST /api/scraping-tasks/{task_id}/run/

运行指定抓取任务。

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/scraping-tasks/1/run/
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "任务已开始执行",
    "data": {
        "task_id": 1,
        "status": "pending"
    }
}
```

---

## 定时任务

### GET /api/scheduled-tasks/

获取定时任务列表。

**请求示例**:
```bash
curl http://localhost:8000/api/scheduled-tasks/
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "success",
    "data": [
        {
            "id": 1,
            "name": "每小时搜索玄幻",
            "task_type": "search",
            "keyword": "玄幻",
            "source_name": "笔趣阁",
            "interval_type": "interval",
            "interval_seconds": 3600,
            "status": "active",
            "last_run_time": "2024-01-15 14:00:00",
            "next_run_time": "2024-01-15 15:00:00",
            "total_runs": 15,
            "last_result_count": 5
        }
    ]
}
```

### POST /api/scheduled-tasks/

创建定时任务。

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 任务名称 |
| task_type | string | 否 | 任务类型：search/import，默认search |
| keyword | string | 是 | 搜索关键词或书籍URL |
| source_url | string | 是 | 书源URL |
| interval_type | string | 否 | 执行类型：interval/cron，默认interval |
| interval_seconds | int | 否 | 间隔秒数，默认3600 |
| cron_expression | string | 否 | Cron表达式 |
| description | string | 否 | 任务描述 |

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/scheduled-tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "每小时搜索玄幻",
    "task_type": "search",
    "keyword": "玄幻",
    "source_url": "https://example.com",
    "interval_type": "interval",
    "interval_seconds": 3600
  }'
```

**响应示例**:
```json
{
    "code": 0,
    "msg": "定时任务创建成功",
    "data": {
        "task_id": 1
    }
}
```

### POST /api/scheduled-tasks/{task_id}/run/

立即执行定时任务。

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/scheduled-tasks/1/run/
```

### DELETE /api/scheduled-tasks/{task_id}/

删除定时任务。

**请求示例**:
```bash
curl -X DELETE http://localhost:8000/api/scheduled-tasks/1/
```

---

## 在阅读3APP中使用

### 导入书源

1. 打开阅读3APP
2. 进入「书源管理」
3. 选择「导入书源」
4. 输入书源地址：`http://你的IP:8000/api/source`
5. 确认导入

### 搜索书籍

1. 在书源列表中找到「本地书源」
2. 点击进入搜索界面
3. 输入关键词搜索
4. 点击书籍进入详情页
5. 添加到书架开始阅读

---

## 错误处理

### 常见错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| -1 | 参数错误 |
| 404 | 资源不存在 |
| 403 | 无权访问 |
| 500 | 服务器错误 |

### 错误响应示例

```json
{
    "code": -1,
    "msg": "搜索关键词不能为空",
    "data": []
}
```

```json
{
    "error": "书籍不存在"
}
```

---

## 附录：所有API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health/` | GET | 健康检查 |
| `/api/search/` | GET | 搜索书籍 |
| `/api/book/{book_id}/` | GET | 书籍详情 |
| `/api/book/{book_id}/toc/` | GET | 章节列表 |
| `/api/chapter/{chapter_id}/` | GET | 章节内容 |
| `/api/explore/` | GET | 发现/分类浏览 |
| `/api/categories/` | GET | 分类列表 |
| `/api/source/` | GET | 获取书源配置 |
| `/api/sources/` | GET | 获取书源列表 |
| `/api/scraping-tasks/` | GET/POST | 抓取任务列表/创建 |
| `/api/scraping-tasks/{id}/run/` | POST | 运行抓取任务 |
| `/api/scheduled-tasks/` | GET/POST | 定时任务列表/创建 |
| `/api/scheduled-tasks/{id}/run/` | POST | 立即执行定时任务 |
| `/api/scheduled-tasks/{id}/` | DELETE | 删除定时任务 |
