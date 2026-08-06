import os
import sys
import json
import re
import urllib.request
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from playwright.sync_api import sync_playwright
from scripts.config import SESSIONS_DIR, RAW_FAVS_FILE, IDEAS_DB_FILE, CDP_PORT
from scripts.storage import add_new_favs, load_raw_favs

def parse_raw_item(item: dict) -> dict:
    platform = item.get("platform", "unknown")
    raw_id = item.get("id", str(hash(str(item))))
    action_type = item.get("action_type", "favorite")
    title = item.get("title", "").strip()
    url = item.get("url", "")
    text_snippet = item.get("text_snippet", "").strip()
    tags = item.get("tags", [])

    item_id = f"{platform}_{raw_id}" if not str(raw_id).startswith(platform) else str(raw_id)

    return {
        "id": item_id,
        "platform": platform,
        "action_type": action_type,
        "title": title if title else f"{platform}_item_{raw_id}",
        "url": url,
        "text_snippet": text_snippet,
        "tags": tags if isinstance(tags, list) else [],
        "scraped_at": datetime.now().isoformat()
    }

def extract_items_from_json(platform: str, json_data: dict, action_type: str = "favorite") -> list:
    items = []
    if not isinstance(json_data, dict):
        return items

    # Douyin API: aweme_list / data
    aweme_list = json_data.get("aweme_list") or json_data.get("data")
    if isinstance(aweme_list, list):
        for aweme in aweme_list:
            if isinstance(aweme, dict):
                vid_id = aweme.get("aweme_id") or aweme.get("id")
                desc = aweme.get("desc") or aweme.get("title") or ""
                if vid_id and desc:
                    items.append(parse_raw_item({
                        "platform": "douyin",
                        "action_type": action_type,
                        "id": str(vid_id),
                        "title": str(desc).strip(),
                        "url": f"https://www.douyin.com/video/{vid_id}"
                    }))

    # Xiaohongshu API: notes / items / data / collect_notes
    notes_list = json_data.get("notes") or json_data.get("items") or json_data.get("collect_notes")
    if not notes_list and isinstance(json_data.get("data"), dict):
        d_obj = json_data.get("data", {})
        notes_list = d_obj.get("notes") or d_obj.get("items") or d_obj.get("collect_notes") or d_obj.get("notes_list")

    if isinstance(notes_list, list):
        for note in notes_list:
            if isinstance(note, dict):
                note_id = note.get("note_id") or note.get("id") or note.get("noteId")
                display_title = note.get("display_title") or note.get("title") or note.get("desc")
                xsec_token = note.get("xsec_token") or note.get("xsecToken") or ""
                
                if note_id and display_title:
                    note_id_str = str(note_id)
                    if xsec_token:
                        full_url = f"https://www.xiaohongshu.com/explore/{note_id_str}?xsec_token={xsec_token}&xsec_source=pc_feed"
                    else:
                        full_url = f"https://www.xiaohongshu.com/explore/{note_id_str}"
                        
                    items.append(parse_raw_item({
                        "platform": "xiaohongshu",
                        "action_type": action_type,
                        "id": note_id_str,
                        "title": str(display_title).strip(),
                        "url": full_url
                    }))

    return items

def is_cdp_port_active(port: int = CDP_PORT) -> bool:
    for host in ["localhost", "127.0.0.1"]:
        try:
            req = urllib.request.urlopen(f"http://{host}:{port}/json/version", timeout=1)
            if req.status == 200:
                return True
        except Exception:
            pass
    return False

