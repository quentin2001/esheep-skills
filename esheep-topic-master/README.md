# esheep-topic-master (选题管理系统)

`esheep-topic-master` 是电子羊 (esheep) 系列的内容选题管理系统，提供从社媒灵感采集、选题筛选、创作跟进到归档完成的全生命周期管理。

---

## 🌟 核心特性 (Features)

1. **4阶段选题看板 (Kanban Pipeline)**
   - `inbox` (收集箱): 自动或手动收集的灵感选题
   - `selected` (已筛选): 精选确认立项的选题
   - `in_progress` (创作中): 正在进行大纲编写或内容创作的选题
   - `completed` (已完成): 已发布或归档的选题

2. **社媒收藏自动同步 (Social Favs Auto-Sync)**
   - 支持从 `esheep-social-favs-copilot` 等采集源自动同步 JSON 数据
   - 基于 URL 和标题的高效去重机制

3. **可视化 Web 看板 (Web Dashboard)**
   - 内置零依赖 HTTP REST API 服务器
   - 支持拖拽变更选题状态、分类筛选、实时搜索、编辑弹窗与一键同步

4. **命令行 CLI & REST API**
   - 命令行工具支持 `list` / `add` / `move` 状态切换
   - RESTful API 易于第三方系统或 Agent 集成

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

### 3. 同步社媒收藏灵感 (Import Social Favs)
```bash
python scripts/import_favs.py
```
或指定数据源路径：
```bash
python scripts/import_favs.py --favs-path path/to/raw_favs.json --db-path data/topics.json
```

### 4. 命令行 CLI 使用 (CLI Usage)

- **查看选题列表**:
  ```bash
  python scripts/topic_manager.py list
  python scripts/topic_manager.py list --status inbox
  ```

- **添加新选题**:
  ```bash
  python scripts/topic_manager.py add --title "DeepSeek-V3 架构详解" --category "AI技术" --hook "10分钟带你搞懂"
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
│   ├── import_favs.py       # 收藏灵感导入与去重逻辑
│   ├── server.py            # REST API 与静态资源 HTTP 服务器
│   └── topic_manager.py     # 选题数据 CRUD 与 CLI 逻辑
├── tests/
│   ├── test_import_favs.py   # import_favs 单元测试
│   ├── test_server.py        # REST API 单元测试
│   └── test_topic_manager.py # TopicManager 单元测试
├── web/
│   ├── index.html           # 看板页面结构
│   ├── styles.css           # 看板样式与主题
│   └── app.js               # 看板交互与 API 联动逻辑
├── pyproject.toml           # 项目元数据配置
└── README.md                # 项目说明文档
```
