import json
import urllib.error
from unittest.mock import MagicMock, patch
import pytest

# Import module to test
from scripts.fetch_url import fetch_article_content, extract_article_from_html, main


SAMPLE_HTML_BASIC = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Understanding MoE Architecture - AI Insights</title>
    <meta name="description" content="A comprehensive guide to Mixture of Experts architecture in modern LLMs.">
</head>
<body>
    <header>
        <h1>Site Header</h1>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/topics">Topics</a>
    </nav>
    <main>
        <article>
            <h1>Understanding MoE Architecture</h1>
            <p>Mixture of Experts (MoE) is a machine learning technique.</p>
            <p>It divides computation across multiple specialized expert sub-networks.</p>
        </article>
    </main>
    <footer>
        <p>Copyright 2026</p>
    </footer>
    <script>
        console.log("Analytics script");
    </script>
</body>
</html>
"""

SAMPLE_HTML_OG_TAGS = """
<!DOCTYPE html>
<html>
<head>
    <meta property="og:title" content="DeepSeek-V3 Technical Deep Dive" />
    <meta property="og:description" content="Exploring MLA and DeepSeekMoE innovations." />
    <title>Default Title</title>
    <style>
        body { font-size: 16px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="content">
        <h2>Key Innovations</h2>
        <ul>
            <li>Multi-Head Latent Attention (MLA)</li>
            <li>Auxiliary-loss-free load balancing</li>
        </ul>
    </div>
</body>
</html>
"""

SAMPLE_HTML_NOISY = """
<html>
<head>
    <title>Clean Title</title>
    <style type="text/css">
        .nav { background: #fff; }
    </style>
    <script>
        var token = "secret";
    </script>
    <noscript>Please enable javascript</noscript>
</head>
<body>
    <nav>
        <ul><li>Nav item 1</li><li>Nav item 2</li></ul>
    </nav>
    <svg><path d="M0 0h24v24H0z"/></svg>
    <article>
        <h1>Main Heading</h1>
        <p>First paragraph with   extra    spaces.</p>
        <br/>
        <p>Second paragraph with <a href="#">a link</a> and <b>bold text</b>.</p>
    </article>
    <footer>Footer notes</footer>
</body>
</html>
"""


def test_extract_html_basic():
    result = extract_article_from_html(SAMPLE_HTML_BASIC, url="https://example.com/moe")
    assert result["url"] == "https://example.com/moe"
    assert result["title"] == "Understanding MoE Architecture - AI Insights"
    assert result["description"] == "A comprehensive guide to Mixture of Experts architecture in modern LLMs."
    assert "Mixture of Experts (MoE) is a machine learning technique." in result["content"]
    assert "It divides computation across multiple specialized expert sub-networks." in result["content"]
    assert "Analytics script" not in result["content"]
    assert "Home" not in result["content"]  # nav excluded
    assert result["error"] is None


def test_extract_html_og_metadata():
    result = extract_article_from_html(SAMPLE_HTML_OG_TAGS, url="https://example.com/deepseek")
    assert result["title"] == "DeepSeek-V3 Technical Deep Dive"
    assert result["description"] == "Exploring MLA and DeepSeekMoE innovations."
    assert "Multi-Head Latent Attention (MLA)" in result["content"]
    assert "font-size" not in result["content"]
    assert result["error"] is None


def test_strips_scripts_styles_and_noise():
    result = extract_article_from_html(SAMPLE_HTML_NOISY)
    content = result["content"]
    assert "var token" not in content
    assert "background: #fff" not in content
    assert "Please enable javascript" not in content
    assert "Nav item" not in content
    assert "Main Heading" in content
    assert "First paragraph with extra spaces." in content
    assert "Second paragraph with a link and bold text." in content


def test_whitespace_normalization():
    html = """
    <div>
        <p>Line 1</p>
        
        
        <p>Line 2</p>
    </div>
    """
    result = extract_article_from_html(html)
    assert "Line 1\n\nLine 2" in result["content"]


@patch("urllib.request.urlopen")
def test_fetch_article_content_success(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.read.return_value = SAMPLE_HTML_BASIC.encode("utf-8")
    mock_resp.headers.get_content_charset.return_value = "utf-8"
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    result = fetch_article_content("https://example.com/moe")
    assert result["error"] is None
    assert result["title"] == "Understanding MoE Architecture - AI Insights"
    assert "Mixture of Experts" in result["content"]
    assert mock_urlopen.call_count == 1
    
    # Check that request included a User-Agent header
    req = mock_urlopen.call_args[0][0]
    assert "User-agent" in req.headers or "User-Agent" in req.headers


@patch("urllib.request.urlopen")
def test_fetch_article_content_http_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="https://example.com/404",
        code=404,
        msg="Not Found",
        hdrs={},
        fp=None,
    )

    result = fetch_article_content("https://example.com/404")
    assert result["title"] == ""
    assert result["content"] == ""
    assert result["error"] is not None
    assert "404" in result["error"]


def test_fetch_article_content_invalid_url():
    result = fetch_article_content("not-a-valid-url")
    assert result["error"] is not None
    assert result["content"] == ""


def test_cli_json_output(capsys, monkeypatch):
    test_url = "https://example.com/test"
    with patch("scripts.fetch_url.fetch_article_content") as mock_fetch:
        mock_fetch.return_value = {
            "url": test_url,
            "title": "Test Title",
            "description": "Test Desc",
            "content": "Test Content",
            "error": None,
        }
        monkeypatch.setattr("sys.argv", ["fetch_url.py", test_url, "--json"])
        exit_code = main()
        assert exit_code == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["title"] == "Test Title"
        assert data["content"] == "Test Content"


def test_cli_text_output(capsys, monkeypatch):
    test_url = "https://example.com/test"
    with patch("scripts.fetch_url.fetch_article_content") as mock_fetch:
        mock_fetch.return_value = {
            "url": test_url,
            "title": "Test Title",
            "description": "Test Desc",
            "content": "Test Content",
            "error": None,
        }
        monkeypatch.setattr("sys.argv", ["fetch_url.py", test_url])
        exit_code = main()
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Title: Test Title" in captured.out
        assert "Description: Test Desc" in captured.out
        assert "Test Content" in captured.out


@patch("urllib.request.urlopen")
def test_fetch_article_content_url_error(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.URLError(reason="Connection refused")
    result = fetch_article_content("https://example.com/unavailable")
    assert result["error"] is not None
    assert "Connection refused" in result["error"]
    assert result["content"] == ""


@patch("urllib.request.urlopen")
def test_fetch_article_content_timeout(mock_urlopen):
    mock_urlopen.side_effect = TimeoutError("Request timed out")
    result = fetch_article_content("https://example.com/timeout")
    assert result["error"] is not None
    assert "timed out" in result["error"].lower()


@patch("urllib.request.urlopen")
def test_fetch_article_content_gbk_charset(mock_urlopen):
    html_gbk = "<html><head><title>中文标题</title></head><body><p>中文正文内容</p></body></html>"
    mock_resp = MagicMock()
    mock_resp.read.return_value = html_gbk.encode("gbk")
    mock_resp.headers.get_content_charset.return_value = "gbk"
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    result = fetch_article_content("https://example.com/gbk")
    assert result["error"] is None
    assert result["title"] == "中文标题"
    assert "中文正文内容" in result["content"]


def test_extract_html_malformed_and_entities():
    raw_html = "<title>&lt;Python &amp; AI&gt;</title><p>&copy; 2026 <b>Hello &quot;World&quot;</b><br>Unclosed tag"
    result = extract_article_from_html(raw_html)
    assert result["title"] == "<Python & AI>"
    assert '© 2026 Hello "World"' in result["content"]
    assert "Unclosed tag" in result["content"]


def test_cli_error_handling(capsys, monkeypatch):
    test_url = "https://example.com/error"
    with patch("scripts.fetch_url.fetch_article_content") as mock_fetch:
        mock_fetch.return_value = {
            "url": test_url,
            "title": "",
            "description": "",
            "content": "",
            "error": "HTTP Error 500: Internal Server Error",
        }
        monkeypatch.setattr("sys.argv", ["fetch_url.py", test_url])
        exit_code = main()
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: HTTP Error 500" in captured.err

