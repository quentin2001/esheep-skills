import os
import json
import pytest
from scripts.storage import load_raw_favs, save_raw_favs, add_new_favs

TEST_FILE = "tests/test_raw_favs.json"

@pytest.fixture(autouse=True)
def cleanup():
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    yield
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_load_empty_storage():
    assert load_raw_favs(TEST_FILE) == []

def test_save_and_load_storage():
    sample = [{"id": "bili_123", "platform": "bilibili", "title": "Test Video", "url": "https://bilibili.com/video/123"}]
    assert save_raw_favs(sample, TEST_FILE) is True
    loaded = load_raw_favs(TEST_FILE)
    assert len(loaded) == 1
    assert loaded[0]["id"] == "bili_123"

def test_add_new_favs_deduplication():
    initial = [{"id": "bili_123", "platform": "bilibili", "title": "Test 1"}]
    save_raw_favs(initial, TEST_FILE)
    
    new_incoming = [
        {"id": "bili_123", "platform": "bilibili", "title": "Test 1"},
        {"id": "xhs_456", "platform": "xiaohongshu", "title": "Test 2"}
    ]
    added = add_new_favs(new_incoming, TEST_FILE)
    assert len(added) == 1
    assert added[0]["id"] == "xhs_456"
    assert len(load_raw_favs(TEST_FILE)) == 2
