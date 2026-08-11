---
name: esheep-whisperme-insight
description: >-
  Use when transcribing audio or video content to text and generating
  AI-powered deep content analysis reports. Supports cloud ASR APIs
  (OpenAI Whisper, custom HTTP), local ASR service detection (FunASR,
  faster-whisper), and local/URL media files. After transcription,
  leverages the agent's own context window for structured insight generation.
metadata:
  author: quentin2001
  version: "1.1.0"
  source: https://github.com/quentin2001/esheep-skills
---

# esheep-whisperme-insight

## Overview

将音频/视频内容转录为文字，然后利用 Agent 自身的上下文窗口进行深度内容挖掘与结构化分析。

**核心原则**:
1. **依赖自动接管**: 首次使用遇到缺失依赖（如 `ffmpeg`），Agent 直接带着明确结果询问用户许可并代为执行安装，绝不让小白用户手动切终端输入命令。
2. **零 LLM 额外开销**: AI 深度总结完全由 Agent 自身的上下文窗口和推理能力完成，用户无需准备任何大语言模型 API Key 或本地运行开源 LLM。
3. **方案自由切换**: 清楚提示「云端 ASR」与「本地方案（免费，耗电脑算力）」的差别，并随时允许用户更改配置。

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
[Step 0] 首次依赖检测 (ffmpeg 检查)
    └── 若缺失 → Agent 明确询问许可并代为执行安装命令
    │
    ▼
[Step 1] ASR 方案配置 (云端 API vs 本地免费算力)
    ├── 路径 A (云端 API): 提示需 API Key（支持通用 OpenAI-compatible / Custom ASR）
    └── 路径 B (本地方案): 运行算力检测 → 推荐 FunASR / faster-whisper 或探查本地服务
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

## Step 0: First-Time Environment Auto-Setup (首次启动环境检查)

Agent 执行前优先检测系统环境：

```bash
ffmpeg -version
```

- **正常安装**: 继续后续流程。
- **缺失 `ffmpeg`**: **严禁要求小白用户手动打开终端输入命令**。Agent 必须直接给出确定性询问并带结果请求确认：
  > “首次启动必须安装音视频基础组件 `ffmpeg`，是否允许我现在为您自动执行安装？”
  > (后台安装命令: Windows 为 `winget install ffmpeg` / macOS 为 `brew install ffmpeg`)
- 用户回应“可以/允许/好的”后，Agent 直接使用 `run_command` 执行安装。

## Step 1: ASR Solution Configuration (云端 vs 本地方案引导)

当用户首次发起转录请求，或主动要求修改设置时，Agent 引导用户选择方案：

```text
为将音视频转为文字，请选择您偏好的 ASR 语音识别方案（您可以随时在后续对话中要求更改）：

1. 🌐 云端 API 方案
   - 优点：稳定、速度快，不消耗您电脑的算力。
   - 要求：需要提供您的 ASR API Key（支持标准 OpenAI-compatible Whisper 或通用 HTTP 接口）。

2. 💻 本地免费方案
   - 优点：完全免费，数据不出本地。
   - 要求：消耗您电脑自身的 GPU/CPU 算力。Agent 将为您检测硬件并推选最适宜的模型（如 FunASR / faster-whisper）。
```

### 路径 A: 用户选择云端 API

引导提示：
> “请发送您的云端 ASR API Key（支持任何 OpenAI-compatible Whisper API 格式服务）。”

直接运行转录命令：
```bash
python scripts/asr_cloud.py <media_file> \
  --provider openai \
  --api-key <USER_API_KEY> \
  --base-url <OPTIONAL_BASE_URL>
```

### 路径 B: 用户选择本地方案

1. Agent 先运行本地服务探查：
   ```bash
   python scripts/asr_cloud.py --probe-local
   ```
   若检测到已运行的本地 ASR 服务（如 `localhost:9101` 或 `localhost:10095`），直接对接使用。

2. 若无已运行服务，参考 `references/gpu-probe-guide.md` 检测 GPU 算力：
   ```bash
   # Windows NVIDIA 检测
   nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
   ```
   - **NVIDIA GPU (显存 ≥ 4GB)**：优先推荐部署 **FunASR** (SenseVoice / Paraformer) 或 `faster-whisper`（中文识别精度高、推理速度极快）。
   - **Apple Silicon (Mac M系列)**：推荐使用 CoreML 加速的 `faster-whisper` 或 FunASR。
   - **低显存 / 纯 CPU**：告知用户本地推演速度较慢，引导是否尝试轻量 FunASR CPU 模式或切换回云端。

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

## Step 3: AI Insight Generation in Agent Context (Agent 内全自动总结)

**极其重要**: 本 Skill 生成结构化总结**完全依靠 Agent 自身的对话上下文**，用户不需要部署任何本地 LLM 或购买大语言模型 API Key。

1. **组合数据**: 媒体元数据 + 去噪转录文本。
2. **注入 Prompt**: 调取 `references/prompt-templates.md` 的深度分析模板。
3. **输出报告**: Agent 直接在聊天框生成标准的 8 节 Markdown 深度分析报告。

## Common Mistakes

| 错误 | 正确做法 |
|---|---|
| 发现缺少 ffmpeg 时抛给用户自己命令去终端敲 | 带着明确命令询问“首次启动必须安装...是否允许我执行？”，确认后 Agent 自动执行 |
| 推荐特定的具体商业云端 API 厂商 | 保持通用，提示用户提供 OpenAI-compatible 或标准 HTTP ASR Key |
| 本地方案写死只支持 whisper | 优先根据硬件推荐适合中文的 **FunASR** 及 faster-whisper |
| 提示用户需要配备大模型 API Key 才能总结 | 明确告知 AI 深度总结由 Agent 自身完成，0 额外大模型 API 费用 |
