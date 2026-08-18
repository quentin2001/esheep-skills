#!/usr/bin/env python3
"""
Topic Helper - Markdown Topic Management and Lifecycle CLI

Manages Markdown topic files with YAML frontmatter across lifecycle statuses:
  - inbox: Raw ideas and analyzed drafts
  - selected: Approved topics scheduled for production
  - in_progress: Topics currently being drafted / scripted
  - completed: Published or archived topics
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

VALID_STATUSES = ["inbox", "selected", "in_progress", "completed"]


def slugify(text: str) -> str:
    """Convert title to a clean URL/filename friendly slug."""
    text = text.strip().lower()
    # Replace non-alphanumeric chars (excluding CJK characters and hyphens) with hyphen
    text = re.sub(r"[^\w\u4e00-\u9fa5]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "topic"


def format_yaml_frontmatter(meta: dict) -> str:
    """Format metadata dictionary into YAML frontmatter string."""
    lines = ["---"]
    for key, value in meta.items():
        if isinstance(value, list):
            items_str = ", ".join(f'"{v}"' if "," in str(v) else str(v) for v in value)
            lines.append(f"{key}: [{items_str}]")
        elif isinstance(value, str):
            if value == "":
                lines.append(f'{key}: ""')
            elif "\n" in value or ":" in value or '"' in value or value.startswith("[") or value.startswith("{"):
                clean_val = value.replace('"', '\\"')
                lines.append(f'{key}: "{clean_val}"')
            else:
                lines.append(f"{key}: {value}")
        elif value is None:
            lines.append(f"{key}: null")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def parse_yaml_frontmatter(text: str) -> Tuple[dict, str]:
    """Parse YAML frontmatter and Markdown body from text."""
    meta: Dict[str, Union[str, list, None, bool]] = {}
    body = text

    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        return meta, body

    yaml_content, body = match.group(1), match.group(2)
    current_key = None

    for raw_line in yaml_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Handle list item: - value
        if line.startswith("- ") or line.startswith("-"):
            val = line.lstrip("-").strip().strip('"\'')
            if current_key:
                if not isinstance(meta.get(current_key), list):
                    meta[current_key] = [val] if val else []
                else:
                    if val:
                        meta[current_key].append(val)
            continue

        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            current_key = k

            # Handle list format [a, b, c]
            if v.startswith("[") and v.endswith("]"):
                inner = v[1:-1].strip()
                if not inner:
                    meta[k] = []
                else:
                    items = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
                    meta[k] = items
            # Handle quoted string
            elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                meta[k] = v[1:-1]
            elif v.lower() == "null":
                meta[k] = None
            elif v.lower() == "true":
                meta[k] = True
            elif v.lower() == "false":
                meta[k] = False
            elif v == "":
                meta[k] = ""
            else:
                meta[k] = v

    return meta, body


def create_topic(
    title: str,
    source_type: str = "idea",
    content: str = "",
    tags: Optional[List[str]] = None,
    source_url: Optional[str] = None,
    status: str = "inbox",
    potential_score: Optional[Union[str, float]] = None,
    base_dir: Union[str, Path] = "topics",
) -> Path:
    """Create a new topic Markdown file in the appropriate status directory."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")

    base_path = Path(base_dir)
    status_dir = base_path / status
    status_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    clean_title = title.strip()
    slug = slugify(clean_title)[:40]

    # Generate unique ID and filename
    topic_id = f"{now.strftime('%Y%m%d')}-{slug}"
    filename = f"{date_str}-{slug}.md"
    file_path = status_dir / filename

    # Avoid collision
    counter = 1
    while file_path.exists():
        filename = f"{date_str}-{slug}-{counter}.md"
        topic_id = f"{now.strftime('%Y%m%d')}-{slug}-{counter}"
        file_path = status_dir / filename
        counter += 1

    meta = {
        "id": topic_id,
        "title": clean_title,
        "created_at": date_str,
        "source_type": source_type,
        "source_url": source_url or "",
        "tags": tags or [],
        "status": status,
        "potential_score": str(potential_score) if potential_score is not None else "",
    }

    full_content = format_yaml_frontmatter(meta) + "\n\n" + (content.strip() or f"# 📌 选题：{clean_title}\n")
    file_path.write_text(full_content, encoding="utf-8")
    return file_path


