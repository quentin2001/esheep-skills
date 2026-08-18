#!/usr/bin/env python3
"""
esheep-whisperme-insight - Unified ASR Engine
Supports:
1. 3-Tier Media Acquisition (yt-dlp -> Dynamic Stream Sniffer -> Local Fallback)
2. Local ASR: SenseVoiceSmall (220MB, ultra-fast, built-in VAD & punctuation, emotion detection)
3. Cloud ASR: OpenAI-compatible Whisper API, Custom HTTP endpoints
"""

import os
import sys
import re
import json
import math
import time
import urllib.request
import urllib.parse
import urllib.error
import subprocess
import argparse
import tempfile

# Prevent OpenMP collision on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Force UTF-8 on stdout and stderr for multi-platform / emoji support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ==============================================================================
# Logging Helpers
# ==============================================================================

def log_info(msg: str):
    sys.stderr.write(f"[INFO] {msg}\n")
    sys.stderr.flush()

def log_warn(msg: str):
    sys.stderr.write(f"[WARN] {msg}\n")
    sys.stderr.flush()

def log_error(msg: str):
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()

# ==============================================================================
# Tier 1 & 2: Media Acquisition Pipeline
# ==============================================================================

def extract_audio_from_media(input_source: str, output_mp3: str) -> bool:
    """
    Unified media acquisition with 3-tier fallback:
    Tier 1: yt-dlp direct extraction
    Tier 2: Stream / Douyin shortlink capture (with Playwright fallback if available)
    Tier 3: Local ffmpeg extraction if input is already a local video/audio file
    """
    # If already a local file
    if os.path.exists(input_source):
        log_info(f"Extracting audio from local file: {input_source}")
        cmd = [
            "ffmpeg", "-y",
            "-i", input_source,
            "-vn", "-codec:a", "libmp3lame", "-b:a", "128k",
            output_mp3
        ]
        res = subprocess.run(cmd, capture_output=True)
        return os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0

    if not (input_source.startswith("http://") or input_source.startswith("https://")):
        log_error(f"Input source not found or invalid URL: {input_source}")
        return False

    url = input_source
    log_info(f"Acquiring audio from URL: {url}")

    # Tier 1: yt-dlp
    log_info("Tier 1: Attempting yt-dlp direct extraction...")
    yt_cmd = [
        "yt-dlp",
        "--no-playlist",
        "-x",
        "--audio-format", "mp3",
        "-o", output_mp3.replace(".mp3", "") + ".%(ext)s",
        url
    ]
    try:
        res = subprocess.run(yt_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=60)
        if res.returncode == 0 and os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
            log_info(f"✅ Tier 1 (yt-dlp) succeeded! Audio saved: {output_mp3}")
            return True
        log_warn(f"Tier 1 yt-dlp failed or blocked: {res.stderr.strip()[:200]}")
    except Exception as e:
        log_warn(f"Tier 1 yt-dlp exception: {e}")

    # Tier 2: Dynamic / Douyin short-link resolver
    log_info("Tier 2: Attempting dynamic stream sniffer...")
    try:
        # Check if Playwright is available for dynamic stream interception
        from playwright.sync_api import sync_playwright
        target_urls = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            def on_res(response):
                u = response.url
                if ("douyinvod.com" in u or "douyinvideo.com" in u or ".mp4" in u or "video/tos/" in u):
                    if u not in target_urls and not u.startswith("blob:"):
                        target_urls.append(u)
            page.on("response", on_res)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(4000)
            except Exception:
                pass
            browser.close()

        if target_urls:
            log_info(f"Captured stream URL: {target_urls[0][:80]}...")
            cmd = [
                "ffmpeg", "-y",
                "-headers", "Referer: https://www.douyin.com/\r\n",
                "-i", target_urls[0],
                "-vn", "-codec:a", "libmp3lame", "-b:a", "128k",
                output_mp3
            ]
            res = subprocess.run(cmd, capture_output=True)
            if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
                log_info(f"✅ Tier 2 (Stream sniffer) succeeded! Audio saved: {output_mp3}")
                return True
    except ImportError:
        log_warn("Playwright not installed, skipping browser stream sniffer.")
    except Exception as e:
        log_warn(f"Tier 2 stream sniffer failed: {e}")

    # Tier 3: Return False and signal graceful fallback
    log_error("❌ Tier 1 & Tier 2 failed. Platform anti-scraping / verification active.")
    return False

# ==============================================================================
# Local ASR: SenseVoiceSmall (Primary Engine)
# ==============================================================================

