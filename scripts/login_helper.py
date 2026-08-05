import os
import sys

# Ensure root project directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import argparse
from scripts.config import SESSIONS_DIR

PLATFORMS = {
    "bilibili": "https://passport.bilibili.com/login",
    "zhihu": "https://www.zhihu.com/signin",
    "xiaohongshu": "https://www.xiaohongshu.com",
    "douyin": "https://www.douyin.com",
    "x": "https://x.com/i/flow/login"
}

def get_session_path(platform: str) -> str:
    if platform not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}")
    return os.path.join(SESSIONS_DIR, f"{platform}_state.json")

def login_platform(platform: str):
    import platform as sys_platform
    import webbrowser
    from playwright.sync_api import sync_playwright

    url = PLATFORMS[platform]
    save_path = get_session_path(platform)
    print(f"[*] Opening browser for {platform}. Please log in manually...")

    # Cross-platform popup fallback: Open system default browser just in case
    try:
        webbrowser.open(url)
    except Exception:
        pass

    with sync_playwright() as p:
        browser = None
        # Try native system Chrome or Edge first for best desktop focus on Mac & Windows
        for channel in ["chrome", "msedge", None]:
            try:
                if channel:
                    browser = p.chromium.launch(channel=channel, headless=False, args=["--start-maximized"])
                else:
                    browser = p.chromium.launch(headless=False, args=["--start-maximized"])
                break
            except Exception:
                continue

        if not browser:
            raise RuntimeError("Could not launch Chromium browser.")

        try:
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.goto(url)
            try:
                page.bring_to_front()
            except Exception:
                pass

            # Mac osascript bring window to front fallback
            if sys_platform.system() == "Darwin":
                try:
                    import subprocess
                    subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'], check=False)
                except Exception:
                    pass

            input(f"[>] Press ENTER in this console after you have successfully logged into {platform}...")
            context.storage_state(path=save_path)
            print(f"[✓] Saved session state to {save_path}")
        finally:
            browser.close()

def main():
    parser = argparse.ArgumentParser(description="Interactive Login Helper for Social Platforms")
    parser.add_argument(
        "--platform",
        choices=list(PLATFORMS.keys()) + ["all"],
        required=True,
        help="Platform to log in"
    )
    args = parser.parse_args()

    if args.platform == "all":
        for p in PLATFORMS:
            login_platform(p)
    else:
        login_platform(args.platform)

if __name__ == "__main__":
    main()
