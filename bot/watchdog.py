"""Runtime watchdog for the bot process.

If the heartbeat stops advancing for more than 120 seconds (event loop hung,
deadlock, or a blocked I/O call), the process exits with a non-zero status so
that the GitHub Actions runner / supervisor can restart it instead of leaving a
zombie that reports «online» forever.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

# Reuse the same status location as scripts.status (kept in sync).
try:
    from scripts.status import STATE_PATH as _STATE_PATH
except Exception:  # pragma: no cover
    _STATE_PATH = Path("data") / "runtime" / "status.json"

_CHECK_INTERVAL = 30.0
_STALE_AFTER = 120.0


def _heartbeat_age() -> float | None:
    try:
        with open(_STATE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        hb = (data.get("bot") or {}).get("last_heartbeat")
        if not hb:
            return None
        # Parse "YYYY-MM-DDTHH:MM:SSZ"
        import datetime as _dt
        t = _dt.datetime.strptime(hb, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=_dt.timezone.utc).timestamp()
        return time.time() - t
    except Exception:
        return None


def _watch() -> None:
    # Give the bot time to write its first heartbeat before judging.
    time.sleep(90)
    while True:
        age = _heartbeat_age()
        if age is not None and age > _STALE_AFTER:
            try:
                print(f"[watchdog] heartbeat stale for {int(age)}s — exiting for restart",
                      flush=True)
            except Exception:
                pass
            os._exit(1)
        time.sleep(_CHECK_INTERVAL)


def start() -> threading.Thread:
    t = threading.Thread(target=_watch, name="runtime-watchdog", daemon=True)
    t.start()
    return t
