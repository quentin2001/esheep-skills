import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
import downloader


def test_downloader_module_exists():
    assert downloader is not None, "downloader module should be importable"


def test_build_info_cmd():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = downloader.build_info_cmd(url)
    assert cmd == ["yt-dlp", "--no-playlist", "-j", url]


def test_parse_info_json():
    sample_yt_dlp_json = json.dumps({
        "title": "Sample Video Title",
        "uploader": "Sample Uploader",
        "duration": 120,
        "thumbnail": "https://example.com/thumb.jpg",
        "formats": [
            {"format_id": "1", "height": 360, "vcodec": "avc1"},
            {"format_id": "2", "height": 720, "vcodec": "avc1"},
            {"format_id": "3", "height": 1080, "vcodec": "vp9"},
            {"format_id": "4", "height": 720, "vcodec": "avc1"},
            {"format_id": "5", "height": None, "vcodec": "none"},
            {"format_id": "6", "height": 480, "vcodec": "none"},
        ]
    })

    raw_stdout = f"[info] Extracting URL\n{sample_yt_dlp_json}\n"
    res = downloader.parse_info_json(raw_stdout)

    assert res["title"] == "Sample Video Title"
    assert res["uploader"] == "Sample Uploader"
    assert res["duration"] == 120
    assert res["thumbnail"] == "https://example.com/thumb.jpg"
    assert res["available_qualities"] == ["1080p", "720p", "360p"]


def test_build_download_cmd_default():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = downloader.build_download_cmd(url)
    assert "yt-dlp" in cmd
    assert "--no-playlist" in cmd
    assert url in cmd
    assert "-o" in cmd
    out_idx = cmd.index("-o")
    assert "%(title).100s [%(id)s].%(ext)s" in cmd[out_idx + 1]
    assert "-f" in cmd
    f_idx = cmd.index("-f")
    assert cmd[f_idx + 1] == "bestvideo+bestaudio/best"
    assert "--merge-output-format" in cmd
    mof_idx = cmd.index("--merge-output-format")
    assert cmd[mof_idx + 1] == "mp4"


def test_build_download_cmd_custom_quality_and_sections():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = downloader.build_download_cmd(
        url,
        format_type="mp4",
        quality="1080p",
        start="00:01:00",
        end="00:02:30",
        outdir="/tmp/output"
    )
    assert "-f" in cmd
    f_idx = cmd.index("-f")
    assert cmd[f_idx + 1] == "bestvideo[height<=1080]+bestaudio/best"
    assert "--download-sections" in cmd
    ds_idx = cmd.index("--download-sections")
    assert cmd[ds_idx + 1] == "*00:01:00-00:02:30"
    assert "-o" in cmd
    out_idx = cmd.index("-o")
    assert cmd[out_idx + 1].startswith("/tmp/output") or cmd[out_idx + 1].startswith("\\tmp\\output") or "/tmp/output" in cmd[out_idx + 1]


def test_build_download_cmd_single_start_or_end():
    url = "https://example.com/video"
    # start only
    cmd_start = downloader.build_download_cmd(url, start="00:01:00")
    assert "--download-sections" in cmd_start
    idx = cmd_start.index("--download-sections")
    assert cmd_start[idx + 1] == "*00:01:00-inf"

    # end only
    cmd_end = downloader.build_download_cmd(url, end="00:02:30")
    assert "--download-sections" in cmd_end
    idx = cmd_end.index("--download-sections")
    assert cmd_end[idx + 1] == "*00:00:00-00:02:30"


def test_build_download_cmd_cookies_from_browser():
    url = "https://example.com/video"
    cmd = downloader.build_download_cmd(url, cookies_from_browser="chrome")
    assert "--cookies-from-browser" in cmd
    idx = cmd.index("--cookies-from-browser")
    assert cmd[idx + 1] == "chrome"


def test_build_download_cmd_mp3():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = downloader.build_download_cmd(url, format_type="mp3")
    assert "-x" in cmd
    assert "--audio-format" in cmd
    af_idx = cmd.index("--audio-format")
    assert cmd[af_idx + 1] == "mp3"


