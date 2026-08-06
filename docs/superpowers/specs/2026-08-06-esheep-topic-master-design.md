# Design Spec: esheep-topic-master (硅基电子羊 · 选题掌管者)

## 1. Overview & Goals
`esheep-topic-master` 是 eSheep (硅基电子羊) 自媒体 AI 技能组的核心选题流转与数据库管理系统。
它负责接收来自 `esheep-social-favs-copilot`（社媒抓取与灵感拆解）及人工手动输入的选题，提供 4 阶段生命周期管理与轻量 Web 拖拽编辑看板。

### 4 阶段生命周期：
1. `inbox` **未选中的散落选题 (Raw Inbox Pool)**：未过滤或新导入的原始灵感。
2. `selected` **选中的选题 (Selected Backlog)**：评估后确认准备制作的储备选题。
3. `in_progress` **正在做的选题 (In Production)**：撰写文案/脚本、录制切片或排版中的选题。
4. `completed` **做完的选题 (Completed / Archive)**：已发布归档的选题。

---

## 2. Architecture & Tech Stack

```
esheep-topic-master/
├── .agents/skills/esheep-topic-master/
│   └── SKILL.md                 # Agent 指令与使用说明
├── data/
│   └── topics.json              # 本地选题数据库（主存储）
├── web/
│   ├── index.html               # 4列 Kanban Web 前端界面 (Vanilla JS + CSS)
│   └── styles.css               # Modern Dark/Glassmorphism 样式
├── scripts/
│   ├── server.py                # Python 原生 HTTP API 服务 (localhost:8000)
│   ├── topic_manager.py         # CLI 命令行数据管理工具 (增删改查流转)
│   └── import_favs.py           # 联动 esheep-social-favs-copilot 数据导入器
├── pyproject.toml
└── README.md
```

### 关键设计原则：
- **Zero Heavy Dependencies**: 后端基于 Python 标准库 HTTP Server，无需大型应用框架，开箱即用。
- **Lightweight Web UI**: 原生 HTML5 Drag-and-Drop + Responsive Glassmorphism Dashboard，提供丝滑移动卡片与弹窗编辑功能。
- **AI Agent & Human Dual Access**: 人类可通过网页点拽编辑，AI Agent 可通过 CLI / JSON 接口读写流转状态。

---

## 3. Data Schema (`data/topics.json`)

```json
[
  {
    "id": "topic_1722920000_a1b2",
    "title": "如何用 Python 自动化打造社媒选题库",
    "status": "inbox",
    "category": "AI / 效率工具",
    "source_platform": "xiaohongshu",
    "source_title": "这个自媒体工作流太香了",
    "source_url": "https://www.xiaohongshu.com/explore/...",
    "hook": "不用复杂数据库，一个 JSON 文件+拖拽看板搞定自媒体管理",
    "angles": [
      "入门教程：如何 10 分钟搭好选题看板",
      "避坑指南：自媒体选题管理最常踩的 3 个坑",
      "案例拆解：从点赞收藏到爆款输出的全流程"
    ],
    "outline": "1. 引入痛点：收藏不等于学会...\n2. 解决方案：4阶段流转看板...\n3. 实操步骤...",
    "tags": ["自媒体", "效率", "Python"],
    "created_at": "2026-08-06T14:30:00",
    "updated_at": "2026-08-06T14:30:00"
  }
]
```

---

## 4. Web UI Features & Interface

1. **4 列看板 (4-Column Kanban)**:
   - 顶部显示各列选题计数（如 `散落选题 (12)` | `已选中 (3)` | `正在做 (1)` | `已完成 (8)`）。
   - 卡片显示：标题、平台 Icon/标签、核心 Hook、更新时间。
   - 支持卡片在列之间直接拖拽完成状态切换（同步更新 HTTP REST API）。
2. **编辑弹窗 (Topic Modal)**:
   - 双击或点击编辑图标弹出 Modal。
   - 可实时修改：标题、分类、切入角度 (Angles)、脚本/文案大纲 (Outline)、标签 (Tags)。
3. **快捷交互工具栏**:
   - 🔍 **搜索框**：按关键词即时过滤选题。
   - 🔄 **一键同步**：调用后端 `/api/import-favs`，把 `esheep-social-favs-copilot` 最新爆款拉入 Inbox。
   - ➕ **新增选题**：手动快速创建新选题。

---

## 5. Agent & CLI Workflow

```bash
# 启动本地看板服务
python scripts/server.py --port 8000

# 从 esheep-social-favs-copilot 导入最新收藏
python scripts/import_favs.py

# 命令行操作 (方便 AI Agent 无界面交互)
python scripts/topic_manager.py list --status selected
python scripts/topic_manager.py move --id topic_1722920000_a1b2 --status in_progress
python scripts/topic_manager.py update --id topic_1722920000_a1b2 --outline "新大纲..."
```

---

## 6. Verification Plan

### Manual & Automated Verification:
1. **API & Data Tests**: 验证 `scripts/topic_manager.py` 和 `scripts/server.py` 的增删改查与 HTTP API 读写。
2. **Favs Import Integration**: 验证是否能够成功解析 `esheep-social-favs-copilot` 的 `raw_favs.json` / `content_ideas_database.md` 并增量导入。
3. **Web UI Verification**: 在浏览器中加载 `http://localhost:8000`，测试 4 列拖拽流转、弹窗编辑、实时保存等功能。
