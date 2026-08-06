import argparse
import json
import os
import sys
from pathlib import Path

# Ensure topic_manager can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

from topic_manager import TopicManager

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FAVS_PATH = BASE_DIR.parent / "esheep-social-favs-copilot" / "data" / "raw_favs.json"
DEFAULT_DB_PATH = BASE_DIR / "data" / "topics.json"


def import_from_favs(favs_path=None, db_path=None):
    if favs_path is None:
        favs_path = DEFAULT_FAVS_PATH
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    favs_path = Path(favs_path)
    db_path = Path(db_path)

    if not favs_path.exists():
        return 0

    try:
        with open(favs_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return 0
            favs_data = json.loads(content)
    except (json.JSONDecodeError, OSError):
        return 0

    if not isinstance(favs_data, list):
        return 0

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
    for fav in favs_data:
        if not isinstance(fav, dict):
            continue

        url = fav.get("url") or fav.get("source_url") or ""
        title = fav.get("title") or fav.get("source_title") or ""
        platform = fav.get("platform") or fav.get("source_platform") or "unknown"
        snippet = fav.get("text_snippet") or fav.get("hook") or ""
        tags = fav.get("tags") or []

        # Deduplication check on URL or Title
        if url and url in existing_urls:
            continue
        if title and title in existing_titles:
            continue

        topic_title = title if title else f"来自于 {platform} 的未命名灵感"
        category = tags[0] if (isinstance(tags, list) and len(tags) > 0) else "社媒采集"

        tm.add(
            title=topic_title,
            category=category,
            hook=snippet,
            source_platform=platform,
            source_title=title,
            source_url=url,
            tags=tags if isinstance(tags, list) else [],
            status="inbox",
        )

        if url:
            existing_urls.add(url)
        if title:
            existing_titles.add(title)
        imported_count += 1

    return imported_count


def main():
    parser = argparse.ArgumentParser(
        description="Import social media favorites into esheep-topic-master inbox."
    )
    parser.add_argument(
        "--favs-path",
        default=str(DEFAULT_FAVS_PATH),
        help="Path to raw_favs.json",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="Path to topics.json",
    )

    args = parser.parse_args()
    count = import_from_favs(favs_path=args.favs_path, db_path=args.db_path)
    print(f"Successfully imported {count} items into Inbox.")


if __name__ == "__main__":
    main()
