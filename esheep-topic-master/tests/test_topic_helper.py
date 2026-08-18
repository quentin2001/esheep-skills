import json
import subprocess
import sys
from pathlib import Path
import pytest

from scripts.topic_helper import (
    VALID_STATUSES,
    create_topic,
    list_topics,
    move_topic,
    search_topics,
    find_topic_file,
    slugify,
    parse_yaml_frontmatter,
    format_yaml_frontmatter,
)


def test_slugify():
    assert slugify("DeepSeek-V3 架构深度解析") == "deepseek-v3-架构深度解析"
    assert slugify("Hello World! 2026") == "hello-world-2026"
    assert slugify("---***---") == "topic"
    assert slugify("Python & Rust: The Future") == "python-rust-the-future"


def test_format_and_parse_yaml_frontmatter():
    meta = {
        "id": "20260818-test-topic",
        "title": "测试选题标题",
        "created_at": "2026-08-18",
        "source_type": "idea",
        "source_url": "https://example.com/article",
        "tags": ["AI", "深度拆解"],
        "status": "inbox",
        "potential_score": "8.5/10",
        "is_active": True,
        "is_archived": False,
        "note": None,
    }
    body = "# 📌 选题：测试选题标题\n\n## 🎯 受众画像\n开发者群体\n"

    formatted = format_yaml_frontmatter(meta) + "\n\n" + body
    parsed_meta, parsed_body = parse_yaml_frontmatter(formatted)

    assert parsed_meta["id"] == "20260818-test-topic"
    assert parsed_meta["title"] == "测试选题标题"
    assert parsed_meta["created_at"] == "2026-08-18"
    assert parsed_meta["source_type"] == "idea"
    assert parsed_meta["source_url"] == "https://example.com/article"
    assert parsed_meta["tags"] == ["AI", "深度拆解"]
    assert parsed_meta["status"] == "inbox"
    assert parsed_meta["potential_score"] == "8.5/10"
    assert parsed_meta["is_active"] is True
    assert parsed_meta["is_archived"] is False
    assert parsed_meta["note"] is None
    assert "## 🎯 受众画像" in parsed_body


def test_parse_yaml_frontmatter_edge_cases():
    # No frontmatter
    meta, body = parse_yaml_frontmatter("Just simple markdown text")
    assert meta == {}
    assert body == "Just simple markdown text"

    # Multiline list format in frontmatter
    yaml_with_list = """---
id: test-multiline
tags:
  - tag1
  - tag2
status: inbox
---
Markdown content here
"""
    m, b = parse_yaml_frontmatter(yaml_with_list)
    assert m["id"] == "test-multiline"
    assert m["tags"] == ["tag1", "tag2"]
    assert m["status"] == "inbox"
    assert "Markdown content here" in b


def test_create_topic_basic(tmp_path):
    base_dir = tmp_path / "topics"
    title = "DeepSeek-V3 架构深度解析"
    content = "# 📌 选题：DeepSeek-V3 架构深度解析\n\n## 🎯 受众画像\n- AI 开发者\n"

    file_path = create_topic(
        title=title,
        source_type="idea",
        content=content,
        tags=["AI技术", "架构"],
        source_url="https://github.com/deepseek-ai",
        status="inbox",
        potential_score="8.5/10",
        base_dir=base_dir,
    )

    assert file_path.exists()
    assert file_path.parent.name == "inbox"
    assert file_path.name.startswith("20")
    assert "deepseek-v3" in file_path.name.lower()

    raw_text = file_path.read_text(encoding="utf-8")
    meta, parsed_content = parse_yaml_frontmatter(raw_text)

    assert meta["title"] == title
    assert meta["source_type"] == "idea"
    assert meta["source_url"] == "https://github.com/deepseek-ai"
    assert meta["tags"] == ["AI技术", "架构"]
    assert meta["status"] == "inbox"
    assert meta["potential_score"] == "8.5/10"
    assert "AI 开发者" in parsed_content


def test_create_topic_custom_status_and_defaults(tmp_path):
    base_dir = tmp_path / "topics"
    file_path = create_topic(
        title="极简灵感",
        source_type="original_idea",
        content="一段碎片灵感记录",
        base_dir=base_dir,
    )

    assert file_path.exists()
    assert file_path.parent.name == "inbox"
    raw_text = file_path.read_text(encoding="utf-8")
    meta, content = parse_yaml_frontmatter(raw_text)
    assert meta["title"] == "极简灵感"
    assert meta["status"] == "inbox"
    assert meta["tags"] == []
    assert meta["source_url"] == ""
    assert "一段碎片灵感记录" in content


