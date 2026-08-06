---
name: esheep-topic-master
description: Use when managing topic lifecycles, serving the web kanban board, syncing raw social media favorites, or executing CLI topic status updates.
---

# esheep-topic-master

## Overview
`esheep-topic-master` provides full lifecycle management for content topics—from raw social media inspiration to completed articles or video scripts. Topics move through 4 distinct statuses in a structured Kanban pipeline.

## 4 Topic Lifecycle Statuses
1. `inbox`: Raw inspirations imported automatically or added manually.
2. `selected`: Curated topics selected for production.
3. `in_progress`: Topics currently being written, scripted, or edited.
4. `completed`: Published or finished topics.

## Core Workflows

### 1. Launch Web Kanban Dashboard
Runs the local REST API server and serves the visual Kanban board interface.
```bash
python scripts/server.py --port 8000
```
- Access Kanban Dashboard: `http://localhost:8000`
- Options:
  - `--port PORT`: Set listening port (default: `8000`).
  - `--db-path PATH`: Custom path to `topics.json`.
  - `--web-dir PATH`: Custom path to web static files.

### 2. Auto Sync from Social Favorites
Syncs raw social media favorites (e.g. from `esheep-social-favs-copilot`) into `inbox` with automatic deduplication by URL and title.
```bash
python scripts/import_favs.py
```
- Custom path usage:
```bash
python scripts/import_favs.py --favs-path ../esheep-social-favs-copilot/data/raw_favs.json --db-path data/topics.json
```

### 3. CLI Operations & Status Transitions
Use `topic_manager.py` for direct command-line query and state transitions:

- **List Topics**:
  ```bash
  python scripts/topic_manager.py list
  python scripts/topic_manager.py list --status inbox
  python scripts/topic_manager.py list --category "AI技术"
  ```
- **Add Topic**:
  ```bash
  python scripts/topic_manager.py add --title "DeepSeek-V3 架构剖析" --category "AI技术" --hook "10分钟看懂" --status inbox
  ```
- **Move Topic Status**:
  ```bash
  python scripts/topic_manager.py move --id <TOPIC_ID> --status selected
  python scripts/topic_manager.py move --id <TOPIC_ID> --status in_progress
  python scripts/topic_manager.py move --id <TOPIC_ID> --status completed
  ```

### 4. REST API Overview
- `GET /api/topics?status=<status>&category=<category>` - List topics
- `POST /api/topics` - Add a new topic (JSON payload)
- `PUT /api/topics/<id>` - Update topic fields or status (JSON payload)
- `DELETE /api/topics/<id>` - Delete a topic
- `POST /api/import-favs` - Trigger favs sync (`{"favs_path": "..."}`)

## Quick Reference
| Status | Description | Typical Action |
| --- | --- | --- |
| `inbox` | Unscreened idea | Review and transition to `selected` |
| `selected` | Approved idea | Assign angle/outline, transition to `in_progress` |
| `in_progress` | Active writing | Draft content, transition to `completed` |
| `completed` | Finished work | Archived for reference |