def test_build_playlist_cmd():
    url = "https://www.youtube.com/playlist?list=PL12345"
    cmd = downloader.build_playlist_cmd(url)
    assert cmd == ["yt-dlp", "--flat-playlist", "-J", url]


def test_parse_playlist_json():
    sample_playlist_json = json.dumps({
        "_type": "playlist",
        "entries": [
            {"url": "https://www.youtube.com/watch?v=video1"},
            {"webpage_url": "https://bilibili.com/video/BV123"},
            {"title": "no url entry"}
        ]
    })
    res = downloader.parse_playlist_json(sample_playlist_json)
    assert res == {
        "urls": [
            "https://www.youtube.com/watch?v=video1",
            "https://bilibili.com/video/BV123"
        ]
    }


def test_build_subtitle_cmd():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    cmd = downloader.build_subtitle_cmd(url, lang="zh-Hans,en", outdir="subs_dir")
    assert "--no-playlist" in cmd
    assert "--write-subs" in cmd
    assert "--write-auto-subs" in cmd
    assert "--sub-lang" in cmd
    lang_idx = cmd.index("--sub-lang")
    assert cmd[lang_idx + 1] == "zh-Hans,en"
    assert "--sub-format" in cmd
    sf_idx = cmd.index("--sub-format")
    assert cmd[sf_idx + 1] == "vtt/srt"
    assert "--skip-download" in cmd
    assert "-o" in cmd
    out_idx = cmd.index("-o")
    assert "subs_dir" in cmd[out_idx + 1]


@patch("subprocess.run")
def test_main_cli_info(mock_run, capsys):
    mock_stdout = json.dumps({
        "title": "Test Title",
        "uploader": "Test Channel",
        "duration": 60,
        "thumbnail": "http://img.jpg",
        "formats": [{"height": 720, "vcodec": "h264"}]
    })
    mock_run.return_value = MagicMock(returncode=0, stdout=mock_stdout, stderr="")

    test_args = ["downloader.py", "info", "https://example.com/watch?v=123"]
    with patch("sys.argv", test_args):
        downloader.main()

    captured = capsys.readouterr()
    parsed_out = json.loads(captured.out)
    assert parsed_out["title"] == "Test Title"
    assert parsed_out["available_qualities"] == ["720p"]


@patch("subprocess.run")
def test_main_cli_download(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    test_args = [
        "downloader.py", "download", "https://example.com/watch?v=123",
        "--format", "mp4", "--quality", "720p", "--start", "00:00:10", "--end", "00:00:30"
    ]
    with patch("sys.argv", test_args):
        downloader.main()
    mock_run.assert_called_once()
    executed_cmd = mock_run.call_args[0][0]
    assert "*00:00:10-00:00:30" in executed_cmd


@patch("subprocess.run")
def test_main_cli_playlist(mock_run, capsys):
    mock_stdout = json.dumps({
        "entries": [{"url": "https://example.com/v1"}]
    })
    mock_run.return_value = MagicMock(returncode=0, stdout=mock_stdout, stderr="")
    test_args = ["downloader.py", "playlist", "https://example.com/playlist"]
    with patch("sys.argv", test_args):
        downloader.main()
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed == {"urls": ["https://example.com/v1"]}


@patch("subprocess.run")
def test_main_cli_subtitle(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    test_args = ["downloader.py", "subtitle", "https://example.com/v1", "--lang", "en"]
    with patch("sys.argv", test_args):
        downloader.main()
    mock_run.assert_called_once()
    executed_cmd = mock_run.call_args[0][0]
    assert "--sub-lang" in executed_cmd
    assert "en" in executed_cmd


def test_run_ytdlp_error_handling(capsys):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = downloader.subprocess.CalledProcessError(
            returncode=1, cmd=["yt-dlp"], stderr="ERROR: Private video"
        )
        with pytest.raises(SystemExit) as exc_info:
            downloader.run_ytdlp(["yt-dlp"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "ERROR: Private video" in captured.err
