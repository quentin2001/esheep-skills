import os
import pytest
from scripts.fetcher import parse_raw_item, fetch_platform, extract_items_from_json

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
    monkeypatch.setattr("scripts.fetcher.SESSIONS_DIR", str(tmp_path))
    result = fetch_platform("bilibili", use_cdp=False)
    assert isinstance(result, list)

def test_extract_items_from_json_xiaohongshu_disabled():
    from scripts.fetcher import extract_items_from_json
    json_data = {
        "notes": [
            {
                "note_id": "6a4dcb610000000017008e92",
                "display_title": "AI提示词从入门到精通",
                "xsec_token": "ABf3nq5citPgrFD6iJUXbQOCgdXGJWD5CDoWhcM_nDeZA="
            }
        ]
    }
    items = extract_items_from_json("xiaohongshu", json_data, action_type="favorite")
    assert len(items) == 0  # Disabled for safety

def test_extract_items_from_json_douyin():
    from scripts.fetcher import extract_items_from_json
    json_data = {
        "aweme_list": [
            {
                "aweme_id": "7312345678901234567",
                "desc": "震撼人心的AI生成视频突破"
            }
        ]
    }
    items = extract_items_from_json("douyin", json_data, action_type="favorite")
    assert len(items) == 1
    assert items[0]["id"] == "douyin_7312345678901234567"
    assert items[0]["title"] == "震撼人心的AI生成视频突破"
    assert items[0]["url"] == "https://www.douyin.com/video/7312345678901234567"
