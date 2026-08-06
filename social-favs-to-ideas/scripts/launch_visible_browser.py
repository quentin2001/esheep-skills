import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from playwright.sync_api import sync_playwright

print("[*] Launching Visible Chromium Browser Window for X Login...")

with sync_playwright() as p:
    user_data = os.path.join(BASE_DIR, ".sessions", "x_playwright_profile")
    context = p.chromium.launch_persistent_context(
        user_data_dir=user_data,
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://x.com/i/bookmarks")
    
    print("[OK] Visible Browser Launched! Waiting for user ENTER in console...")
    input(">>> 请在弹出的浏览器中完成 X 登录，登录完成后在此处按回车键 (ENTER) 确认 >>> ")
    
    print("[*] Saving storage state...")
    state_path = os.path.join(BASE_DIR, ".sessions", "x_state.json")
    context.storage_state(path=state_path)
    print(f"[OK] State saved to {state_path}")
