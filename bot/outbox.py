# -*- coding: utf-8 -*-
"""outbox.py — صفِ پایدارِ ارسال به کانال + دفترِ idempotency.

چرا لازم است (و چرا همان offset قبلی کافی نبود)
──────────────────────────────────────────────
نسخهٔ قبلی با یک شمارندهٔ `offset` در فایلِ JSON کار می‌کرد. سه نقصِ سنجیده:

1. **تکرارِ ارسال**: در CI هر برش یک ماشینِ تازه است و فایلِ offset با خودش
   نمی‌آید؛ نتیجه این بود که هر ۲۵ دقیقه همان کانفیگ‌های ابتدای فهرست
   دوباره به کانال می‌رفتند.
2. **گم‌شدنِ ارسال**: اگر فرایند وسطِ دسته کشته می‌شد، offset فقط با موفقیتِ
   کلِ دسته ذخیره می‌شد؛ ارسال‌های انجام‌شده دوباره فرستاده می‌شدند.
3. **خطای کانال**: وقتی `send_message` شکست می‌خورد، آن کانفیگ عملاً دور
   ریخته می‌شد (حلقه `break` می‌کرد و offset جلو نمی‌رفت، ولی هیچ صفی هم
   نبود که بعداً جبران کند).

این ماژول صف را در SQLite نگه می‌دارد (همان موتورِ `bot/db.py`) و هر کانفیگ
یک کلیدِ محتوایی دارد:

    key = sha256(بخشِ اتصالِ کانفیگ، بدونِ remark)[:16]

پس یک کانفیگ با هر ترتیب/برش/ری‌استارت حداکثر یک بار به کانال می‌رود و
شکست‌ها در صف می‌مانند با backoff نمایی.

⚠️ حدِ صادقانه: اگر پروسه *بینِ* پاسخِ موفقِ تلگرام و نوشتنِ `mark_sent`
کشته شود، آن یک پیام در اجرای بعد دوباره فرستاده می‌شود. Telegram برای
`sendMessage` کلیدِ idempotency ندارد، پس این پنجرهٔ چند میلی‌ثانیه‌ای با
هیچ روشی کاملاً بسته نمی‌شود؛ فقط کوچک نگه داشته شده است (نوشتن بی‌درنگ
پس از پاسخ، بدونِ کارِ دیگر در این میان).
"""

from __future__ import annotations

import hashlib
import sqlite3
import time
from pathlib import Path

from .config import DB_PATH

OUTBOX_DB = Path(DB_PATH).with_name("outbox.db")

#: پس از این تعداد تلاش، ردیف دیگر تلاش نمی‌شود ولی حذف هم نمی‌شود (قابلِ
#: بازرسی). ۲۰ تلاش با backoffِ سقف‌دار ۵ دقیقه‌ای ≈ بیش از یک ساعت.
MAX_ATTEMPTS = 20
BACKOFF_BASE = 5.0
BACKOFF_CAP = 300.0


