import os
import sys
import json

# Ensure root project directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.config import SESSIONS_DIR
from scripts.login_helper import PLATFORMS, get_session_path

DOMAIN_MAP = {
    "bilibili": ".bilibili.com",
    "zhihu": ".zhihu.com",
    "xiaohongshu": ".xiaohongshu.com",
    "douyin": ".douyin.com",
    "x": ".x.com"
}

def cookie_str_to_storage_state(platform: str, cookie_str: str) -> dict:
    domain = DOMAIN_MAP.get(platform, f".{platform}.com")
    cookies = []
    
    # Parse cookie string like "a=1; b=2"
    parts = cookie_str.split(";")
    for part in parts:
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain,
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax"
            })
            
    return {
        "cookies": cookies,
        "origins": []
    }

def set_platform_cookie(platform: str, cookie_str: str) -> str:
    save_path = get_session_path(platform)
    state_data = cookie_str_to_storage_state(platform, cookie_str)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(state_data, f, ensure_ascii=False, indent=2)
        
    return save_path

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        p = sys.argv[1]
        c = " ".join(sys.argv[2:])
        path = set_platform_cookie(p, c)
        print(f"[✓] Successfully set session for {p} at {path}")
