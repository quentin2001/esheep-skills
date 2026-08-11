# eSheep whisperMe Insight (音视频 ASR 转录与 AI 深度分析 Skill)

`esheep-whisperme-insight` 是从 [whisperMe](https://github.com/quentin2001/whisperMe) 提取并蒸馏出的轻量级 Antigravity Skill。

它将音视频 ASR 转录与 AI 深度分析能力解耦：ASR 转录通过云端轻量 API 或本地已有服务完成，AI 深度挖掘直接由 Agent 在对话上下文内处理。

## 目录结构

```
esheep-whisperme-insight/
├── README.md                           # 模块说明文档
├── .agents/skills/esheep-whisperme-insight/
│   └── SKILL.md                        # Agent 指令主入口
├── scripts/
│   └── asr_cloud.py                    # 零依赖 ASR 转录脚本 (仅需 Python 标准库 + ffmpeg)
└── references/
    ├── prompt-templates.md             # 深度分析 Prompt 模板库与防幻觉守则
    └── gpu-probe-guide.md              # 本地算力与 ASR 服务端点探查指南
```

## 核心工作流

1. **媒体获取**：支持本地音视频文件，或 URL 直链 / yt-dlp 提取。
2. **ASR 转录**：通过 `scripts/asr_cloud.py` 调用云端 ASR（MiMo / OpenAI Whisper / Custom HTTP API）或检测本地服务。
3. **文本去噪**：剔除高频中文语气填充词。
4. **AI 深度分析**：将转录结果注入 Agent 上下文，应用 8 节结构化 Prompt 模板生成高含金量分析报告。

## 使用方法

将本 Skill 安装至项目 `.agents/skills` 目录后，Agent 会根据用户提问（如“帮你总结播客”、“转录音视频并分析”）自动激活并执行相应逻辑。
