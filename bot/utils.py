import base64
import binascii
from pathlib import Path

from .config import (VERIFIED_DIR, FAST_DIR, SECURE_DIR, ALL_DIR,
                     HEAVY_DIR, LIGHT_DIR, GOOGLE_DIR, TOP100_PATH)


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    # سرآیندهای ساب‌سکریپشن (`#profile-title:`, `# criterion:` و …) کانفیگ
    # نیستند؛ شمردنشان عددِ دسته را از محتوای واقعی جدا می‌کرد.
    return [ln for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def _read_base64_subscription(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return []
    if not raw:
        return []
    try:
        data = base64.b64decode("".join(raw.split()), validate=False)
    except (binascii.Error, ValueError):
        return []
    text = data.decode("utf-8", errors="replace")
    return [ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


# برچسبِ هر دسته برای پنل ربات — همان تعاریفِ مستندِ پروژه.
CATEGORY_LABELS = {
    "top100": "🏆 ۱۰۰ برتر (کوتاه‌ترین، سه بار آزموده)",
    "verified": "🏆 Verified (در هر ۳ دور موفق — پیشنهادی)",
    "fast": "⚡ Fast (verified و میانهٔ تأخیر < ۸۰۰ms)",
    "secure": "🔐 Secure (verified و forward secrecy)",
    "google": "🟢 Google (verified و آزمون gstatic/YouTube/Play/Maven/Gemini)",
    "all": "🌐 All (همه، dedup، بزرگ‌ترین)",
    "heavy": "📦 Heavy (۵ منبع پرحجم)",
    "light": "⭐ Light (۸ منبع گزیده)",
}


def _dir_for(bucket: str) -> Path | None:
    return {
        "verified": VERIFIED_DIR, "fast": FAST_DIR, "secure": SECURE_DIR,
        "all": ALL_DIR, "heavy": HEAVY_DIR, "light": LIGHT_DIR,
        "google": GOOGLE_DIR,
    }.get(bucket)


def load_configs(bucket: str = "verified", limit: int | None = None) -> list[str]:
    if bucket == "top100":
        lines = _read_lines(TOP100_PATH)
        if limit is not None:
            lines = lines[:limit]
        return lines
    d = _dir_for(bucket)
    if d is None:
        return []
    lines = _read_lines(d / "configs.txt")
    if not lines:
        # فایلِ base64 یک خطِ کدشده است؛ اگر آن را به‌عنوان «یک کانفیگ» برگردانیم
        # ربات چیزی می‌فرستد که هیچ کلاینتی نمی‌شناسد. باید باز شود.
        lines = _read_base64_subscription(d / "configs_base64.txt")
    if limit is not None:
        lines = lines[:limit]
    return lines


def filter_by_protocol(lines: list[str], proto: str) -> list[str]:
    p = proto.lower()
    out = []
    for ln in lines:
        low = ln.lower()
        if p in ("vless", "vmess", "trojan", "ss", "shadowsocks", "hysteria", "tuic"):
            if low.startswith(p + "://") or p in low.split("://", 1)[0]:
                out.append(ln)
        else:
            if p in low:
                out.append(ln)
    return out


def filter_by_country(lines: list[str], country: str) -> list[str]:
    c = country.lower()
    return [ln for ln in lines if c in ln.lower()]


def chunk_text(lines: list[str], max_chars: int = 3900) -> list[str]:
    chunks: list[str] = []
    cur: list[str] = []
    cur_len = 0
    for ln in lines:
        if cur_len + len(ln) + 1 > max_chars and cur:
            chunks.append("\n".join(cur))
            cur = []
            cur_len = 0
        cur.append(ln)
        cur_len += len(ln) + 1
    if cur:
        chunks.append("\n".join(cur))
    return chunks
