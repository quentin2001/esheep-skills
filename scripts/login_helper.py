import os
import sys
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
    from playwright.sync_api import sync_playwright
    url = PLATFORMS[platform]
    save_path = get_session_path(platform)
    print(f"[*] Opening browser for {platform}. Please log in manually...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
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
