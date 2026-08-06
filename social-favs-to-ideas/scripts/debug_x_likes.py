import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from playwright.sync_api import sync_playwright

print("[*] Accessing X Likes page for yangzhuo291996 in live Chrome 9222...")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://x.com/yangzhuo291996/likes", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    for _ in range(3):
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(1000)

    articles = page.query_selector_all("article[data-testid='tweet']")
    print(f"\n[+] Total X Like Articles Found: {len(articles)}")
    
    seen = set()
    for idx, art in enumerate(articles, 1):
        try:
            status_a = art.query_selector("a[href*='/status/']")
            if status_a:
                href = status_a.get_attribute("href") or ""
                sm = re.search(r'/status/(\d+)', href)
                if sm:
                    tid = sm.group(1)
                    if tid not in seen:
                        seen.add(tid)
                        text_elem = art.query_selector("[data-testid='tweetText']")
                        txt = text_elem.inner_text().strip().replace("\n", " ") if text_elem else art.inner_text().strip().replace("\n", " ")
                        print(f"{idx}. [{tid}] {txt[:80]}")
        except Exception as e:
            print(f"Error parsing article {idx}: {e}")
