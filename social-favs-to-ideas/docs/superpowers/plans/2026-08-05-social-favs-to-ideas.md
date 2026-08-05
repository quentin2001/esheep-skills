# Social Favorites to Content Ideas Skill (`social-favs-to-ideas`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an automated Agent Skill (`social-favs-to-ideas`) that scans a user's likes and favorites across Bilibili, Zhihu, Xiaohongshu, Douyin, and X/Twitter using Playwright, and transforms them into a structured self-media topic database (`data/content_ideas_database.md`).

**Architecture:** A Python-based Playwright scraper (`scripts/fetcher.py`) uses saved browser session states (`.sessions/`) to extract new liked/bookmarked posts from 5 platforms and deduplicate them into `data/raw_favs.json`. An Agent Skill (`.agents/skills/social-favs-to-ideas/SKILL.md`) processes newly cached items, reverse-engineers viral hooks, suggests 3 distinct topic angles, and appends them to `data/content_ideas_database.md`.

**Tech Stack:** Python 3.10+, Playwright, pytest, Markdown.

## Global Constraints
- Target platforms: Bilibili, Zhihu, Xiaohongshu, Douyin (likes & favorites), X/Twitter.
- All session states stored locally in `.sessions/`.
- No hardcoded user credentials or passwords.
- Output database path: `data/content_ideas_database.md`.
- Scraped raw data cache: `data/raw_favs.json`.

---

### Task 1: Environment Setup & Data Cache Model

**Files:**
- Create: `scripts/config.py`
- Create: `scripts/storage.py`
- Test: `tests/test_storage.py`

**Interfaces:**
- Consumes: None
- Produces: `storage.load_raw_favs(file_path)` -> list, `storage.save_raw_favs(items, file_path)` -> bool, `storage.add_new_favs(new_items, file_path)` -> list

- [ ] **Step 1: Write failing test for storage module**

Create `tests/test_storage.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage.py`
Expected: FAIL with ModuleNotFoundError or AttributeError.

- [ ] **Step 3: Write minimal implementation for config and storage**

Create `scripts/config.py`:
```python
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_DIR = os.path.join(BASE_DIR, ".sessions")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_FAVS_FILE = os.path.join(DATA_DIR, "raw_favs.json")
IDEAS_DB_FILE = os.path.join(DATA_DIR, "content_ideas_database.md")

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
```

Create `scripts/storage.py`:
```python
import os
import json

def load_raw_favs(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_raw_favs(items, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return True

def add_new_favs(new_items, file_path):
    existing = load_raw_favs(file_path)
    existing_ids = {item["id"] for item in existing if "id" in item}
    
    truly_new = []
    for item in new_items:
        if item.get("id") not in existing_ids:
            existing.append(item)
            existing_ids.add(item.get("id"))
            truly_new.append(item)
            
    save_raw_favs(existing, file_path)
    return truly_new
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/config.py scripts/storage.py tests/test_storage.py
git commit -m "feat: add storage and configuration module for favs caching"
```

---

### Task 2: Interactive Login Helper (`login_helper.py`)

**Files:**
- Create: `scripts/login_helper.py`
- Test: `tests/test_login_helper.py`

**Interfaces:**
- Consumes: `scripts/config.py:SESSIONS_DIR`
- Produces: `.sessions/<platform>_state.json` (Playwright storage state files)

- [ ] **Step 1: Write failing test for login_helper CLI argument parser**

Create `tests/test_login_helper.py`:
```python
import pytest
from scripts.login_helper import get_session_path, PLATFORMS

def test_get_session_path():
    path = get_session_path("bilibili")
    assert path.endswith("bilibili_state.json")
    assert "bilibili" in PLATFORMS

def test_invalid_platform():
    with pytest.raises(ValueError):
        get_session_path("unknown_platform")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_login_helper.py`
Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 3: Write minimal implementation for login_helper**

