import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

VALID_STATUSES = ["inbox", "selected", "in_progress", "completed"]


class TopicManager:
    def __init__(self, data_file=None):
        if data_file is None:
            data_file = Path(__file__).parent.parent / "data" / "topics.json"
        self.data_file = Path(data_file)

    def _load(self):
        if not self.data_file.exists():
            return []
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, data):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(
        self,
        title,
        category="",
        hook="",
        source_platform="",
        source_title="",
        source_url="",
        angles=None,
        outline=None,
        tags=None,
        status="inbox",
    ):
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")

        now = datetime.now().isoformat()
        topic = {
            "id": str(uuid.uuid4()),
            "title": title,
            "category": category,
            "hook": hook,
            "source_platform": source_platform,
            "source_title": source_title,
            "source_url": source_url,
            "angles": angles if angles is not None else [],
            "outline": outline if outline is not None else [],
            "tags": tags if tags is not None else [],
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        topics = self._load()
        topics.append(topic)
        self._save(topics)
        return topic

    def get_all(self, status=None, category=None):
        topics = self._load()
        if status:
            topics = [t for t in topics if t.get("status") == status]
        if category:
            topics = [t for t in topics if t.get("category") == category]
        return topics

    def move(self, topic_id, new_status):
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of {VALID_STATUSES}")

        topics = self._load()
        found = False
        updated_topic = None
        for t in topics:
            if t.get("id") == topic_id:
                t["status"] = new_status
                t["updated_at"] = datetime.now().isoformat()
                found = True
                updated_topic = t
                break

        if not found:
            raise KeyError(f"Topic with ID '{topic_id}' not found.")

        self._save(topics)
        return updated_topic

    def update(self, topic_id, updates):
        if "status" in updates and updates["status"] not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{updates['status']}'. Must be one of {VALID_STATUSES}")

        topics = self._load()
        found = False
        updated_topic = None
        for t in topics:
            if t.get("id") == topic_id:
                for k, v in updates.items():
                    t[k] = v
                t["updated_at"] = datetime.now().isoformat()
                found = True
                updated_topic = t
                break

        if not found:
            raise KeyError(f"Topic with ID '{topic_id}' not found.")

        self._save(topics)
        return updated_topic

    def delete(self, topic_id):
        topics = self._load()
        initial_len = len(topics)
        topics = [t for t in topics if t.get("id") != topic_id]
        if len(topics) == initial_len:
            raise KeyError(f"Topic with ID '{topic_id}' not found.")

        self._save(topics)
        return True


def main():
    parser = argparse.ArgumentParser(description="esheep-topic-master Topic Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # List sub-command
    list_parser = subparsers.add_parser("list", help="List topics")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--category", help="Filter by category")

    # Add sub-command
    add_parser = subparsers.add_parser("add", help="Add a new topic")
    add_parser.add_argument("--title", required=True, help="Topic title")
    add_parser.add_argument("--category", default="", help="Category")
    add_parser.add_argument("--hook", default="", help="Hook/Angle entry point")
    add_parser.add_argument("--source-platform", default="", help="Source platform")
    add_parser.add_argument("--source-title", default="", help="Source title")
    add_parser.add_argument("--source-url", default="", help="Source URL")
    add_parser.add_argument("--angles", nargs="*", default=[], help="List of angles")
    add_parser.add_argument("--outline", nargs="*", default=[], help="Outline list")
    add_parser.add_argument("--tags", nargs="*", default=[], help="Tags list")
    add_parser.add_argument("--status", default="inbox", help="Initial status")

    # Move sub-command
    move_parser = subparsers.add_parser("move", help="Move topic to a new status")
    move_parser.add_argument("--id", required=True, help="Topic ID")
    move_parser.add_argument("--status", required=True, help="New status")

    args = parser.parse_args()
    tm = TopicManager()

    if args.command == "list":
        topics = tm.get_all(status=args.status, category=args.category)
        print(json.dumps(topics, ensure_ascii=False, indent=2))
    elif args.command == "add":
        topic = tm.add(
            title=args.title,
            category=args.category,
            hook=args.hook,
            source_platform=args.source_platform,
            source_title=args.source_title,
            source_url=args.source_url,
            angles=args.angles,
            outline=args.outline,
            tags=args.tags,
            status=args.status,
        )
        print(f"Topic added successfully: {topic['id']}")
    elif args.command == "move":
        try:
            topic = tm.move(topic_id=args.id, new_status=args.status)
            print(f"Topic {args.id} moved to status {args.status}")
        except (KeyError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
