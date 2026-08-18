---
name: esheep-topic-master
description: Use when capturing fleeting ideas, analyzing external links or tweets, processing screenshot inspirations via Vision OCR, and managing Markdown-based topic cards and content lifecycle pipeline.
---

# eSheep Topic Master (硅基电子羊 · 深度选题助手)

`esheep-topic-master` 是面向内容创作者的 Markdown 驱动型**专业、深度、高价值内容选题助手智能体**。
它将碎片灵感、外部文章/推文链接、截图图片即时转化为高信息密度、多维切入角、带结构化大纲的 Markdown 选题卡片，并在本地 `topics/` 知识库中进行生命周期全流程管理。

---

## 🎯 核心定位与原则

1. **深度优先，拒绝浅尝辄止**：不只记录“一句话标题”，而是即时完成受众痛点分析、3 个高点击 Hook、3 种差异化切入视角与结构化内容大纲。
2. **纯粹 Markdown 驱动**：所有选题均以标准 Markdown + YAML Frontmatter 形式存储在本地 `topics/` 目录中，天然适配 Git 版本管理与 Obsidian / Logseq 等笔记生态。
3. **零图片留存原则 (Zero Local Image Footprint)**：处理图片/截图时，通过 Vision OCR 提取结构化文本后即抛即存，不生成任何本地图片垃圾与缓存。

---

## 📥 三大输入通道与工作流 (3 Ingestion Channels)

用户可以通过对话以三种方式向智能体提供选题素材，Agent 需自动调用相应工具并执行深度拆解：

```
                    ┌─────────────────────────┐
                    │      用户输入素材       │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
    💡 碎片想法/文本        🔗 外部文章/推文链接       📸 截图/图片灵感
         │                       │                       │
   直接提取核心要点        调用 fetch_url.py 抓取正文   Agent Vision OCR 提取文本
         │                       │                  (不保留本地图片文件)
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                     ⚡ 即时深度拆解分析
                 (受众画像 / 3 Hooks / 3 视角 / 大纲)
                                 │
                                 ▼
                     💾 自动保存至 Markdown
                    topics/inbox/YYYY-MM-DD-<slug>.md
```

### 1. 💡 碎片想法 / 原创文本 (Idea / Text)
- **触发场景**：用户在聊天中丢入一两句话、灵感片段、行业观察或关键词。
- **处理方式**：直接提炼核心论点与潜在爆点，立即进行深度选题拆解。

### 2. 🔗 外部链接 / 推文 / 文章 (URL / Link)
- **触发场景**：用户丢入知乎、微信公众号、X (Twitter)、B站专栏或技术博客 URL。
- **处理方式**：
  1. 调用 `scripts/fetch_url.py` 提取网页标题、摘要与正文文本：
     ```bash
     python scripts/fetch_url.py "<URL>" --json
     ```
  2. 结合抓取到的正文内容与原作者观点，提取核心增量价值与痛点，执行深度拆解。
  3. 在元数据中保留 `source_url`。

### 3. 📸 截图 / 图片灵感 (Screenshot / Image OCR)
- **触发场景**：用户在聊天中发送社交媒体截图、文章段落截图或聊天记录截图。
- **处理方式**：
  1. 利用 Agent 视觉多模态能力（Vision）立即进行 OCR 与关键信息提取（标题、论点、数据、评论金句）。
  2. **严格禁止在本地持久化保存截图文件**，实现零本地图片占用（即抛即存）。
  3. 将提取的结构化文本作为素材执行深度拆解，`source_type` 标记为 `screenshot`。

---

## 📋 即时深度拆解标准模版 (Deep Analysis Specification)

每当接收到新素材并完成深度分析后，Agent 需输出完整的选题卡片，并自动写入 `topics/inbox/YYYY-MM-DD-<slug>.md`：