Create `scripts/login_helper.py`:
```python
import os
import sys
import argparse
from scripts.config import SESSIONS_DIR

PLATFORMS = {
    "bilibili": "https://passport.bilibili.com/login",
    "zhihu": "https://www.zhihu.com/signin",
    "xiaohongshu": "https://www.xiaohongshu.com",
    "douyin": "https://www.douyin.com",
    "x": "https://x.com/i/flow/login"
}

def get_session_path(platform: str) -> str:
    if platform not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}")
    return os.path.join(SESSIONS_DIR, f"{platform}_state.json")

def login_platform(platform: str):
    from playwright.sync_api import sync_playwright
    url = PLATFORMS[platform]
    save_path = get_session_path(platform)
    print(f"[*] Opening browser for {platform}. Please log in manually...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        input(f"[>] Press ENTER in this console after you have successfully logged into {platform}...")
        context.storage_state(path=save_path)
        print(f"[✓] Saved session state to {save_path}")
        browser.close()

def main():
    parser = argparse.ArgumentParser(description="Interactive Login Helper for Social Platforms")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], required=True, help="Platform to log in")
    args = parser.parse_args()

    if args.platform == "all":
        for p in PLATFORMS:
            login_platform(p)
    else:
        login_platform(args.platform)

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_login_helper.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/login_helper.py tests/test_login_helper.py
git commit -m "feat: add login_helper for initial platform session capture"
```

---

### Task 3: Multi-Platform Scraper Engine (`fetcher.py`)

**Files:**
- Create: `scripts/fetcher.py`
- Test: `tests/test_fetcher.py`

**Interfaces:**
- Consumes: `.sessions/<platform>_state.json`, `scripts/storage.py:add_new_favs`
- Produces: Scraped raw JSON records stored in `data/raw_favs.json`

- [ ] **Step 1: Write failing unit test for parser logic**

Create `tests/test_fetcher.py`:
```python
import pytest
from scripts.fetcher import parse_raw_item

def test_parse_raw_item_normalization():
    raw_bili = {
        "platform": "bilibili",
        "id": "BV123456",
        "title": "AI Agent Tutorial",
        "url": "https://www.bilibili.com/video/BV123456",
        "tags": ["AI", "Tech"]
    }
    normalized = parse_raw_item(raw_bili)
    assert normalized["id"] == "bilibili_BV123456"
    assert normalized["platform"] == "bilibili"
    assert normalized["title"] == "AI Agent Tutorial"
    assert "scraped_at" in normalized
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fetcher.py`
Expected: FAIL with ModuleNotFoundError.

- [ ] **Step 3: Implement fetcher engine with Playwright page scrapers**

