import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from playwright.sync_api import sync_playwright

print("[*] Clicking Profile -> Likes tab on X in live Chrome 9222...")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://x.com/home", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Click Profile in sidebar
    profile_btn = page.query_selector("a[data-testid='AppTabBar_Profile_Link']")
    if profile_btn:
        print("[+] Clicking Profile link in left sidebar...")
        profile_btn.click()
        page.wait_for_timeout(3000)

    # Click Likes tab in main profile header
    likes_tab = None
    tabs = page.query_selector_all("a[role='tab']")
    for t in tabs:
        try:
            txt = t.inner_text().strip()
            if "likes" in txt.lower() or "喜欢" in txt:
                likes_tab = t
                break
        except Exception:
            pass

    if likes_tab:
        print(f"[+] Clicking Tab: '{likes_tab.inner_text()}'")
        likes_tab.click()
        page.wait_for_timeout(4000)
    else:
        print("[!] Could not find 'Likes' tab in Profile header.")

    for _ in range(3):
        page.evaluate("window.scrollBy(0, 800)")
        page.wait_for_timeout(1000)

    screenshot_path = os.path.join(BASE_DIR, "data", "x_likes_page.png")
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"[OK] Screenshot saved to: {screenshot_path}")

    articles = page.query_selector_all("article[data-testid='tweet']")
    print(f"\n[+] Total X Like Articles Found After Tab Click: {len(articles)}")
    for idx, art in enumerate(articles, 1):
        try:
            status_a = art.query_selector("a[href*='/status/']")
            if status_a:
                href = status_a.get_attribute("href") or ""
                text_elem = art.query_selector("[data-testid='tweetText']")
                txt = text_elem.inner_text().strip().replace("\n", " ") if text_elem else art.inner_text().strip().replace("\n", " ")
                print(f"{idx}. {href} | {txt[:60]}")
        except Exception:
            pass
