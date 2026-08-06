import argparse
import json
import os
import sys
import subprocess


def build_info_cmd(url: str) -> list[str]:
    return ["yt-dlp", "--no-playlist", "-j", url]


def parse_info_json(stdout_text: str) -> dict:
    data = None
    for line in stdout_text.splitlines():
        line_str = line.strip()
        if line_str.startswith("{") and line_str.endswith("}"):
            try:
                data = json.loads(line_str)
                break
            except Exception:
                continue
    if not data:
        data = json.loads(stdout_text)

    title = data.get("title", "")
    uploader = data.get("uploader") or data.get("uploader_id") or data.get("channel", "")
    duration = data.get("duration", 0)
    thumbnail = data.get("thumbnail", "")

    heights = set()
    formats = data.get("formats", [])
    for fmt in formats:
        height = fmt.get("height")
        vcodec = fmt.get("vcodec")
        if height and isinstance(height, int) and vcodec and vcodec != "none":
            heights.add(height)

    sorted_heights = sorted(list(heights), reverse=True)
    available_qualities = [f"{h}p" for h in sorted_heights]

    return {
        "title": title,
        "uploader": uploader,
        "duration": duration,
        "thumbnail": thumbnail,
        "available_qualities": available_qualities,
    }


def build_download_cmd(
    url: str,
    format_type: str = "mp4",
    quality: str = "best",
    start: str = None,
    end: str = None,
    outdir: str = "."
) -> list[str]:
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = ["yt-dlp", "-o", out_template]

    if start and end:
        cmd.extend(["--download-sections", f"*{start}-{end}"])

    if format_type == "mp3":
        cmd.extend(["-x", "--audio-format", "mp3"])
    else:
        if quality and quality != "best":
            h = quality.rstrip("p")
            cmd.extend(["-f", f"bestvideo[height<={h}]+bestaudio/best", "--merge-output-format", "mp4"])
        else:
            cmd.extend(["-f", "bestvideo+bestaudio/best", "--merge-output-format", "mp4"])

    cmd.append(url)
    return cmd


def build_playlist_cmd(url: str) -> list[str]:
    return ["yt-dlp", "--flat-playlist", "-J", url]


def parse_playlist_json(stdout_text: str) -> dict:
    data = None
    for line in stdout_text.splitlines():
        line_str = line.strip()
        if line_str.startswith("{") and line_str.endswith("}"):
            try:
                data = json.loads(line_str)
                break
            except Exception:
                continue
    if not data:
        data = json.loads(stdout_text)

    entries = data.get("entries", [])
    urls = []
    for entry in entries:
        u = entry.get("url") or entry.get("webpage_url")
        if not u and entry.get("id"):
            u = f"https://www.youtube.com/watch?v={entry.get('id')}"
        if u:
            urls.append(u)
    return {"urls": urls}


def build_subtitle_cmd(url: str, lang: str = "zh-Hans,en", outdir: str = ".") -> list[str]:
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
    parser = argparse.ArgumentParser(description="esheep media downloader helper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: info
    parser_info = subparsers.add_parser("info", help="Get media metadata")
    parser_info.add_argument("url", help="Media URL")

    # Subcommand: download
    parser_dl = subparsers.add_parser("download", help="Download media")
    parser_dl.add_argument("url", help="Media URL")
    parser_dl.add_argument("--format", choices=["mp4", "mp3"], default="mp4", help="Output format")
    parser_dl.add_argument("--quality", default="best", help="Quality (e.g. 1080p, 720p, best)")
    parser_dl.add_argument("--start", help="Start timestamp HH:MM:SS")
    parser_dl.add_argument("--end", help="End timestamp HH:MM:SS")
    parser_dl.add_argument("--outdir", default=".", help="Output directory")

    # Subcommand: playlist
    parser_pl = subparsers.add_parser("playlist", help="Extract playlist video URLs")
    parser_pl.add_argument("url", help="Playlist URL")

    # Subcommand: subtitle
    parser_sub = subparsers.add_parser("subtitle", help="Download subtitles")
    parser_sub.add_argument("url", help="Media URL")
    parser_sub.add_argument("--lang", default="zh-Hans,en", help="Subtitle language comma separated")
    parser_sub.add_argument("--outdir", default=".", help="Output directory")

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
