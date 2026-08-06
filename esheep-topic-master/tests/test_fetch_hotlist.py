import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add scripts directory to python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fetch_hotlist import (
    ZhihuHotAdapter,
    WeiboHotAdapter,
    AIHotAdapter,
    fetch_hotlist,
    ingest_hotlist,
)
from topic_manager import TopicManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")
    return str(db_file)


# Mock Zhihu API response
MOCK_ZHIHU_RESPONSE = json.dumps({
    "data": [
        {
            "target": {
                "id": 10001,
                "title": "Zhihu Hot Topic 1",
                "excerpt": "Excerpt for zhihu topic 1",
                "url": "https://api.zhihu.com/questions/10001"
            },
            "detail_text": "1000 万热度"
        },
        {
            "target": {
                "id": 10002,
                "title": "Zhihu Hot Topic 2",
                "excerpt": "Excerpt for zhihu topic 2"
            },
            "detail_text": "800 万热度"
        }
    ]
}).encode("utf-8")

# Mock Weibo API response
MOCK_WEIBO_RESPONSE = json.dumps({
    "data": {
        "band_list": [
            {
                "word": "Weibo Hot Topic 1",
                "raw_hot": 2000000,
                "category": "科技"
            },
            {
                "note": "Weibo Hot Topic 2",
                "raw_hot": 1500000,
                "category": "娱乐"
            }
        ]
    }
}).encode("utf-8")

# Mock AIHot API response
MOCK_AIHOT_RESPONSE = json.dumps({
    "code": 200,
    "data": [
        {
            "title": "AIHot Topic 1",
            "url": "https://example.com/aihot/1",
            "description": "Description 1",
            "site": "aihot",
            "hot": 99
        },
        {
            "title": "AIHot Topic 2",
            "url": "https://example.com/aihot/2",
            "description": "Description 2",
            "site": "aihot",
            "hot": 88
        }
    ]
}).encode("utf-8")


def mock_urlopen_handler(url_or_req, timeout=10):
    url = url_or_req.full_url if hasattr(url_or_req, "full_url") else str(url_or_req)
    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    
    # Check browser User-Agent header
    if hasattr(url_or_req, "headers"):
        headers = url_or_req.headers
        user_agent = headers.get("User-agent") or headers.get("User-Agent")
        assert user_agent is not None, "Browser User-Agent header missing"
        assert "Mozilla" in user_agent

    if "zhihu.com" in url:
        mock_resp.read.return_value = MOCK_ZHIHU_RESPONSE
    elif "weibo.com" in url:
        mock_resp.read.return_value = MOCK_WEIBO_RESPONSE
    elif "aihot" in url:
        mock_resp.read.return_value = MOCK_AIHOT_RESPONSE
    else:
        raise ValueError(f"Unexpected URL: {url}")
    return mock_resp


@patch("urllib.request.urlopen", side_effect=mock_urlopen_handler)
def test_zhihu_adapter(mock_urlopen):
    adapter = ZhihuHotAdapter()
    items = adapter.fetch(limit=10)
    assert len(items) == 2
    assert items[0]["title"] == "Zhihu Hot Topic 1"
    assert items[0]["source_platform"] == "zhihu"
    assert items[0]["source_type"] == "hotlist"
    assert "https://www.zhihu.com/question/10001" in items[0]["source_url"]


@patch("urllib.request.urlopen", side_effect=mock_urlopen_handler)
def test_weibo_adapter(mock_urlopen):
    adapter = WeiboHotAdapter()
    items = adapter.fetch(limit=10)
    assert len(items) == 2
    assert items[0]["title"] == "Weibo Hot Topic 1"
    assert items[0]["source_platform"] == "weibo"
    assert items[0]["source_type"] == "hotlist"
    assert "weibo.com" in items[0]["source_url"]


@patch("urllib.request.urlopen", side_effect=mock_urlopen_handler)
def test_aihot_adapter(mock_urlopen):
    adapter = AIHotAdapter()
    items = adapter.fetch(limit=10)
    assert len(items) == 2
    assert items[0]["title"] == "AIHot Topic 1"
    assert items[0]["source_platform"] == "aihot"
    assert items[0]["source_type"] == "hotlist"
    assert items[0]["source_url"] == "https://example.com/aihot/1"


@patch("urllib.request.urlopen", side_effect=Exception("Network Connection Refused"))
def test_adapters_network_error_resilience(mock_urlopen):
    assert ZhihuHotAdapter().fetch() == []
    assert WeiboHotAdapter().fetch() == []
    assert AIHotAdapter().fetch() == []


@patch("urllib.request.urlopen", side_effect=mock_urlopen_handler)
def test_fetch_hotlist_multi_source(mock_urlopen):
    items = fetch_hotlist(sources=["zhihu", "weibo"], limit=1)
    assert len(items) == 2  # 1 from zhihu, 1 from weibo
    platforms = [item["source_platform"] for item in items]
    assert "zhihu" in platforms
    assert "weibo" in platforms


@patch("urllib.request.urlopen", side_effect=mock_urlopen_handler)
def test_ingest_hotlist(mock_urlopen, temp_db):
    items = fetch_hotlist(sources=["zhihu", "weibo", "aihot"], limit=10)
    count = ingest_hotlist(items, db_path=temp_db)
    assert count == 6

    tm = TopicManager(data_file=temp_db)
    topics = tm.get_all()
    assert len(topics) == 6
    for t in topics:
        assert t["status"] == "inbox"
        assert t["source_type"] == "hotlist"

    # Deduplication test
    count_second_time = ingest_hotlist(items, db_path=temp_db)
    assert count_second_time == 0
