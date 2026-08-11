---
name: esheep-whisperme-insight
description: >-
  Use when transcribing audio or video content to text and generating
  AI-powered deep content analysis reports. Supports cloud ASR APIs,
  local ASR service detection (FunASR, faster-whisper), and local/URL
  media files. After transcription, leverages the agent's own context
  window for structured insight generation.
metadata:
  author: quentin2001
  version: "1.2.0"
  source: https://github.com/quentin2001/esheep-skills
---

# esheep-whisperme-insight

## Overview

将音频/视频内容转录为文字，然后利用 Agent 自身的上下文窗口进行深度内容挖掘与结构化分析。

**核心原则**:
1. **亲和流畅的依赖处理**: 检测缺少 `ffmpeg` 时，用自然体贴的语气请求许可，并由 Agent 自动一键安装，绝不要求用户手动输入命令。
2. **0 LLM 额外开销**: AI 深度总结完全由 Agent 自身的上下文窗口和推理能力完成，用户无需准备任何大模型 API Key。
3. **云端 / 本地自由切换**: 自然引导用户选择「云端 API」或「本地免费算力」，且随时允许切换。

## When to Use

- 用户提供了音频/视频文件（本地路径或 URL）需要转录并分析
- 需要从播客、会议录音、讲座、访谈中提取深度结构化洞察
- 用户需要配置或选择 ASR 语音识别服务（云端 API vs 本地免费算力）

**When NOT to Use:**
- 用户已经有了文字转录稿，只需要分析 → 直接使用 `references/prompt-templates.md` 中的 Prompt 模板
- 用户需要实时语音识别（流式 ASR）→ 本 Skill 处理的是离线音视频文件

## Core Workflow

```
媒体输入 (本地文件 / URL)
    │
    ▼
[Step 0] 环境依赖检查 (ffmpeg)
    └── 缺失时：用亲和语气询问“方便我现在帮您一键安装吗？”，确认后 Agent 自动安装
    │
    ▼
[Step 1] ASR 方案配置 (云端 API vs 本地免费算力)
    ├── 路径 A (云端 API): 提示发送 API Key
    └── 路径 B (本地方案): 算力检测 → 推荐 FunASR / faster-whisper 或自动连已有的本地服务
    │
    ▼
[Step 2] 媒体获取与 ASR 转录 (运行 scripts/asr_cloud.py)
    │
    ▼
[Step 3] 文本去噪 (去除中文语气词填充)
    │
    ▼
[Step 4] Agent 上下文内 AI 深度分析 (无需外部 LLM API)
    └── 将转录文本注入当前对话 → 匹配 references/prompt-templates.md 模板
    │
    ▼
输出: 结构化 Markdown 深度分析报告
```

## Step 0: First-Time Environment Setup (亲和化依赖引导)

Agent 执行前优先检测系统环境：

```bash
ffmpeg -version
```

- **正常安装**: 继续后续流程。
- **缺失 `ffmpeg`**: Agent 使用自然体贴的语气直接询问：
  > “为了能顺利读取和切分音视频内容，我们需要一个小助手组件 `ffmpeg`。我看您电脑上还没配置，方便我现在帮您一键安装一下吗？”
  > (后台自动安装命令: Windows 为 `winget install ffmpeg` / macOS 为 `brew install ffmpeg`)
- 用户回应“好的/可以/安装吧”后，Agent 直接使用 `run_command` 执行安装，无需用户任何终端操作。

## Step 1: ASR Solution Guidance (云端 vs 本地 亲和引导)

当用户首次发起转录请求，或主动要求修改设置时，Agent 用自然的口吻引导选择：

```text
在开始转录之前，先问问您的偏好（后续随时可以说‘换成云端/本地’来切换）：

1. 🌐 云端 API 方案
   - 特点：速度快、不占您电脑资源。
   - 需要：发送您已有的语音识别 API Key。

2. 💻 本地免费方案
   - 特点：完全免费，数据不出本地。
   - 需要：使用您电脑的硬件算力。我会先为您检测配置并推荐最合适的本地引擎（如 FunASR）。
```

### 路径 A: 用户选择云端 API

简明提示：
> “好的！请把您的云端 ASR API Key 发送给我，我来为您开始转录。”

后台运行转录命令：
```bash
python scripts/asr_cloud.py <media_file> \
  --provider openai \
  --api-key <USER_API_KEY> \
  --base-url <OPTIONAL_BASE_URL>
```

### 路径 B: 用户选择本地方案

1. 先运行本地服务探查：
   ```bash
   python scripts/asr_cloud.py --probe-local
   ```
   若检测到已开启的本地 ASR 服务（如 `localhost:9101` 或 `localhost:10095`），直接自动对接使用。

2. 若无已运行服务，参考 `references/gpu-probe-guide.md` 检测 GPU 算力：
   - **NVIDIA GPU (显存 ≥ 4GB)**：优先推荐部署适用于中文的 **FunASR** (SenseVoice / Paraformer) 或 `faster-whisper`。
   - **Apple Silicon (Mac M系列)**：推荐 CoreML / MPS 加速的 **FunASR** 或 `faster-whisper`。
   - **低显存 / 纯 CPU**：告知用户本地推演速度可能稍慢，可尝试 FunASR CPU 轻量模式，或根据需要随时切回云端。

## Step 2: Transcript Denoising (转录文本去噪)

对转录出的原始中文文本进行文本去噪，剔除高频无意义语气助词：

```python
import re
# 纯语气词行过滤
filler_pattern = re.compile(
    r'^[\s]*(嗯+|啊+|呃+|额+|哦+|唉+|哎+|诶+|对对对|是是是|好好好|'
    r'对的对的|没错没错|就是就是|然后然后)[\s。，、！？.,!?]*$'
)
# 行内语气词清理
filler_inline = re.compile(
    r'(?:^|(?<=[。，、！？.,!?\s]))'
    r'(?:嗯+|啊+|呃+|额+|哦+|就是说|那个|然后嘛|对吧|你知道吗|怎么说呢)'
    r'(?=[。，、！？.,!?\s]|$)'
)
```

## Step 3: AI Insight Generation in Agent Context (Agent 上下文总结)

1. **组合数据**: 媒体元数据 + 去噪转录文本。
2. **注入 Prompt**: 调取 `references/prompt-templates.md` 的深度分析模板。
3. **输出报告**: Agent 直接在对话框中生成标准的 8 节 Markdown 深度分析报告。

## Common Mistakes

| 错误 | 正确做法 |
|---|---|
| 用硬梆梆的语气要求“首次启动必须...” | 使用体贴亲和的口吻：“为了能顺利读取音视频...方便我现在帮您一键安装吗？” |
| 在提示词里加上括号解释“中立支持”、“不强加品牌”等内部废话 | 直接展示给用户简洁自然的选择项 |
| 本地方案硬套 whisper | 优先推荐中文识别效果出色的 FunASR 及 faster-whisper |
| 提示用户需要准备大模型 API Key | 明确告知 AI 深度总结由 Agent 自身完成，0 额外费用 |
