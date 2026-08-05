---
name: social-favs-to-ideas
description: Use when scanning bookmarked or liked social media posts from Bilibili, Zhihu, Xiaohongshu, Douyin, or X, and transforming them into structured self-media content topic ideas.
---

# Social Media Favorites to Content Ideas

Transform raw social media likes and favorites into an actionable self-media topic database.

## Overview

This skill guides the agent through fetching user favorites/likes across social platforms (Bilibili, Zhihu, Xiaohongshu, Douyin, X/Twitter), parsing raw data stored in `data/raw_favs.json`, reverse-engineering viral hooks and topic angles, and appending structured content ideas to `data/content_ideas_database.md`.

## Conversational Agent Workflow

The user will interact with you **purely through chat messages**. You must automatically execute the required background commands using `run_command` without asking the user to use the command line.

### Scenario A: Initial Login or Changing Accounts
When the user asks to log in or switch accounts for specific platforms (e.g., "帮我登录小红书", "换一个B站账号"):
1. Execute: `python scripts/login_helper.py --platform <platform>` (or `--platform all` if they want to log into all).
2. Prompt the user in chat: "我已经调起了 [<platform>] 的登录窗口，请在弹出的浏览器中登录您的账号。登录完成后请回复我‘登录完成了’。"

### Scenario B: Selective Platform Scanning
When the user asks to fetch likes/favorites from specific platforms (e.g., "只抓取小红书和抖音", "查看B站近期的收藏"):
1. Parse the requested platforms.
2. Execute `python scripts/fetcher.py --platform <platform>` for each requested platform.
3. Read `data/raw_favs.json` and process newly added entries.

### Scenario C: Full Automatic Topic Generation
When the user asks to generate topics (e.g., "扫描我最近喜欢的内容生成选题"):
1. Execute `python scripts/fetcher.py --platform all` (or specific platforms if specified).
2. If any platform session is missing, inform the user and automatically trigger Scenario A for that platform.
3. Process `data/raw_favs.json`, perform topic reverse-engineering, and update `data/content_ideas_database.md`.

## Workflow Details

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
