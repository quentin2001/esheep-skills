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

## 3 Topic Source Taxonomy
1. `hotlist`: Hot topic items collected automatically from platforms (Zhihu, Weibo, AIHot).
2. `social_fav`: Social media favorites/bookmarks imported from tools like `esheep-social-favs-copilot`.
3. `original_idea`: Native or manually added creative ideas (including OCR-extracted screenshot inspirations).

## Zero-Image Storage Screenshot Workflow (截图灵感“即抛即抠，文本化入库”)
When the user sends a screenshot or image in chat to add as a topic:
1. **Never store image files locally**: The system database (`topics.json`) stores 100% pure text structured data.
2. **Instant Agent Vision OCR & Extraction**: The Agent uses vision capabilities to immediately extract:
   - Topic Title (选题标题)
   - Hook / Core Insights (爆点观点与摘要)
   - Source Platform (识别原截图平台，如“小红书截图”、“微信群截图”)
3. **Ingest Pure Text Card**: Agent calls `TopicManager.add(source_type="original_idea", tag="📸 截图灵感")` to add the pure text card to `inbox`.
4. **Fallback for Non-Multimodal Models**: If using a text-only LLM, the user or agent can use system native OCR (e.g. `tesseract` / `Windows.Media.Ocr`) or copy-paste OCR text directly.

## Core Workflows

### 1. Auto-Start Web Kanban Dashboard
Whenever the user starts discussing topics, querying topics, or adding ideas in chat, the Agent MUST automatically ensure the local REST API server is running in the background:
- Run `python scripts/server.py --port 18922` via `run_command` (IsDaemon=true).
- Inform user on first start: "选题看板已在后台静默运行：http://localhost:18922"
- Options:
  - `--port PORT`: Set listening port (default: `18922`).
  - `--db-path PATH`: Custom path to `topics.json`.
  - `--web-dir PATH`: Custom path to web static files.

### 2. Multi-Adapter Hotlist Fetching
Fetches trending hot topics with default 5-source strategy (`aihot`, `weibo`, `zhihu`, `xiaohongshu`, `douyin`) and optional ingestion into `inbox` (`source_type="hotlist"`).
- Default execution (5 core sources):
```bash
python scripts/fetch_hotlist.py --sources aihot,weibo,zhihu,xiaohongshu,douyin --limit 15 --ingest
```
- Full platform catalog supported: `aihot`, `weibo`, `zhihu`, `xiaohongshu`, `douyin`, `toutiao`, `bilibili`, `baidu`.
- Print JSON without ingesting:
```bash
python scripts/fetch_hotlist.py --sources aihot,weibo,zhihu --limit 10
```

### 3. Auto Sync from Social Favorites
Syncs raw social media favorites (e.g. from `esheep-social-favs-copilot`) into `inbox` (`source_type="social_fav"`) with automatic deduplication by URL and title.
```bash
python scripts/import_favs.py
```
- Custom path usage:
```bash
python scripts/import_favs.py --favs-path ../esheep-social-favs-copilot/data/raw_favs.json --db-path data/topics.json
```

### 4. CLI Operations & Status Transitions
Use `topic_manager.py` for direct command-line query and state transitions:

- **List Topics**:
  ```bash
  python scripts/topic_manager.py list
  python scripts/topic_manager.py list --status inbox
  python scripts/topic_manager.py list --source-type hotlist
  python scripts/topic_manager.py list --category "AI技术"
  ```
- **Add Topic**:
  ```bash
  python scripts/topic_manager.py add --title "DeepSeek-V3 架构剖析" --category "AI技术" --hook "10分钟看懂" --source-type original_idea --status inbox
  ```
- **Move Topic Status**:
  ```bash
  python scripts/topic_manager.py move --id <TOPIC_ID> --status selected
  python scripts/topic_manager.py move --id <TOPIC_ID> --status in_progress
  python scripts/topic_manager.py move --id <TOPIC_ID> --status completed
  ```

### 5. Auto-Archiving Completed Topics
Archives completed topics older than N days (default 30 days) from `data/topics.json` into `data/archive_topics.json` with deduplication:
```bash
python scripts/archive_topics.py --days 30
```
- Custom path usage:
```bash
python scripts/archive_topics.py --days 30 --db-path data/topics.json --archive-path data/archive_topics.json
```

### 6. REST API Overview
- `GET /api/topics?status=<status>&category=<category>&source_type=<source_type>` - List topics
- `POST /api/topics` - Add a new topic (JSON payload)
- `PUT /api/topics/<id>` - Update topic fields or status (JSON payload)
- `DELETE /api/topics/<id>` - Delete a topic
- `POST /api/import-favs` - Trigger favs sync (`{"favs_path": "..."}`)
- `POST /api/fetch-hotlist` - Trigger hotlist fetch (`{"sources": ["zhihu", "weibo", "aihot"], "limit": 15, "ingest": true}`)
- `POST /api/topics/archive` - Trigger auto-archiving (`{"days": 30}`)

## Quick Reference
| Status | Description | Typical Action |
| --- | --- | --- |
| `inbox` | Unscreened idea | Review and transition to `selected` |
| `selected` | Approved idea | Assign angle/outline, transition to `in_progress` |
| `in_progress` | Active writing | Draft content, transition to `completed` |
| `completed` | Finished work | Archived for reference |

