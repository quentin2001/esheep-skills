# esheep-topic-master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `esheep-topic-master`, a lightweight topic library and 4-stage Kanban workflow management Skill for eSheep content creators, featuring JSON storage, CLI management, auto-import from `esheep-social-favs-copilot`, and a single-page HTML/JS web dashboard.

**Architecture:** Python standard library HTTP server (`http.server`) hosting REST API endpoints and static web assets for a responsive 4-column Kanban UI (`inbox` -> `selected` -> `in_progress` -> `completed`). CLI tools manage `data/topics.json` and sync items from social media favorites.

**Tech Stack:** Python 3.10+, Standard Library (http.server, json, argparse), Vanilla HTML5/CSS3/JavaScript.

## Global Constraints
- Target directory: `e:\Projects\skill-maker\esheep-topic-master`
- Data store: `e:\Projects\skill-maker\esheep-topic-master\data\topics.json`
- 4 Kanban statuses: `inbox`, `selected`, `in_progress`, `completed`
- No third-party pip dependencies required for basic server and CLI execution.

---

### Task 1: Core Topic Model & CLI Database Manager

**Files:**
- Create: `esheep-topic-master/data/topics.json`
- Create: `esheep-topic-master/scripts/topic_manager.py`
- Create: `esheep-topic-master/tests/test_topic_manager.py`

**Interfaces:**
- Consumes: None
- Produces: `TopicManager` class in `scripts/topic_manager.py` with methods `get_all()`, `add(topic_data)`, `move(topic_id, new_status)`, `update(topic_id, updates)`, `delete(topic_id)`.

- [ ] **Step 1: Write failing test for TopicManager**

```python
# esheep-topic-master/tests/test_topic_manager.py
import json
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.topic_manager import TopicManager

@pytest.fixture
def tmp_db(tmp_path):
    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")
    return str(db_file)

def test_add_and_get_topic(tmp_db):
    tm = TopicManager(db_path=tmp_db)
    topic = tm.add(title="测试选题", category="AI", hook="Hook测试")
    assert topic["id"].startswith("topic_")
    assert topic["status"] == "inbox"
    assert topic["title"] == "测试选题"
    
    all_topics = tm.get_all()
    assert len(all_topics) == 1
    assert all_topics[0]["title"] == "测试选题"

def test_move_topic_status(tmp_db):
    tm = TopicManager(db_path=tmp_db)
    topic = tm.add(title="流转选题", category="效率")
    updated = tm.move(topic["id"], "selected")
    assert updated["status"] == "selected"

def test_update_topic(tmp_db):
    tm = TopicManager(db_path=tmp_db)
    topic = tm.add(title="原标题")
    updated = tm.update(topic["id"], {"title": "新标题", "outline": "1. 步骤一"})
    assert updated["title"] == "新标题"
    assert updated["outline"] == "1. 步骤一"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest esheep-topic-master/tests/test_topic_manager.py -v`
Expected: FAIL with ModuleNotFoundError or FileNotFoundError

- [ ] **Step 3: Implement initial empty data store and TopicManager**

```python
# esheep-topic-master/data/topics.json
[]
```

