import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS_DIR = os.path.join(BASE_DIR, ".sessions")
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_FAVS_FILE = os.path.join(DATA_DIR, "raw_favs.json")
IDEAS_DB_FILE = os.path.join(DATA_DIR, "content_ideas_database.md")

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
