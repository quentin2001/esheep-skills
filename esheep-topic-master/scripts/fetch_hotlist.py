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
            data = resp.read().decode("utf-8", errors="replace")
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
            url = item.get("url") or item.get("link") or item.get("item_url") or ""
            desc = item.get("description") or item.get("summary") or item.get("hook") or ""
            hot = item.get("hot") or item.get("hot_score") or item.get("views")
            hook = desc if desc else (f"热度: {hot}" if hot else "")
            site = item.get("site") or item.get("source") or item.get("platform") or "aihot"
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": str(site).lower(),
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
    URL = "https://api.bilibili.com/x/web-interface/popular?ps=20&pn=1"

    def fetch(self, limit=15):
        resp_data = _fetch_json(self.URL)
        if not resp_data or not isinstance(resp_data, dict):
            return []

        data_obj = resp_data.get("data", {})
        if not isinstance(data_obj, dict):
            return []

        list_items = data_obj.get("list", [])
        if not isinstance(list_items, list):
            return []

        results = []
        for item in list_items:
            if len(results) >= limit:
                break
            if not isinstance(item, dict):
                continue
            title = item.get("title") or ""
            if not title:
                continue
            bvid = item.get("bvid") or ""
            url = f"https://www.bilibili.com/video/{bvid}" if bvid else item.get("short_link", "")
            desc = item.get("desc") or item.get("rcmd_reason", {}).get("content", "")
            results.append({
                "title": title,
                "source_title": title,
                "source_url": url,
                "source_platform": "bilibili",
                "source_type": "hotlist",
                "hook": desc,
                "category": item.get("tname") or "B站热门",
            })
        return results


ADAPTER_MAP = {
    "zhihu": ZhihuHotAdapter,
    "weibo": WeiboHotAdapter,
    "aihot": AIHotAdapter,
    "toutiao": ToutiaoHotAdapter,
    "bilibili": BilibiliHotAdapter,
}


def fetch_hotlist(sources=None, limit=15):
    if sources is None:
        sources = ["zhihu", "weibo", "aihot"]

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

    parser = argparse.ArgumentParser(description="Fetch hotlist topics from Zhihu, Weibo, AIHot, Toutiao, Bilibili.")
    parser.add_argument(
        "--sources",
        default="zhihu,weibo,aihot",
        help="Comma-separated sources to fetch (zhihu, weibo, aihot)",
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
