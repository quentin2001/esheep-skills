# [Fetch Hotlist & 3-Source Topic Pipeline] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement extensible multi-adapter hotlist fetching (`fetch_hotlist.py`), support 3-source topic metadata (`source_type`: `hotlist` | `social_fav` | `original_idea`) across `TopicManager`, REST API, and `SKILL.md`.

**Architecture:** Add `source_type` attribute to `TopicManager`. Create modular `fetch_hotlist.py` with extensible adapter classes (`ZhihuHotAdapter`, `WeiboHotAdapter`, `AIHotAdapter`) that fetch public APIs with browser User-Agents, normalize entries, deduplicate, and ingest into `topics.json` under `inbox` status.

**Tech Stack:** Python 3 standard library (`urllib.request`, `json`, `hashlib`, `argparse`, `unittest.mock`), pytest.

## Global Constraints

- No third-party mandatory Python runtime dependencies (use Python stdlib `urllib.request`, `json`).
- Graceful degradation: failing endpoints must return empty lists without crashing the process.
- 100% TDD test coverage for all new adapters and database ingestion logic.

---

### Task 1: Extend `TopicManager` to support `source_type` metadata & filtering

**Files:**
- Modify: `esheep-topic-master/scripts/topic_manager.py`
- Test: `esheep-topic-master/tests/test_topic_manager.py`

**Interfaces:**
- Consumes: `topics.json`
- Produces: `TopicManager.add(..., source_type="original_idea")`, `TopicManager.get_all(source_type=None)`

- [ ] **Step 1: Write failing tests in `test_topic_manager.py`**

```python
def test_topic_manager_source_type_filter(tmp_path):
    db_path = tmp_path / "topics.json"
    tm = TopicManager(db_path=str(db_path))
    tm.add("Hot News 1", "Tech", source_type="hotlist")
    tm.add("Social Pin", "Tech", source_type="social_fav")
    tm.add("My Thought", "Tech", source_type="original_idea")
    
    assert len(tm.get_all(source_type="hotlist")) == 1
    assert tm.get_all(source_type="hotlist")[0]["title"] == "Hot News 1"
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `pytest esheep-topic-master/tests/test_topic_manager.py -v`
Expected: FAIL (`unexpected keyword argument 'source_type'`)

- [ ] **Step 3: Implement `source_type` in `topic_manager.py`**

```python
VALID_SOURCE_TYPES = ["hotlist", "social_fav", "original_idea"]
# Update add() and get_all() methods
```

- [ ] **Step 4: Run pytest to verify pass**

Run: `pytest esheep-topic-master/tests/test_topic_manager.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add esheep-topic-master/scripts/topic_manager.py esheep-topic-master/tests/test_topic_manager.py
git commit -m "feat(topic-master): add source_type metadata and filtering to TopicManager"
```

---

### Task 2: Implement `fetch_hotlist.py` Multi-Adapter Fetcher & Ingestion

**Files:**
- Create: `esheep-topic-master/scripts/fetch_hotlist.py`
- Create: `esheep-topic-master/tests/test_fetch_hotlist.py`

**Interfaces:**
- Consumes: Public API endpoints (Zhihu, Weibo, AIHot)
- Produces: `fetch_hotlist(sources, limit=15)`, `ingest_hotlist(items, db_path)`

- [ ] **Step 1: Write failing test in `test_fetch_hotlist.py`**

```python
from unittest.mock import patch
from scripts.fetch_hotlist import fetch_hotlist, ingest_hotlist

def test_fetch_hotlist_zhihu_mock():
    # Mock urllib response for zhihu
    pass
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `pytest esheep-topic-master/tests/test_fetch_hotlist.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'scripts.fetch_hotlist'`)

- [ ] **Step 3: Implement `fetch_hotlist.py` adapters**

Implement `ZhihuHotAdapter`, `WeiboHotAdapter`, `AIHotAdapter`, `fetch_hotlist()`, and `ingest_hotlist()`.

- [ ] **Step 4: Run pytest to verify pass**

Run: `pytest esheep-topic-master/tests/test_fetch_hotlist.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add esheep-topic-master/scripts/fetch_hotlist.py esheep-topic-master/tests/test_fetch_hotlist.py
git commit -m "feat(topic-master): add fetch_hotlist multi-adapter fetcher and deduplicating ingestion"
```

---

### Task 3: Update `SKILL.md` and CLI documentation for 3-Source Workflows

**Files:**
- Modify: `esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md`
- Modify: `esheep-topic-master/README.md`

- [ ] **Step 1: Update `SKILL.md` with 3-source taxonomy and `fetch_hotlist.py` instructions**
- [ ] **Step 2: Run full pytest suite across `esheep-topic-master/tests`**

Run: `pytest esheep-topic-master/tests/ -v`
Expected: 100% PASS

- [ ] **Step 3: Commit**

```bash
git add esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md esheep-topic-master/README.md
git commit -m "docs(topic-master): document 3-source topic workflows and fetch_hotlist usage in SKILL.md"
```
