import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# بارگذاری .env از ریشهٔ پروژه (در صورت وجود)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0") or "0")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "jojo_config").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GH_OWNER = os.getenv("GH_OWNER", "farshid78").strip()
GH_REPO = os.getenv("GH_REPO", "Free-v2ray-Configs").strip()

DB_PATH = os.getenv("BOT_DB", str(REPO_ROOT / "data" / "bot.db"))
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://farshid78.github.io/Free-v2ray-Configs/miniapp.html").strip()
VERIFIED_DIR = REPO_ROOT / "verified"
FAST_DIR = REPO_ROOT / "fast"
SECURE_DIR = REPO_ROOT / "secure"
ALL_DIR = REPO_ROOT / "all"
HEAVY_DIR = REPO_ROOT / "heavy"
LIGHT_DIR = REPO_ROOT / "light"
GOOGLE_DIR = REPO_ROOT / "google"
TOP100_PATH = REPO_ROOT / "top100.txt"
COUNTRIES_DIR = REPO_ROOT / "Countries"


def is_owner(user_id: int) -> bool:
    return bool(OWNER_ID) and user_id == OWNER_ID
