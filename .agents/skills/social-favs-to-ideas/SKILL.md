---
name: social-favs-to-ideas
description: Use when scanning bookmarked or liked social media posts from Bilibili, Zhihu, Xiaohongshu, Douyin, or X, and transforming them into structured self-media content topic ideas.
---

# Social Media Favorites to Content Ideas

Transform raw social media likes and favorites into an actionable self-media topic database.

## Overview

This skill guides the agent through fetching user favorites/likes across social platforms (Bilibili, Zhihu, Xiaohongshu, Douyin, X/Twitter), parsing raw data stored in `data/raw_favs.json`, reverse-engineering viral hooks and topic angles, and appending structured content ideas to `data/content_ideas_database.md`.

## Workflow

### 1. Trigger Data Scraper

Run the scraper script to capture newly liked or favorited posts across all supported platforms:

```bash
python scripts/fetcher.py --platform all
```

*Note: If browser session credentials have expired or are missing, run `python scripts/login_helper.py --platform <platform>` first.*

### 2. Scan Raw Favorites & Likes

Read and inspect `data/raw_favs.json` to find unprocessed or newly added items. Each item contains:
- `id`: Platform-prefixed unique ID
- `platform`: Platform name (`bilibili`, `zhihu`, `xiaohongshu`, `douyin`, `x`)
- `action_type`: `favorite` or `like`
- `title`: Post title or summary
- `url`: Direct post link
- `text_snippet`: Excerpt or post content (if available)
- `tags`: Associated tags
- `scraped_at`: Timestamp of collection

### 3. Reverse Engineering & Topic Extraction

For each new item (or cluster of related posts), perform content reverse engineering:

1. **Hook Extraction**:
   - Analyze why this post grabbed user attention (headline formula, emotional trigger, high contrast, pain point, or mystery gap).
2. **Topic Clustering**:
   - Categorize into core domain buckets (e.g., AI/Tech, Productivity, Career Development, Personal Finance, Lifestyle).
3. **3 Distinct Angle Generation**:
   - **Angle 1: How-To / Beginner Guide**: Step-by-step practical guide addressing a direct goal or problem.
   - **Angle 2: Pitfalls / Counter-Intuitive Viewpoint**: Common mistakes, myth-busting, or controversial perspectives.
   - **Angle 3: Case Study / Debate**: Deep-dive analysis, comparison, or real-world application story.
4. **Title Suggestions**:
   - Provide 3 catchy, high-CTR title options tailored for platforms like Xiaohongshu, Bilibili, or Zhihu.

### 4. Output Formatting & Database Append

Append each processed topic idea into `data/content_ideas_database.md` using the following standardized markdown template:

```markdown
### 💡 [<Topic Category>] <Topic Title>

- **Source Reference**: [<Platform>] <Original Post Title> (<URL>)
- **Action Type**: <Favorite / Like>
- **Core Hook**: <Why this caught attention / Key psychological trigger>
- **Content Angles**:
  1. **[How-To Guide]**: <Title Suggestion 1> - <Brief angle description>
  2. **[Pitfalls & Myths]**: <Title Suggestion 2> - <Brief angle description>
  3. **[Case Study / Debate]**: <Title Suggestion 3> - <Brief angle description>
- **Key Outline & Call-to-Action**:
  - **Point 1**: <Core argument / Step 1>
  - **Point 2**: <Key takeaway / Step 2>
  - **Point 3**: <Supporting evidence / Step 3>
  - **CTA**: <Engagement question or follow call-to-action>
---
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python scripts/login_helper.py --platform <name>` | Save browser login state for a platform |
| `python scripts/fetcher.py --platform all` | Scrape latest likes/favorites across all platforms |
| `python scripts/fetcher.py --platform bilibili` | Scrape from a specific platform |