def _conn() -> sqlite3.Connection:
    OUTBOX_DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(OUTBOX_DB, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute(
        "CREATE TABLE IF NOT EXISTS outbox ("
        " key TEXT PRIMARY KEY, text TEXT NOT NULL,"
        " created_at REAL NOT NULL, next_at REAL NOT NULL,"
        " attempts INTEGER NOT NULL DEFAULT 0, sent_at REAL, last_error TEXT)"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS ledger (key TEXT PRIMARY KEY, sent_at REAL NOT NULL)"
    )
    c.execute("CREATE INDEX IF NOT EXISTS outbox_due ON outbox(sent_at, next_at)")
    c.commit()
    return c


def config_key(line: str) -> str:
    """کلیدِ پایدارِ یک کانفیگ (بدونِ remark، تا تغییرِ برچسب کلید را عوض نکند)."""
    base = line.split("#", 1)[0].strip()
    return hashlib.sha256(base.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def enqueue(items: list[tuple[str, str]]) -> int:
    """(key, text) ها را در صف می‌گذارد؛ تعدادِ ردیف‌های *تازه* را برمی‌گرداند."""
    if not items:
        return 0
    now = time.time()
    added = 0
    c = _conn()
    try:
        for key, text in items:
            if not key or not text:
                continue
            try:
                cur = c.execute(
                    "INSERT OR IGNORE INTO outbox(key, text, created_at, next_at)"
                    " SELECT ?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM ledger WHERE key=?)",
                    (key, text, now, now, key),
                )
                added += cur.rowcount if cur.rowcount > 0 else 0
            except sqlite3.Error:
                continue
        c.commit()
    finally:
        c.close()
    return added


def due(limit: int = 1) -> list[dict]:
    """ردیف‌های آمادهٔ ارسال (صفِ FIFO)، بدونِ ردیف‌های تسلیم‌شده."""
    c = _conn()
    try:
        rows = c.execute(
            "SELECT key, text, attempts FROM outbox"
            " WHERE sent_at IS NULL AND next_at <= ? AND attempts < ?"
            " ORDER BY created_at LIMIT ?",
            (time.time(), MAX_ATTEMPTS, int(limit)),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        c.close()


def mark_sent(key: str) -> None:
    now = time.time()
    c = _conn()
    try:
        c.execute("INSERT OR REPLACE INTO ledger(key, sent_at) VALUES(?,?)", (key, now))
        c.execute("DELETE FROM outbox WHERE key=?", (key,))
        c.commit()
    finally:
        c.close()


def mark_failed(key: str, error: str = "") -> int:
    """تلاشِ ناموفق: attempts++ و next_at با backoff نمایی. تعدادِ تلاش را برمی‌گرداند."""
    c = _conn()
    try:
        row = c.execute("SELECT attempts FROM outbox WHERE key=?", (key,)).fetchone()
        attempts = int(row["attempts"]) + 1 if row else 1
        delay = min(BACKOFF_CAP, BACKOFF_BASE * (2 ** min(attempts, 10)))
        c.execute(
            "UPDATE outbox SET attempts=?, next_at=?, last_error=? WHERE key=?",
            (attempts, time.time() + delay, str(error)[:300], key),
        )
        c.commit()
        return attempts
    finally:
        c.close()


def stats() -> dict:
    c = _conn()
    try:
        pending = c.execute(
            "SELECT COUNT(*) FROM outbox WHERE sent_at IS NULL AND attempts < ?",
            (MAX_ATTEMPTS,),
        ).fetchone()[0]
        dead = c.execute(
            "SELECT COUNT(*) FROM outbox WHERE sent_at IS NULL AND attempts >= ?",
            (MAX_ATTEMPTS,),
        ).fetchone()[0]
        oldest = c.execute("SELECT MIN(created_at) FROM outbox WHERE sent_at IS NULL").fetchone()[0]
        sent_total = c.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
        failures = c.execute(
            "SELECT COALESCE(SUM(attempts),0) FROM outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
        return {
            "pending": int(pending),
            "dead": int(dead),
            "oldest_age_s": int(time.time() - oldest) if oldest else 0,
            "sent_total": int(sent_total),
            "failed_attempts": int(failures),
        }
    finally:
        c.close()


def dead_letter(limit: int = 100) -> list[dict]:
    """ردیف‌های تسلیم‌شده (به سقفِ تلاش رسیده) را برمی‌گرداند."""
    c = _conn()
    try:
        rows = c.execute(
            "SELECT key, text, attempts, last_error, created_at, next_at"
            " FROM outbox WHERE sent_at IS NULL AND attempts >= ?"
            " ORDER BY created_at LIMIT ?",
            (MAX_ATTEMPTS, int(limit)),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        c.close()


def retry_dead(keys: list[str] | None = None) -> int:
    """ردیف‌های dead را برای تلاشِ مجدد آماده می‌کند (attempts را صفر می‌کند).
    اگر keys=None باشد، همهٔ deadها reset می‌شوند. تعدادِ resetشده را برمی‌گرداند."""
    c = _conn()
    try:
        if keys:
            placeholders = ",".join("?" for _ in keys)
            cur = c.execute(
                f"UPDATE outbox SET attempts=0, next_at=?, last_error=NULL"
                f" WHERE key IN ({placeholders}) AND sent_at IS NULL",
                (time.time(), *keys),
            )
        else:
            cur = c.execute(
                "UPDATE outbox SET attempts=0, next_at=?, last_error=NULL"
                " WHERE sent_at IS NULL AND attempts >= ?",
                (time.time(), MAX_ATTEMPTS),
            )
        c.commit()
        return int(cur.rowcount or 0)
    finally:
        c.close()


def seen(key: str) -> bool:
    c = _conn()
    try:
        return c.execute("SELECT 1 FROM ledger WHERE key=?", (key,)).fetchone() is not None
    finally:
        c.close()


def reset() -> None:
    """برای تست: صف و دفتر را پاک می‌کند."""
    c = _conn()
    try:
        c.execute("DELETE FROM outbox")
        c.execute("DELETE FROM ledger")
        c.commit()
    finally:
        c.close()
