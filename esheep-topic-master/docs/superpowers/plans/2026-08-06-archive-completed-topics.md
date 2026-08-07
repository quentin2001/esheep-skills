# [Auto-Archiving Completed Topics] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement auto-archiving for completed topics older than N days (`scripts/archive_topics.py`), storing them in `data/archive_topics.json` and integrating auto-archiving into `TopicManager` & `SKILL.md`.

**Architecture:** Create `scripts/archive_topics.py` with `archive_completed_topics(days=30, db_path, archive_path)`. Extend `TopicManager` to support optional auto-archiving on load or via API endpoint `/api/topics/archive`. Update `SKILL.md` to document archive CLI commands and querying past archives.

**Tech Stack:** Python 3 standard library (`json`, `datetime`, `pathlib`, `argparse`), pytest.

## Global Constraints

- Zero third-party Python runtime dependencies.
- Deduplicate archived topics when appending to `data/archive_topics.json`.
- 100% TDD test coverage for `archive_topics.py`.

---

### Task 1: Implement `archive_topics.py` and unit tests

**Files:**
- Create: `esheep-topic-master/scripts/archive_topics.py`
- Create: `esheep-topic-master/tests/test_archive_topics.py`

**Interfaces:**
- Consumes: `topics.json`
- Produces: `archive_completed_topics(days=30, db_path=None, archive_path=None) -> int`

- [ ] **Step 1: Write failing test in `test_archive_topics.py`**

```python
from datetime import datetime, timedelta
from scripts.archive_topics import archive_completed_topics
from scripts.topic_manager import TopicManager

def test_archive_completed_topics(tmp_path):
    db_path = tmp_path / "topics.json"
    archive_path = tmp_path / "archive_topics.json"
    tm = TopicManager(db_path=str(db_path))
    
    t1 = tm.add("Recent Done", "Tech", status="completed")
    t2 = tm.add("Old Done", "Tech", status="completed")
    
    # Backdate t2 created_at to 40 days ago
    old_date = (datetime.now() - timedelta(days=40)).isoformat()
    tm.update(t2["id"], {"created_at": old_date, "updated_at": old_date})
    
    archived_count = archive_completed_topics(days=30, db_path=str(db_path), archive_path=str(archive_path))
    assert archived_count == 1
```

- [ ] **Step 2: Run pytest to verify failure**

Run: `pytest esheep-topic-master/tests/test_archive_topics.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'scripts.archive_topics'`)

- [ ] **Step 3: Implement `scripts/archive_topics.py`**

```python
def archive_completed_topics(days=30, db_path=None, archive_path=None):
    # Move completed topics older than N days from db_path to archive_path
    pass
```

- [ ] **Step 4: Run pytest to verify pass**

Run: `pytest esheep-topic-master/tests/test_archive_topics.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add esheep-topic-master/scripts/archive_topics.py esheep-topic-master/tests/test_archive_topics.py
git commit -m "feat(topic-master): add archive_topics.py for auto-archiving old completed topics"
```

---

### Task 2: Integrate Auto-Archiving into REST Server & `SKILL.md`

**Files:**
- Modify: `esheep-topic-master/scripts/server.py`
- Modify: `esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md`
- Test: `esheep-topic-master/tests/test_server.py`

- [ ] **Step 1: Add `/api/topics/archive` endpoint to `server.py`**
- [ ] **Step 2: Update `SKILL.md` with auto-archiving workflows**
- [ ] **Step 3: Run full pytest suite**

Run: `pytest esheep-topic-master/tests/ -v`
Expected: 100% PASS

- [ ] **Step 4: Commit**

```bash
git add esheep-topic-master/scripts/server.py esheep-topic-master/.agents/skills/esheep-topic-master/SKILL.md
git commit -m "feat(topic-master): integrate archiving endpoint and update SKILL.md documentation"
```