def test_create_topic_filename_collision(tmp_path):
    base_dir = tmp_path / "topics"
    p1 = create_topic(title="重名选题测试", source_type="idea", content="内容1", base_dir=base_dir)
    p2 = create_topic(title="重名选题测试", source_type="idea", content="内容2", base_dir=base_dir)

    assert p1.exists()
    assert p2.exists()
    assert p1 != p2
    assert p1.name != p2.name


def test_create_topic_invalid_status(tmp_path):
    base_dir = tmp_path / "topics"
    with pytest.raises(ValueError, match="Invalid status"):
        create_topic(title="非法状态测试", source_type="idea", content="", status="invalid_status", base_dir=base_dir)


def test_list_topics_and_filters(tmp_path):
    base_dir = tmp_path / "topics"

    create_topic(title="Topic 1", source_type="idea", content="1", tags=["tech", "ai"], status="inbox", base_dir=base_dir)
    create_topic(title="Topic 2", source_type="link", content="2", tags=["design"], status="selected", base_dir=base_dir)
    create_topic(title="Topic 3", source_type="screenshot", content="3", tags=["tech"], status="inbox", base_dir=base_dir)
    create_topic(title="Topic 4", source_type="idea", content="4", tags=["tech"], status="completed", base_dir=base_dir)

    # List all
    all_topics = list_topics(base_dir=base_dir)
    assert len(all_topics) == 4

    # List by status
    inbox_topics = list_topics(status="inbox", base_dir=base_dir)
    assert len(inbox_topics) == 2
    assert all(t["status"] == "inbox" for t in inbox_topics)

    selected_topics = list_topics(status="selected", base_dir=base_dir)
    assert len(selected_topics) == 1
    assert selected_topics[0]["title"] == "Topic 2"

    # List by tag
    tech_topics = list_topics(tag="tech", base_dir=base_dir)
    assert len(tech_topics) == 3

    design_topics = list_topics(tag="design", base_dir=base_dir)
    assert len(design_topics) == 1
    assert design_topics[0]["title"] == "Topic 2"

    # Nonexistent tag
    none_topics = list_topics(tag="nonexistent_tag", base_dir=base_dir)
    assert len(none_topics) == 0

    # Nonexistent base_dir
    assert list_topics(base_dir=tmp_path / "does_not_exist") == []


def test_find_topic_file(tmp_path):
    base_dir = tmp_path / "topics"
    p = create_topic(title="查找测试选题", source_type="idea", content="内容", status="inbox", base_dir=base_dir)
    meta, _ = parse_yaml_frontmatter(p.read_text(encoding="utf-8"))
    topic_id = meta["id"]

    # By Path object
    assert find_topic_file(p, base_dir=base_dir) == p.resolve()
    # By filename string
    assert find_topic_file(p.name, base_dir=base_dir) == p.resolve()
    # By stem without .md
    assert find_topic_file(p.stem, base_dir=base_dir) == p.resolve()
    # By frontmatter id
    assert find_topic_file(topic_id, base_dir=base_dir) == p.resolve()

    with pytest.raises(FileNotFoundError):
        find_topic_file("not_exist_file", base_dir=base_dir)


def test_move_topic_by_path_and_id(tmp_path):
    base_dir = tmp_path / "topics"

    p = create_topic(title="移动测试选题", source_type="idea", content="待立项内容", status="inbox", base_dir=base_dir)
    raw_meta, _ = parse_yaml_frontmatter(p.read_text(encoding="utf-8"))
    topic_id = raw_meta["id"]

    assert p.exists()
    assert p.parent.name == "inbox"

    # Move by path to selected
    new_path = move_topic(p, "selected", base_dir=base_dir)
    assert new_path.exists()
    assert new_path.parent.name == "selected"
    assert not p.exists()

    meta_selected, _ = parse_yaml_frontmatter(new_path.read_text(encoding="utf-8"))
    assert meta_selected["status"] == "selected"

    # Move by id to in_progress
    in_prog_path = move_topic(topic_id, "in_progress", base_dir=base_dir)
    assert in_prog_path.exists()
    assert in_prog_path.parent.name == "in_progress"
    assert not new_path.exists()

    meta_in_prog, _ = parse_yaml_frontmatter(in_prog_path.read_text(encoding="utf-8"))
    assert meta_in_prog["status"] == "in_progress"

    # Invalid status
    with pytest.raises(ValueError, match="Invalid status"):
        move_topic(in_prog_path, "unknown_status", base_dir=base_dir)

    # Nonexistent topic
    with pytest.raises(FileNotFoundError):
        move_topic("nonexistent-topic-id", "completed", base_dir=base_dir)


