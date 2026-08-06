# Task 1 Report: Implement `scripts/downloader.py` CLI Helper Tool

## Status: DONE

## Overview
Successfully implemented the `downloader.py` CLI helper script and associated unit tests in `.agents/skills/esheep-media-downloader/scripts/` following strict TDD guidelines.

## Created Files
- `.agents/skills/esheep-media-downloader/scripts/downloader.py`
- `.agents/skills/esheep-media-downloader/scripts/test_downloader.py`

## TDD Workflow Execution
1. **Red Phase**: Wrote unit tests covering all 4 CLI subcommands and JSON parsing logic in `test_downloader.py`. Executed `pytest` and verified expected failure (10 failing tests due to missing module).
2. **Green Phase**: Implemented `downloader.py` CLI helper tool with standard library (`argparse`, `json`, `subprocess`, `os`, `sys`) and commands targeting `yt-dlp`.
3. **Verification**: Re-ran `pytest .agents/skills/esheep-media-downloader/scripts/test_downloader.py`. All 13 unit tests passed (100% pass rate in 0.07s).
4. **Git Commit**: Staged and committed changes with message `"feat: add downloader.py helper script and unit tests"` (Commit hash: `90271c5`).

## Implemented Functionality
1. `downloader.py info <URL>`:
   - Command: `yt-dlp --no-playlist -j <URL>`
   - Safely parses JSON stdout, extracts title, uploader, duration, thumbnail.
   - Filters video formats where `height` is present and `vcodec != 'none'`.
   - Returns JSON output with sorted `available_qualities` (e.g. `["1080p", "720p", "480p"]`).

2. `downloader.py download <URL> [--format mp4|mp3] [--quality 1080p|720p|best] [--start HH:MM:SS] [--end HH:MM:SS] [--outdir DIR]`:
   - Output template: `DIR/%(title).100s [%(id)s].%(ext)s`
   - Supports `--download-sections "*start-end"` when `--start` and `--end` are supplied.
   - Supports mp3 audio extraction (`-x --audio-format mp3`).
   - Supports quality selection (`-f bestvideo[height<=1080]+bestaudio/best --merge-output-format mp4`).

3. `downloader.py playlist <URL>`:
   - Command: `yt-dlp --flat-playlist -J <URL>`
   - Extracts video URLs from entries and returns `{"urls": [...]}`.

4. `downloader.py subtitle <URL> [--lang zh-Hans,en] [--outdir DIR]`:
   - Command: `yt-dlp --no-playlist --write-subs --write-auto-subs --sub-lang <lang> --sub-format vtt/srt --skip-download -o DIR/%(title).100s [%(id)s].%(ext)s <URL>`
