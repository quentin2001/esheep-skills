import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Ensure topic_manager can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from topic_manager import TopicManager

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _fetch_json(url, custom_headers=None, timeout=10):
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if custom_headers:
        headers.update(custom_headers)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            encoding = "utf-8"
            content_type = resp.headers.get("Content-Type", "")
            if "charset=" in content_type.lower():
                encoding = content_type.lower().split("charset=")[-1].split(";")[0].strip()
            try:
                data = raw.decode(encoding)
            except Exception:
                try:
                    data = raw.decode("utf-8")
                except Exception:
                    data = raw.decode("gbk", errors="ignore")
            return json.loads(data)
    except Exception:
        return None


class ZhihuHotAdapter:
    URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        raw_items = resp_data.get("data", [])
        results = []
        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            target = item.get("target", {})
            if not isinstance(target, dict):
                target = {}
            title = target.get("title") or target.get("title_area", {}).get("text", "")
            if not title:
                continue
            item_id = target.get("id")
            if item_id:
                url = f"https://www.zhihu.com/question/{item_id}"
            else:
                url = target.get("url", "")

            excerpt = target.get("excerpt") or item.get("detail_text", "")
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "zhihu",
                "source_type": "hotlist",
                "hook": excerpt,
                "category": "热榜",
            })
        return results


class WeiboHotAdapter:
    URL = "https://weibo.com/ajax/side/hotBand"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        data_obj = resp_data.get("data", {})
        if not isinstance(data_obj, dict):
            return []

        band_list = data_obj.get("band_list", [])
        if not isinstance(band_list, list):
            return []

        results = []
        for item in band_list:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            word = item.get("word") or item.get("note") or ""
            if not word:
                continue
            url = f"https://s.weibo.com/weibo?q={urllib.parse.quote(word)}"
            raw_hot = item.get("raw_hot")
            hook = f"热度: {raw_hot}" if raw_hot else ""
            category = item.get("category") or "微博热搜"
            results.append({
                "title": word,
                "source_title": word,
                "source_url": url,
                "source_platform": "weibo",
                "source_type": "hotlist",
                "hook": hook,
                "category": category,
            })
        return results


class AIHotAdapter:
    URL = "https://aihot.virxact.com/api/v1/items"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data:
            return []

        if isinstance(resp_data, dict):
            raw_items = resp_data.get("items", []) or resp_data.get("data", [])
            if isinstance(raw_items, dict):
                raw_items = raw_items.get("items", [])
        elif isinstance(resp_data, list):
            raw_items = resp_data
        else:
            raw_items = []

        if not isinstance(raw_items, list):
            return []

        results = []
        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("name") or ""
            if not title:
                continue
            links = item.get("links")
            if isinstance(links, dict) and (links.get("original") or links.get("aihot")):
                url = links.get("original") or links.get("aihot") or ""
            else:
                url = item.get("url") or item.get("link") or item.get("item_url") or ""
            desc = item.get("description") or item.get("summary") or item.get("hook") or ""
            hot = item.get("hot") or item.get("hot_score") or item.get("views")
            hook = desc if desc else (f"热度: {hot}" if hot else "")
            site_val = item.get("site") or item.get("source") or item.get("platform") or "aihot"
            if isinstance(site_val, dict):
                site_name = site_val.get("name") or site_val.get("title") or "aihot"
            else:
                site_name = str(site_val)

            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": site_name.strip(),
                "source_type": "hotlist",
                "hook": hook,
                "category": "AI热点",
            })
        return results


class ToutiaoHotAdapter:
    URL = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        raw_items = resp_data.get("data", [])
        if not isinstance(raw_items, list):
            return []

        results = []
        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("Title") or item.get("title") or ""
            if not title:
                continue
            url = item.get("Url") or item.get("url") or ""
            hot = item.get("HotValue") or item.get("hot_value") or ""
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "toutiao",
                "source_type": "hotlist",
                "hook": f"热度: {hot}" if hot else "",
                "category": "热搜综合",
            })
        return results


class BilibiliHotAdapter:
    URL_POPULAR = "https://api.bilibili.com/x/web-interface/popular?ps=20&pn=1"
    URL_TECH = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=188"

    def fetch(self, limit=15):
        raw_items = []
        
        # 1. Fetch Tech ranking first
        resp_tech = _fetch_json(self.URL_TECH)
        if resp_tech and isinstance(resp_tech, dict):
            raw_items.extend(resp_tech.get("data", {}).get("list", []))

        # 2. Fetch popular feed
        resp_pop = _fetch_json(self.URL_POPULAR)
        if resp_pop and isinstance(resp_pop, dict):
            raw_items.extend(resp_pop.get("data", {}).get("list", []))

        results = []
        seen_bvids = set()

        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("title") or ""
            if not title:
                continue
            bvid = item.get("bvid") or ""
            if bvid and bvid in seen_bvids:
                continue
            if bvid:
                seen_bvids.add(bvid)

            url = f"https://www.bilibili.com/video/{bvid}" if bvid else item.get("short_link", "")
            desc = item.get("desc") or item.get("rcmd_reason", {}).get("content", "")
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "bilibili",
                "source_type": "hotlist",
                "hook": desc,
                "category": item.get("tname") or "B站科技",
            })
        return results


