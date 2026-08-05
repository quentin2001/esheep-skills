import os
import json
import pytest
from scripts.storage import add_new_favs, load_raw_favs
from scripts.fetcher import parse_raw_item

def test_e2e_pipeline_multi_platform_and_deduplication(tmp_path):
    raw_file = tmp_path / "raw_favs.json"
    ideas_file = tmp_path / "content_ideas_database.md"

    # 1. Simulate scraped raw items across multiple platforms:
    # Bilibili, Xiaohongshu, Douyin likes & favorites, Zhihu, X
    scraped_batch_1 = [
        parse_raw_item({
            "platform": "bilibili",
            "action_type": "favorite",
            "id": "BV123456",
            "title": "Bilibili AI Agent Guide",
            "url": "https://www.bilibili.com/video/BV123456"
        }),
        parse_raw_item({
            "platform": "xiaohongshu",
            "action_type": "favorite",
            "id": "note_789",
            "title": "Xiaohongshu Productivity Hacks",
            "url": "https://www.xiaohongshu.com/explore/note_789"
        }),
        parse_raw_item({
            "platform": "douyin",
            "action_type": "like",
            "id": "like_111",
            "title": "Douyin Liked Video Title",
            "url": "https://www.douyin.com/user/self?showTab=like"
        }),
        parse_raw_item({
            "platform": "douyin",
            "action_type": "favorite",
            "id": "fav_222",
            "title": "Douyin Favorited Video Title",
            "url": "https://www.douyin.com/user/self?showTab=favorite"
        }),
        parse_raw_item({
            "platform": "zhihu",
            "action_type": "favorite",
            "id": "collection_333",
            "title": "Zhihu Tech Column Answer",
            "url": "https://www.zhihu.com/question/123/answer/456"
        }),
        parse_raw_item({
            "platform": "x",
            "action_type": "favorite",
            "id": "tweet_444",
            "title": "X Tweet snippet preview...",
            "text_snippet": "Full X post content on LLM agents",
            "url": "https://x.com/i/bookmarks"
        })
    ]

    # Verify add_new_favs appends all 6 items on initial run
    added_1 = add_new_favs(scraped_batch_1, str(raw_file))
    assert len(added_1) == 6
    assert os.path.exists(raw_file)

    loaded_raw = load_raw_favs(str(raw_file))
    assert len(loaded_raw) == 6
    platforms_found = {item["platform"] for item in loaded_raw}
    assert platforms_found == {"bilibili", "xiaohongshu", "douyin", "zhihu", "x"}

    # 2. Verify generating formatted topic entries in a mock content_ideas_database.md file
    entries = []
    for item in added_1:
        entry = (
            f"### 💡 [{item['platform'].upper()}] {item['title']}\n\n"
            f"- **Source Reference**: [{item['platform']}] {item['title']} ({item['url']})\n"
            f"- **Core Hook**: Deconstructing viral topic from {item['platform']}\n"
            f"- **Content Angles**:\n"
            f"  1. **[How-To Guide]**: 3 steps to master {item['title']}\n"
            f"  2. **[Common Pitfalls]**: Why most fail at {item['title']}\n"
            f"  3. **[Case Study]**: Real-world application of {item['title']}\n"
            f"- **Key Outline & Call-to-Action**:\n"
            f"  - Point 1: Key takeaway\n"
            f"  - CTA: Follow for more\n"
            f"---\n"
        )
        entries.append(entry)

    with open(ideas_file, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

    assert os.path.exists(ideas_file)
    with open(ideas_file, "r", encoding="utf-8") as f:
        db_content = f.read()

    assert "Bilibili AI Agent Guide" in db_content
    assert "Xiaohongshu Productivity Hacks" in db_content
    assert "Douyin Liked Video Title" in db_content
    assert "Douyin Favorited Video Title" in db_content
    assert "Zhihu Tech Column Answer" in db_content
    assert "Full X post content on LLM agents" in db_content or "X Tweet snippet preview..." in db_content

    # 3. Test deduplication across multiple simulated fetch runs
    scraped_batch_2 = [
        # Duplicate items from batch 1
        parse_raw_item({
            "platform": "bilibili",
            "action_type": "favorite",
            "id": "BV123456",
            "title": "Bilibili AI Agent Guide",
            "url": "https://www.bilibili.com/video/BV123456"
        }),
        parse_raw_item({
            "platform": "douyin",
            "action_type": "like",
            "id": "like_111",
            "title": "Douyin Liked Video Title",
            "url": "https://www.douyin.com/user/self?showTab=like"
        }),
        # New item in batch 2
        parse_raw_item({
            "platform": "bilibili",
            "action_type": "favorite",
            "id": "BV999999",
            "title": "New Bilibili Video",
            "url": "https://www.bilibili.com/video/BV999999"
        })
    ]

    added_2 = add_new_favs(scraped_batch_2, str(raw_file))
    assert len(added_2) == 1
    assert added_2[0]["id"] == "bilibili_BV999999"

    total_loaded = load_raw_favs(str(raw_file))
    assert len(total_loaded) == 7
