# 抓取任务使用说明

## 抓取任务工作流程

### 1. 创建书源配置

在后台管理中创建书源配置（`书源配置`模型）：

```
必填字段：
- 书源名称：例如"笔趣阁"
- 书源URL：网站的根URL，例如 https://www.biquge.com
- 搜索URL模板：搜索页面的URL，使用 {{key}} 表示关键词，{{page}} 表示页码
  例如：https://www.biquge.com/search.php?q={{key}}&page={{page}}

规则字段（根据目标网站填写）：
- 书籍列表规则：用于匹配搜索结果中的书籍列表
- 书名规则：提取书名的规则
- 作者规则：提取作者名的规则
- 分类规则：提取分类的规则
- 封面规则：提取封面URL的规则
- 简介规则：提取简介的规则
- 最新章节规则：提取最新章节名的规则
- 书籍URL规则：提取书籍详情页URL的规则
```

### 2. 创建抓取任务

在后台管理的`抓取任务`中创建新任务：

```
任务类型：
- search：搜索抓取 - 根据关键词搜索并导入书籍
- import：导入抓取 - 根据书籍URL导入完整书籍（包括章节和正文）

创建搜索任务：
- 任务类型：search
- 关键词：要搜索的关键词，例如"斗破"
- 书源：选择已配置的书源

创建导入任务：
- 任务类型：import
- 关键词：要导入的书籍详情页URL
- 书源：选择已配置的书源
```

### 3. 运行抓取任务

#### 方式一：后台管理界面

1. 进入`抓取任务`管理页面
2. 选中要运行的任务
3. 从`动作`下拉菜单选择`运行选中任务`
4. 点击`执行`按钮

#### 方式二：API触发

```bash
# 创建新任务
curl -X POST http://localhost:8000/api/scraping-tasks/ \
  -H "Content-Type: application/json" \
  -d '{"task_type": "search", "keyword": "斗破", "source_url": "https://www.biquge.com"}'

# 运行指定任务
curl -X POST http://localhost:8000/api/scraping-tasks/1/run/
```

#### 方式三：命令行

```bash
# 运行所有待执行任务
python run_task.py

# 运行指定任务
python run_task.py --task-id=1

# 运行所有任务（包括失败的）
python run_task.py --all
```

### 4. 查看结果

抓取任务完成后：
- 可以在`书籍`管理页面查看已导入的书籍
- 任务状态会变为`completed`
- `结果数量`显示导入的数据条数

## 抓取流程详解

### 搜索抓取流程

```
1. 根据搜索URL模板构造完整URL
   例如：https://www.biquge.com/search.php?q=斗破&page=1

2. 发送HTTP请求获取搜索结果页面

3. 使用`书籍列表规则`匹配页面中的书籍列表元素

4. 对每个列表元素，使用相应的规则提取：
   - 书名
   - 作者
   - 分类
   - 封面URL
   - 简介
   - 最新章节
   - 书籍URL

5. 将提取的数据保存到数据库
```

### 导入抓取流程

```
1. 访问指定的书籍URL

2. 使用详情页规则提取书籍信息：
   - 书名
   - 作者
   - 分类
   - 封面
   - 简介
   - 最新章节
   - 目录URL

3. 访问目录URL，获取章节列表

4. 使用目录规则提取章节信息：
   - 章节标题
   - 章节URL
   - 章节序号

5. 对每个章节，访问章节URL获取正文内容

6. 将所有数据保存到数据库（完全本地化）
```

## 规则语法说明

### JSOUP规则示例

```
class.bookbox        # 查找class="bookbox"的元素
tag.div              # 查找div标签
id.content           # 查找id="content"的元素
text.第一章          # 查找包含"第一章"文本的元素

@class.list.0       # 获取class="list"的第1个元素（索引从0开始）
@tag.a.@text        # 查找a标签的文本
@href               # 获取href属性值
@src                # 获取src属性值
@html               # 获取HTML内容
@text               # 获取纯文本

组合示例：
class.item.0@tag.a@text              # 第1个class="item"下的a标签文本
class.list.0@tag.li.[1]@text         # 第1个class="list"下第2个li的文本

排除示例：
class.list.!0@tag.li@text            # 排除第1个，取所有li的文本
```

### 完整配置示例

假设我们要配置一个书源，用于抓取"笔趣阁"网站：

```
书源名称：笔趣阁
书源URL：https://www.biquge.com
搜索URL模板：https://www.biquge.com/search.php?q={{key}}&page={{page}}

书籍列表规则：class.search-list@tag.li
书名规则：class.s-title@text
作者规则：class.s-author@text
分类规则：class.s-cat@text
封面规则：class.s-img@tag.img@src
简介规则：class.s-desc@text
最新章节规则：class.s-new@text
书籍URL规则：class.s-title@tag.a@href
```

## 常见问题

### 1. 抓取失败

检查项：
- 书源URL是否可访问
- 搜索URL模板是否正确
- 规则是否匹配页面内容
- 网络连接是否正常

### 2. 部分数据抓取不到

可能原因：
- 规则不够精确，需要调整
- 页面结构变化，需要更新规则
- 需要使用正则表达式进行二次处理

### 3. 章节内容为空

检查：
- 正文规则是否正确
- 章节URL是否可访问
- 是否需要登录才能访问

## 高级用法

### 使用正则表达式

在规则后面可以使用 `##正则表达式##替换内容` 来处理提取的文本：

```
示例：
author@text##作者：(\S+)##$1

这会提取类似"作者：天蚕土豆"中的"天蚕土豆"
```

### 使用JavaScript

对于复杂的处理，可以使用JavaScript（部分支持）：

```
在规则中可以使用简单的JS进行计算
```

## 监控和维护

### 查看任务日志

任务执行过程中，可以在命令行看到：
- 请求的URL
- 抓取进度
- 导入结果

### 清理无效任务

定期清理状态为`failed`的任务：
```bash
# 删除所有失败的任务
python manage.py shell
>>> from books.models import ScrapingTask
>>> ScrapingTask.objects.filter(status='failed').delete()
```
