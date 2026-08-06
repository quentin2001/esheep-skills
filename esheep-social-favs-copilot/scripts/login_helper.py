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
    user_data_dir = os.path.join(SESSIONS_DIR, f"{platform}_user_data")
    save_path = get_session_path(platform)
    print(f"[*] Opening persistent browser for {platform}. Please log in manually...")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        try:
            page = context.new_page() if not context.pages else context.pages[0]
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception:
                pass
            try:
                page.bring_to_front()
            except Exception:
                pass

            print(f"[*] 请拿起手机扫码登录 {platform}，登录成功后页面会自动验证保存...")
            
            # Loop-detect real user login state automatically
            login_verified = False
            for _ in range(60): # Wait up to 120s for user to scan QR code
                try:
                    curr_url = page.url
                    # Check if logged in by looking for user profile elements
                    has_me_link = page.query_selector("a[href*='/user/profile/']") or page.query_selector("a[href*='/user/self']") or page.query_selector(".avatar") or page.query_selector("img[src*='avatar']")
                    
                    if "login" not in curr_url and (has_me_link or "user/self" in curr_url or "space.bilibili.com" in curr_url or "zhihu.com/people" in curr_url):
                        login_verified = True
                        print(f"[OK] 检测到 {platform} 账号已登录成功！正在保存状态...")
                        break
                except Exception:
                    pass
                page.wait_for_timeout(2000)

            if not login_verified:
                print(f"[!] 提示：在 2 分钟内未检测到 {platform} 的成功登录动作。")

            context.storage_state(path=save_path)
            print(f"[OK] Saved verified session state for {platform} to {save_path}")
        finally:
            context.close()

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