class BaiduHotAdapter:
    URL = "https://top.baidu.com/api/board?platform=down&tab=realtime"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        cards = resp_data.get("data", {}).get("cards", [])
        if not cards or not isinstance(cards, list):
            return []

        raw_items = cards[0].get("content", [])
        if not isinstance(raw_items, list):
            return []

        results = []
        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("word") or ""
            if not title:
                continue
            url = item.get("url") or item.get("rawUrl") or ""
            desc = item.get("desc") or item.get("hotScore") or ""
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "baidu",
                "source_type": "hotlist",
                "hook": f"热度: {desc}" if desc else "",
                "category": "百度热搜",
            })
        return results


class XiaohongshuHotAdapter:
    URL = "https://www.xiaohongshu.com/explore"

    def fetch(self, limit=15):
        resp_data = _fetch_json("https://tenapi.cn/v2/xhshot")
        if not resp_data or not isinstance(resp_data, dict):
            return []

        raw_items = resp_data.get("data", [])
        if not isinstance(raw_items, list):
            return []

        results = []
        for item in raw_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("name") or item.get("word") or ""
            if not title:
                continue
            url = item.get("url") or f"https://www.xiaohongshu.com/search_result?keyword={urllib.parse.quote(title)}"
            hot = item.get("hot") or item.get("views") or ""
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "xiaohongshu",
                "source_type": "hotlist",
                "hook": f"热度: {hot}" if hot else "",
                "category": "小红书热搜",
            })
        return results


class DouyinHotAdapter:
    URL = "https://www.douyin.com/aweme/v1/web/hot/search/list/"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        word_list = resp_data.get("data", {}).get("word_list", [])
        if not isinstance(word_list, list):
            return []

        results = []
        for item in word_list:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            word = item.get("word") or ""
            if not word:
                continue
            hot_value = item.get("hot_value") or ""
            results.append({
                "title": word,
                "source_title": word,
                "source_url": f"https://www.douyin.com/search/{urllib.parse.quote(word)}",
                "source_platform": "douyin",
                "source_type": "hotlist",
                "hook": f"热度: {hot_value}" if hot_value else "",
                "category": "抖音热榜",
            })
        return results


DEFAULT_SOURCES = ["aihot", "weibo", "zhihu", "xiaohongshu", "douyin"]

ADAPTER_MAP = {
    "aihot": AIHotAdapter,
    "weibo": WeiboHotAdapter,
    "zhihu": ZhihuHotAdapter,
    "xiaohongshu": XiaohongshuHotAdapter,
    "douyin": DouyinHotAdapter,
    "toutiao": ToutiaoHotAdapter,
    "bilibili": BilibiliHotAdapter,
    "baidu": BaiduHotAdapter,
}


def fetch_hotlist(sources=None, limit=15):
    if sources is None:
        sources = DEFAULT_SOURCES

    if isinstance(sources, str):
        sources = [s.strip() for s in sources.split(",") if s.strip()]

    all_items = []
    for source in sources:
        adapter_cls = ADAPTER_MAP.get(source.lower())
        if not adapter_cls:
            continue
        try:
            adapter = adapter_cls()
            items = adapter.fetch(limit=limit)
            all_items.extend(items)
        except Exception:
            continue
    return all_items


def ingest_hotlist(items, db_path=None):
    if db_path is None:
        db_path = Path(__file__).resolve().parent.parent / "data" / "topics.json"

    db_path = Path(db_path)
    tm = TopicManager(data_file=db_path)
    existing_topics = tm.get_all()

    existing_urls = {
        t.get("source_url") for t in existing_topics if t.get("source_url")
    }
    existing_titles = {
        t.get("title") for t in existing_topics if t.get("title")
    } | {
        t.get("source_title") for t in existing_topics if t.get("source_title")
    }

    imported_count = 0
    for item in items:
        if not isinstance(item, dict):
            continue

        url = item.get("source_url") or item.get("url") or ""
        title = item.get("title") or item.get("source_title") or ""
        platform = item.get("source_platform") or "unknown"
        hook = item.get("hook") or ""
        category = item.get("category") or "热榜采集"
        source_type = item.get("source_type") or "hotlist"

        # Deduplication check
        if url and url in existing_urls:
            continue
        if title and title in existing_titles:
            continue

        topic_title = title if title else f"来自于 {platform} 的热榜话题"

        tm.add(
            title=topic_title,
            category=category,
            hook=hook,
            source_platform=platform,
            source_title=title,
            source_url=url,
            source_type=source_type,
            status="inbox",
        )

        if url:
            existing_urls.add(url)
        if title:
            existing_titles.add(title)
        imported_count += 1

    return imported_count


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Fetch hotlist topics from AIHot, Weibo, Zhihu, Xiaohongshu, Douyin, Toutiao, Bilibili, Baidu.")
    parser.add_argument(
        "--sources",
        default="aihot,weibo,zhihu,xiaohongshu,douyin",
        help="Comma-separated sources to fetch (aihot, weibo, zhihu, xiaohongshu, douyin, toutiao, bilibili, baidu)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help="Limit of items per source",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Directly ingest fetched topics into topics.json",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Path to topics.json when ingesting",
    )

    args = parser.parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    items = fetch_hotlist(sources=sources, limit=args.limit)

    if args.ingest:
        count = ingest_hotlist(items, db_path=args.db_path)
        print(f"Successfully fetched and ingested {count} new hotlist topics into Inbox.")
    else:
        print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
