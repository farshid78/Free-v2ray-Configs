import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# بارگذاری .env از ریشهٔ پروژه (در صورت وجود)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

def _env(name: str, default: str = "") -> str:
    """مقدارِ env با پیش‌فرض — کلیدِ خالی همان «تعریف‌نشده» است.

    `MINI_APP_URL=` (کلیدِ موجود با مقدارِ تهی) با `os.getenv(name, default)`
    رشتهٔ تهی برمی‌گرداند، نه پیش‌فرض را. نتیجه‌اش دکمهٔ Web App با URLِ تهی بود
    و تلگرام *کلِ* پیامِ `/start` را رد می‌کرد:
    `Bad Request: inline keyboard button Web App URL '' is invalid: URL host is empty`.
    یعنی کاربر استارت می‌زد و هیچ پیامی نمی‌دید، بدونِ هیچ خطای قابل‌فهم.
    """
    return (os.getenv(name) or "").strip() or default


BOT_TOKEN = _env("BOT_TOKEN")
OWNER_ID = int(_env("OWNER_ID", "0") or "0")
CHANNEL_USERNAME = _env("CHANNEL_USERNAME", "jojo_config")
GITHUB_TOKEN = _env("GITHUB_TOKEN")
GH_OWNER = _env("GH_OWNER", "farshid78")
GH_REPO = _env("GH_REPO", "Free-v2ray-Configs")

DB_PATH = _env("BOT_DB", str(REPO_ROOT / "data" / "bot.db"))
#: آدرسِ پنلِ گلس. تلگرام فقط HTTPS را برای Web App قبول می‌کند، پس هر مقدارِ
#: غیرِ HTTPS در `keyboards.main_menu` کنار گذاشته می‌شود (دکمهٔ بی‌اعتبار نباید
#: کلِ منو را از کار بیندازد).
MINI_APP_URL = _env("MINI_APP_URL",
                    "https://farshid78.github.io/Free-v2ray-Configs/miniapp.html")
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