```python
# esheep-topic-master/scripts/topic_manager.py
import os
import json
import time
import argparse

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "topics.json")
VALID_STATUSES = ["inbox", "selected", "in_progress", "completed"]

class TopicManager:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def get_all(self):
        with open(self.db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_all(self, topics):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)

    def add(self, title, category="未分类", hook="", source_platform="", source_title="", source_url="", angles=None, outline="", tags=None, status="inbox"):
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        topics = self.get_all()
        now_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        topic_id = f"topic_{int(time.time())}_{os.urandom(2).hex()}"
        new_item = {
            "id": topic_id,
            "title": title,
            "status": status,
            "category": category,
            "source_platform": source_platform,
            "source_title": source_title,
            "source_url": source_url,
            "hook": hook,
            "angles": angles or [],
            "outline": outline,
            "tags": tags or [],
            "created_at": now_str,
            "updated_at": now_str
        }
        topics.append(new_item)
        self.save_all(topics)
        return new_item

    def move(self, topic_id, new_status):
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        topics = self.get_all()
        target = None
        for item in topics:
            if item["id"] == topic_id:
                item["status"] = new_status
                item["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                target = item
                break
        if target:
            self.save_all(topics)
        return target

    def update(self, topic_id, updates):
        topics = self.get_all()
        target = None
        for item in topics:
            if item["id"] == topic_id:
                for k, v in updates.items():
                    if k in item and k != "id":
                        item[k] = v
                item["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
                target = item
                break
        if target:
            self.save_all(topics)
        return target

    def delete(self, topic_id):
        topics = self.get_all()
        new_topics = [t for t in topics if t["id"] != topic_id]
        if len(new_topics) != len(topics):
            self.save_all(new_topics)
            return True
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="esheep-topic-master CLI")
    subparsers = parser.add_subparsers(dest="command")

    # list
    list_p = subparsers.add_parser("list")
    list_p.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")

    # add
    add_p = subparsers.add_parser("add")
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--category", default="未分类")
    add_p.add_argument("--hook", default="")

    # move
    move_p = subparsers.add_parser("move")
    move_p.add_argument("--id", required=True)
    move_p.add_argument("--status", required=True, choices=VALID_STATUSES)

    args = parser.parse_args()
    tm = TopicManager()

    if args.command == "list":
        topics = tm.get_all()
        if args.status:
            topics = [t for t in topics if t["status"] == args.status]
        print(json.dumps(topics, ensure_ascii=False, indent=2))
    elif args.command == "add":
        item = tm.add(title=args.title, category=args.category, hook=args.hook)
        print(f"Added: {item['id']} - {item['title']}")
    elif args.command == "move":
        item = tm.move(args.id, args.status)
        print(f"Moved: {item['id']} -> {args.status}" if item else "Topic not found")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest esheep-topic-master/tests/test_topic_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

Commit changes with message `feat(topic-master): add TopicManager and core JSON database`

---

### Task 2: Favs Import Integration Script

**Files:**
- Create: `esheep-topic-master/scripts/import_favs.py`
- Create: `esheep-topic-master/tests/test_import_favs.py`

**Interfaces:**
- Consumes: `TopicManager` from `scripts/topic_manager.py`, reads `esheep-social-favs-copilot/data/raw_favs.json` if available.
- Produces: `import_from_favs(favs_json_path, db_path)` function.

- [ ] **Step 1: Write failing test for import_favs**

```python
# esheep-topic-master/tests/test_import_favs.py
import json
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.topic_manager import TopicManager
from scripts.import_favs import import_from_favs

def test_import_from_favs(tmp_path):
    raw_favs_file = tmp_path / "raw_favs.json"
    raw_favs_data = [
        {
            "id": "xhs_123",
            "platform": "xiaohongshu",
            "action_type": "favorite",
            "title": "爆款小红书排版技巧",
            "url": "https://xiaohongshu.com/explore/123",
            "text_snippet": "钩子：如何实现自媒体高效增长",
            "tags": ["小红书", "运营"]
        }
    ]
    raw_favs_file.write_text(json.dumps(raw_favs_data, ensure_ascii=False), encoding="utf-8")

    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")

    count = import_from_favs(favs_path=str(raw_favs_file), db_path=str(db_file))
    assert count == 1

    tm = TopicManager(db_path=str(db_file))
    topics = tm.get_all()
    assert len(topics) == 1
    assert topics[0]["title"] == "爆款小红书排版技巧"
    assert topics[0]["source_platform"] == "xiaohongshu"
    assert topics[0]["status"] == "inbox"

    # Re-importing should deduplicate based on source_url or source_title
    count2 = import_from_favs(favs_path=str(raw_favs_file), db_path=str(db_file))
    assert count2 == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest esheep-topic-master/tests/test_import_favs.py -v`
Expected: FAIL with ModuleNotFoundError or FileNotFoundError

- [ ] **Step 3: Implement import_favs.py**

```python
# esheep-topic-master/scripts/import_favs.py
import os
import json
import argparse
from scripts.topic_manager import TopicManager, DEFAULT_DB_PATH

