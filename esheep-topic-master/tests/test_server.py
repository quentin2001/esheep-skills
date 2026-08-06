import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import pytest
from pathlib import Path

# Ensure scripts dir is in sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from server import run_server


@pytest.fixture
def server_env(tmp_path):
    db_path = tmp_path / "topics.json"
    web_dir = tmp_path / "web"
    web_dir.mkdir()
    index_file = web_dir / "index.html"
    index_file.write_text("<h1>eSheep Topic Master</h1>", encoding="utf-8")

    # Start server on port 0 (auto select port)
    httpd = run_server(port=0, db_path=db_path, web_dir=web_dir, block=False)
    port = httpd.server_address[1]
    base_url = f"http://127.0.0.1:{port}"

    yield {
        "base_url": base_url,
        "db_path": db_path,
        "web_dir": web_dir,
        "httpd": httpd,
    }

    httpd.shutdown()
    httpd.server_close()


def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
        req.data = body

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return resp.status, json.loads(resp_body) if resp_body else None
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            parsed_json = json.loads(resp_body)
        except Exception:
            parsed_json = resp_body
        return e.code, parsed_json


def test_get_topics_empty(server_env):
    url = f"{server_env['base_url']}/api/topics"
    status, data = make_request(url)
    assert status == 200
    assert data == []


def test_post_create_topic(server_env):
    url = f"{server_env['base_url']}/api/topics"
    payload = {
        "title": "AIGC 视频创作技巧",
        "category": "AI/剪辑",
        "hook": "3个步骤让你的视频播放量翻倍",
        "tags": ["AI", "短视频"],
    }
    status, data = make_request(url, method="POST", data=payload)
    assert status in (200, 201)
    assert data["title"] == "AIGC 视频创作技巧"
    assert data["category"] == "AI/剪辑"
    assert data["status"] == "inbox"
    assert "id" in data


def test_get_topics_filtering(server_env):
    url_post = f"{server_env['base_url']}/api/topics"
    make_request(url_post, method="POST", data={"title": "Topic 1", "category": "CatA", "status": "inbox"})
    make_request(url_post, method="POST", data={"title": "Topic 2", "category": "CatB", "status": "selected"})

    # Filter status=inbox
    status, data = make_request(f"{server_env['base_url']}/api/topics?status=inbox")
    assert status == 200
    assert len(data) == 1
    assert data[0]["title"] == "Topic 1"

    # Filter category=CatB
    status, data = make_request(f"{server_env['base_url']}/api/topics?category=CatB")
    assert status == 200
    assert len(data) == 1
    assert data[0]["title"] == "Topic 2"


def test_put_update_topic(server_env):
    url_post = f"{server_env['base_url']}/api/topics"
    _, created = make_request(url_post, method="POST", data={"title": "Original Title"})
    topic_id = created["id"]

    url_put = f"{server_env['base_url']}/api/topics/{topic_id}"
    update_payload = {"title": "Updated Title", "status": "in_progress"}
    status, data = make_request(url_put, method="PUT", data=update_payload)
    assert status == 200
    assert data["title"] == "Updated Title"
    assert data["status"] == "in_progress"


def test_put_update_topic_not_found(server_env):
    url_put = f"{server_env['base_url']}/api/topics/nonexistent-id"
    status, data = make_request(url_put, method="PUT", data={"title": "New Title"})
    assert status == 404
    assert "error" in data


def test_delete_topic(server_env):
    url_post = f"{server_env['base_url']}/api/topics"
    _, created = make_request(url_post, method="POST", data={"title": "To Delete"})
    topic_id = created["id"]

    url_del = f"{server_env['base_url']}/api/topics/{topic_id}"
    status, data = make_request(url_del, method="DELETE")
    assert status == 200
    assert data.get("success") is True

    # Verify deleted
    status, data = make_request(f"{server_env['base_url']}/api/topics")
    assert len(data) == 0


def test_delete_topic_not_found(server_env):
    url_del = f"{server_env['base_url']}/api/topics/nonexistent-id"
    status, data = make_request(url_del, method="DELETE")
    assert status == 404
    assert "error" in data


def test_post_import_favs(server_env, tmp_path):
    favs_file = tmp_path / "raw_favs.json"
    favs_data = [
        {
            "platform": "bilibili",
            "title": "B站热门灵感",
            "url": "https://www.bilibili.com/video/BV123456",
            "text_snippet": "精彩文案 hook",
            "tags": ["科普"],
        }
    ]
    favs_file.write_text(json.dumps(favs_data, ensure_ascii=False), encoding="utf-8")

    url_import = f"{server_env['base_url']}/api/import-favs"
    status, data = make_request(url_import, method="POST", data={"favs_path": str(favs_file)})
    assert status == 200
    assert data["imported"] == 1

    # Check imported topics
    status, data = make_request(f"{server_env['base_url']}/api/topics")
    assert len(data) == 1
    assert data[0]["source_title"] == "B站热门灵感"


def test_serve_static_file(server_env):
    url_static = f"{server_env['base_url']}/index.html"
    req = urllib.request.Request(url_static)
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        content = resp.read().decode("utf-8")
        assert "<h1>eSheep Topic Master</h1>" in content or "esheep-topic-master" in content


def test_serve_default_web_dir(tmp_path):
    # Test server serving the default BASE_DIR / web directory
    db_path = tmp_path / "topics.json"
    httpd = run_server(port=0, db_path=db_path, web_dir=None, block=False)
    port = httpd.server_address[1]
    base_url = f"http://127.0.0.1:{port}"

    try:
        with urllib.request.urlopen(f"{base_url}/") as resp:
            assert resp.status == 200
            content = resp.read().decode("utf-8")
            assert "Topic Master" in content
            assert "list-inbox" in content
    finally:
        httpd.shutdown()
        httpd.server_close()