Create `scripts/fetcher.py`:
```python
import os
import time
import argparse
from datetime import datetime
from scripts.config import RAW_FAVS_FILE, SESSIONS_DIR
from scripts.storage import add_new_favs
from scripts.login_helper import get_session_path, PLATFORMS

def parse_raw_item(item: dict) -> dict:
    raw_id = item.get("id", str(time.time()))
    platform = item.get("platform", "generic")
    return {
        "id": f"{platform}_{raw_id}",
        "platform": platform,
        "action_type": item.get("action_type", "favorite"), # 'favorite' or 'like'
        "title": item.get("title", "").strip(),
        "url": item.get("url", ""),
        "text_snippet": item.get("text_snippet", "").strip(),
        "tags": item.get("tags", []),
        "scraped_at": datetime.now().isoformat()
    }

def fetch_platform(platform: str, headless: bool = True) -> list:
    session_file = get_session_path(platform)
    if not os.path.exists(session_file):
        print(f"[!] Session state for {platform} not found. Please run login_helper.py --platform {platform} first.")
        return []

    items = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(storage_state=session_file)
        page = context.new_page()

        try:
            if platform == "bilibili":
                page.goto("https://space.bilibili.com/favlist")
                page.wait_for_timeout(3000)
                cards = page.query_selector_all(".fav-video-list li")
                for c in cards[:10]:
                    title_el = c.query_selector("a.title")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "bilibili",
                            "action_type": "favorite",
                            "id": title_el.get_attribute("href") or "",
                            "title": title_el.inner_text(),
                            "url": "https:" + (title_el.get_attribute("href") or "")
                        }))
            elif platform == "zhihu":
                page.goto("https://www.zhihu.com/collections/mine")
                page.wait_for_timeout(3000)
                titles = page.query_selector_all(".SelfCollectionItem-title")
                for t in titles[:10]:
                    items.append(parse_raw_item({
                        "platform": "zhihu",
                        "action_type": "favorite",
                        "id": t.inner_text(),
                        "title": t.inner_text(),
                        "url": page.url
                    }))
            elif platform == "xiaohongshu":
                page.goto("https://www.xiaohongshu.com/user/profile/self")
                page.wait_for_timeout(3000)
                notes = page.query_selector_all(".note-item")
                for n in notes[:10]:
                    title_el = n.query_selector(".title")
                    link_el = n.query_selector("a")
                    if title_el and link_el:
                        href = link_el.get_attribute("href") or ""
                        items.append(parse_raw_item({
                            "platform": "xiaohongshu",
                            "action_type": "favorite",
                            "id": href,
                            "title": title_el.inner_text(),
                            "url": "https://www.xiaohongshu.com" + href
                        }))
            elif platform == "douyin":
                # Scrape Douyin Likes
                page.goto("https://www.douyin.com/user/self?showTab=like")
                page.wait_for_timeout(3000)
                vids = page.query_selector_all("li.E5C77L8Q")
                for v in vids[:5]:
                    title_el = v.query_selector("p")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "douyin",
                            "action_type": "like",
                            "id": title_el.inner_text()[:20],
                            "title": title_el.inner_text(),
                            "url": page.url
                        }))
                # Scrape Douyin Favorites
                page.goto("https://www.douyin.com/user/self?showTab=favorite")
                page.wait_for_timeout(3000)
                fav_vids = page.query_selector_all("li.E5C77L8Q")
                for v in fav_vids[:5]:
                    title_el = v.query_selector("p")
                    if title_el:
                        items.append(parse_raw_item({
                            "platform": "douyin",
                            "action_type": "favorite",
                            "id": "fav_" + title_el.inner_text()[:20],
                            "title": title_el.inner_text(),
                            "url": page.url
                        }))
            elif platform == "x":
                page.goto("https://x.com/i/bookmarks")
                page.wait_for_timeout(3000)
                tweets = page.query_selector_all("article[data-testid='tweet']")
                for tw in tweets[:10]:
                    text_el = tw.query_selector("div[data-testid='tweetText']")
                    if text_el:
                        items.append(parse_raw_item({
                            "platform": "x",
                            "action_type": "favorite",
                            "id": text_el.inner_text()[:20],
                            "title": text_el.inner_text()[:50],
                            "text_snippet": text_el.inner_text(),
                            "url": page.url
                        }))
        except Exception as e:
            print(f"[!] Error fetching {platform}: {e}")

        browser.close()
    return items

def main():
    parser = argparse.ArgumentParser(description="Fetch social media favorites & likes")
    parser.add_argument("--platform", choices=list(PLATFORMS.keys()) + ["all"], default="all")
    parser.add_argument("--headless", action="store_true", default=True)
    args = parser.parse_args()

    all_fetched = []
    platforms = list(PLATFORMS.keys()) if args.platform == "all" else [args.platform]

    for p in platforms:
        print(f"[*] Fetching from {p}...")
        fetched = fetch_platform(p, headless=args.headless)
        all_fetched.extend(fetched)

    added = add_new_favs(all_fetched, RAW_FAVS_FILE)
    print(f"[✓] Fetch complete. Scraped {len(all_fetched)} items, added {len(added)} new items to {RAW_FAVS_FILE}.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_fetcher.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/fetcher.py tests/test_fetcher.py
git commit -m "feat: add multi-platform scraper engine for favs and likes"
```

---

### Task 4: Agent Skill Specification (`SKILL.md`)

**Files:**
- Create: `.agents/skills/social-favs-to-ideas/SKILL.md`
- Test: `.agents/skills/social-favs-to-ideas/SKILL.md` (Self-verification)

**Interfaces:**
- Consumes: `data/raw_favs.json`
- Produces: Formatted entries in `data/content_ideas_database.md`