DEFAULT_FAVS_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "esheep-social-favs-copilot", "data", "raw_favs.json"))

def import_from_favs(favs_path=DEFAULT_FAVS_PATH, db_path=DEFAULT_DB_PATH):
    if not os.path.exists(favs_path):
        print(f"Favs raw file not found at: {favs_path}")
        return 0

    with open(favs_path, "r", encoding="utf-8") as f:
        try:
            favs_data = json.load(f)
        except json.JSONDecodeError:
            return 0

    tm = TopicManager(db_path=db_path)
    existing_topics = tm.get_all()
    existing_urls = {t.get("source_url") for t in existing_topics if t.get("source_url")}
    existing_titles = {t.get("source_title") for t in existing_topics if t.get("source_title")}

    imported_count = 0
    for fav in favs_data:
        url = fav.get("url", "")
        title = fav.get("title", "")
        if (url and url in existing_urls) or (title and title in existing_titles):
            continue

        platform = fav.get("platform", "unknown")
        snippet = fav.get("text_snippet", "")
        tags = fav.get("tags", [])

        tm.add(
            title=title or f"来自于 {platform} 的未命名灵感",
            category=tags[0] if tags else "社媒采集",
            hook=snippet,
            source_platform=platform,
            source_title=title,
            source_url=url,
            tags=tags,
            status="inbox"
        )
        imported_count += 1

    return imported_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import favs into topic master inbox")
    parser.add_argument("--favs-path", default=DEFAULT_FAVS_PATH)
    args = parser.parse_args()
    count = import_from_favs(favs_path=args.favs_path)
    print(f"Successfully imported {count} new topics into Inbox.")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest esheep-topic-master/tests/test_import_favs.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

Commit changes with message `feat(topic-master): add social favs auto-import integration`

---

### Task 3: Lightweight REST API & Web Server

**Files:**
- Create: `esheep-topic-master/scripts/server.py`
- Create: `esheep-topic-master/tests/test_server.py`

**Interfaces:**
- GET `/api/topics` -> Returns JSON array of topics
- POST `/api/topics` -> Creates new topic
- PUT `/api/topics/<id>` -> Updates topic fields or status
- DELETE `/api/topics/<id>` -> Deletes topic
- POST `/api/import-favs` -> Triggers import script
- GET `/` & `/static/*` -> Serves static files from `web/`

- [ ] **Step 1: Write failing test for server API endpoints**

```python
# esheep-topic-master/tests/test_server.py
import json
import pytest
import urllib.request
import threading
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.server import run_server

@pytest.fixture(scope="module")
def server_url(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("db")
    db_file = tmp_dir / "topics.json"
    db_file.write_text("[]", encoding="utf-8")

    port = 8899
    server = threading.Thread(target=run_server, kwargs={"port": port, "db_path": str(db_file), "block": False}, daemon=True)
    server.start()
    time.sleep(0.5)
    return f"http://127.0.0.1:{port}"

def test_api_topics_crud(server_url):
    # GET empty
    req = urllib.request.urlopen(f"{server_url}/api/topics")
    assert req.status == 200
    data = json.loads(req.read().decode("utf-8"))
    assert data == []

    # POST add topic
    post_data = json.dumps({"title": "API测试选题", "category": "测试"}).encode("utf-8")
    req_post = urllib.request.Request(f"{server_url}/api/topics", data=post_data, headers={"Content-Type": "application/json"}, method="POST")
    res_post = urllib.request.urlopen(req_post)
    assert res_post.status == 200
    created = json.loads(res_post.read().decode("utf-8"))
    topic_id = created["id"]
    assert created["title"] == "API测试选题"

    # PUT update status
    put_data = json.dumps({"status": "selected"}).encode("utf-8")
    req_put = urllib.request.Request(f"{server_url}/api/topics/{topic_id}", data=put_data, headers={"Content-Type": "application/json"}, method="PUT")
    res_put = urllib.request.urlopen(req_put)
    assert res_put.status == 200
    updated = json.loads(res_put.read().decode("utf-8"))
    assert updated["status"] == "selected"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest esheep-topic-master/tests/test_server.py -v`
