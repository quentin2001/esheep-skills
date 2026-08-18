<p align="center">
  <img src="assets/logo.png" alt="eSheep Logo" width="120" />
</p>

# eSheep Skills (硅基电子羊 Agent Skill 集合)

本仓库包含了 eSheep (硅基电子羊) 开发维护的一系列通用 AI Agent Skills。  
每个 Skill 以标准化的独立模块形式提供特定的自媒体、内容抓取、音视频分析与选题管理能力。  
兼容各类主流 AI Coding Agent（如 Claude Code, Cursor, OpenCode, Antigravity 等）。

## 模块列表

| Skill 名称 | 说明 |
|---|---|
| [🎬 **esheep-media-downloader**](./esheep-media-downloader) | 社交媒体无水印音视频/封面极速下载工具 |
| [🗃️ **esheep-social-favs-copilot**](./esheep-social-favs-copilot) | 抖音、X(Twitter) 个人收藏与点赞记录精准捕获与归档 |
| [🗂️ **esheep-topic-master**](./esheep-topic-master) | 自媒体爆款选题全生命周期看板与灵感文本化管理系统 |
| [🎙️ **esheep-whisperme-insight**](./esheep-whisperme-insight) | 播客与音视频 ASR 云端转录 + Agent 上下文 AI 深度内容提炼 |

## 安装与同步

每个 Skill 包含标准的 `.agents/skills/<skill-name>/SKILL.md` 配置，置于 Agent 工作区后即可自动识别激活。
