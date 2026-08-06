import pytest
from scripts.login_helper import get_session_path, PLATFORMS

def test_get_session_path():
    for platform in ["bilibili", "zhihu", "douyin", "x"]:
        path = get_session_path(platform)
        assert path.endswith(f"{platform}_state.json")
        assert platform in PLATFORMS

def test_invalid_platform():
    with pytest.raises(ValueError):
        get_session_path("unknown_platform")
