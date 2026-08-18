#!/usr/bin/env python3
"""External URL article content and metadata extractor.

Extracts article title, og/meta description, and cleaned body text
using only the Python standard library.
"""

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, Optional


class ArticleHTMLParser(HTMLParser):
    """HTML parser to extract title, metadata, and clean body text."""

    IGNORE_TAGS = {
        "script",
        "style",
        "noscript",
        "nav",
        "header",
        "footer",
        "aside",
        "svg",
        "iframe",
        "button",
        "form",
        "canvas",
        "select",
        "option",
    }

    BLOCK_TAGS = {
        "p",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "article",
        "section",
        "blockquote",
        "tr",
        "table",
        "hr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.ignore_depth = 0
        self.in_title = False
        self.title = ""
        self.og_title = ""
        self.meta_description = ""
        self.og_description = ""
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        if tag_lower in self.IGNORE_TAGS:
            self.ignore_depth += 1
            return

        if self.ignore_depth > 0:
            return

        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta":
            attr_dict = {k.lower(): (v or "") for k, v in attrs}
            prop = attr_dict.get("property", "").lower()
            name = attr_dict.get("name", "").lower()
            content = attr_dict.get("content", "").strip()

            if prop == "og:title" or name == "twitter:title":
                if not self.og_title and content:
                    self.og_title = content
            elif prop == "og:description" or name == "twitter:description":
                if not self.og_description and content:
                    self.og_description = content
            elif name == "description":
                if not self.meta_description and content:
                    self.meta_description = content
        elif tag_lower == "br":
            self.text_chunks.append("\n")
        elif tag_lower in self.BLOCK_TAGS:
            self.text_chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower in self.IGNORE_TAGS:
            if self.ignore_depth > 0:
                self.ignore_depth -= 1
            return

        if self.ignore_depth > 0:
            return

        if tag_lower == "title":
            self.in_title = False
        elif tag_lower in self.BLOCK_TAGS:
            self.text_chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self.ignore_depth > 0:
            return

        if self.in_title:
            self.title += data
        else:
            self.text_chunks.append(data)


def extract_article_from_html(html_text: str, url: str = "") -> Dict[str, Any]:
    """Parse HTML and extract title, description, and clean text."""
    parser = ArticleHTMLParser()
    try:
        parser.feed(html_text)
    except Exception:
        # Fallback if parser encounters any malformed HTML
        pass

    # Extract & decode title
    raw_title = parser.og_title.strip() if parser.og_title else parser.title.strip()
    title = html.unescape(raw_title)

    # Extract & decode description
    raw_desc = (
        parser.og_description.strip()
        if parser.og_description
        else parser.meta_description.strip()
    )
    description = html.unescape(raw_desc)

    # Clean and normalize body text
    raw_content = "".join(parser.text_chunks)
    raw_content = html.unescape(raw_content)

    # Clean whitespace per line and collapse redundant empty lines
    lines = raw_content.splitlines()
    cleaned_lines: list[str] = []
    prev_empty = False

    for line in lines:
        cleaned = re.sub(r"[ \t\f\v\xa0]+", " ", line).strip()
        if cleaned:
            cleaned_lines.append(cleaned)
            prev_empty = False
        elif not prev_empty:
            cleaned_lines.append("")
            prev_empty = True

    content = "\n".join(cleaned_lines).strip()

    return {
        "url": url,
        "title": title,
        "description": description,
        "content": content,
        "error": None,
    }


def fetch_article_content(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Fetch article content from a web URL using standard urllib.

    Returns:
        dict: {
            "url": str,
            "title": str,
            "description": str,
            "content": str,
            "error": Optional[str]
        }
    """
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or parsed.scheme not in ("http", "https") or not parsed.netloc:
        return {
            "url": url,
            "title": "",
            "description": "",
            "content": "",
            "error": f"Invalid URL scheme or format: {url}",
        }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            raw_bytes = resp.read()
            try:
                html_text = raw_bytes.decode(charset)
            except (UnicodeDecodeError, LookupError):
                try:
                    html_text = raw_bytes.decode("utf-8", errors="replace")
                except Exception:
                    html_text = raw_bytes.decode("latin-1", errors="replace")

            return extract_article_from_html(html_text, url=url)
    except urllib.error.HTTPError as e:
        return {
            "url": url,
            "title": "",
            "description": "",
            "content": "",
            "error": f"HTTP Error {e.code}: {e.reason}",
        }
    except urllib.error.URLError as e:
        return {
            "url": url,
            "title": "",
            "description": "",
            "content": "",
            "error": f"URL Error: {e.reason}",
        }
    except Exception as e:
        return {
            "url": url,
            "title": "",
            "description": "",
            "content": "",
            "error": f"Error fetching {url}: {str(e)}",
        }


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch article title, description, and content from a web URL."
    )
    parser.add_argument("url", help="URL of the web page to fetch")
    parser.add_argument(
        "--json", action="store_true", help="Output result as formatted JSON"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    args = parser.parse_args()
    result = fetch_article_content(args.url, timeout=args.timeout)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["error"]:
            print(f"Error: {result['error']}", file=sys.stderr)
            return 1
        print("=" * 60)
        print(f"Title: {result['title']}")
        if result.get("description"):
            print(f"Description: {result['description']}")
        print(f"URL: {result['url']}")
        print("=" * 60)
        print("\nContent:\n")
        print(result["content"])

    return 0 if not result["error"] else 1


if __name__ == "__main__":
    sys.exit(main())
