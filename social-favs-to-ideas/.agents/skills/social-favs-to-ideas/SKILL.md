---
name: social-favs-to-ideas
description: Use when scanning bookmarked or liked social media posts from Bilibili, Zhihu, Xiaohongshu, Douyin, or X, and transforming them into structured self-media content topic ideas.
---

# Social Media Favorites to Content Ideas

Transform raw social media likes and favorites into an actionable self-media topic database.

## CDP Browser Connection Protocol (Cross-Platform & Dependency Rules)

This Skill requires **Google Chrome** (or Chromium-based browser) as the primary execution engine.

### Cookie Lifetime & Session Reality:
- Logged-in sessions remain active long-term (sharing user's normal browser cookies).
- If a platform's session expires due to official TTL limits or remote logout, the user simply re-logs in during their regular browsing.

### Shortcut & Dependency Fallback SOP:

1. **Check Chrome Installation**:
   - Verify `chrome.exe` (Windows) or `/Applications/Google Chrome.app` (macOS).
   - If not installed, inform the user: *"This Skill currently relies on Google Chrome for CDP extraction. Please install Chrome to proceed."*

2. **Windows (Smart Shortcut Creation / Overwrite)**:
   - Check Desktop and Start Menu for existing `Google Chrome.lnk`.
   - **If shortcut exists**: Overwrite/append `--remote-debugging-port=9222` to target arguments.
   - **If shortcut is missing**: Locate `chrome.exe` in Program Files and generate a new `Google Chrome.lnk` directly on the Desktop with `--remote-debugging-port=9222`.

3. **macOS**:
   - Use Application bundle launch: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222` or configure `~/.zshrc` alias.

## Conversational Agent Workflow

The user will interact with you **purely through chat messages**. You must automatically execute the required background commands using `run_command` without asking the user to use the command line.

### Scenario A: Initial Login or Changing Accounts
When the user wants to set up or change accounts for specific platforms (e.g., "帮我绑定小红书 Cookie", "换一个B站账号"):
- **Option 1 (Direct Cookie Paste in Chat)**: Ask the user to paste their browser cookie string directly in chat. Once provided, run `python scripts/set_cookie.py <platform> "<cookie_string>"`.
- **Option 2 (Automatic Browser Launch)**: Run `python scripts/login_helper.py --platform <platform>` to pop up Chromium. Prompt the user: "已为你尝试打开 [<platform>] 的登录窗口，完成后请告诉我‘登录完成了’。"

### Scenario B: Selective Platform Scanning
When the user asks to fetch likes/favorites from specific platforms (e.g., "只抓取小红书和抖音", "查看B站近期的收藏"):
1. Parse the requested platforms.
2. Execute `python scripts/fetcher.py --platform <platform>` for each requested platform.
3. Read `data/raw_favs.json` and process newly added entries.

### Scenario C: Full Automatic Topic Generation
When the user asks to generate topics (e.g., "扫描我最近喜欢的内容生成选题"):
1. Execute `python scripts/fetcher.py --platform all` (or specific platforms if specified, with `--limit <number>` if count limit requested).
2. If any platform session is missing, inform the user and automatically trigger Scenario A for that platform.
3. Process `data/raw_favs.json`, perform topic reverse-engineering, and update `data/content_ideas_database.md`.

## Pre-Filtering Guidelines (Handling Large Amounts of Likes/Favs)

If the user has a large volume of likes and bookmarks, apply the following filters before performing full topic reverse-engineering:

1. **Domain / Keyword Filtering**:
   - If the user specifies target niches (e.g., "只看 AI、自媒体、效率工具相关的内容"), evaluate the title/snippet of raw items first and discard unrelated items (e.g., pure entertainment, recipes, celebrity news) before reverse-engineering.
2. **Action Type Weighting**:
   - If requested (e.g., "只分析收藏，跳过点赞"), filter items where `action_type == 'favorite'`.
3. **Quantity Limit Control**:
   - Limit the fetch or processing to the top N newest items (e.g., `--limit 5` for latest 5 items per platform).

## Strict Anti-Hallucination & Truthfulness Rule

> **CRITICAL**: Never generate synthetic/mock post items, fake titles, or dead dummy URLs (such as `xiaohongshu.com/explore/65ab1234...` or `douyin.com/video/731234...`) when `data/raw_favs.json` returns 0 items. 
> 
> If no real items are found for a requested platform or filter:
> 1. Report the exact status truthfully: "未能在 [<Platform>] 的真实记录中抓取到符合条件的内容/登录会话失效已重定向"。
> 2. Direct the user to re-verify their login session via `login_helper.py` or check if their account has saved/liked posts matching the criteria.

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
| `python scripts/fetcher.py --platform all` | Scrape latest likes/favorites across all platforms using MediaCrawler CDP Engine |
| `python scripts/fetcher.py --platform xiaohongshu --limit 5` | Scrape latest 5 items from Xiaohongshu |
| `python scripts/fetcher.py --platform douyin --limit 5` | Scrape latest 5 items from Douyin |
| `python scripts/fetcher.py --platform <name> --no-cdp` | Fallback to Playwright persistent context mode |