Expected: FAIL with ModuleNotFoundError or connection refused

- [ ] **Step 3: Implement server.py using http.server**

```python
# esheep-topic-master/scripts/server.py
import http.server
import socketserver
import json
import os
import urllib.parse
import argparse
from scripts.topic_manager import TopicManager, DEFAULT_DB_PATH
from scripts.import_favs import import_from_favs

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web"))

class TopicRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, db_path=DEFAULT_DB_PATH, **kwargs):
        self.db_path = db_path
        self.tm = TopicManager(db_path=self.db_path)
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/topics":
            self.send_json_response(200, self.tm.get_all())
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/topics":
            body = self.read_json_body()
            if not body or "title" not in body:
                self.send_json_response(400, {"error": "Title required"})
                return
            new_item = self.tm.add(
                title=body["title"],
                category=body.get("category", "未分类"),
                hook=body.get("hook", ""),
                source_platform=body.get("source_platform", ""),
                source_title=body.get("source_title", ""),
                source_url=body.get("source_url", ""),
                angles=body.get("angles", []),
                outline=body.get("outline", ""),
                tags=body.get("tags", []),
                status=body.get("status", "inbox")
            )
            self.send_json_response(200, new_item)
        elif parsed.path == "/api/import-favs":
            count = import_from_favs(db_path=self.db_path)
            self.send_json_response(200, {"message": f"Imported {count} items", "imported_count": count})
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/topics/"):
            topic_id = parsed.path.split("/")[-1]
            body = self.read_json_body()
            if "status" in body and len(body) == 1:
                updated = self.tm.move(topic_id, body["status"])
            else:
                updated = self.tm.update(topic_id, body)
            if updated:
                self.send_json_response(200, updated)
            else:
                self.send_json_response(404, {"error": "Topic not found"})
        else:
            self.send_json_response(404, {"error": "Not found"})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/topics/"):
            topic_id = parsed.path.split("/")[-1]
            success = self.tm.delete(topic_id)
            if success:
                self.send_json_response(200, {"success": True})
            else:
                self.send_json_response(404, {"error": "Topic not found"})
        else:
            self.send_json_response(404, {"error": "Not found"})

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body_bytes = self.rfile.read(content_length)
        try:
            return json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

def make_handler(db_path):
    return lambda *args, **kwargs: TopicRequestHandler(*args, db_path=db_path, **kwargs)

def run_server(port=8000, db_path=DEFAULT_DB_PATH, block=True):
    handler = make_handler(db_path)
    httpd = socketserver.TCPServer(("0.0.0.0", port), handler)
    print(f"esheep-topic-master Server running at http://localhost:{port}")
    if block:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
    else:
        httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="esheep-topic-master Server")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_server(port=args.port)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest esheep-topic-master/tests/test_server.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

Commit changes with message `feat(topic-master): add HTTP REST API server`

---

### Task 4: Vanilla JS & Glassmorphism 4-Column Kanban Web UI

**Files:**
- Create: `esheep-topic-master/web/index.html`
- Create: `esheep-topic-master/web/styles.css`
- Create: `esheep-topic-master/web/app.js`

**Interfaces:**
- Connects to `/api/topics` and `/api/import-favs`.
- HTML5 Drag and Drop across 4 columns (`inbox`, `selected`, `in_progress`, `completed`).
- Topic Detail & Edit Modal dialog.

- [ ] **Step 1: Create HTML structure with 4 Kanban columns and Modal**

```html
<!-- esheep-topic-master/web/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>esheep-topic-master 选题掌管者</title>
  <link rel="stylesheet" href="styles.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-title">
        <span class="logo">🐑</span>
        <h1>esheep-topic-master 选题掌管者</h1>
      </div>
      <div class="actions">
        <input type="text" id="search-input" placeholder="🔍 搜索选题标题/标签..." class="search-bar">
        <button id="import-btn" class="btn btn-secondary">🔄 一键导入社媒收藏</button>
        <button id="new-topic-btn" class="btn btn-primary">➕ 新增选题</button>
      </div>
    </header>

    <main class="kanban-board">
      <!-- Column 1: Inbox -->
      <div class="kanban-column" data-status="inbox">
        <div class="column-header inbox-header">
          <h2>📥 未选中的散落选题 <span class="count" id="count-inbox">0</span></h2>
        </div>
        <div class="card-list" id="list-inbox" ondragover="allowDrop(event)" ondrop="drop(event, 'inbox')"></div>
      </div>

      <!-- Column 2: Selected -->
      <div class="kanban-column" data-status="selected">
        <div class="column-header selected-header">
          <h2>🎯 选中的选题 <span class="count" id="count-selected">0</span></h2>
        </div>
        <div class="card-list" id="list-selected" ondragover="allowDrop(event)" ondrop="drop(event, 'selected')"></div>
      </div>

      <!-- Column 3: In Progress -->
      <div class="kanban-column" data-status="in_progress">
        <div class="column-header progress-header">
          <h2>🚧 正在做的选题 <span class="count" id="count-in_progress">0</span></h2>
        </div>
        <div class="card-list" id="list-in_progress" ondragover="allowDrop(event)" ondrop="drop(event, 'in_progress')"></div>
      </div>

      <!-- Column 4: Completed -->
      <div class="kanban-column" data-status="completed">
        <div class="column-header completed-header">
          <h2>✅ 做完的选题 <span class="count" id="count-completed">0</span></h2>
        </div>
        <div class="card-list" id="list-completed" ondragover="allowDrop(event)" ondrop="drop(event, 'completed')"></div>
      </div>
    </main>
  </div>

  <!-- Modal for Topic View/Edit -->
  <div id="topic-modal" class="modal hidden">
    <div class="modal-content glass-panel">
      <span class="close-btn" id="modal-close">&times;</span>
      <h3 id="modal-heading">编辑选题</h3>
      <form id="topic-form">
        <input type="hidden" id="edit-id">
        <div class="form-group">
          <label>选题标题</label>
          <input type="text" id="edit-title" required class="input-field">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>阶段状态</label>
            <select id="edit-status" class="input-field">
              <option value="inbox">📥 未选中的散落选题</option>
              <option value="selected">🎯 选中的选题</option>
              <option value="in_progress">🚧 正在做的选题</option>
              <option value="completed">✅ 做完的选题</option>
            </select>
          </div>
          <div class="form-group">
            <label>分类 / 领域</label>
            <input type="text" id="edit-category" class="input-field">
          </div>
        </div>
        <div class="form-group">
          <label>核心 Hook / 吸引点</label>
          <textarea id="edit-hook" rows="2" class="input-field"></textarea>
        </div>
        <div class="form-group">
          <label>切入角度 (每行一个)</label>
          <textarea id="edit-angles" rows="3" class="input-field"></textarea>
        </div>
        <div class="form-group">
          <label>文案 / 脚本大纲</label>
          <textarea id="edit-outline" rows="5" class="input-field" placeholder="1. 痛点引入..."></textarea>
        </div>
        <div class="form-actions">
          <button type="button" id="delete-btn" class="btn btn-danger">🗑️ 删除</button>
          <button type="submit" class="btn btn-primary">💾 保存</button>
        </div>
      </form>
    </div>
  </div>

  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Add CSS styles with dark glassmorphism aesthetic**

