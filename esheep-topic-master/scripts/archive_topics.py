import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        # Handle 'Z' suffix if present
        cleaned_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned_str)
    except (ValueError, TypeError):
        return None


def archive_completed_topics(days=30, db_path=None, archive_path=None) -> int:
    if db_path is None:
        db_path = BASE_DIR / "data" / "topics.json"
    else:
        db_path = Path(db_path)

    if archive_path is None:
        archive_path = BASE_DIR / "data" / "archive_topics.json"
    else:
        archive_path = Path(archive_path)

    if not db_path.exists():
        return 0

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            db_topics = json.loads(content) if content else []
    except (json.JSONDecodeError, OSError):
        return 0

    cutoff_date = datetime.now()

    to_archive = []
    to_keep = []

    for topic in db_topics:
        if topic.get("status") == "completed":
            dt_str = topic.get("updated_at") or topic.get("created_at")
            dt = parse_iso_datetime(dt_str)
            if dt and (cutoff_date - dt.replace(tzinfo=None)) >= timedelta(days=days):
                to_archive.append(topic)
                continue
        to_keep.append(topic)

    if not to_archive:
        return 0

    # Load existing archive
    archive_topics = []
    if archive_path.exists():
        try:
            with open(archive_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    archive_topics = json.loads(content)
        except (json.JSONDecodeError, OSError):
            archive_topics = []

    # Map existing archived topics by id for deduplication
    archived_map = {t["id"]: t for t in archive_topics if isinstance(t, dict) and "id" in t}

    for topic in to_archive:
        archived_map[topic["id"]] = topic

    # Preserve array form
    updated_archive_topics = list(archived_map.values())

    # Save active topics
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(to_keep, f, ensure_ascii=False, indent=2)

    # Save archive topics
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(updated_archive_topics, f, ensure_ascii=False, indent=2)

    return len(to_archive)


def main():
    parser = argparse.ArgumentParser(description="Archive completed topics older than specified days")
    parser.add_argument("--days", type=int, default=30, help="Days threshold for archiving (default: 30)")
    parser.add_argument("--db-path", default=None, help="Path to topics.json")
    parser.add_argument("--archive-path", default=None, help="Path to archive_topics.json")

    args = parser.parse_args()
    count = archive_completed_topics(days=args.days, db_path=args.db_path, archive_path=args.archive_path)
    print(f"Archived {count} topic(s) older than {args.days} days.")


if __name__ == "__main__":
    main()
