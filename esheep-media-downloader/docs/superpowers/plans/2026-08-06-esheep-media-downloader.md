# esheep-media-downloader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a multi-platform media downloading & section-clipping Agent Skill (`esheep-media-downloader`) under `.agents/skills/esheep-media-downloader/`.

**Architecture:** A Python 3 CLI tool (`scripts/downloader.py`) wrapping `yt-dlp` and `ffmpeg` to provide structured JSON metadata parsing, resolution selection, remote section clipping (`--start`/`--end`), MP3 audio extraction, and subtitle downloading. Accompanied by a standard `SKILL.md` specification.

**Tech Stack:** Python 3, `yt-dlp`, `ffmpeg`, pytest.

## Global Constraints

- Skill location: `.agents/skills/esheep-media-downloader/`
- Helper script: `.agents/skills/esheep-media-downloader/scripts/downloader.py`
- Markdown skill: `.agents/skills/esheep-media-downloader/SKILL.md`

---

### Task 1: Implement `scripts/downloader.py` CLI Helper Tool

**Files:**
- Create: `.agents/skills/esheep-media-downloader/scripts/downloader.py`
- Test: `.agents/skills/esheep-media-downloader/scripts/test_downloader.py`

**Interfaces:**
- CLI commands:
  - `python downloader.py info <url>` -> JSON output
  - `python downloader.py download <url> [--format mp4|mp3] [--quality 1080p|720p] [--start HH:MM:SS] [--end HH:MM:SS] [--outdir DIR]`
  - `python downloader.py playlist <url>` -> JSON list of URLs
  - `python downloader.py subtitle <url> [--lang zh-Hans,en] [--outdir DIR]`

- [ ] **Step 1: Write unit tests for `downloader.py` command line interface**

```python
# .agents/skills/esheep-media-downloader/scripts/test_downloader.py
import json
import pytest
from unittest.mock import patch, MagicMock
import downloader

def test_parse_ytdlp_json():
    sample_output = '{"title": "Test Video", "duration": 120, "uploader": "Tester"}\n'
    info = downloader.parse_ytdlp_json(sample_output)
    assert info["title"] == "Test Video"
    assert info["duration"] == 120

def test_build_download_cmd_basic():
    cmd = downloader.build_download_cmd(
        url="https://youtube.com/watch?v=12345",
        format_choice="mp4",
        quality="1080p",
        start="00:01:00",
        end="00:02:30",
        outdir="./downloads"
    )
    assert "yt-dlp" in cmd
    assert "--download-sections" in cmd
    assert "*00:01:00-00:02:30" in cmd
    assert "bestvideo[height<=1080]+bestaudio/best" in cmd
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest .agents/skills/esheep-media-downloader/scripts/test_downloader.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'downloader'`

- [ ] **Step 3: Implement `downloader.py`**