```css
/* esheep-topic-master/web/styles.css */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background-color: #0f172a;
  color: #f8fafc;
  min-height: 100vh;
  padding: 24px;
}

.app-container {
  max-width: 1600px;
  margin: 0 auto;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.logo-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo { font-size: 32px; }
h1 { font-size: 20px; font-weight: 700; }

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-bar {
  padding: 8px 16px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #fff;
  min-width: 260px;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.btn-primary { background: #3b82f6; color: white; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: #334155; color: #f8fafc; }
.btn-secondary:hover { background: #475569; }
.btn-danger { background: #ef4444; color: white; }
.btn-danger:hover { background: #dc2626; }

.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-items: start;
}

.kanban-column {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 16px;
  min-height: 80vh;
}

.column-header {
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 2px solid #334155;
}

.column-header h2 {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
}

.count {
  background: #334155;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 13px;
}

.card-list {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 14px;
  cursor: grab;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.topic-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
}

.card-tag {
  display: inline-block;
  font-size: 11px;
  padding: 2px 6px;
  background: #0f172a;
  border-radius: 4px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
}

.card-hook {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.3;
}

/* Modal */
.modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal.hidden { display: none; }

.modal-content {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
  width: 550px;
  max-width: 90vw;
  padding: 24px;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px; right: 20px;
  font-size: 24px;
  cursor: pointer;
  color: #94a3b8;
}

.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
.input-field {
  width: 100%;
  padding: 8px 12px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: white;
  font-family: inherit;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-actions { display: flex; justify-content: space-between; margin-top: 20px; }
```

