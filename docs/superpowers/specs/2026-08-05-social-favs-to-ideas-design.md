# Design Spec: Social Media Favorites to Content Ideas Skill (`social-favs-to-ideas`)

## 1. Overview
A lightweight, automated Agent Skill that periodically or manually scans a user's liked and favorited/bookmarked posts across 5 major social media platforms (Bilibili, Zhihu, Xiaohongshu, Douyin, X/Twitter). It extracts user interest topics, reverse-engineers viral hooks, and generates a structured, actionable self-media topic database (`content_ideas_database.md`).

## 2. Platform Target Matrix

| Platform | Target Action | URL Path | Extraction Method |
| :--- | :--- | :--- | :--- |
| **Bilibili** | Fav Folders & Likes | `bilibili.com` space/fav | Playwright + Cookie session |
| **Zhihu** | Collections & Agree/Likes | `zhihu.com/people/self` | Playwright + Cookie session |
| **Xiaohongshu** | Favorites & Likes | `xiaohongshu.com/user/profile/self` | Playwright + Cookie session |
| **Douyin** | Likes & Favorites | `douyin.com/user/self?showTab=like` & `?showTab=favorite` | Playwright + Cookie session |
| **X (Twitter)** | Bookmarks & Likes | `x.com/i/bookmarks` & `i/likes` | Playwright + Cookie session |

## 3. Architecture & File Structure

```
skill-maker/
├── .agents/
│   └── skills/
│       └── social-favs-to-ideas/
│           ├── SKILL.md                 # Agent Skill instructions & prompt workflow
│           └── scripts/
│               ├── fetcher.py           # Playwright background fetcher script
│               ├── login_helper.py      # Interactive initial login helper
│               └── config.json          # Platform credentials/cookies state
├── data/
│   ├── raw_favs.json                    # Incremental cache of scraped posts
│   └── content_ideas_database.md        # The output topic database for self-media
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-08-05-social-favs-to-ideas-design.md
```

## 4. Key Workflows

### 4.1 First-Time Setup (`login_helper.py`)
- Launches a browser window for the user to log into the 5 target platforms.
- Captures and stores browser storage state (Cookies, LocalStorage) into `.sessions/state.json`.

### 4.2 Incremental Scraper (`fetcher.py`)
- Runs headlessly using Playwright and saved sessions.
- Navigates to each platform's likes and bookmarks pages.
- Extracts post titles, URLs, tags, and summary text.
- Deduplicates against `data/raw_favs.json` and returns only new items.

### 4.3 Content Idea Transformation (Agent Skill Workflow)
- Converts raw extracted items into structured topic records.
- Extracts core Hooks (what caught the user's attention).
- Provides 3 distinct angles per topic (e.g., Guide, Common Pitfalls, Hot Debate).
- Appends new topics to `data/content_ideas_database.md`.

## 5. Verification & Testing Plan
- Execute `python scripts/fetcher.py --check-login` to ensure valid session states.
- Run `python scripts/fetcher.py --dry-run` to verify DOM selectors for all 5 platforms.
- Trigger the Agent Skill to process sample items and format `content_ideas_database.md`.
