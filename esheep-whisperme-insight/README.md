# eSheep whisperMe Insight (音视频 ASR 转录与 AI 深度分析 Skill)

`esheep-whisperme-insight` 是从 [whisperMe](https://github.com/quentin2001/whisperMe) 提取并重构优化的轻量级 Antigravity Skill。

它将音视频 ASR 转录与 AI 深度分析能力解耦：支持云端 ASR API 与本地算力，AI 深度挖掘由 Agent 直接在对话上下文内 0 成本完成。

## 目录结构

```
esheep-whisperme-insight/
├── README.md                               # 模块说明
├── .agents/skills/esheep-whisperme-insight/
│   └── SKILL.md                            # Agent 指导主入口
├── scripts/
│   └── asr_cloud.py                        # 零依赖 ASR 转录脚本 (仅需 Python 标准库 + ffmpeg)
└── references/
    ├── prompt-templates.md                 # 场景自适应 Prompt 模板库（播客/会议/讲座/访谈）
    └── gpu-probe-guide.md                  # 本地算力探测与端点探查指南
```

## 核心设计

1. **依赖自动代为执行**：检测缺失 `ffmpeg` 时，Agent 干练地向用户确认后自动安装，无需用户操作终端。
2. **云端 vs 本地双模式切换**：
   - 🌐 **云端 API 方案**：速度快、不占本地资源，提示用户发送 API Key 即可。
   - 💻 **本地方案**：免费免 Key，使用本地电脑算力，自动探测硬件环境并推荐合适的本地引擎。
   - 用户可随时在对话中自由切换。
3. **0 LLM API 开销**：总结分析 100% 走 Agent 上下文推理，无需配置任何第三方大语言模型 API Key。
4. **场景自适应**：自动识别内容类型（播客 / 会议 / 讲座 / 访谈），匹配最合适的分析模板和报告深度。
