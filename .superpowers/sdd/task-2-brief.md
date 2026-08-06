# Task 2 Brief: Create `SKILL.md` Document

## Work Files
- Create: `.agents/skills/esheep-media-downloader/SKILL.md`

## Requirements
Write `.agents/skills/esheep-media-downloader/SKILL.md` adhering strictly to `writing-skills` guidelines:

1. **YAML Frontmatter**:
   - `name: esheep-media-downloader`
   - `description`: Starts with "Use when...", third person, triggering conditions only (DO NOT summarize workflow/process details):
     `description: Use when downloading video or audio from YouTube, Bilibili, TikTok, Douyin, X/Twitter, Instagram, clipping video/audio time sections, or extracting subtitles/transcripts.`

2. **Overview & Purpose**:
   - Brief explanation of the Skill's role as a multi-platform media downloader & section clipper.

3. **Quick Reference Table**:
   - Show commands to invoke `.agents/skills/esheep-media-downloader/scripts/downloader.py` for:
     - Getting info JSON (`info <URL>`)
     - Downloading video with specified resolution (`download <URL> --quality 1080p`)
     - Section clipping (`download <URL> --start HH:MM:SS --end HH:MM:SS`)
     - Extracting MP3 audio (`download <URL> --format mp3`)
     - Downloading subtitles (`subtitle <URL> --lang zh-Hans,en`)
     - Expanding playlists (`playlist <URL>`)

4. **Direct CLI Fallback Section**:
   - Provide direct `yt-dlp` and `ffmpeg` commands if the helper script is not used.

5. **Commit**:
   - Commit with message: `"docs: add SKILL.md for esheep-media-downloader"`
