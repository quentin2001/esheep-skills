# eSheep whisperMe Insight (音视频 ASR 转录与 AI 深度分析 Skill)

`esheep-whisperme-insight` 是从 [whisperMe](https://github.com/quentin2001/whisperMe) 提取并重构优化的轻量级 Antigravity Skill。

它将音视频 ASR 转录与 AI 深度分析能力解耦：支持云端 ASR API 与本地算力（如 FunASR / faster-whisper），AI 深度挖掘由 Agent 直接在对话上下文内 0 成本完成。

## 目录结构

```
esheep-whisperme-insight/
├── README.md                           # 模块说明文档
├── .agents/skills/esheep-whisperme-insight/
│   └── SKILL.md                        # Agent 指导主入口 (含依赖自动安装、云端/本地模式引导)
├── scripts/
│   └── asr_cloud.py                    # 零依赖 ASR 转录脚本 (仅需 Python 标准库 + ffmpeg)
└── references/
    ├── prompt-templates.md             # 深度分析 Prompt 模板库与防幻觉守则
    └── gpu-probe-guide.md              # 本地算力 (FunASR / faster-whisper) 与端点探查指南
```

## 核心设计与交互原则

1. **依赖自动代为执行**：检测缺失 `ffmpeg` 等基础依赖时，Agent 自动带命令向用户寻求确认（“首次启动必须...是否允许我为您执行安装？”），获得许可后用 `run_command` 自动代为执行。
2. **云端 vs 本地双模式切换**：
   - 🌐 **云端 API 方案**：稳定高效，提示用户输入通用 API Key（OpenAI-compatible Whisper / Custom HTTP）。
   - 💻 **本地方案**：免费免 Key，使用本地电脑算力。自动探测硬件环境并优先推荐适用于中文识别的 **FunASR** 或 `faster-whisper`。
   - 用户可随时在对话中自由切换。
3. **0 LLM API 开销**：总结分析 100% 走 Agent 上下文推理，无需配置任何第三方大语言模型 API Key 或本地大模型。
