import sqlite3
from pathlib import Path

from .config import DB_PATH


def _conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id INTEGER PRIMARY KEY, username TEXT, joined_at TEXT DEFAULT (datetime('now')))"
    )
    c.execute(
        "CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)"
    )
    c.commit()
    return c


def add_user(user_id: int, username: str | None) -> None:
    c = _conn()
    c.execute("INSERT OR IGNORE INTO users(user_id, username) VALUES(?,?)", (user_id, username))
    c.commit()
    c.close()


def user_count() -> int:
    c = _conn()
    n = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    c.close()
    return n


def add_admin(user_id: int) -> None:
    c = _conn()
    c.execute("INSERT OR IGNORE INTO admins(user_id) VALUES(?)", (user_id,))
    c.commit()
    c.close()


def remove_admin(user_id: int) -> None:
    c = _conn()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    c.commit()
    c.close()


def is_admin(user_id: int) -> bool:
    c = _conn()
    row = c.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
    c.close()
    return row is not None
