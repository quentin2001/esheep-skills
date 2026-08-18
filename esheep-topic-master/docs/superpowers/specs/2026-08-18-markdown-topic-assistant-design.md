# Markdown 驱动型选题助手 (Markdown-Driven Topic Assistant) 设计方案

## 1. 目标与定位 (Goals & Value)
将 `esheep-topic-master` 从原有的“可视化 Web 看板与热榜爬虫”全面重构为纯粹、高价值、基于 Markdown 的**深度选题助手智能体**。
帮助创作者在日常中快速沉淀碎片灵感、截图、推文/文章链接，并即时进行深度选题拆解、受众画像分析、差异化切入点构思与结构化大纲生成。

---

## 2. 架构与目录规划 (Architecture & Directory Structure)

```
esheep-topic-master/
├── .agents/skills/esheep-topic-master/
│   └── SKILL.md                 # 核心 Skill 定义与深度选题分析 Prompt 规范
├── topics/                      # 选题 Markdown 文档库 (按状态分层)
│   ├── inbox/                   # 灵感收集箱（新丢入并拆解的题目）
│   ├── selected/                # 已确认立项的选题
│   ├── in_progress/             # 创作中的大纲与草稿
│   └── completed/               # 已完稿/已发布的归档选题
├── scripts/
│   ├── topic_helper.py          # 极简轻量工具：索引、检索、状态转移、去重
│   └── fetch_url.py             # 链接正文提取器：丢入外部链接时抓取正文/摘要
├── tests/
│   ├── test_topic_helper.py     # topic_helper 单元测试
│   └── test_fetch_url.py        # fetch_url 单元测试
├── pyproject.toml               # Python 基础元数据
└── README.md                    # 简洁清晰的项目使用文档
```

---

## 3. 核心功能与工作流 (Core Workflows)

### 3.1 三大输入通道 (3 Ingestion Channels)
1. **💡 碎片灵感 / 想法**：用户直接丢入一两句话或关键词。
2. **🔗 外部链接**：用户丢入文章/推文/帖子 URL，系统自动抓取正文要点与原作者视角。
3. **📸 截图 / 图片**：通过 Agent Vision 能力即时 OCR 识别并提取核心论点，不保留任何本地图片缓存，即抛即存。

### 3.2 即时深度拆解模版 (Instant Deep Analysis Card)
每个选题以结构化 Markdown 文件保存（命名格式：`YYYY-MM-DD-<slug>.md`），模版规范如下：

```markdown
---
id: 20260818-deepseek-architecture
title: DeepSeek-V3 架构深度解析
created_at: 2026-08-18
source_type: idea | link | screenshot
source_url: https://...
tags: [AI技术, 架构, 深度拆解]
status: inbox
potential_score: 8.5/10
---

# 📌 选题：DeepSeek-V3 架构深度解析

## 🎯 受众画像与痛点
- **目标受众**：对大模型架构感兴趣的开发者、AI 从业者与技术爱好者
- **核心痛点**：官方论文太硬核难读，市面解读碎片化，需要系统通俗的视角

## 🪝 3 个黄金 Hook（吸睛封面/开头标题）
1. 《为什么说 DeepSeek 的架构创新，颠覆了大模型训练逻辑？》
2. 《别再硬啃论文了！10分钟带你彻底搞懂 DeepSeek-V3 底层架构》
3. 《DeepSeek 是如何做到在极低算力下打平顶级闭源模型的？》

## 🧭 3 种切入视角（差异化打法）
- **视角 A（硬核技术流）**：聚焦 MLA 与 MoE 路由机制的代码与算法实现细节
- **视角 B（通俗降维流）**：用“餐厅厨房分配任务”的生活化比喻拆解 MoE 调度
- **视角 C（商业降本流）**：从算力成本和行业落地角度分析其带来的产业冲击

## 📝 推荐内容大纲
1. **引入**：DeepSeek 为什么火爆？背后真正的技术突破是什么？
2. **核心拆解 1**：MLA 多头潜在注意力机制——显存杀手的克星
3. **核心拆解 2**：DeepSeekMoE 无辅助损失负载均衡——高效路由的秘密
4. **实践启示**：对中小团队和大模型部署的技术启示
5. **结尾升华**：未来开源技术演进趋势与行动建议

## 💭 个人笔记与思考
（创作者可随时在本地 Markdown 中继续追加批注和创作素材）
```

---

## 4. 辅助脚本设计 (Scripts & Utilities)

### 4.1 `scripts/topic_helper.py`
- `list(status="inbox")`: 扫描 `topics/` 目录，列出选题清单及评分。
- `move(topic_id_or_file, target_status)`: 将选题 `.md` 文件在 `inbox/`、`selected/`、`in_progress/`、`completed/` 之间移动。
- `search(query)`: 按标题、标签或正文关键字搜索选题。
- `create(...)`: 根据元数据和内容生成规范的 Markdown 选题文件。

### 4.2 `scripts/fetch_url.py`
- 给定 URL，通过纯 Python 标准库/基础请求提取网页标题、正文文本并去噪，为选题分析提供输入源。

---

## 5. 清理执行清单 (Cleanup Actions)
1. **删除** `web/` 目录；
2. **删除** `scripts/server.py`、`scripts/fetch_hotlist.py`、`scripts/archive_topics.py`、`scripts/import_favs.py`、`scripts/topic_manager.py`（重构为极简的 `topic_helper.py` 和 `fetch_url.py`）；
3. **清理** 旧的 `data/topics.json`（将已有有价值选题转存为 Markdown）；
4. **更新** `tests/` 测试套件适配新的 Markdown 管理与 URL 提取工具；
5. **重写** `.agents/skills/esheep-topic-master/SKILL.md` 与 `README.md`。
