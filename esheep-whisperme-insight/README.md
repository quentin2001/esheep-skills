# eSheep whisperMe Insight (音视频 ASR 转录与 AI 深度分析 Skill)

`esheep-whisperme-insight` 是从 [whisperMe](https://github.com/quentin2001/whisperMe) 提取并重构优化的工业级轻量 Antigravity Skill。

它将音视频 ASR 转录与 AI 深度分析解耦：默认内置 **SenseVoiceSmall（220MB 超轻量本地底座）**，支持云端 Whisper API 与三级全平台媒体抓取管道，AI 深度挖掘由 Agent 直接在对话上下文内 0 成本完成。

## 目录结构

```
esheep-whisperme-insight/
├── README.md                               # 模块说明
├── .agents/skills/esheep-whisperme-insight/
│   └── SKILL.md                            # Agent 指导主入口 (v1.5.0)
├── scripts/
│   └── asr_engine.py                       # 统一 ASR 引擎 (SenseVoiceSmall + Cloud Whisper + 三级媒体抓取)
└── references/
    ├── prompt-templates.md                 # 场景自适应 Prompt 模板库（播客/开箱/会议/讲座/访谈）
    └── gpu-probe-guide.md                  # 本地算力探测与模型匹配指南
```

## 核心设计

1. **220MB 极速本地底座（SenseVoiceSmall）**：
   - 相比传统 2GB+ 大模型，体积缩小 90%，显存占用 < 1GB，GPU 上可达 **100x ~ 300x 实时速**；
   - 内置 VAD 与标点恢复，彻底杜绝长音频“重复吐字”；
   - 原生支持富文本声音事件与情绪感知（🎼 BGM、😊 笑声、😡 激烈情绪）。
2. **三级媒体抓取容错管道**：
   - **Tier 1**: `yt-dlp` 极速直下；
   - **Tier 2**: 动态流 / 无头浏览器嗅探（攻克抖音等短链防盗链）；
   - **Tier 3**: 优雅降级（支持本地音视频文件直接拖入）。
3. **极速直达与智能算力路由**：
   - 首次使用干练引导（云端 vs 本地 SenseVoiceSmall 220MB）；
   - 具备环境时静默全自动跑完流水线，零反复确认。
4. **0 LLM API 开销**：
   - 深度分析 100% 走 Agent 上下文推理，无需配置第三方大模型 Key。
