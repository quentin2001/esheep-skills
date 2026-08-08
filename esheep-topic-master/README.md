# esheep-topic-master (选题管理系统)

`esheep-topic-master` 是电子羊 (esheep) 系列的内容选题管理系统，提供从热榜抓取、社媒灵感采集、原创构思到选题筛选、创作跟进与归档完成的全生命周期管理。

---

## 🌟 核心特性 (Features)

1. **4阶段选题看板 (Kanban Pipeline)**
   - `inbox` (收集箱): 自动或手动收集的灵感选题
   - `selected` (已筛选): 精选确认立项的选题
   - `in_progress` (创作中): 正在进行大纲编写或内容创作的选题
   - `completed` (已完成): 已发布或归档的选题

2. **3大来源分类体系 (3-Source Taxonomy)**
   - `hotlist` (全网热榜): 来自知乎热榜、微博热搜、AIHot 等平台的自动抓取热点
   - `social_fav` (社媒收藏): 来自 `esheep-social-favs-copilot` 等采集工具的收藏书签
   - `original_idea` (原创构思): 手动创建或原生思考的选题灵感

3. **全网热榜多源抓取 (Multi-Adapter Hotlist Fetching)**
   - 支持从知乎、微博、AIHot 抓取热门话题
   - 包含基于 User-Agent 模拟、自动解析与高弹性容错机制
   - 支持一键抓取并入库至 Inbox 收集箱

4. **社媒收藏自动同步 (Social Favs Auto-Sync)**
   - 支持从 `esheep-social-favs-copilot` 等采集源自动同步 JSON 数据
   - 基于 URL 和标题的高效去重机制

5. **可视化 Web 看板 (Web Dashboard)**
   - 内置零依赖 HTTP REST API 服务器
   - 支持拖拽变更选题状态、分类筛选、来源筛选、实时搜索、编辑弹窗与一键同步

6. **命令行 CLI & REST API**
   - 命令行工具支持 `fetch_hotlist` 抓取、`import_favs` 导入以及 `topic_manager` 检索/新增/状态转移

---

## 🚀 快速开始 (Quickstart)

### 1. 环境准备 (Requirements)
确保 Python 3.8+ 已安装：
```bash
python --version
```

### 2. 启动 Web 看板与服务 (Start Web Dashboard)
```bash
python scripts/server.py --port 18922
```
启动后在浏览器访问 `http://localhost:18922` 即可使用可视化看板。

### 3. 抓取全网热榜选题 (Fetch Hotlist Topics)
```bash
python scripts/fetch_hotlist.py --sources zhihu,weibo,aihot --limit 15 --ingest
```
- 或仅打印热榜 JSON:
```bash
python scripts/fetch_hotlist.py --sources zhihu,weibo --limit 10
```

### 4. 同步社媒收藏灵感 (Import Social Favs)
```bash
python scripts/import_favs.py
```
或指定数据源路径：
```bash
python scripts/import_favs.py --favs-path path/to/raw_favs.json --db-path data/topics.json
```

### 5. 命令行 CLI 使用 (CLI Usage)

- **查看选题列表**:
  ```bash
  python scripts/topic_manager.py list
  python scripts/topic_manager.py list --status inbox
  python scripts/topic_manager.py list --source-type hotlist
  ```

- **添加新选题**:
  ```bash
  python scripts/topic_manager.py add --title "DeepSeek-V3 架构详解" --category "AI技术" --hook "10分钟带你搞懂" --source-type original_idea
  ```

- **移动选题状态**:
  ```bash
  python scripts/topic_manager.py move --id <TOPIC_ID> --status selected
  ```

---

## 🧪 测试 (Testing)

运行 pytest 单元测试套件：
```bash
pytest
```

---

## 📁 目录结构 (Directory Structure)

```
esheep-topic-master/
├── .agents/skills/esheep-topic-master/
│   └── SKILL.md             # Agent Skill 定义
├── data/
│   └── topics.json          # 选题数据库文件 (JSON)
├── scripts/
│   ├── fetch_hotlist.py     # 多适配器热榜抓取与入库逻辑
│   ├── import_favs.py       # 收藏灵感导入与去重逻辑
│   ├── server.py            # REST API 与静态资源 HTTP 服务器
│   └── topic_manager.py     # 选题数据 CRUD 与 CLI 逻辑
├── tests/
│   ├── test_fetch_hotlist.py # fetch_hotlist 单元测试
│   ├── test_import_favs.py   # import_favs 单元测试
│   ├── test_server.py        # REST API 单元测试
│   └── test_topic_manager.py # TopicManager 单元测试
├── web/
│   ├── index.html           # 看板页面结构
│   ├── server.cjs           # Node 服务器产物
│   └── assets/              # 前端 JS & CSS 静态 Bundle 产物
├── pyproject.toml           # 项目元数据配置
└── README.md                # 项目说明文档
```