def test_search_topics(tmp_path):
    base_dir = tmp_path / "topics"

    create_topic(title="深度学习模型优化", source_type="idea", content="讨论量化与剪枝技术", tags=["AI", "ML"], base_dir=base_dir)
    create_topic(title="前端性能调优指南", source_type="link", content="探讨 Webpack 与 Vite 打包", tags=["Web", "Frontend"], base_dir=base_dir)
    create_topic(title="极简生活日常", source_type="idea", content="断舍离的心得体会", tags=["Life"], base_dir=base_dir)

    # Empty search query returns all
    assert len(search_topics("", base_dir=base_dir)) == 3

    # Search by title keyword
    r1 = search_topics("深度学习", base_dir=base_dir)
    assert len(r1) == 1
    assert r1[0]["title"] == "深度学习模型优化"

    # Search by tag
    r2 = search_topics("Frontend", base_dir=base_dir)
    assert len(r2) == 1
    assert r2[0]["title"] == "前端性能调优指南"

    # Search by content
    r3 = search_topics("断舍离", base_dir=base_dir)
    assert len(r3) == 1
    assert r3[0]["title"] == "极简生活日常"

    # Search nonexistent
    r4 = search_topics("不存在的关键词", base_dir=base_dir)
    assert len(r4) == 0


def test_cli_integration(tmp_path):
    import os
    base_dir = tmp_path / "topics"
    script_path = Path(__file__).parent.parent / "scripts" / "topic_helper.py"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    # 1. CLI help (no args)
    res_help = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, encoding="utf-8", env=env)
    assert "usage:" in res_help.stdout or "usage:" in res_help.stderr or "Markdown Topic" in res_help.stdout

    # 2. CLI create
    cmd_create = [
        sys.executable,
        str(script_path),
        "create",
        "CLI 创建测试",
        "--source-type", "link",
        "--source-url", "https://esheep.com",
        "--tags", "CLI,Test",
        "--status", "inbox",
        "--potential-score", "9.2/10",
        "--content", "# 正文内容测试",
        "--base-dir", str(base_dir),
    ]
    res_create = subprocess.run(cmd_create, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    assert "Created topic:" in res_create.stdout or "Created:" in res_create.stdout

    # 3. CLI list (json)
    cmd_list = [
        sys.executable,
        str(script_path),
        "list",
        "--status", "inbox",
        "--base-dir", str(base_dir),
        "--json",
    ]
    res_list = subprocess.run(cmd_list, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    topics_data = json.loads(res_list.stdout)
    assert len(topics_data) == 1
    assert topics_data[0]["title"] == "CLI 创建测试"
    topic_id = topics_data[0]["id"]

    # 4. CLI list (table format)
    cmd_list_table = [
        sys.executable,
        str(script_path),
        "list",
        "--base-dir", str(base_dir),
    ]
    res_list_table = subprocess.run(cmd_list_table, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    assert "CLI 创建测试" in res_list_table.stdout

    # 5. CLI search (json)
    cmd_search = [
        sys.executable,
        str(script_path),
        "search",
        "CLI",
        "--base-dir", str(base_dir),
        "--json",
    ]
    res_search = subprocess.run(cmd_search, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    search_data = json.loads(res_search.stdout)
    assert len(search_data) == 1
    assert search_data[0]["id"] == topic_id

    # 6. CLI search (table format)
    cmd_search_table = [
        sys.executable,
        str(script_path),
        "search",
        "CLI",
        "--base-dir", str(base_dir),
    ]
    res_search_table = subprocess.run(cmd_search_table, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    assert "CLI 创建测试" in res_search_table.stdout

    # 7. CLI move
    cmd_move = [
        sys.executable,
        str(script_path),
        "move",
        topic_id,
        "selected",
        "--base-dir", str(base_dir),
    ]
    res_move = subprocess.run(cmd_move, capture_output=True, text=True, encoding="utf-8", env=env, check=True)
    assert "Moved" in res_move.stdout or "selected" in res_move.stdout

    # Verify moved
    inbox_list = list_topics(status="inbox", base_dir=base_dir)
    assert len(inbox_list) == 0
    selected_list = list_topics(status="selected", base_dir=base_dir)
    assert len(selected_list) == 1
    assert selected_list[0]["title"] == "CLI 创建测试"