- [ ] **Step 3: Add JavaScript interactivity (API fetch, drag and drop, modal editing)**

```javascript
// esheep-topic-master/web/app.js
let allTopics = [];

document.addEventListener("DOMContentLoaded", () => {
  fetchTopics();

  document.getElementById("import-btn").addEventListener("click", importFavs);
  document.getElementById("new-topic-btn").addEventListener("click", openNewModal);
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("topic-form").addEventListener("submit", saveTopic);
  document.getElementById("delete-btn").addEventListener("click", deleteTopic);
  document.getElementById("search-input").addEventListener("input", filterTopics);
});

async function fetchTopics() {
  try {
    const res = await fetch("/api/topics");
    allTopics = await res.json();
    renderBoard(allTopics);
  } catch (err) {
    console.error("Failed to fetch topics:", err);
  }
}

function renderBoard(topics) {
  const statuses = ["inbox", "selected", "in_progress", "completed"];
  statuses.forEach(s => {
    const listEl = document.getElementById(`list-${s}`);
    const countEl = document.getElementById(`count-${s}`);
    listEl.innerHTML = "";
    
    const filtered = topics.filter(t => t.status === s);
    countEl.textContent = filtered.length;

    filtered.forEach(item => {
      const card = document.createElement("div");
      card.className = "topic-card";
      card.draggable = true;
      card.dataset.id = item.id;
      card.ondragstart = (e) => e.dataTransfer.setData("text/plain", item.id);
      card.ondblclick = () => openEditModal(item);

      card.innerHTML = `
        <span class="card-tag">${escapeHtml(item.category || "未分类")}</span>
        <div class="card-title">${escapeHtml(item.title)}</div>
        ${item.hook ? `<div class="card-hook">💡 ${escapeHtml(item.hook)}</div>` : ''}
      `;
      listEl.appendChild(card);
    });
  });
}

function allowDrop(ev) {
  ev.preventDefault();
}

async function drop(ev, newStatus) {
  ev.preventDefault();
  const id = ev.dataTransfer.getData("text/plain");
  if (!id) return;

  const item = allTopics.find(t => t.id === id);
  if (item && item.status !== newStatus) {
    item.status = newStatus;
    renderBoard(allTopics);
    await fetch(`/api/topics/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
  }
}

async function importFavs() {
  const btn = document.getElementById("import-btn");
  btn.textContent = "⏳ 正在同步...";
  try {
    const res = await fetch("/api/import-favs", { method: "POST" });
    const result = await res.json();
    alert(`成功同步 ${result.imported_count} 条最新选题到未选池！`);
    fetchTopics();
  } catch (e) {
    alert("导入失败，请确保 esheep-social-favs-copilot 已有数据");
  } finally {
    btn.textContent = "🔄 一键导入社媒收藏";
  }
}

function openEditModal(topic) {
  document.getElementById("edit-id").value = topic.id;
  document.getElementById("edit-title").value = topic.title || "";
  document.getElementById("edit-status").value = topic.status || "inbox";
  document.getElementById("edit-category").value = topic.category || "";
  document.getElementById("edit-hook").value = topic.hook || "";
  document.getElementById("edit-angles").value = (topic.angles || []).join("\n");
  document.getElementById("edit-outline").value = topic.outline || "";
  
  document.getElementById("modal-heading").textContent = "编辑选题";
  document.getElementById("delete-btn").style.display = "block";
  document.getElementById("topic-modal").classList.remove("hidden");
}