def run_sensevoice_asr(audio_path: str, device: str = "auto", output_format: str = "jsonl") -> list:
    """
    Run SenseVoiceSmall ASR on audio file.
    Returns list of dicts: [{"start": 0.0, "end": 0.0, "text": "...", "emotion": "..."}]
    """
    try:
        from funasr import AutoModel
        from funasr.utils.postprocess_utils import rich_transcription_postprocess
    except ImportError:
        log_error("funasr is not installed. Please install via: pip install funasr modelscope")
        sys.exit(1)

    if device == "auto":
        # Check CUDA availability
        try:
            import torch
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"

    log_info(f"Loading SenseVoiceSmall (220MB) on device: {device}...")
    t0 = time.time()
    model = AutoModel(
        model="iic/SenseVoiceSmall",
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device=device,
        disable_update=True
    )
    log_info(f"SenseVoiceSmall ready in {round(time.time() - t0, 2)}s. Transcribing...")

    t_inf = time.time()
    res = model.generate(
        input=audio_path,
        cache={},
        language="auto",
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    log_info(f"Transcription completed in {round(time.time() - t_inf, 2)}s.")

    segments = []
    if res and len(res) > 0:
        raw_text = res[0].get("text", "")
        clean_text = rich_transcription_postprocess(raw_text)
        
        # SenseVoiceSmall with merge_vad returns full postprocessed text
        segments.append({
            "start": 0.0,
            "end": round(time.time() - t_inf, 2),
            "text": clean_text,
            "raw_rich_text": raw_text
        })

    return segments

# ==============================================================================
# Cloud ASR: OpenAI-compatible Whisper API
# ==============================================================================

def get_media_duration(file_path: str) -> float:
    try:
        cmd = ["ffmpeg", "-i", file_path]
        result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        output = result.stderr
        match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", output)
        if match:
            hours, minutes, seconds = match.groups()
            return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except Exception:
        pass
    return 0.0

def extract_mp3_chunk(file_path: str, start_sec: float, duration_sec: float, output_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-ss", str(start_sec), "-t", str(duration_sec),
            "-i", file_path, "-vn", "-acodec", "libmp3lame", "-ab", "128k", output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def call_openai_whisper(chunk_path: str, api_key: str, base_url: str = "", model: str = "whisper-1") -> list:
    if not base_url:
        base_url = "https://api.openai.com/v1"
    base_url = base_url.rstrip("/")
    url = f"{base_url}/audio/transcriptions"
    boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"

    with open(chunk_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(chunk_path)}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: audio/mpeg\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="model"\r\n\r\n'.encode("utf-8"))
    body.extend(f"{model or 'whisper-1'}\r\n".encode("utf-8"))

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="response_format"\r\n\r\n'.encode("utf-8"))
    body.extend(b"verbose_json\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }

    req = urllib.request.Request(url, data=bytes(body), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "segments" in data:
                return [{"start": s.get("start", 0.0), "end": s.get("end", 0.0), "text": s.get("text", "")} for s in data["segments"]]
            elif "text" in data:
                return [{"start": 0.0, "end": 0.0, "text": data["text"]}]
    except Exception as e:
        log_error(f"OpenAI Whisper API error: {e}")
    return []

# ==============================================================================
# Main Unified CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified ASR Engine: SenseVoiceSmall (Local 220MB) + Cloud Whisper + 3-Tier Media Fetcher"
    )
    parser.add_argument("media", nargs="?", help="Local path or URL (Douyin, XHS, Bilibili, YouTube, Podcasts, etc.)")
    parser.add_argument("--mode", choices=["auto", "local", "cloud"], default="auto", help="Execution mode (default: auto)")
    parser.add_argument("--device", default="auto", help="Compute device for local mode: auto, cuda, cpu")
    parser.add_argument("--provider", choices=["openai", "custom"], default="openai", help="Cloud ASR provider")
    parser.add_argument("--api-key", default="", help="Cloud API key")
    parser.add_argument("--base-url", default="", help="Cloud API base URL")
    parser.add_argument("--model", default="whisper-1", help="Cloud model name")
    parser.add_argument("--probe-hardware", action="store_true", help="Probe local hardware compute & exit")

    args = parser.parse_args()

    if args.probe_hardware:
        # Hardware probe
        log_info("=== Probing Hardware Compute ===")
        has_cuda = False
        gpu_name = "None"
        try:
            res = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                gpu_name = res.stdout.strip().splitlines()[0]
                has_cuda = True
        except Exception:
            pass

        print(json.dumps({
            "has_gpu": has_cuda,
            "gpu_info": gpu_name,
            "recommended_local_engine": "SenseVoiceSmall (220MB)",
            "can_run_local": True
        }, ensure_ascii=False, indent=2))
        sys.exit(0)

    if not args.media:
        parser.print_help()
        sys.exit(1)

    # 1. Acquire audio to temporary mp3
    tmp_dir = tempfile.mkdtemp()
    target_mp3 = os.path.join(tmp_dir, "extracted_audio.mp3")

    try:
        success = extract_audio_from_media(args.media, target_mp3)
        if not success:
            log_error(
                "❌ 无法从该链接自动提取音频。\n"
                "提示：平台可能启用了高级人机验证，请将该音视频文件下载到本地后，直接提供本地文件路径即可！"
            )
            sys.exit(1)

        # 2. Decide Execution Mode
        run_mode = args.mode
        if run_mode == "auto":
            # If api-key provided, prefer cloud; otherwise local SenseVoiceSmall
            if args.api_key:
                run_mode = "cloud"
            else:
                run_mode = "local"

        segments = []
        if run_mode == "local":
            log_info("Running Local ASR Engine: SenseVoiceSmall (220MB)...")
            segments = run_sensevoice_asr(target_mp3, device=args.device)
        else:
            log_info("Running Cloud ASR Engine: Whisper...")
            duration = get_media_duration(target_mp3)
            chunk_duration = 120.0
            total_chunks = max(1, math.ceil(duration / chunk_duration)) if duration > 0 else 1
            for i in range(total_chunks):
                offset = i * chunk_duration
                chunk_file = os.path.join(tmp_dir, f"chunk_{i}.mp3")
                extract_mp3_chunk(target_mp3, offset, chunk_duration, chunk_file)
                if os.path.exists(chunk_file):
                    chunk_segs = call_openai_whisper(chunk_file, args.api_key, args.base_url, args.model)
                    for s in chunk_segs:
                        s["start"] += offset
                        s["end"] += offset
                        segments.append(s)
                    os.remove(chunk_file)

        # 3. Output standard JSON Lines
        for seg in segments:
            sys.stdout.write(json.dumps(seg, ensure_ascii=False) + "\n")
            sys.stdout.flush()

    finally:
        if os.path.exists(target_mp3):
            os.remove(target_mp3)
        if os.path.exists(tmp_dir):
            try:
                os.rmdir(tmp_dir)
            except Exception:
                pass

if __name__ == "__main__":
    main()