def list_topics(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    base_dir: Union[str, Path] = "topics",
) -> List[dict]:
    """List all topics, optionally filtered by status and tag."""
    base_path = Path(base_dir)
    topics = []

    statuses = [status] if status else VALID_STATUSES

    for st in statuses:
        st_dir = base_path / st
        if not st_dir.exists():
            continue
        for md_file in sorted(st_dir.glob("*.md"), reverse=True):
            try:
                raw_text = md_file.read_text(encoding="utf-8")
                meta, body = parse_yaml_frontmatter(raw_text)
                meta["file_path"] = str(md_file.resolve())
                meta["filename"] = md_file.name
                meta["status"] = st
                meta["content"] = body
                
                # Tag filter
                if tag:
                    tags = meta.get("tags") or []
                    if isinstance(tags, list):
                        if not any(tag.lower() == str(t).lower() for t in tags):
                            continue
                    elif tag.lower() not in str(tags).lower():
                        continue

                topics.append(meta)
            except Exception as e:
                print(f"Warning: Failed to parse {md_file}: {e}", file=sys.stderr)

    topics.sort(
        key=lambda t: (str(t.get("created_at", "")), str(t.get("filename", ""))),
        reverse=True,
    )
    return topics


def find_topic_file(
    file_path_or_id: Union[str, Path],
    base_dir: Union[str, Path] = "topics",
) -> Path:
    """Find the path of a topic by exact file path, filename, or topic id."""
    target_str = str(file_path_or_id).strip()
    path_obj = Path(target_str)

    if path_obj.exists() and path_obj.is_file():
        return path_obj.resolve()

    base_path = Path(base_dir)
    if (base_path / path_obj).exists() and (base_path / path_obj).is_file():
        return (base_path / path_obj).resolve()

    for st in VALID_STATUSES:
        st_dir = base_path / st
        if not st_dir.exists():
            continue
        # Direct filename match
        candidate = st_dir / target_str
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
        if not target_str.endswith(".md"):
            candidate_md = st_dir / f"{target_str}.md"
            if candidate_md.exists() and candidate_md.is_file():
                return candidate_md.resolve()

        # Search by id or slug match
        for f in st_dir.glob("*.md"):
            if target_str in f.stem:
                return f.resolve()
            try:
                meta, _ = parse_yaml_frontmatter(f.read_text(encoding="utf-8"))
                if meta.get("id") == target_str:
                    return f.resolve()
            except Exception:
                continue

    raise FileNotFoundError(f"Topic not found for identifier: {target_str}")


def move_topic(
    file_path_or_id: Union[str, Path],
    target_status: str,
    base_dir: Union[str, Path] = "topics",
) -> Path:
    """Move a topic Markdown file to a new status directory and update its frontmatter."""
    if target_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {target_status}. Must be one of {VALID_STATUSES}")

    source_file = find_topic_file(file_path_or_id, base_dir=base_dir)
    base_path = Path(base_dir)
    target_dir = base_path / target_status
    target_dir.mkdir(parents=True, exist_ok=True)

    raw_text = source_file.read_text(encoding="utf-8")
    meta, body = parse_yaml_frontmatter(raw_text)
    meta["status"] = target_status
    meta["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d")

    updated_content = format_yaml_frontmatter(meta) + "\n\n" + (body.strip() + "\n" if body else "")

    target_file = target_dir / source_file.name
    # Handle duplicate filename in target
    if target_file.exists() and target_file.resolve() != source_file.resolve():
        stem = source_file.stem
        target_file = target_dir / f"{stem}-moved.md"

    target_file.write_text(updated_content, encoding="utf-8")
    if target_file.resolve() != source_file.resolve() and source_file.exists():
        source_file.unlink()

    return target_file


