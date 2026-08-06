import os
import sys
import pytest
import json
from pathlib import Path

# Add scripts directory to python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from topic_manager import TopicManager, VALID_STATUSES


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "topics.json"
    db_file.write_text("[]", encoding="utf-8")
    return str(db_file)


def test_add_topic(temp_db):
    tm = TopicManager(data_file=temp_db)
    topic = tm.add(
        title="Test Topic",
        category="Tech",
        hook="An intriguing tech hook",
        source_platform="Bilibili",
        source_title="Source Video Title",
        source_url="https://example.com/video",
        angles=["Angle 1", "Angle 2"],
        outline=["Part 1", "Part 2"],
        tags=["tag1", "tag2"],
        status="inbox"
    )
    assert topic["title"] == "Test Topic"
    assert topic["category"] == "Tech"
    assert topic["status"] == "inbox"
    assert "id" in topic
    assert "created_at" in topic
    assert "updated_at" in topic

    all_topics = tm.get_all()
    assert len(all_topics) == 1
    assert all_topics[0]["id"] == topic["id"]


def test_add_topic_invalid_status(temp_db):
    tm = TopicManager(data_file=temp_db)
    with pytest.raises(ValueError):
        tm.add(
            title="Test Topic",
            category="Tech",
            hook="Hook",
            source_platform="Platform",
            source_title="Title",
            source_url="URL",
            angles=[],
            outline=[],
            tags=[],
            status="invalid_status"
        )


def test_get_all_filtering(temp_db):
    tm = TopicManager(data_file=temp_db)
    t1 = tm.add(
        title="Topic 1", category="AI", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="inbox"
    )
    t2 = tm.add(
        title="Topic 2", category="Tech", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="selected"
    )
    t3 = tm.add(
        title="Topic 3", category="AI", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="in_progress"
    )

    assert len(tm.get_all()) == 3
    assert len(tm.get_all(status="inbox")) == 1
    assert tm.get_all(status="inbox")[0]["id"] == t1["id"]

    ai_topics = tm.get_all(category="AI")
    assert len(ai_topics) == 2
    assert {t["id"] for t in ai_topics} == {t1["id"], t3["id"]}

    filtered = tm.get_all(status="selected", category="Tech")
    assert len(filtered) == 1
    assert filtered[0]["id"] == t2["id"]


def test_move_topic(temp_db):
    tm = TopicManager(data_file=temp_db)
    t = tm.add(
        title="Topic 1", category="AI", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="inbox"
    )

    updated = tm.move(t["id"], "selected")
    assert updated["status"] == "selected"
    assert tm.get_all(status="selected")[0]["id"] == t["id"]

    with pytest.raises(ValueError):
        tm.move(t["id"], "non_existent_status")

    with pytest.raises(KeyError):
        tm.move("invalid_id", "completed")


def test_update_topic(temp_db):
    tm = TopicManager(data_file=temp_db)
    t = tm.add(
        title="Original Title", category="AI", hook="Old Hook", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="inbox"
    )

    updated = tm.update(t["id"], {"title": "Updated Title", "hook": "New Hook", "tags": ["new_tag"]})
    assert updated["title"] == "Updated Title"
    assert updated["hook"] == "New Hook"
    assert updated["tags"] == ["new_tag"]

    # Verify update persisted
    all_topics = tm.get_all()
    assert all_topics[0]["title"] == "Updated Title"

    with pytest.raises(KeyError):
        tm.update("non_existent_id", {"title": "New Title"})

    with pytest.raises(ValueError):
        tm.update(t["id"], {"status": "invalid_status"})


def test_delete_topic(temp_db):
    tm = TopicManager(data_file=temp_db)
    t1 = tm.add(
        title="Topic 1", category="AI", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="inbox"
    )
    t2 = tm.add(
        title="Topic 2", category="Tech", hook="", source_platform="",
        source_title="", source_url="", angles=[], outline=[], tags=[], status="inbox"
    )

    assert tm.delete(t1["id"]) is True
    remaining = tm.get_all()
    assert len(remaining) == 1
    assert remaining[0]["id"] == t2["id"]

    with pytest.raises(KeyError):
        tm.delete("non_existent_id")


def test_add_topic_with_source_type(temp_db):
    tm = TopicManager(data_file=temp_db)
    # Test default source_type
    t1 = tm.add(title="Default Source Type Topic")
    assert t1.get("source_type") == "original_idea"

    # Test explicit source_type
    t2 = tm.add(title="Hotlist Topic", source_type="hotlist")
    assert t2.get("source_type") == "hotlist"

    t3 = tm.add(title="Social Fav Topic", source_type="social_fav")
    assert t3.get("source_type") == "social_fav"


def test_add_topic_invalid_source_type(temp_db):
    tm = TopicManager(data_file=temp_db)
    with pytest.raises(ValueError):
        tm.add(title="Invalid Source Type", source_type="invalid_type")


def test_get_all_source_type_filtering(temp_db):
    tm = TopicManager(data_file=temp_db)
    t1 = tm.add(title="Topic 1", source_type="hotlist")
    t2 = tm.add(title="Topic 2", source_type="social_fav")
    t3 = tm.add(title="Topic 3", source_type="original_idea")

    hotlist_topics = tm.get_all(source_type="hotlist")
    assert len(hotlist_topics) == 1
    assert hotlist_topics[0]["id"] == t1["id"]

    social_fav_topics = tm.get_all(source_type="social_fav")
    assert len(social_fav_topics) == 1
    assert social_fav_topics[0]["id"] == t2["id"]

    original_topics = tm.get_all(source_type="original_idea")
    assert len(original_topics) == 1
    assert original_topics[0]["id"] == t3["id"]

