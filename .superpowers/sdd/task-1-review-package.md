# Task 1 Review Package

BASE: cb7bfeae78317ce8158376d91d6f08e9e1fcb012
HEAD: Task 1 commit

## Files Changed
- `.agents/skills/esheep-media-downloader/scripts/downloader.py`
- `.agents/skills/esheep-media-downloader/scripts/test_downloader.py`

## Implementation Code (`downloader.py`)
```python
import argparse
import json
import os
import subprocess
import sys


def parse_info_json(stdout: str) -> dict:
    """Parse yt-dlp -j stdout to extract relevant metadata."""
    data = None
    for line in stdout.splitlines():
        line = line.strip()
        if line and line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

    if not data:
        raise ValueError("Could not parse valid JSON from yt-dlp output")

    best_by_height = {}
    for f in data.get("formats", []):
        height = f.get("height")
        vcodec = f.get("vcodec", "none")
        if height and vcodec and vcodec != "none":
            tbr = f.get("tbr") or 0
            if height not in best_by_height or tbr > (best_by_height[height].get("tbr") or 0):
                best_by_height[height] = f

    qualities = [f"{h}p" for h in sorted(best_by_height.keys(), reverse=True)]

    return {
        "title": data.get("title", ""),
        "uploader": data.get("uploader", ""),
        "duration": data.get("duration"),
        "thumbnail": data.get("thumbnail", ""),
        "available_qualities": qualities,
    }


def build_info_cmd(url: str) -> list:
    return ["yt-dlp", "--no-playlist", "-j", url]


def build_download_cmd(
    url: str,
    format_type: str = "mp4",
    quality: str = "best",
    start: str = None,
    end: str = None,
    outdir: str = ".",
) -> list:
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "-o", out_template]

    if start or end:
        s = start if start else ""
        e = end if end else ""
        cmd.extend(["--download-sections", f"*{s}-{e}"])

    if format_type == "mp3":
        cmd.extend(["-x", "--audio-format", "mp3"])
    else:
        if quality and quality != "best":
            try:
                height = int(quality.replace("p", ""))
                cmd.extend(
                    [
                        "-f",
                        f"bestvideo[height<={height}]+bestaudio/best",
                        "--merge-output-format",
                        "mp4",
                    ]
                )
            except ValueError:
                cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])

    cmd.append(url)
    return cmd


def build_playlist_cmd(url: str) -> list:
    return ["yt-dlp", "--flat-playlist", "-J", url]


def parse_playlist_json(stdout: str) -> dict:
    data = json.loads(stdout)
    urls = []
    for entry in data.get("entries", []):
        url = entry.get("url") or entry.get("webpage_url")
        if not url and entry.get("id"):
            url = f"https://www.youtube.com/watch?v={entry.get('id')}"
        if url:
            urls.append(url)
    return {"urls": urls}


def build_subtitle_cmd(url: str, lang: str = "zh-Hans,en", outdir: str = ".") -> list:
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    return [
        "yt-dlp",
        "--no-playlist",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang",
        lang,
        "--sub-format",
        "vtt/srt",
        "--skip-download",
        "-o",
        out_template,
        url,
    ]


def main():
    parser = argparse.ArgumentParser(description="esheep-media-downloader CLI Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Get media metadata")
    info_parser.add_argument("url", help="Media URL")

    dl_parser = subparsers.add_parser("download", help="Download media")
    dl_parser.add_argument("url", help="Media URL")
    dl_parser.add_argument(
        "--format", choices=["mp4", "mp3"], default="mp4", help="Output format"
    )
    dl_parser.add_argument(
        "--quality", default="best", help="Video quality height (e.g. 1080p, 720p)"
    )
    dl_parser.add_argument("--start", help="Start time for clipping (HH:MM:SS)")
    dl_parser.add_argument("--end", help="End time for clipping (HH:MM:SS)")
    dl_parser.add_argument("--outdir", default=".", help="Output directory")

    pl_parser = subparsers.add_parser("playlist", help="Expand playlist URLs")
    pl_parser.add_argument("url", help="Playlist URL")

    sub_parser = subparsers.add_parser("subtitle", help="Download subtitles")
    sub_parser.add_argument("url", help="Media URL")
    sub_parser.add_argument(
        "--lang", default="zh-Hans,en", help="Subtitle languages (comma separated)"
    )
    sub_parser.add_argument("--outdir", default=".", help="Output directory")

    args = parser.parse_args()

    if args.command == "info":
        cmd = build_info_cmd(args.url)
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        res = parse_info_json(proc.stdout)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "download":
        cmd = build_download_cmd(
            args.url,
            format_type=args.format,
            quality=args.quality,
            start=args.start,
            end=args.end,
            outdir=args.outdir,
        )
        proc = subprocess.run(cmd, check=True)

    elif args.command == "playlist":
        cmd = build_playlist_cmd(args.url)
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        res = parse_playlist_json(proc.stdout)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "subtitle":
        cmd = build_subtitle_cmd(args.url, lang=args.lang, outdir=args.outdir)
        proc = subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
```