```markdown
---
id: 20260818-deepseek-architecture
title: DeepSeek-V3 架构深度解析
created_at: 2026-08-18
source_type: idea | link | screenshot | original_idea
source_url: https://example.com/article
tags: [AI技术, 架构设计, 深度拆解]
status: inbox
potential_score: 8.8/10
---

# 📌 选题：DeepSeek-V3 架构深度解析

## 🎯 受众画像与核心痛点
- **目标受众**：对大模型架构与工程落地感兴趣的开发者、AI 从业者与技术博主。
- **核心痛点**：官方论文专业术语多、门槛高；市面解读多为浅层复述，缺乏对 MLA 注意力机制与 MoE 路由工程创新的直观剖析。

## 🪝 3 个黄金 Hook（吸睛封面 / 开头标题）
1. 《为什么说 DeepSeek 的架构创新，颠覆了大模型训练逻辑？》
2. 《别再硬啃论文了！10分钟带你彻底搞懂 DeepSeek-V3 底层架构》
3. 《DeepSeek 是如何做到在极低算力下打平顶级闭源模型的？》

## 🧭 3 种切入视角（差异化打法）
- **视角 A（硬核技术流）**：聚焦 MLA 与 MoE 路由机制的代码与算法实现细节，对比传统 Transformer 架构。
- **视角 B（通俗降维流）**：用“餐厅厨房分配任务”的生活化比喻拆解 MoE 调度，适合做短视频或通俗科普。
- **视角 C（商业降本流）**：从算力成本和行业落地角度分析其带来的产业冲击与中小企业开源落地方案。

## 📝 推荐内容大纲
1. **引入**：DeepSeek 为什么火爆？背后真正的技术突破是什么？
2. **核心拆解 1**：MLA 多头潜在注意力机制——显存杀手的克星。
3. **核心拆解 2**：DeepSeekMoE 无辅助损失负载均衡——高效路由的秘密。
4. **实践启示**：对中小团队和大模型部署的技术启示与工程权衡。
5. **结尾升华**：未来开源技术演进趋势与行动建议。

## 💭 个人笔记与思考
（创作者可随时在本地 Markdown 中继续追加批注、案例素材与金句）
```

---

## 🗂️ 选题 4 阶段生命周期与目录规范

选题卡片按照创作推进状态在 `topics/` 目录下分层管理：

| 状态 (Status) | 所在目录 | 说明 | 典型操作 |
|---|---|---|---|
| `inbox` | `topics/inbox/` | 收集箱：新录入、待评估的深度拆解卡片 | 审阅评估，立项移至 `selected` |
| `selected` | `topics/selected/` | 已立项：确认准备投入生产的优质选题 | 细化大纲与素材，移至 `in_progress` |
| `in_progress` | `topics/in_progress/` | 创作中：正在进行文案草稿或视频脚本撰写 | 完成成稿，移至 `completed` |
| `completed` | `topics/completed/` | 已完成：已成稿发布或归档的选题 | 沉淀为历史资产供后续复用 |

---

## 🛠️ CLI 辅助工具命令参考

所有文件与状态流转操作可通过 `scripts/topic_helper.py` 和 `scripts/fetch_url.py` 极简完成：

### 1. 创建选题 (`create`)
```bash
python scripts/topic_helper.py create "选题标题" \
  --source-type link \
  --source-url "https://example.com" \
  --tags "AI,大模型" \
  --status inbox \
  --potential-score "8.5/10" \
  --content "## 🎯 受众画像与核心痛点\n..."
```

### 2. 查看选题列表 (`list`)
```bash
# 查看所有状态选题
python scripts/topic_helper.py list

# 按状态筛选
python scripts/topic_helper.py list --status inbox
python scripts/topic_helper.py list --status selected

# 按标签筛选
python scripts/topic_helper.py list --tag "AI技术"

# 输出 JSON 格式
python scripts/topic_helper.py list --json
```

### 3. 移动选题状态 (`move`)
```bash
# 支持按 Topic ID、文件名或相对路径移动
python scripts/topic_helper.py move 20260818-deepseek-architecture selected
python scripts/topic_helper.py move 20260818-deepseek-architecture in_progress
python scripts/topic_helper.py move 20260818-deepseek-architecture completed
```

### 4. 关键词搜索 (`search`)
```bash
python scripts/topic_helper.py search "DeepSeek"
python scripts/topic_helper.py search "AI" --json
```

### 5. 抓取外部网页正文 (`fetch_url.py`)
```bash
python scripts/fetch_url.py "https://example.com/article"
python scripts/fetch_url.py "https://example.com/article" --json
```

---

## 💡 对话交互准则 (Agent Guidelines)

1. **自动入库沉淀**：当用户在对话中抛出点子、链接或截图时，Agent 完成深度拆解后应**立即调用 `scripts/topic_helper.py create` 或写入 Markdown 文件**，并在回答最后告知用户卡片已存储路径（例如 `topics/inbox/2026-08-18-deepseek-v3.md`）。
2. **主动提供下一步建议**：给出拆解后，询问用户是否要立项（移入 `selected`）或针对其中某个切入视角展开撰写初稿。
3. **保持高信息密度**：3 个 Hook 需具备传播爆款属性，3 个切入视角需风格鲜明各具特色，大纲需逻辑严密具备可执行性。
