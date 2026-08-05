import os
import re
import time
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
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

def extract_items_from_html(platform: str, html_content: str, action_type: str = "favorite", limit: int = 10) -> list:
    soup = BeautifulSoup(html_content, "html.parser")
    items = []
    seen_ids = set()

    if platform == "bilibili":
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a.get("href", "")
            bv_match = re.search(r'BV[a-zA-Z0-9]+', href)
            if bv_match:
                bv_id = bv_match.group(0)
                if bv_id in seen_ids:
                    continue
                seen_ids.add(bv_id)

                title = a.get_text(strip=True)
                if not title or len(title) < 2:
                    parent = a.find_parent(["li", "div", "article"])
                    if parent:
                        title_el = parent.find(class_=re.compile(r'title', re.I)) or parent.find(["h3", "h2", "h1"])
                        if title_el:
                            title = title_el.get_text(strip=True)
                        else:
                            title = parent.get_text(strip=True)
                if not title:
                    title = bv_id

                items.append(parse_raw_item({
                    "platform": "bilibili",
                    "action_type": action_type,
                    "id": bv_id,
                    "title": title,
                    "url": f"https://www.bilibili.com/video/{bv_id}"
                }))
                if len(items) >= limit:
                    break

    elif platform == "zhihu":
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a.get("href", "")
            ans_match = re.search(r'/question/(\d+)/answer/(\d+)', href)
            p_match = re.search(r'/p/(\d+)', href)
            q_match = re.search(r'/question/(\d+)', href)

            raw_id = None
            url = None

            if ans_match:
                q_id, a_id = ans_match.groups()
                raw_id = f"answer_{a_id}"
                url = f"https://www.zhihu.com/question/{q_id}/answer/{a_id}"
            elif p_match:
                p_id = p_match.group(1)
                raw_id = f"p_{p_id}"
                url = f"https://www.zhihu.com/p/{p_id}"
            elif q_match and not ans_match:
                q_id = q_match.group(1)
                raw_id = f"question_{q_id}"
                url = f"https://www.zhihu.com/question/{q_id}"

            if raw_id and url and raw_id not in seen_ids:
                seen_ids.add(raw_id)
                title = a.get_text(strip=True)
                if not title or len(title) < 2:
                    parent = a.find_parent(["div", "li", "article", "h2", "h3"])
                    if parent:
                        title_el = parent.find(class_=re.compile(r'title', re.I)) or parent.find(["h2", "h3"])
                        if title_el:
                            title = title_el.get_text(strip=True)
                        else:
                            title = parent.get_text(strip=True)
                if not title:
                    title = raw_id

                items.append(parse_raw_item({
                    "platform": "zhihu",
                    "action_type": action_type,
                    "id": raw_id,
                    "title": title,
                    "url": url
                }))
                if len(items) >= limit:
                    break

    elif platform == "xiaohongshu":
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a.get("href", "")
            exp_match = re.search(r'/explore/([a-zA-Z0-9]+)', href)
            if exp_match:
                note_id = exp_match.group(1)
                if note_id in seen_ids:
                    continue
                seen_ids.add(note_id)

                title = ""
                parent = a.find_parent(class_=re.compile(r'note-item', re.I)) or a.find_parent(["section", "div", "li"])
                if parent:
                    title_el = parent.find(class_=re.compile(r'title', re.I))
                    if title_el:
                        title = title_el.get_text(strip=True)
                if not title:
                    title = a.get_text(strip=True)
                if not title:
                    title = note_id

                items.append(parse_raw_item({
                    "platform": "xiaohongshu",
                    "action_type": action_type,
                    "id": note_id,
                    "title": title,
                    "url": f"https://www.xiaohongshu.com/explore/{note_id}"
                }))
                if len(items) >= limit:
                    break

    elif platform == "douyin":
        anchors = soup.find_all("a", href=True)
        for a in anchors:
            href = a.get("href", "")
            vid_match = re.search(r'/video/([a-zA-Z0-9_-]+)', href)
            if vid_match:
                vid_id = vid_match.group(1)
                raw_id = f"{action_type}_{vid_id}" if action_type == "like" else vid_id
                if vid_id in seen_ids:
                    continue
                seen_ids.add(vid_id)

                title = ""
                p_el = a.find("p")
                if p_el:
                    title = p_el.get_text(strip=True)
                if not title:
                    parent = a.find_parent(["li", "div"])
                    if parent:
                        p_el = parent.find("p")
                        if p_el:
                            title = p_el.get_text(strip=True)
                if not title:
                    title = a.get_text(strip=True)
                if not title:
                    title = vid_id

                items.append(parse_raw_item({
                    "platform": "douyin",
                    "action_type": action_type,
                    "id": raw_id,
                    "title": title,
                    "url": f"https://www.douyin.com/video/{vid_id}"
                }))
                if len(items) >= limit:
                    break

    elif platform == "x":
        tweets = soup.find_all("article", attrs={"data-testid": "tweet"})
        if tweets:
            for tw in tweets:
                status_a = tw.find("a", href=re.compile(r'/status/\d+'))
                if status_a:
                    status_href = status_a.get("href", "")
                    st_match = re.search(r'/status/(\d+)', status_href)
                    if st_match:
                        tweet_id = st_match.group(1)
                        if tweet_id in seen_ids:
                            continue
                        seen_ids.add(tweet_id)

                        text_el = tw.find("div", attrs={"data-testid": "tweetText"})
                        text_snippet = text_el.get_text(strip=True) if text_el else tw.get_text(strip=True)
                        title = text_snippet[:50] if text_snippet else tweet_id

                        items.append(parse_raw_item({
                            "platform": "x",
                            "action_type": action_type,
                            "id": tweet_id,
                            "title": title,
                            "text_snippet": text_snippet,
                            "url": f"https://x.com/i/web/status/{tweet_id}"
                        }))
                        if len(items) >= limit:
                            break
        else:
            anchors = soup.find_all("a", href=re.compile(r'/status/\d+'))
            for a in anchors:
                href = a.get("href", "")
                st_match = re.search(r'/status/(\d+)', href)
                if st_match:
                    tweet_id = st_match.group(1)
                    if tweet_id in seen_ids:
                        continue
                    seen_ids.add(tweet_id)
                    text_snippet = a.get_text(strip=True) or tweet_id
                    items.append(parse_raw_item({
                        "platform": "x",
                        "action_type": action_type,
                        "id": tweet_id,
                        "title": text_snippet[:50],
                        "text_snippet": text_snippet,
                        "url": f"https://x.com/i/web/status/{tweet_id}"
                    }))
                    if len(items) >= limit:
                        break

    return items

