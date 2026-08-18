# eSheep Topic Master (硅基电子羊 · 深度选题助手)

`esheep-topic-master` 是电子羊 (eSheep) 系列面向自媒体与技术内容创作者的 **Markdown 驱动型深度选题助手智能体**。

告别低信息密度的“一句话备忘”，通过三大输入通道（**碎片灵感**、**外部链接**、**截图 OCR**），即时进行多维受众画像剖析、提炼 3 个高转化 Hook、构思 3 种差异化切入视角，并输出结构化内容大纲，全流程沉淀为本地 Markdown 知识库。

---

## 🌟 核心特性 (Features)

1. **💡 三大即时输入通道 (3 Ingestion Channels)**
   - **碎片想法 / 原创文本**：直接丢入一两句话或关键词，即时提炼痛点与爆点。
   - **外部链接 / 文章 / 推文**：内置 `fetch_url.py` 正文提取器，自动抓取网页与要点进行深度拆解。
   - **截图 / 图片 OCR**：利用 Agent 视觉能力（Vision）即时识别，**零本地图片留存 (Zero Image Footprint)**，即抛即存。

2. **⚡ 即时深度拆解模版 (Deep Analysis Card)**
   - 包含标准 YAML Frontmatter 元数据（ID、创建时间、来源、标签、潜力评分）。
   - **受众画像与核心痛点**：精准锚定目标读者。
   - **3 个黄金 Hook**：高点击封面标题与吸睛开头。
   - **3 种差异化切入视角**：硬核技术流 / 通俗降维流 / 商业痛点流。
   - **推荐内容大纲**：起承转合结构清晰，立即可写。
   - **个人灵感留白**：方便创作者随时批注与追加素材。

3. **🗂️ 4 阶段 Markdown 选题生命周期 (Kanban Pipeline)**
   - `topics/inbox/`：灵感收集箱（新丢入并拆解的题目）
   - `topics/selected/`：已立项选题（确认投入生产）
   - `topics/in_progress/`：创作中（正在撰写大纲、草稿或脚本）
   - `topics/completed/`：已完成 / 历史归档

4. **🛠️ 极简轻量工具链 (Zero Heavy Dependencies)**
   - 基于纯 Python 3.8+ 标准库开发，零大型第三方依赖。
   - 内置 `topic_helper.py`（创建、列表、移动状态、搜索）与 `fetch_url.py`（网页正文提取）。

---

## 📁 目录结构 (Directory Structure)

```
esheep-topic-master/
├── .agents/skills/esheep-topic-master/
│   └── SKILL.md                 # Agent Skill 规范与深度拆解 Prompt 定义
├── topics/                      # Markdown 选题文档库 (按状态分层)
│   ├── inbox/                   # 灵感收集箱
│   ├── selected/                # 已立项选题
│   ├── in_progress/             # 创作中大纲与草稿
│   └── completed/               # 已完成归档
├── scripts/
│   ├── topic_helper.py          # 选题管理 CLI：创建、索引、状态移动、搜索
│   └── fetch_url.py             # 外部网页/推文正文提取器
├── tests/
│   ├── test_topic_helper.py     # topic_helper 单元测试
│   └── test_fetch_url.py        # fetch_url 单元测试
├── pyproject.toml               # Python 基础元数据与 pytest 配置
└── README.md                    # 项目使用说明
```

---

## 🚀 快速开始 (Quickstart)

### 1. 环境准备 (Requirements)
确保安装了 Python 3.8+ 与 pytest：
```bash
python --version
```

### 2. 命令行 CLI 快速操作 (CLI Reference)

#### 📝 创建新选题卡片 (`create`)
```bash
python scripts/topic_helper.py create "DeepSeek-V3 架构深度解析" \
  --source-type link \
  --source-url "https://github.com/deepseek-ai" \
  --tags "AI技术,大模型" \
  --status inbox \
  --potential-score "8.8/10" \
  --content "## 🎯 受众画像与核心痛点\n- 目标受众: 开发者\n..."
```

#### 📋 查看选题列表 (`list`)
```bash
# 查看所有选题
python scripts/topic_helper.py list

# 按状态筛选 (inbox / selected / in_progress / completed)
python scripts/topic_helper.py list --status inbox
python scripts/topic_helper.py list --status selected

# 按标签筛选
python scripts/topic_helper.py list --tag "AI技术"

# 输出 JSON 格式 (便于外部工具或脚本集成)
python scripts/topic_helper.py list --json
```

#### 🔄 移动选题状态 (`move`)
```bash
# 通过 Topic ID、文件名或路径移动状态
python scripts/topic_helper.py move 20260818-deepseek-architecture selected
python scripts/topic_helper.py move 20260818-deepseek-architecture in_progress
python scripts/topic_helper.py move 20260818-deepseek-architecture completed
```

#### 🔍 关键词搜索 (`search`)
```bash
python scripts/topic_helper.py search "DeepSeek"
python scripts/topic_helper.py search "架构" --json
```

#### 🔗 抓取外部网页正文 (`fetch_url.py`)
```bash
python scripts/fetch_url.py "https://example.com/article"
python scripts/fetch_url.py "https://example.com/article" --json
```

---

## 🤖 配合 AI 智能体使用 (Agent Workflows)

将本 Skill 安装至 Antigravity、Claude Desktop 或其他兼容 Agent 后：

- **输入想法**：“我发现最近很多人在聊 MoE 架构，帮我拆解个选题” ➡️ Agent 即时完成受众与痛点分析、3 个 Hook、3 视角、大纲，并自动写入 `topics/inbox/`。
- **输入链接**：“分析下这篇文章 https://... 帮我构思成自媒体选题” ➡️ Agent 自动抓取正文、提炼增量价值并生成 Markdown 卡片。
- **输入截图**：直接在聊天框粘贴截图 ➡️ Agent 视觉 OCR 提炼核心观点，生成纯文本选题，不占用任何本地图片空间。
- **状态流转**：“把刚才那个 DeepSeek 选题立项” ➡️ Agent 调用 `topic_helper.py move` 自动移至 `topics/selected/`。

---

## 🧪 单元测试 (Testing)

运行全量测试套件：
```bash
pytest
```
确保所有 23+ 项单元测试全部通过。
