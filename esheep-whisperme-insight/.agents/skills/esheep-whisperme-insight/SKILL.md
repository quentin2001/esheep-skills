---
name: esheep-whisperme-insight
description: >-
  Use when transcribing audio or video content to text and generating
  AI-powered deep content analysis reports. Supports zero-cost local
  SenseVoiceSmall (220MB, ultra-fast with rich emotion tags) and cloud ASR APIs,
  3-tier universal media acquisition (Douyin, XHS, Bilibili, YouTube, Podcasts),
  and local media files. Leverages the agent's context window for structured insight.
metadata:
  author: quentin2001
  version: "1.5.0"
  source: https://github.com/quentin2001/esheep-skills
---

# esheep-whisperme-insight

## Overview

将音频/视频内容转录为文字，利用 Agent 自身的上下文窗口进行深度内容挖掘与结构化分析。

**核心原则**:
1. **轻量极速的本地底座**: 默认采用阿里开源的 **SenseVoiceSmall（仅 220MB）**，毫秒级转录，自带标点与情感/BGM 感知，完全免费且 0 门槛跑在任意硬件（GPU / CPU / Mac）上。
2. **三级媒体抓取容错**: 面对各类平台链接，依次按 `yt-dlp 快速直下` $\rightarrow$ `无头动态流嗅探` $\rightarrow$ `本地文件拖入降级` 阶梯执行，抗反爬防盗链。
3. **极速直达（Zero-Friction Auto-Pilot）**: 只要环境可用，Agent 一键静默执行全流程，直接交付结构化深度分析报告。
4. **0 LLM 额外开销**: AI 深度分析 100% 由 Agent 自身上下文完成，无需第三方大模型 Key。

## When to Use

- 用户提供了音视频链接（抖音、小红书、B站、YouTube、播客等）或本地音视频文件
- 需要对播客、会议录音、讲座、访谈、潮流开箱进行结构化深度剖析与自媒体文案逆向

## Core Workflow

```
媒体输入 (URL / 本地文件)
    │
    ▼
[Step 0] 依赖与环境检查 (ffmpeg)
    └── 缺失时：干练询问许可，确认后 Agent 自动代为安装
    │
    ▼
[Step 1] 算力探测与方案路由
    ├── 首次使用或用户要求修改偏好：呈现清晰二选一（云端 API vs 本地 SenseVoiceSmall 220MB）
    └── 具备 GPU / 已有设置：默认自动选择最优模式，静默直接执行
    │
    ▼
[Step 2] 3 级媒体抓取与 ASR 转录 (运行 scripts/asr_engine.py)
    ├── 第 1 级：yt-dlp 快速直下
    ├── 第 2 级：动态流 / 无头浏览器嗅探 (针对抖音等防盗链)
    └── 第 3 级：优雅降级（提示用户拖入本地文件）
    │
    ▼
[Step 3] 场景识别与 Agent 上下文深度分析
    └── 自动识别内容类型（播客/开箱/会议/讲座/访谈）→ 匹配 references/prompt-templates.md 模板
    │
    ▼
输出: 场景适配的结构化 Markdown 深度分析报告
```

## Step 0: Environment Setup (依赖自动代为执行)

Agent 执行前优先检测系统与 Python 环境：

1. **音视频基础组件 (`ffmpeg`)**：
   ```bash
   ffmpeg -version
   ```
   - 缺失时，Agent 干练询问：
     > “检测到当前系统尚未配置 `ffmpeg`（解析音视频所必需的组件），是否允许我现在为您自动安装？”
   - 用户确认后，Agent 直接使用 `run_command` 执行安装（Windows: `winget install ffmpeg` / macOS: `brew install ffmpeg`）。

2. **本地语音模型组件 (`funasr`, `modelscope`)**：
   若用户选择本地免费模式，Agent 预先检测 Python 库：
   ```bash
   python -c "import funasr, modelscope; print('OK')"
   ```
   - 缺失时，Agent 干练询问：
     > “首次在本地运行语音模型需要安装轻量组件（`funasr` 与 `modelscope`），是否允许我现在为您自动安装？”
   - 用户确认后，Agent 直接执行 `pip install funasr modelscope`，完成后自动加载 220MB 模型至系统公用缓存目录（`~/.cache/modelscope`），无需用户手动配置路径。

## Step 1: Compute Routing & Solution Guidance (算力路由与方案引导)

若用户首次发起转录且未指定引擎，或主动要求修改设置：

```text
在开始转录之前，先问问您的偏好（后续随时可以说‘换成云端/本地’来切换）：

1. 🌐 云端 API 方案
   - 特点：速度快、不占您电脑资源与空间。
   - 需要：发送您已有的语音识别 API Key。

2. 💻 本地免费方案 (推荐)
   - 特点：完全免费，数据不出本地。
   - 底座：采用超轻量 SenseVoiceSmall 引擎（仅 220MB，自带标点与情感感知），支持 GPU/CPU 极速运行。
```

- **路径 A（云端 API）**：提示用户发送 API Key 后执行：
  ```bash
  python scripts/asr_engine.py "<media_or_url>" --mode cloud --api-key <USER_API_KEY>
  ```
- **路径 B（本地免费，默认）**：直接运行本地极速引擎：
  ```bash
  python scripts/asr_engine.py "<media_or_url>" --mode local
  ```

## Step 2: 3-Tier Media Acquisition (三级媒体抓取执行)

`scripts/asr_engine.py` 内部已封装三级抓取管道：
- **Tier 1**: 调用 `yt-dlp` 极速抽取音轨。
- **Tier 2**: 若遇到防盗链（如抖音短链接），自动启用流嗅探捕获底层音轨。
- **Tier 3 (优雅降级)**：若平台启用强力风控滑块导致抓取失败，Agent 友好提示：
  > “检测到该平台当前启用了高级人机验证，请将该音视频下载到本地后，直接将文件路径或文件发送给我，我将立即为您解析！”

## Step 3: AI Insight Generation in Agent Context (Agent 上下文分析)

1. **读取转录结果**: 从 `asr_engine.py` 标准 JSON Lines 输出中提取去噪文本。
2. **识别内容类型**: 自动推断类型（播客 / 开箱种草 / 会议纪要 / 讲座授课 / 访谈），详见 `references/prompt-templates.md`。
3. **结合富文本情绪**: 利用 SenseVoiceSmall 转录出的声音事件与情绪标签（如 🎼背景音乐、😊笑声、😡激烈情绪），辅助分析讲者态度与视频节奏。
4. **输出报告**: Agent 直接在对话框中渲染场景适配的 Markdown 深度分析报告。
