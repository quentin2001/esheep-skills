import os
import time
import argparse
from datetime import datetime
from scripts.config import RAW_FAVS_FILE, SESSIONS_DIR
from scripts.storage import add_new_favs
from scripts.login_helper import get_session_path, PLATFORMS

def parse_raw_item(item: dict) -> dict:
    raw_id = item.get("id", str(time.time()))
    platform = item.get("platform", "generic")
    return {
        "id": f"{platform}_{raw_id}",
        "platform": platform,
        "action_type": item.get("action_type", "favorite"),
        "title": item.get("title", "").strip(),
        "url": item.get("url", ""),
        "text_snippet": item.get("text_snippet", "").strip(),
        "tags": item.get("tags", []),
        "scraped_at": datetime.now().isoformat()
    }

def fetch_platform(platform: str, headless: bool = True) -> list:
    session_file = get_session_path(platform)
    if not os.path.exists(session_file):
        print(f"[!] Session state for {platform} not found. Please run login_helper.py --platform {platform} first.")
        return []

    items = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=session_file)
        page = context.new_page()

        try:
            if platform == "bilibili":
                page.goto("https://space.bilibili.com/favlist")
                page.wait_for_timeout(3000)
                cards = page.query_selector_all(".fav-video-list li")
                for c in cards[:10]:
                    title_el = c.query_selector("a.title")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "bilibili",
                            "action_type": "favorite",
                            "id": title_el.get_attribute("href") or "",
                            "title": title_el.inner_text(),
                            "url": "https:" + (title_el.get_attribute("href") or "")
                        }))
            elif platform == "zhihu":
                page.goto("https://www.zhihu.com/collections/mine")
                page.wait_for_timeout(3000)
                titles = page.query_selector_all(".SelfCollectionItem-title")
                for t in titles[:10]:
                    items.append(parse_raw_item({
                        "platform": "zhihu",
                        "action_type": "favorite",
                        "id": t.inner_text(),
                        "title": t.inner_text(),
                        "url": page.url
                    }))
            elif platform == "xiaohongshu":
                page.goto("https://www.xiaohongshu.com/user/profile/self")
                page.wait_for_timeout(3000)
                notes = page.query_selector_all(".note-item")
                for n in notes[:10]:
                    title_el = n.query_selector(".title")
                    link_el = n.query_selector("a")
                    if title_el and link_el:
                        href = link_el.get_attribute("href") or ""
                        items.append(parse_raw_item({
                            "platform": "xiaohongshu",
                            "action_type": "favorite",
                            "id": href,
                            "title": title_el.inner_text(),
                            "url": "https://www.xiaohongshu.com" + href
                        }))
            elif platform == "douyin":
                # Scrape Douyin Likes
                page.goto("https://www.douyin.com/user/self?showTab=like")
                page.wait_for_timeout(3000)
                vids = page.query_selector_all("li.E5C77L8Q")
                for v in vids[:5]:
                    title_el = v.query_selector("p")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "douyin",
                            "action_type": "like",
                            "id": title_el.inner_text()[:20],
                            "title": title_el.inner_text(),
                            "url": page.url
                        }))
                # Scrape Douyin Favorites
                page.goto("https://www.douyin.com/user/self?showTab=favorite")
                page.wait_for_timeout(3000)
                fav_vids = page.query_selector_all("li.E5C77L8Q")
                for v in fav_vids[:5]:
                    title_el = v.query_selector("p")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "douyin",
                            "action_type": "favorite",
                            "id": "fav_" + title_el.inner_text()[:20],
                            "title": title_el.inner_text(),
                            "url": page.url
                        }))
            elif platform == "x":
                page.goto("https://x.com/i/bookmarks")
                page.wait_for_timeout(3000)
                tweets = page.query_selector_all("article[data-testid='tweet']")
                for tw in tweets[:10]:
                    text_el = tw.query_selector("div[data-testid='tweetText']")
                    if text_el:
                        items.append(parse_raw_item({
                            "platform": "x",
                            "action_type": "favorite",
                            "id": text_el.inner_text()[:20],
                            "title": text_el.inner_text()[:50],
                            "text_snippet": text_el.inner_text(),
                            "url": page.url
                        }))
        except Exception as e:
            print(f"[!] Error fetching {platform}: {e}")

        browser.close()
    return items

def main():
    parser = argparse.ArgumentParser(description="Fetch social media favorites & likes")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], default="all")
    parser.add_argument("--headless", action="store_true", default=True)
    args = parser.parse_args()

    all_fetched = []
    platforms = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]

    for p in platforms:
        print(f"[*] Fetching from {p}...")
        fetched = fetch_platform(p, headless=args.headless)
        all_fetched.extend(fetched)

    added = add_new_favs(all_fetched, RAW_FAVS_FILE)
    print(f"[✓] Fetch complete. Scraped {len(all_fetched)} items, added {len(added)} new items to {RAW_FAVS_FILE}.")

if __name__ == "__main__":
    main()
