import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from archive_topics import archive_completed_topics


def create_sample_topic(topic_id, status="completed", days_ago=35):
    updated_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
    return {
        "id": topic_id,
        "title": f"Topic {topic_id}",
        "category": "Tech",
        "status": status,
        "updated_at": updated_at,
        "created_at": updated_at,
    }


def test_archive_completed_topics_moves_old_completed(tmp_path):
    db_path = tmp_path / "topics.json"
    archive_path = tmp_path / "archive_topics.json"

    # Old completed (35 days old) -> should be archived
    t1 = create_sample_topic("1", status="completed", days_ago=35)
    # Recent completed (10 days old) -> should stay
    t2 = create_sample_topic("2", status="completed", days_ago=10)
    # Old non-completed (40 days old, inbox) -> should stay
    t3 = create_sample_topic("3", status="inbox", days_ago=40)

    db_path.write_text(json.dumps([t1, t2, t3], ensure_ascii=False), encoding="utf-8")

    archived_count = archive_completed_topics(days=30, db_path=db_path, archive_path=archive_path)
    assert archived_count == 1

    # Verify db_path topics
    db_topics = json.loads(db_path.read_text(encoding="utf-8"))
    assert len(db_topics) == 2
    db_ids = {t["id"] for t in db_topics}
    assert db_ids == {"2", "3"}

    # Verify archive_path topics
    archive_topics = json.loads(archive_path.read_text(encoding="utf-8"))
    assert len(archive_topics) == 1
    assert archive_topics[0]["id"] == "1"


def test_archive_completed_topics_deduplication(tmp_path):
    db_path = tmp_path / "topics.json"
    archive_path = tmp_path / "archive_topics.json"

    t1 = create_sample_topic("1", status="completed", days_ago=35)
    t2 = create_sample_topic("2", status="completed", days_ago=40)

    db_path.write_text(json.dumps([t1, t2], ensure_ascii=False), encoding="utf-8")
    # archive already contains t1
    existing_t1 = create_sample_topic("1", status="completed", days_ago=50)
    existing_t1["title"] = "Old Title 1"
    archive_path.write_text(json.dumps([existing_t1], ensure_ascii=False), encoding="utf-8")

    archived_count = archive_completed_topics(days=30, db_path=db_path, archive_path=archive_path)
    assert archived_count == 2

    # Verify archive has 2 items total (no duplicate t1 id)
    archive_topics = json.loads(archive_path.read_text(encoding="utf-8"))
    assert len(archive_topics) == 2
    archived_ids = [t["id"] for t in archive_topics]
    assert archived_ids.count("1") == 1
    assert archived_ids.count("2") == 1


def test_archive_completed_topics_empty_db(tmp_path):
    db_path = tmp_path / "topics.json"
    archive_path = tmp_path / "archive_topics.json"

    archived_count = archive_completed_topics(days=30, db_path=db_path, archive_path=archive_path)
    assert archived_count == 0
    assert not archive_path.exists()
