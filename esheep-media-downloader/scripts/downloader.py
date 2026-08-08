import argparse
import json
import os
import subprocess
import sys


def build_info_cmd(url: str) -> list[str]:
    return ["yt-dlp", "--no-playlist", "-j", url]


def parse_info_json(stdout_text: str) -> dict:
    """Parse yt-dlp -j stdout, extracting structured metadata."""
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
    for fmt in data.get("formats", []):
        height = fmt.get("height")
        vcodec = fmt.get("vcodec")
        if height and isinstance(height, int) and vcodec and vcodec != "none":
            heights.add(height)

    available_qualities = [f"{h}p" for h in sorted(heights, reverse=True)]

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
    outdir: str = ".",
    cookies_from_browser: str = None,
) -> list[str]:
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "-o", out_template]

    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])

    # Support --start only, --end only, or both
    if start and end:
        cmd.extend(["--download-sections", f"*{start}-{end}"])
    elif start:
        cmd.extend(["--download-sections", f"*{start}-inf"])
    elif end:
        cmd.extend(["--download-sections", f"*00:00:00-{end}"])

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
    """Parse yt-dlp --flat-playlist -J stdout, extracting video URLs."""
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

    urls = []
    for entry in data.get("entries", []):
        u = entry.get("url") or entry.get("webpage_url")
        if u:
            urls.append(u)
    return {"urls": urls}


def build_subtitle_cmd(url: str, lang: str = "zh-Hans,en", outdir: str = ".",
                       cookies_from_browser: str = None) -> list[str]:
    out_template = os.path.join(outdir, "%(title).100s [%(id)s].%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang", lang,
        "--sub-format", "vtt/srt",
        "--skip-download",
        "-o", out_template,
    ]
    if cookies_from_browser:
        cmd.extend(["--cookies-from-browser", cookies_from_browser])
    cmd.append(url)
    return cmd


def run_ytdlp(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    """Run a yt-dlp command with friendly error handling."""
    try:
        return subprocess.run(cmd, capture_output=capture, text=True, check=True)
    except FileNotFoundError:
        print("Error: yt-dlp not found. Install it with: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        # Extract the last meaningful error line from yt-dlp output
        error_lines = [l for l in stderr.splitlines() if l.strip().startswith("ERROR")]
        if error_lines:
            print(f"yt-dlp error: {error_lines[-1]}", file=sys.stderr)
        else:
            print(f"yt-dlp failed (exit code {e.returncode}): {stderr[-200:]}", file=sys.stderr)
        sys.exit(e.returncode)


def main():
    parser = argparse.ArgumentParser(description="esheep media downloader helper CLI")
    parser.add_argument("--cookies-from-browser", default=None,
                        help="Browser to extract cookies from (e.g. chrome, edge, firefox)")
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
    cookies = args.cookies_from_browser

    if args.command == "info":
        cmd = build_info_cmd(args.url)
        if cookies:
            cmd.insert(-1, "--cookies-from-browser")
            cmd.insert(-1, cookies)
        proc = run_ytdlp(cmd, capture=True)
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
            cookies_from_browser=cookies,
        )
        run_ytdlp(cmd)

    elif args.command == "playlist":
        cmd = build_playlist_cmd(args.url)
        if cookies:
            cmd.insert(-1, "--cookies-from-browser")
            cmd.insert(-1, cookies)
        proc = run_ytdlp(cmd, capture=True)
        res = parse_playlist_json(proc.stdout)
        print(json.dumps(res, ensure_ascii=False, indent=2))

    elif args.command == "subtitle":
        cmd = build_subtitle_cmd(args.url, lang=args.lang, outdir=args.outdir,
                                 cookies_from_browser=cookies)
        run_ytdlp(cmd)


if __name__ == "__main__":
    main()
