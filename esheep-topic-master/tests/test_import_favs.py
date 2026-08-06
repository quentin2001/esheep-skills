import json
import os
import sys
import pytest
from pathlib import Path

# Add scripts directory to python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from topic_manager import TopicManager
from import_favs import import_from_favs


def test_import_from_favs_basic(tmp_path):
    favs_file = tmp_path / "raw_favs.json"
    favs_data = [
        {
            "id": "xhs_123",
            "platform": "xiaohongshu",
            "action_type": "favorite",
            "title": "爆款小红书排版技巧",
            "url": "https://xiaohongshu.com/explore/123",
            "text_snippet": "钩子：如何实现自媒体高效增长",
            "tags": ["小红书", "运营"],
        }
    ]
    favs_file.write_text(json.dumps(favs_data, ensure_ascii=False), encoding="utf-8")

    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")

    count = import_from_favs(favs_path=str(favs_file), db_path=str(db_file))
    assert count == 1

    tm = TopicManager(data_file=str(db_file))
    topics = tm.get_all()
    assert len(topics) == 1
    assert topics[0]["title"] == "爆款小红书排版技巧"
    assert topics[0]["source_platform"] == "xiaohongshu"
    assert topics[0]["source_url"] == "https://xiaohongshu.com/explore/123"
    assert topics[0]["status"] == "inbox"


def test_import_from_favs_deduplication(tmp_path):
    favs_file = tmp_path / "raw_favs.json"
    favs_data = [
        {
            "id": "bili_1",
            "platform": "bilibili",
            "title": "视频1",
            "url": "https://bilibili.com/video/BV1",
        },
        {
            "id": "bili_2",
            "platform": "bilibili",
            "title": "视频2",
            "url": "https://bilibili.com/video/BV2",
        },
    ]
    favs_file.write_text(json.dumps(favs_data, ensure_ascii=False), encoding="utf-8")

    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")

    # Initial import
    count1 = import_from_favs(favs_path=str(favs_file), db_path=str(db_file))
    assert count1 == 2

    # Re-importing same items should produce 0 new imports (deduplicated by URL/title)
    count2 = import_from_favs(favs_path=str(favs_file), db_path=str(db_file))
    assert count2 == 0

    # Add new item with same URL but different title -> duplicate by URL
    favs_data_new = [
        {
            "id": "bili_3",
            "platform": "bilibili",
            "title": "视频1 新标题",
            "url": "https://bilibili.com/video/BV1",
        },
        {
            "id": "bili_4",
            "platform": "bilibili",
            "title": "视频3全新",
            "url": "https://bilibili.com/video/BV3",
        },
    ]
    favs_file.write_text(json.dumps(favs_data_new, ensure_ascii=False), encoding="utf-8")

    count3 = import_from_favs(favs_path=str(favs_file), db_path=str(db_file))
    assert count3 == 1

    tm = TopicManager(data_file=str(db_file))
    topics = tm.get_all()
    assert len(topics) == 3


def test_import_from_favs_nonexistent_file(tmp_path):
    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")

    count = import_from_favs(favs_path=str(tmp_path / "nonexistent.json"), db_path=str(db_file))
    assert count == 0