```python
# .agents/skills/esheep-media-downloader/scripts/downloader.py
import sys
import os
import json
import argparse
import subprocess

def parse_ytdlp_json(stdout):
    for line in stdout.splitlines():
        line = line.strip()
        if line:
            return json.loads(line)
    raise ValueError("No valid JSON output from yt-dlp")

def build_download_cmd(url, format_choice="mp4", quality="best", start=None, end=None, outdir="."):
    os.makedirs(outdir, exist_ok=True)
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "-o", out_template]

    if start and end:
        cmd.extend(["--download-sections", f"*{start}-{end}"])
    elif start:
        cmd.extend(["--download-sections", f"*{start}-inf"])

    if format_choice == "mp3":
        cmd.extend(["-x", "--audio-format", "mp3"])
    else:
        if quality and quality != "best":
            try:
                height = int(quality.replace("p", ""))
                cmd.extend(["-f", f"bestvideo[height<={height}]+bestaudio/best", "--merge-output-format", "mp4"])
            except ValueError:
                cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])

    cmd.append(url)
    return cmd

def cmd_info(args):
    cmd = ["yt-dlp", "--no-playlist", "-j", args.url]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = parse_ytdlp_json(res.stdout)
    formats = []
    best_by_height = {}
    for f in data.get("formats", []):
        height = f.get("height")
        if height and f.get("vcodec", "none") != "none":
            tbr = f.get("tbr") or 0
            if height not in best_by_height or tbr > (best_by_height[height].get("tbr") or 0):
                best_by_height[height] = f
    for h in sorted(best_by_height.keys(), reverse=True):
        formats.append(f"{h}p")
    result = {
        "title": data.get("title"),
        "uploader": data.get("uploader"),
        "duration": data.get("duration"),
        "thumbnail": data.get("thumbnail"),
        "available_qualities": formats
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

def cmd_download(args):
    cmd = build_download_cmd(args.url, args.format, args.quality, args.start, args.end, args.outdir)
    res = subprocess.run(cmd, check=True)

def cmd_playlist(args):
    cmd = ["yt-dlp", "--flat-playlist", "-J", args.url]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    urls = [entry.get("url") for entry in data.get("entries", []) if entry.get("url")]
    print(json.dumps({"urls": urls}, indent=2))

def cmd_subtitle(args):
    os.makedirs(args.outdir, exist_ok=True)
    out_template = os.path.join(args.outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = [
        "yt-dlp", "--no-playlist", "--write-subs", "--write-auto-subs",
        "--sub-lang", args.lang, "--sub-format", "vtt/srt", "--skip-download",
        "-o", out_template, args.url
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="esheep-media-downloader CLI Helper")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    info_p = sub.add_parser("info")
    info_p.add_argument("url")
    info_p.set_defaults(func=cmd_info)

    dl_p = sub.add_parser("download")
    dl_p.add_argument("url")
    dl_p.add_argument("--format", choices=["mp4", "mp3"], default="mp4")
    dl_p.add_argument("--quality", default="best")
    dl_p.add_argument("--start", default=None)
    dl_p.add_argument("--end", default=None)
    dl_p.add_argument("--outdir", default=".")
    dl_p.set_defaults(func=cmd_download)

    pl_p = sub.add_parser("playlist")
    pl_p.add_argument("url")
    pl_p.set_defaults(func=cmd_playlist)

    sub_p = sub.add_parser("subtitle")
    sub_p.add_argument("url")
    sub_p.add_argument("--lang", default="zh-Hans,en")
    sub_p.add_argument("--outdir", default=".")
    sub_p.set_defaults(func=cmd_subtitle)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest .agents/skills/esheep-media-downloader/scripts/test_downloader.py -v`
Expected: PASS

- [ ] **Step 5: Commit Task 1**

```bash
git add .agents/skills/esheep-media-downloader/scripts/
git commit -m "feat: add downloader.py helper script and unit tests"
```

---

### Task 2: Create `SKILL.md` Document

**Files:**
- Create: `.agents/skills/esheep-media-downloader/SKILL.md`

- [ ] **Step 1: Write `SKILL.md` following `writing-skills` standards**

```markdown
---
name: esheep-media-downloader
description: Use when downloading video or audio from YouTube, Bilibili, TikTok, Douyin, X/Twitter, Instagram, clipping video/audio time sections, or extracting subtitles/transcripts.
---

# esheep-media-downloader

Universal media downloader and section clipper powered by `yt-dlp` and `ffmpeg`.

## Quick Reference

Use the bundled Python helper script located at `.agents/skills/esheep-media-downloader/scripts/downloader.py`:

| Task | Command |
|---|---|
| Get Video Info & Qualities | `python .agents/skills/esheep-media-downloader/scripts/downloader.py info <URL>` |
| Download Video (MP4) | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --quality 1080p` |
| Clip Time Segment (切片) | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --start 00:01:00 --end 00:02:30` |
| Extract MP3 Audio | `python .agents/skills/esheep-media-downloader/scripts/downloader.py download <URL> --format mp3` |
| Extract Subtitles/Transcript | `python .agents/skills/esheep-media-downloader/scripts/downloader.py subtitle <URL> --lang zh-Hans,en` |
| Expand Playlist | `python .agents/skills/esheep-media-downloader/scripts/downloader.py playlist <URL>` |

## Direct CLI Fallback

If Python helper is unavailable, use `yt-dlp` directly:

- **Section Clipping**: `yt-dlp --download-sections "*00:01:00-00:02:30" -f "bestvideo+bestaudio/best" --merge-output-format mp4 <URL>`
- **Audio Extraction**: `yt-dlp -x --audio-format mp3 <URL>`
- **Local ffmpeg Cut**: `ffmpeg -ss 00:01:00 -to 00:02:30 -i input.mp4 -c copy output.mp4`
```

- [ ] **Step 2: Commit Task 2**

```bash
git add .agents/skills/esheep-media-downloader/SKILL.md
git commit -m "docs: add SKILL.md for esheep-media-downloader"
```