- [ ] **Step 1: Write Agent Skill Definition**

Create `.agents/skills/social-favs-to-ideas/SKILL.md`:
```markdown
---
name: social-favs-to-ideas
description: Use when the user wants to scan their liked/bookmarked social media posts from Bilibili, Zhihu, Xiaohongshu, Douyin, or X, and convert them into actionable self-media topic ideas.
---

# Social Media Favorites to Content Ideas Skill

Transform your passive social media likes and favorites into a high-converting self-media topic database.

## Workflow

1. **Trigger Data Scraper**:
   Execute the background fetcher to gather the latest items from your social accounts:
   ```bash
   python scripts/fetcher.py --platform all
   ```

2. **Read Incremental Raw Data**:
   Read `data/raw_favs.json` to inspect newly fetched items.

3. **Topic & Hook Deconstruction**:
   For each new item (or group of related items), perform self-media reverse engineering:
   - **Core Hook**: Identify what specific headline, pain point, or contrast grabbed attention.
   - **Topic Clustering**: Categorize by domain (e.g., AI/Tech, Productivity, Career, Lifestyle).
   - **3 Angle Conversions**:
     - *Angle 1 (Beginner Guide / How-to)*
     - *Angle 2 (Pitfalls / Counter-intuitive opinion)*
     - *Angle 3 (Practical comparison / Case study)*
   - **Title Options**: Generate 3 high-CTR titles tailored for Xiaohongshu, Bilibili, or Zhihu.

4. **Update Topic Database**:
   Format the resulting topic breakdown and append it to `data/content_ideas_database.md`.

## Database Output Format

```markdown
### 💡 [Topic Category] <Topic Title>

- **Source Reference**: [<Platform>] <Original Post Title> (<URL>)
- **Core Hook**: <Why this caught your attention / Core insight>
- **Content Angles**:
  1. **[How-To Guide]**: <Title Suggestion 1>
  2. **[Common Pitfalls]**: <Title Suggestion 2>
  3. **[Case Study]**: <Title Suggestion 3>
- **Key Outline & Call-to-Action**:
  - Point 1: ...
  - Point 2: ...
  - CTA: ...
---
```
```

- [ ] **Step 2: Commit Skill definition**

```bash
git add .agents/skills/social-favs-to-ideas/SKILL.md
git commit -m "feat: add social-favs-to-ideas agent skill definition"
```

---

### Task 5: End-to-End Pipeline Verification

**Files:**
- Create: `tests/test_e2e_pipeline.py`
- Modify: `data/content_ideas_database.md`

- [ ] **Step 1: Write E2E Pipeline integration test**

Create `tests/test_e2e_pipeline.py`:
```python
import os
import json
import pytest
from scripts.storage import add_new_favs, load_raw_favs
from scripts.config import RAW_FAVS_FILE, IDEAS_DB_FILE

def test_full_pipeline_flow(tmp_path):
    raw_file = tmp_path / "raw_favs.json"
    db_file = tmp_path / "ideas.md"
    
    mock_scraped = [
        {
            "id": "bilibili_BV111",
            "platform": "bilibili",
            "action_type": "favorite",
            "title": "Build AI Agents in 10 Mins",
            "url": "https://bilibili.com/video/BV111",
            "text_snippet": "Full tutorial on AI Agents",
            "scraped_at": "2026-08-05T17:50:00"
        }
    ]
    
    added = add_new_favs(mock_scraped, str(raw_file))
    assert len(added) == 1
    
    # Simulate Skill writing entry
    db_entry = f"### 💡 [AI/Tech] {added[0]['title']}\n- **Source**: {added[0]['url']}\n"
    with open(db_file, "w", encoding="utf-8") as f:
        f.write(db_entry)
        
    assert os.path.exists(db_file)
    with open(db_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Build AI Agents in 10 Mins" in content
```

- [ ] **Step 2: Run test to verify E2E pipeline**

Run: `pytest tests/test_e2e_pipeline.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_e2e_pipeline.py
git commit -m "test: add end-to-end pipeline verification test"
```
