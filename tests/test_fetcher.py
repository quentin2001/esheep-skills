import os
import pytest
from scripts.fetcher import parse_raw_item, fetch_platform, extract_items_from_html

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

def test_extract_bilibili_html_fixture():
    html = """
    <div class="fav-video-list">
        <li>
            <a href="//www.bilibili.com/video/BV17x411c7z9" class="title">Bilibili Agent Tutorial</a>
        </li>
    </div>
    """
    items = extract_items_from_html("bilibili", html, action_type="favorite")
    assert len(items) == 1
    assert items[0]["id"] == "bilibili_BV17x411c7z9"
    assert items[0]["title"] == "Bilibili Agent Tutorial"
    assert items[0]["url"] == "https://www.bilibili.com/video/BV17x411c7z9"
    assert items[0]["action_type"] == "favorite"

def test_extract_zhihu_html_fixture():
    html = """
    <div class="ContentItem">
        <h2 class="ContentItem-title">
            <a href="/question/123456/answer/789012">How to build AI agents?</a>
        </h2>
    </div>
    <div class="SelfCollectionItem">
        <a href="/p/987654">Zhihu Article Title</a>
    </div>
    """
    items = extract_items_from_html("zhihu", html, action_type="like")
    assert len(items) == 2
    assert items[0]["id"] == "zhihu_answer_789012"
    assert items[0]["url"] == "https://www.zhihu.com/question/123456/answer/789012"
    assert items[0]["title"] == "How to build AI agents?"
    assert items[0]["action_type"] == "like"
    assert items[1]["id"] == "zhihu_p_987654"
    assert items[1]["url"] == "https://www.zhihu.com/p/987654"

def test_extract_xiaohongshu_html_fixture():
    html = """
    <div class="note-item">
        <a href="/explore/64f123450000000000000000">
            <span class="title">Xiaohongshu Note Title</span>
        </a>
    </div>
    """
    items = extract_items_from_html("xiaohongshu", html, action_type="favorite")
    assert len(items) == 1
    assert items[0]["id"] == "xiaohongshu_64f123450000000000000000"
    assert items[0]["url"] == "https://www.xiaohongshu.com/explore/64f123450000000000000000"
    assert items[0]["title"] == "Xiaohongshu Note Title"

def test_extract_douyin_html_fixture():
    html = """
    <div class="video-card">
        <a href="/video/7123456789012345678">
            <p>Douyin Video Title</p>
        </a>
    </div>
    """
    items = extract_items_from_html("douyin", html, action_type="like")
    assert len(items) == 1
    assert items[0]["id"] == "douyin_like_7123456789012345678"
    assert items[0]["url"] == "https://www.douyin.com/video/7123456789012345678"
    assert items[0]["title"] == "Douyin Video Title"
    assert items[0]["action_type"] == "like"

def test_extract_x_html_fixture():
    html = """
    <article data-testid="tweet">
        <div data-testid="tweetText">Awesome open source project released!</div>
        <a href="/user/status/18273645590">
            <time>Aug 5</time>
        </a>
    </article>
    """
    items = extract_items_from_html("x", html, action_type="favorite")
    assert len(items) == 1
    assert items[0]["id"] == "x_18273645590"
    assert items[0]["url"] == "https://x.com/i/web/status/18273645590"
    assert items[0]["text_snippet"] == "Awesome open source project released!"
    assert items[0]["title"] == "Awesome open source project released!"
    assert items[0]["action_type"] == "favorite"