function openNewModal() {
  document.getElementById("edit-id").value = "";
  document.getElementById("topic-form").reset();
  document.getElementById("modal-heading").textContent = "新增选题";
  document.getElementById("delete-btn").style.display = "none";
  document.getElementById("topic-modal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("topic-modal").classList.add("hidden");
}

async function saveTopic(e) {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;
  const payload = {
    title: document.getElementById("edit-title").value,
    status: document.getElementById("edit-status").value,
    category: document.getElementById("edit-category").value,
    hook: document.getElementById("edit-hook").value,
    angles: document.getElementById("edit-angles").value.split("\n").filter(a => a.trim()),
    outline: document.getElementById("edit-outline").value
  };

  if (id) {
    await fetch(`/api/topics/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } else {
    await fetch("/api/topics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }
  closeModal();
  fetchTopics();
}

async function deleteTopic() {
  const id = document.getElementById("edit-id").value;
  if (id && confirm("确定要删除此选题吗？")) {
    await fetch(`/api/topics/${id}`, { method: "DELETE" });
    closeModal();
    fetchTopics();
  }
}

function filterTopics(e) {
  const query = e.target.value.toLowerCase();
  const filtered = allTopics.filter(t => 
    (t.title && t.title.toLowerCase().includes(query)) ||
    (t.category && t.category.toLowerCase().includes(query))
  );
  renderBoard(filtered);
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
```

- [ ] **Step 4: Verify static file serving via server test**

Run: `pytest esheep-topic-master/tests/test_server.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

Commit changes with message `feat(topic-master): add responsive 4-column glassmorphism Kanban web UI`

---

### Task 5: Skill Definition & Agent Integration

**Files:**
- Create: `esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md`
- Create: `esheep-topic-master/README.md`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: esheep-topic-master
description: 硅基电子羊 (eSheep) 出品 - 选题流转管理与 4 阶段 (未选中/已选中/进行中/已完成) 看板副驾驶。
---

# eSheep Topic Master (硅基电子羊 · 选题掌管者)

`esheep-topic-master` 提供全流程选题库管理能力，连接前道社媒爆款灵感抓取 (`esheep-social-favs-copilot`)，并提供可视化的本地 4 列 Kanban 状态流转与编辑看板。

## Skill Capabilities & Workflows

### 1. Launch Web Kanban Dashboard
When user asks: "打开选题看板", "启动选题库页面", "查看我的选题看板":
- Run `python scripts/server.py --port 8000` via `run_command` (IsDaemon=true).
- Inform user: "选题看板已在本地启动，访问链接：http://localhost:8000"

### 2. Auto Sync from Social Favs
When user asks: "把最新的社媒收藏同步到选题库", "导入爆款灵感":
- Run `python scripts/import_favs.py`.
- Report: "已成功将最新收藏导入至【散落选题】库。"

### 3. Quick Status Query & Transition via Chat
- View topics: `python scripts/topic_manager.py list --status inbox`
- Move topic: `python scripts/topic_manager.py move --id <topic_id> --status <selected|in_progress|completed>`
- Add manual topic: `python scripts/topic_manager.py add --title "<Title>" --category "<Category>"`

## Topic Life Cycle States
1. `inbox`: 未选中的散落选题
2. `selected`: 选中的选题
3. `in_progress`: 正在做的选题
4. `completed`: 做完的选题
```

- [ ] **Step 2: Write README.md**

```markdown
# esheep-topic-master (硅基电子羊 · 选题掌管者)

轻量级自媒体选题流转与 Kanban 看板管理系统。

## Quick Start

```bash
# 启动 Web 看板 (浏览器打开 http://localhost:8000)
python scripts/server.py --port 8000

# 导入社媒收藏灵感
python scripts/import_favs.py

# CLI 命令
python scripts/topic_manager.py list
```
```

- [ ] **Step 3: Commit**

Commit changes with message `docs(topic-master): add SKILL.md definition and README`
