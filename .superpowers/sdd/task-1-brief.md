# Task 1 Brief: Implement `scripts/downloader.py` CLI Helper Tool

## Work Files
- Create: `.agents/skills/esheep-media-downloader/scripts/downloader.py`
- Test: `.agents/skills/esheep-media-downloader/scripts/test_downloader.py`

## Requirements
Implement a Python 3 CLI tool `downloader.py` using standard library + `yt-dlp` / `ffmpeg` underlying commands via `subprocess`.

### CLI Commands & Behaviors:
1. `python downloader.py info <URL>`:
   - Runs `yt-dlp --no-playlist -j <URL>`
   - Parses stdout JSON (handles multiline yt-dlp output safely via first non-empty line json.loads)
   - Filters formats with height and vcodec != 'none'
   - Outputs JSON string with fields: `title`, `uploader`, `duration`, `thumbnail`, `available_qualities` (sorted high to low, e.g. `["1080p", "720p", "480p"]`)

2. `python downloader.py download <URL> [--format mp4|mp3] [--quality 1080p|720p|best] [--start HH:MM:SS] [--end HH:MM:SS] [--outdir DIR]`:
   - Output template: `DIR/%(title).100s [%(id)s].%(ext)s`
   - If `--start` and `--end` are given: add `--download-sections "*start-end"`
   - If `--format mp3`: `-x --audio-format mp3`
   - If `--format mp4` and quality specified (e.g. `1080p`): `-f bestvideo[height<=1080]+bestaudio/best --merge-output-format mp4`

3. `python downloader.py playlist <URL>`:
   - Runs `yt-dlp --flat-playlist -J <URL>`
   - Outputs JSON object `{"urls": [...]}` listing video URLs in playlist.

4. `python downloader.py subtitle <URL> [--lang zh-Hans,en] [--outdir DIR]`:
   - Runs `yt-dlp --no-playlist --write-subs --write-auto-subs --sub-lang <lang> --sub-format vtt/srt --skip-download -o DIR/%(title).100s [%(id)s].%(ext)s <URL>`

## TDD Workflow
Follow Test-Driven Development:
1. Write failing tests in `test_downloader.py`.
2. Run `pytest .agents/skills/esheep-media-downloader/scripts/test_downloader.py` to confirm failure.
3. Write minimal implementation in `downloader.py`.
4. Run `pytest` to verify passing.
5. Commit changes.
