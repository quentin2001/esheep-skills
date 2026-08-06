---
name: esheep-media-downloader
description: Use when downloading video or audio from YouTube, Bilibili, TikTok, Douyin, X/Twitter, Instagram, clipping video/audio time sections, or extracting subtitles/transcripts.
---

# esheep-media-downloader

## Overview

`esheep-media-downloader` provides a unified Python helper CLI and reference guide for downloading media across multiple video/audio platforms (YouTube, Bilibili, TikTok, Douyin, X/Twitter, Instagram), extracting MP3 audio, clipping specific video time sections, downloading subtitles/transcripts, and parsing playlists.

## Quick Reference

All Python helper commands use `.agents/skills/esheep-media-downloader/scripts/downloader.py`.

| Operation | Command | Description |
|---|---|---|
| **Get Media Info** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py info <URL>` | Extract video title, duration, uploader, thumbnail, and available resolutions JSON |
| **Download Video** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --quality 1080p` | Download video at specified resolution (e.g. 1080p, 720p, or best) |
| **Clip Section** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --start HH:MM:SS --end HH:MM:SS` | Download and cut a specific time section of video/audio |
| **Extract MP3** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --format mp3` | Extract audio-only stream as MP3 file |
| **Download Subtitles** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py subtitle <URL> --lang zh-Hans,en` | Download subtitles/transcripts in specified languages (VTT/SRT) |
| **Expand Playlist** | `python .agents/skills/esheep-media-downloader/scripts/downloader.py playlist <URL>` | Extract list of entry URLs from a playlist |

## Direct CLI Fallback

If the Python helper script `downloader.py` is not used, execute direct `yt-dlp` and `ffmpeg` commands:

### 1. Get Media Info (JSON)
```bash
yt-dlp --no-playlist -j "<URL>"
```

### 2. Download Video with Specified Quality
```bash
# Maximum 1080p height, merged to mp4
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best" --merge-output-format mp4 -o "%(title).100s [%(id)s].%(ext)s" "<URL>"
```

### 3. Time Section Clipping
```bash
# Using yt-dlp section download
yt-dlp --download-sections "*00:01:00-00:02:30" -f "bestvideo+bestaudio/best" --merge-output-format mp4 "<URL>"

# Alternative: ffmpeg precise clip after full download
ffmpeg -ss 00:01:00 -to 00:02:30 -i input.mp4 -c copy output.mp4
```

### 4. Extract MP3 Audio
```bash
yt-dlp -x --audio-format mp3 -o "%(title).100s [%(id)s].%(ext)s" "<URL>"
```

### 5. Download Subtitles / Transcripts
```bash
yt-dlp --no-playlist --write-subs --write-auto-subs --sub-lang "zh-Hans,en" --sub-format "vtt/srt" --skip-download "<URL>"
```

### 6. Expand Playlist URLs
```bash
yt-dlp --flat-playlist -J "<URL>"
```

## Prerequisites & Notes

- **Dependencies**: Requires `yt-dlp` and `ffmpeg` installed and available in system `PATH`.
- **Platform Support**: Works with YouTube, Bilibili, TikTok, Douyin, X/Twitter, Instagram, and 1000+ sites supported by `yt-dlp`.
- **Output Naming**: Default output filename pattern is `%(title).100s [%(id)s].%(ext)s` to prevent filesystem path length limits while ensuring unique identifiers.
