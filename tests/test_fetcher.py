import os
import pytest
from scripts.fetcher import parse_raw_item, fetch_platform

def test_parse_raw_item_normalization():
    raw_bili = {
        "platform": "bilibili",
        "id": "BV123456",
        "title": "  AI Agent Tutorial  ",
        "url": "https://www.bilibili.com/video/BV123456",
        "tags": ["AI", "Tech"]
    }
    normalized = parse_raw_item(raw_bili)
    assert normalized["id"] == "bilibili_BV123456"
    assert normalized["platform"] == "bilibili"
    assert normalized["action_type"] == "favorite"
    assert normalized["title"] == "AI Agent Tutorial"
    assert normalized["url"] == "https://www.bilibili.com/video/BV123456"
    assert normalized["text_snippet"] == ""
    assert normalized["tags"] == ["AI", "Tech"]
    assert "scraped_at" in normalized

def test_parse_raw_item_custom_fields():
    raw_item = {
        "platform": "douyin",
        "id": "like_999",
        "action_type": "like",
        "title": "Short Video",
        "url": "https://www.douyin.com",
        "text_snippet": "  snippet text  ",
        "tags": ["short"]
    }
    normalized = parse_raw_item(raw_item)
    assert normalized["id"] == "douyin_like_999"
    assert normalized["platform"] == "douyin"
    assert normalized["action_type"] == "like"
    assert normalized["title"] == "Short Video"
    assert normalized["text_snippet"] == "snippet text"
    assert normalized["tags"] == ["short"]

def test_fetch_platform_missing_session(tmp_path, monkeypatch):
    # Ensure missing session returns empty list
    monkeypatch.setattr("scripts.fetcher.get_session_path", lambda p: str(tmp_path / f"{p}_nonexistent.json"))
    result = fetch_platform("bilibili")
    assert result == []