def bring_window_to_foreground():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

        def enum_cb(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                if any(k in title for k in ["chrome", "x", "bookmarks", "新标签页"]):
                    user32.ShowWindow(hwnd, 9) # SW_RESTORE
                    user32.SetForegroundWindow(hwnd)
                    return False
            return True

        user32.EnumWindows(EnumWindowsProc(enum_cb), 0)
    except Exception:
        pass

def fetch_platform(platform: str, headless: bool = False, limit: int = 20, use_cdp: bool = True) -> list:
    items = []
    print(f"[*] [MediaCrawler-Engine] 启动 {platform} 提取引擎 (limit={limit})...")

    with sync_playwright() as p:
        browser = None
        context = None

        if use_cdp and is_cdp_port_active(CDP_PORT):
            print(f"[+] 成功通过 CDP 直连端口 127.0.0.1:{CDP_PORT}")
            try:
                browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
                context = browser.contexts[0] if browser.contexts else browser.new_context()
            except Exception as err:
                print(f"[!] CDP 直连失败: {err}")

        if not context:
            user_data = os.path.join(SESSIONS_DIR, f"{platform}_user_data")
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )

        # Reuse current active page if available, or create tab
        page = context.pages[0] if context.pages else context.new_page()

        # Register Response Listener for API Payload Unpacking
        def on_response(response):
            try:
                url_lower = response.url.lower()
                if "json" in response.headers.get("content-type", "").lower() or any(k in url_lower for k in ["collect", "posted", "like", "fav", "aweme", "note", "feed"]):
                    if any(k in url_lower for k in ["collect", "posted", "like", "fav", "aweme", "note", "feed", "user"]):
                        if "collect" in url_lower:
                            atype = "favorite"
                        elif any(k in url_lower for k in ["like", "favorite"]):
                            atype = "like"
                        else:
                            atype = "favorite"

                        data = response.json()
                        parsed = extract_items_from_json(platform, data, action_type=atype)
                        items.extend(parsed)
            except Exception:
                pass

        page.on("response", on_response)

        # Platform Navigation
        try:
            if platform == "xiaohongshu":
                page.goto("https://www.xiaohongshu.com/explore", wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                profile_link = page.query_selector("a[href*='/user/profile/']")
                if profile_link:
                    href = profile_link.get_attribute("href") or ""
                    base_profile = f"https://www.xiaohongshu.com{href}" if href.startswith("/") else href
                    pure_profile = base_profile.split("?")[0]

                    # 1. 真实收藏页 (tab=fav&subTab=note)
                    print(f"[*] 导航至小红书真实收藏页: {pure_profile}?tab=fav&subTab=note")
                    page.goto(f"{pure_profile}?tab=fav&subTab=note", wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)
                    for _ in range(2):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(1000)

                    anchors_c = page.query_selector_all("a[href*='/explore/']")
                    for a in anchors_c:
                        try:
                            href_a = a.get_attribute("href") or ""
                            text_a = a.inner_text().strip()
                            nid_m = re.search(r'/explore/([a-zA-Z0-9]+)', href_a)
                            if nid_m:
                                nid = nid_m.group(1)
                                full_url = f"https://www.xiaohongshu.com{href_a}" if href_a.startswith("/") else href_a
                                if text_a and "小红书" not in text_a and len(text_a) > 2:
                                    items.append(parse_raw_item({
                                        "platform": "xiaohongshu",
                                        "action_type": "favorite",
                                        "id": nid,
                                        "title": text_a,
                                        "url": full_url
                                    }))
                        except Exception:
                            pass

                    # 2. 真实点赞页 (tab=liked&subTab=note)
                    print(f"[*] 导航至小红书真实点赞页: {pure_profile}?tab=liked&subTab=note")
                    page.goto(f"{pure_profile}?tab=liked&subTab=note", wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)
                    for _ in range(2):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(1000)

                    anchors_l = page.query_selector_all("a[href*='/explore/']")
                    for a in anchors_l:
                        try:
                            href_a = a.get_attribute("href") or ""
                            text_a = a.inner_text().strip()
                            nid_m = re.search(r'/explore/([a-zA-Z0-9]+)', href_a)
                            if nid_m:
                                nid = nid_m.group(1)
                                full_url = f"https://www.xiaohongshu.com{href_a}" if href_a.startswith("/") else href_a
                                if text_a and "小红书" not in text_a and len(text_a) > 2:
                                    items.append(parse_raw_item({
                                        "platform": "xiaohongshu",
                                        "action_type": "like",
                                        "id": nid,
                                        "title": text_a,
                                        "url": full_url
                                    }))
                        except Exception:
                            pass

            elif platform == "douyin":
                # 1. 真实收藏页 - 直接前往官方精准 URL (showTab=favorite_collection)
                print("[*] 前往抖音官方收藏页: showTab=favorite_collection")
                page.goto("https://www.douyin.com/user/self?from_tab_name=main&showSubTab=video&showTab=favorite_collection", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                for _ in range(2):
                    page.evaluate("window.scrollBy(0, 800)")
                    page.wait_for_timeout(1000)

                fav_anchors = page.query_selector_all("a[href*='/video/']")
                for a in fav_anchors:
                    try:
                        is_sidebar = a.evaluate("el => !!el.closest('.side-bar, .recommend, .footer, [class*=\"sidebar\"], [class*=\"recommend\"]')")
                        if is_sidebar:
                            continue

                        href_a = a.get_attribute("href") or ""
                        vid_m = re.search(r'(?:/video/|modal_id=)(\d+)', href_a)
                        if vid_m:
                            vid = vid_m.group(1)
                            text_a = a.evaluate("el => { const parent = el.closest('li, div[class*=\"card\"], div[class*=\"item\"]'); return parent ? parent.innerText : el.innerText; }")
                            if text_a:
                                text_a = text_a.strip().replace("\n", " ")
                                text_clean = re.sub(r'^\d+(\.\d+)?[万亿]?\s*', '', text_a).strip()
                                if text_clean and len(text_clean) > 2:
                                    items.append(parse_raw_item({
                                        "platform": "douyin",
                                        "action_type": "favorite",
                                        "id": vid,
                                        "title": text_clean,
                                        "url": f"https://www.douyin.com/video/{vid}"
                                    }))
                    except Exception:
                        pass

                # 2. 真实喜欢/点赞页 - 触发 '喜欢' 选项卡解包
                print("[*] 前往抖音官方个人主页并解锁喜欢(Private)列表...")
                page.goto("https://www.douyin.com/user/self", wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                like_tab = None
                for elem in page.query_selector_all("div, span, li"):
                    try:
                        txt = elem.inner_text().strip()
                        if "喜欢" in txt and len(txt) < 8:
                            like_tab = elem
                            break
                    except Exception:
                        pass

                if like_tab:
                    like_tab.click()
                    page.wait_for_timeout(3000)
                    for _ in range(2):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(1000)

            elif platform == "x":
                # 1. 真实 Bookmarks (书签页)
                print("[*] 导航至 X 官方书签页: https://x.com/i/bookmarks")
                page.goto("https://x.com/i/bookmarks", wait_until="domcontentloaded")
                try:
                    page.wait_for_selector("article[data-testid='tweet']", timeout=6000)
                except Exception:
                    print("[!] 未在 X 页面检测到已登录推文，自动调用 Win32 强行将 Chrome 窗口激活抢占至桌面上方...")
                    bring_window_to_foreground()

                for _ in range(3):
                    page.evaluate("window.scrollBy(0, 800)")
                    page.wait_for_timeout(1000)

                articles_bm = page.query_selector_all("article[data-testid='tweet']")
                for art in articles_bm:
                    try:
                        status_a = art.query_selector("a[href*='/status/']")
                        if status_a:
                            href_a = status_a.get_attribute("href") or ""
                            sm = re.search(r'/status/(\d+)', href_a)
                            if sm:
                                tweet_id = sm.group(1)
                                text_elem = art.query_selector("[data-testid='tweetText']")
                                text_val = text_elem.inner_text().strip().replace("\n", " ") if text_elem else art.inner_text().strip().replace("\n", " ")
                                full_url = f"https://x.com{href_a}" if href_a.startswith("/") else href_a
                                if text_val and len(text_val) > 2:
                                    items.append(parse_raw_item({
                                        "platform": "x",
                                        "action_type": "favorite",
                                        "id": tweet_id,
                                        "title": text_val[:120],
                                        "url": full_url
                                    }))
                    except Exception:
                        pass

                # 2. 真实 Likes (点赞/喜欢页)
                print("[*] 前往 X 个人主页并进入 Likes 标签...")
                page.goto("https://x.com/i/user", wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                profile_a = page.query_selector("a[data-testid='AppTabBar_Profile_Link']") or page.query_selector("a[href*='/status/']")
                user_handle = None
                if profile_a:
                    href_p = profile_a.get_attribute("href") or ""
                    if href_p and href_p != "/":
                        user_handle = href_p.strip("/")

                if user_handle:
                    print(f"[*] 导航至 X 真实 Likes 页面: https://x.com/{user_handle}/likes")
                    page.goto(f"https://x.com/{user_handle}/likes", wait_until="domcontentloaded")
                    try:
                        page.wait_for_selector("article[data-testid='tweet']", timeout=5000)
                    except Exception:
                        pass
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, 800)")
                        page.wait_for_timeout(1000)

                    articles_lk = page.query_selector_all("article[data-testid='tweet']")
                    for art in articles_lk:
                        try:
                            status_a = art.query_selector("a[href*='/status/']")
                            if status_a:
                                href_a = status_a.get_attribute("href") or ""
                                sm = re.search(r'/status/(\d+)', href_a)
                                if sm:
                                    tweet_id = sm.group(1)
                                    text_elem = art.query_selector("[data-testid='tweetText']")
                                    text_val = text_elem.inner_text().strip().replace("\n", " ") if text_elem else art.inner_text().strip().replace("\n", " ")
                                    full_url = f"https://x.com{href_a}" if href_a.startswith("/") else href_a
                                    if text_val and len(text_val) > 2:
                                        items.append(parse_raw_item({
                                            "platform": "x",
                                            "action_type": "like",
                                            "id": tweet_id,
                                            "title": text_val[:120],
                                            "url": full_url
                                        }))
                        except Exception:
                            pass

        except Exception as err:
            print(f"[!] {platform} 页面导航提示: {err}")

    clean_items = []
    seen = set()
    for it in items:
        if it["id"] not in seen:
            seen.add(it["id"])
            clean_items.append(it)

    print(f"[OK] {platform} 抓取完成，提炼到 {len(clean_items)} 条真实个人记录。")
    add_new_favs(clean_items, RAW_FAVS_FILE)
    return clean_items[:limit]

def write_markdown_database():
    all_raw = load_raw_favs(RAW_FAVS_FILE)
    by_platform = {}
    for item in all_raw:
        p = item.get("platform", "other")
        a = item.get("action_type", "favorite")
        by_platform.setdefault(p, {}).setdefault(a, []).append(item)

    md = ["# 自媒体全平台精选内容数据库 (严格个人真数据校验版)\n"]
    for p, actions in by_platform.items():
        md.append(f"## 平台: {p.upper()}\n")
        for a_type, p_items in actions.items():
            a_label = "收藏 (Favorite)" if a_type == "favorite" else "喜欢/点赞 (Like)"
            md.append(f"### 标签: {a_label} (共 {len(p_items)} 条记录)\n")
            for idx, item in enumerate(p_items[:10], 1):
                scraped_date = item.get("scraped_at", "").split("T")[0]
                date_str = f" [捕获日期: {scraped_date}]" if scraped_date else ""
                md.append(f"{idx}. **{item['title']}**{date_str}\n   - 直链地址: [{item['url']}]({item['url']})\n   - 唯一ID: `{item['id']}`\n")

    out_md = "\n".join(md)
    with open(IDEAS_DB_FILE, "w", encoding="utf-8") as f:
        f.write(out_md)
    print(f"[OK] 数据库已更新至: {IDEAS_DB_FILE}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MediaCrawler-inspired Social Media Engine")
    parser.add_argument("--platform", type=str, default="xiaohongshu", choices=["bilibili", "zhihu", "xiaohongshu", "douyin", "x", "all"])
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.platform == "all":
        for plat in ["xiaohongshu", "douyin", "bilibili", "zhihu", "x"]:
            fetch_platform(plat, limit=args.limit)
    else:
        fetch_platform(args.platform, limit=args.limit)

    write_markdown_database()