def search_topics(
    query: str,
    base_dir: Union[str, Path] = "topics",
) -> List[dict]:
    """Search topics by keyword across title, tags, and body content."""
    base_path = Path(base_dir)
    q = query.strip().lower()
    results = []

    for st in VALID_STATUSES:
        st_dir = base_path / st
        if not st_dir.exists():
            continue
        for md_file in sorted(st_dir.glob("*.md"), reverse=True):
            try:
                raw_text = md_file.read_text(encoding="utf-8")
                meta, body = parse_yaml_frontmatter(raw_text)
                title = str(meta.get("title") or "").lower()
                topic_id = str(meta.get("id") or "").lower()
                tags = [str(t).lower() for t in (meta.get("tags") or [])]
                body_lower = body.lower()

                if q in title or q in topic_id or any(q in t for t in tags) or q in body_lower:
                    meta["file_path"] = str(md_file.resolve())
                    meta["filename"] = md_file.name
                    meta["status"] = st
                    meta["content"] = body
                    results.append(meta)
            except Exception:
                continue

    results.sort(
        key=lambda t: (str(t.get("created_at", "")), str(t.get("filename", ""))),
        reverse=True,
    )
    return results


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Markdown Topic Assistant Helper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List topics")
    list_parser.add_argument("--status", "-s", choices=VALID_STATUSES, help="Filter by status")
    list_parser.add_argument("--tag", "-t", help="Filter by tag")
    list_parser.add_argument("--base-dir", "-d", default="topics", help="Base topics directory")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create a new topic Markdown file")
    create_parser.add_argument("title", help="Topic title")
    create_parser.add_argument("--source-type", "-st", default="idea", help="Source type (idea, link, screenshot, original_idea)")
    create_parser.add_argument("--source-url", "-u", default="", help="Source URL")
    create_parser.add_argument("--tags", "-t", help="Comma-separated tags")
    create_parser.add_argument("--status", "-s", default="inbox", choices=VALID_STATUSES, help="Initial status")
    create_parser.add_argument("--potential-score", "-p", default="", help="Potential score (e.g. 8.5/10)")
    create_parser.add_argument("--content", "-c", default="", help="Markdown body content")
    create_parser.add_argument("--base-dir", "-d", default="topics", help="Base topics directory")

    # Command: move
    move_parser = subparsers.add_parser("move", help="Move topic to a new status")
    move_parser.add_argument("target", help="Topic ID, filename, or filepath")
    move_parser.add_argument("status", choices=VALID_STATUSES, help="Target status")
    move_parser.add_argument("--base-dir", "-d", default="topics", help="Base topics directory")

    # Command: search
    search_parser = subparsers.add_parser("search", help="Search topics by keyword")
    search_parser.add_argument("query", help="Search query string")
    search_parser.add_argument("--base-dir", "-d", default="topics", help="Base topics directory")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.command == "list":
        topics = list_topics(status=args.status, tag=args.tag, base_dir=args.base_dir)
        if args.json:
            print(json.dumps(topics, ensure_ascii=False, indent=2))
        else:
            print(f"Total topics: {len(topics)}")
            for t in topics:
                score = f"[{t.get('potential_score')}]" if t.get("potential_score") else ""
                tags = f"#{','.join(t.get('tags') or [])}" if t.get("tags") else ""
                print(f"- [{t.get('status')}] {t.get('title')} {score} {tags} -> {t.get('file_path')}")

    elif args.command == "create":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        file_path = create_topic(
            title=args.title,
            source_type=args.source_type,
            content=args.content,
            tags=tags,
            source_url=args.source_url,
            status=args.status,
            potential_score=args.potential_score,
            base_dir=args.base_dir,
        )
        print(f"Created topic: {file_path}")

    elif args.command == "move":
        new_path = move_topic(args.target, args.status, base_dir=args.base_dir)
        print(f"Moved topic '{args.target}' to '{args.status}': {new_path}")

    elif args.command == "search":
        results = search_topics(args.query, base_dir=args.base_dir)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"Found {len(results)} matching topics for '{args.query}':")
            for t in results:
                print(f"- [{t.get('status')}] {t.get('title')} -> {t.get('file_path')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
