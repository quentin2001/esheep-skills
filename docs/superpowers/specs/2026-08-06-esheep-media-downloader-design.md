# Design Specification: `esheep-media-downloader` Skill

## Overview

`esheep-media-downloader` is a workspace-specific Agent Skill located at `.agents/skills/esheep-media-downloader`. It provides powerful multi-platform media downloading, format selection, time-section clipping (切片), playlist expansion, and subtitle extraction capabilities powered by `yt-dlp` and `ffmpeg`.

## Goals

1. Support 1000+ video/audio platforms (YouTube, Bilibili, TikTok, Douyin, Xiaohongshu, Twitter/X, Instagram, etc.).
2. Offer precise time-range clipping (`--start` / `--end`) directly during download to save bandwidth and execution time.
3. Provide audio extraction (MP3/M4A) and subtitle/transcript downloading for AI processing.
4. Supply a robust Python helper CLI tool (`scripts/downloader.py`) alongside `SKILL.md` to ensure error-free command execution by AI agents.

## Component Structure

```
.agents/skills/esheep-media-downloader/
├── SKILL.md
└── scripts/
    └── downloader.py
```

### 1. `scripts/downloader.py` (CLI Helper Script)

A Python 3 script using standard library + `yt-dlp` / `ffmpeg` underlying tools via `subprocess` or `yt_dlp` Python package.

#### CLI Commands:

- **Metadata Inspection**:
  ```bash
  python .agents/skills/esheep-media-downloader/scripts/downloader.py info <URL>
  ```
  Returns JSON output containing: `title`, `duration`, `uploader`, `thumbnail`, `formats` (resolutions list: 1080p, 720p, etc.), `subtitles`.

- **Media Download & Time Slicing**:
  ```bash
  python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> [--format mp4|mp3] [--quality 1080p|720p|4k|best] [--start HH:MM:SS] [--end HH:MM:SS] [--outdir DIR]
  ```
  - `--format mp4`: Merges best video + best audio matching height requirement.
  - `--format mp3`: Extracts audio stream and converts to MP3.
  - `--start` and `--end`: Appends `--download-sections "*start-end"` to `yt-dlp` to perform remote chunked section clipping without downloading full video.

- **Playlist Unpacking**:
  ```bash
  python .agents/skills/esheep-media-downloader/scripts/downloader.py playlist <URL>
  ```
  Returns JSON list of individual video URLs in the playlist/album.

- **Subtitle Extraction**:
  ```bash
  python .agents/skills/esheep-media-downloader/scripts/downloader.py subtitle <URL> [--lang zh-Hans,en] [--outdir DIR]
  ```
  Downloads VTT/SRT subtitle files for transcripts without downloading video binary.

### 2. `SKILL.md` (Skill Definition)

Follows `writing-skills` standards:
- YAML frontmatter with `name: esheep-media-downloader` and `description` focusing purely on triggering conditions ("Use when...").
- Quick reference table for common workflows (downloading 1080p video, clipping 1-min highlight, extracting MP3 audio, getting transcripts).
- Fallback raw `yt-dlp` and `ffmpeg` CLI commands.

## Environment & Prerequisites

- `yt-dlp`: Auto-detected; if missing, auto-prompt or install via `pip install yt-dlp`. Auto-update attempt when invoking helper script.
- `ffmpeg`: Auto-detected on system PATH.

## Verification & Testing Plan

1. Verify Python CLI helper (`info`, `download`, `audio`, `playlist`, `subtitle`) with test URLs.
2. Test time-slicing functionality (`--start` / `--end`).
3. Verify `SKILL.md` structure against `writing-skills` guidelines.
