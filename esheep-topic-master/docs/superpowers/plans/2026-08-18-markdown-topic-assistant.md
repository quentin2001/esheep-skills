# Markdown 驱动型选题助手重构实施计划 (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `esheep-topic-master` 重构为基于 Markdown 文档库的纯粹、高价值、深度选题助手智能体，支持碎片想法/外部链接/截图即时深度拆解与本地化 Markdown 沉淀。

**Architecture:** 
- 存储层：以 `topics/{inbox,selected,in_progress,completed}/` 分层管理 Markdown 选题卡片，每篇带有 Frontmatter 元数据和深度拆解大纲。
- 工具层：`scripts/fetch_url.py`（外部链接正文提取）与 `scripts/topic_helper.py`（选题创建、移动、搜索、索引 CLI）。
- 智能体层：`.agents/skills/esheep-topic-master/SKILL.md` 定义完整的选题拆解 Prompt 规范、3 大输入通道与工作流。

**Tech Stack:** Python 3.8+ 标准库（`urllib`, `re`, `argparse`, `pathlib`, `html.parser`），`pytest` 测试框架。

## Global Constraints
- 不使用任何大型外部重量级依赖，保持全库极致轻量。
- 零图片本地留存：截图 OCR 后仅保存结构化文本到 Markdown，即抛即存。
- 保证 100% 测试覆盖率，所有 Python 辅助脚本具备完整 `pytest` 测试。

---

## 任务拆解 (Tasks)

### Task 1: 清理废弃旧模块与目录
**Files:**
- Delete: `esheep-topic-master/web/`
- Delete: `esheep-topic-master/scripts/server.py`
- Delete: `esheep-topic-master/scripts/fetch_hotlist.py`
- Delete: `esheep-topic-master/scripts/archive_topics.py`
- Delete: `esheep-topic-master/scripts/import_favs.py`
- Delete: `esheep-topic-master/scripts/topic_manager.py`
- Delete: `esheep-topic-master/tests/test_*.py`

- [ ] **Step 1: 删除旧 Web 与爬虫相关代码**
- [ ] **Step 2: 验证工作区清理干净**
- [ ] **Step 3: Commit 清理提交**

---

### Task 2: 实现外部链接正文提取器 (`scripts/fetch_url.py`)
**Files:**
- Create: `esheep-topic-master/scripts/fetch_url.py`
- Test: `esheep-topic-master/tests/test_fetch_url.py`

**Interfaces:**
- `fetch_article_content(url: str) -> dict`: 返回 `{"title": str, "content": str, "url": str, "error": Optional[str]}`。

- [ ] **Step 1: 编写失败的单元测试 `tests/test_fetch_url.py`**
- [ ] **Step 2: 运行测试验证失败** (`pytest tests/test_fetch_url.py`)
- [ ] **Step 3: 编写 `scripts/fetch_url.py` 核心实现**（支持通用网页正文清洗与标题解析，内置优雅降级与模拟请求头）
- [ ] **Step 4: 运行测试验证全部通过**
- [ ] **Step 5: Commit `feat: add fetch_url utility`**

---

### Task 3: 实现 Markdown 选题管理工具 (`scripts/topic_helper.py`)
**Files:**
- Create: `esheep-topic-master/scripts/topic_helper.py`
- Test: `esheep-topic-master/tests/test_topic_helper.py`

**Interfaces:**
- `create_topic(title, source_type, content, tags=None, source_url=None, status="inbox", potential_score=None, base_dir="topics") -> Path`
- `list_topics(status=None, tag=None, base_dir="topics") -> list[dict]`
- `move_topic(file_path_or_id, target_status, base_dir="topics") -> Path`
- `search_topics(query, base_dir="topics") -> list[dict]`
- CLI 支持: `python scripts/topic_helper.py list`, `create`, `move`, `search`。

- [ ] **Step 1: 编写失败的单元测试 `tests/test_topic_helper.py`**
- [ ] **Step 2: 运行测试验证失败** (`pytest tests/test_topic_helper.py`)
- [ ] **Step 3: 编写 `scripts/topic_helper.py` 完整实现与 CLI 接口**
- [ ] **Step 4: 运行测试验证全部通过**
- [ ] **Step 5: Commit `feat: add topic_helper markdown manager and CLI`**

---

### Task 4: 初始化 `topics/` 目录结构并迁移历史数据
**Files:**
- Create: `esheep-topic-master/topics/inbox/.gitkeep`
- Create: `esheep-topic-master/topics/selected/.gitkeep`
- Create: `esheep-topic-master/topics/in_progress/.gitkeep`
- Create: `esheep-topic-master/topics/completed/.gitkeep`
- Modify/Migrate: 将 `data/topics.json` 中的有效数据通过 `topic_helper` 转换为 `topics/` 下规范的 `.md` 文件
- Delete: `esheep-topic-master/data/topics.json`

- [ ] **Step 1: 创建 `topics/` 4 个状态分层子目录**
- [ ] **Step 2: 迁移现有选题至 Markdown**
- [ ] **Step 3: Commit `feat: initialize markdown topics library and migrate existing topics`**

---

### Task 5: 重写 `SKILL.md` 智能体规范与 `README.md`
**Files:**
- Modify: `esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md`
- Modify: `esheep-topic-master/README.md`

- [ ] **Step 1: 编写全新的 `SKILL.md`**：定义 3 大输入通道（想法/链接/截图 OCR）、即时深度拆解标准模版（受众、Hook、3视角、大纲、评分）与 CLI 自动化指令。
- [ ] **Step 2: 更新 `README.md`**：提供极简的创作者使用指南与工作流说明。
- [ ] **Step 3: 运行全量测试套件并验证工作区**
- [ ] **Step 4: Commit `docs: update SKILL.md and README for markdown topic assistant`**

---

## 验证计划 (Verification Plan)
1. **自动化测试**：运行 `pytest` 确保 `fetch_url` 和 `topic_helper` 100% 绿灯。
2. **端到端流程验证**：
   - 验证通过 CLI 创建/检索/移动 Markdown 选题卡片。
   - 验证通过 Agent 对话丢入链接与灵感时的即时拆解输出与 Markdown 文件生成。
