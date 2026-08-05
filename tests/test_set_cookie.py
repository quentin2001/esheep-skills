import os
import json
import pytest
from scripts.set_cookie import cookie_str_to_storage_state, set_platform_cookie

def test_cookie_str_parsing(tmp_path):
    cookie_raw = "web_session=123456; a1=abcdef; _gid=GA1.2.3"
    state = cookie_str_to_storage_state("xiaohongshu", cookie_raw)
    assert len(state["cookies"]) == 3
    assert state["cookies"][0]["name"] == "web_session"
    assert state["cookies"][0]["value"] == "123456"
    assert state["cookies"][0]["domain"] == ".xiaohongshu.com"