def fetch_platform(platform: str, headless: bool = True, limit: int = 10) -> list:
    session_file = get_session_path(platform)
    if not os.path.exists(session_file):
        print(f"[!] Session state for {platform} not found. Please run login_helper.py --platform {platform} first.")
        return []

    items = []
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

    targets = []
    if platform == "bilibili":
        targets = [
            ("https://space.bilibili.com/favlist", "favorite", "a[href*='/video/'], .fav-video-list"),
            ("https://space.bilibili.com/history", "like", "a[href*='/video/'], .bili-video-card")
        ]
    elif platform == "zhihu":
        targets = [
            ("https://www.zhihu.com/collections/mine", "favorite", "a[href*='/question/'], a[href*='/p/'], a[href*='/answer/']"),
            ("https://www.zhihu.com/people/self/answers", "like", "a[href*='/question/'], a[href*='/p/'], a[href*='/answer/']")
        ]
    elif platform == "xiaohongshu":
        targets = [
            ("https://www.xiaohongshu.com/user/profile/self", "favorite", ".note-item, a[href*='/explore/']"),
            ("https://www.xiaohongshu.com/user/profile/self?tab=likes", "like", ".note-item, a[href*='/explore/']")
        ]
    elif platform == "douyin":
        targets = [
            ("https://www.douyin.com/user/self?showTab=like", "like", "a[href*='/video/']"),
            ("https://www.douyin.com/user/self?showTab=favorite", "favorite", "a[href*='/video/']")
        ]
    elif platform == "x":
        targets = [
            ("https://x.com/i/bookmarks", "favorite", "article[data-testid='tweet']"),
            ("https://x.com/i/likes", "like", "article[data-testid='tweet']")
        ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            context = browser.new_context(storage_state=session_file)
            page = context.new_page()

            for url, action_type, wait_selector in targets:
                try:
                    page.goto(url)
                    try:
                        page.wait_for_selector(wait_selector, timeout=5000)
                    except PlaywrightTimeoutError:
                        pass
                    except Exception:
                        pass

                    html_content = page.content()
                    extracted = extract_items_from_html(platform, html_content, action_type=action_type, limit=limit)
                    items.extend(extracted)
                except Exception as e:
                    print(f"[!] Error fetching {platform} target {url}: {e}")
        finally:
            browser.close()

    return items

def main():
    parser = argparse.ArgumentParser(description="Fetch social media favorites & likes")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], default="all")
    parser.add_argument("--headless", action="store_true", default=True)
    parser.add_argument("--limit", type=int, default=10, help="Max items to fetch per target page")
    args = parser.parse_args()

    all_fetched = []
    platforms = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]

    for p in platforms:
        print(f"[*] Fetching from {p}...")
        fetched = fetch_platform(p, headless=args.headless, limit=args.limit)
        all_fetched.extend(fetched)

    added = add_new_favs(all_fetched, RAW_FAVS_FILE)
    print(f"[✓] Fetch complete. Scraped {len(all_fetched)} items, added {len(added)} new items to {RAW_FAVS_FILE}.")

if __name__ == "__main__":
    main()
