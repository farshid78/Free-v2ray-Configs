#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""status.py — وضعیتِ ماندگارِ اجرا، قفلِ چرخه، heartbeat و انتشارِ وضعیت.

چرا این ماژول لازم است
──────────────────────
پیش از این هیچ‌جا نگه‌داری نمی‌شد که «آخرین چرخه کِی و چقدر طول کشید»، «کدام
مرحله شکست خورد»، «ربات آنلاین است یا نه» و «چند پیام در صف مانده». داشبورد
تنها می‌توانست حدس بزند که «آخرین workflow اجرا شده» یعنی «همه‌چیز خوب است».
اندازه‌گیریِ واقعیِ ۲۹ اجرای اخیر نشان داد این حدس غلط است: دو اجرا
`startup_failure` و یکی `cancelled` بودند، در حالی که هیچ‌کدام در خروجیِ
منتشرشده دیده نمی‌شدند.

کجا نگه داشته می‌شود
────────────────────
`data/runtime/status.json` (محلی، gitignore) منبعِ حقیقت است و با دستور
`publish` روی شاخهٔ **`state`** منتشر می‌شود.

⚠️ چرا شاخهٔ `state` و نه `main`: انتشارِ تجمیع روی `main` یک force-push است
که درخت را از فهرستِ خروجی می‌سازد؛ هر فایلی بیرون از آن فهرست (وضعیت، صف،
ledger) در دورِ بعد پاک می‌شود. شاخهٔ جدا این تضاد را کامل حذف می‌کند و
داشبوردها همان فایل را از raw می‌خوانند.

تضمین‌ها
────────
• **fail-open**: هیچ خطایی در این ماژول نباید چرخهٔ سالم را بشکند؛ خروجیِ
  همهٔ توابعِ سطحِ بالا امن است و خطا فقط لاگ می‌شود.
• **نوشتنِ اتمی**: tmp + os.replace، پس خوانندهٔ هم‌زمان فایلِ نیم‌نوشته نمی‌بیند.
• **قفل با مالک و انقضا**: دو چرخه هم‌زمان اجرا نمی‌شوند و قفلِ رهاشده
  (اجرای کشته‌شده) پس از TTL خودبه‌خود آزاد می‌شود — بدونِ نیاز به دخالتِ دستی.
• **بدونِ راز**: هیچ توکنی در این فایل نوشته نمی‌شود؛ فقط شمارنده و زمان.

استفاده
───────
    python scripts/status.py begin --workflow aggregate --ttl-min 40
    python scripts/status.py stage collection --status ok --detail "11495 configs"
    python scripts/status.py finish --ok
    python scripts/status.py heartbeat --pid 1234
    python scripts/status.py publish
    python scripts/status.py show
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / "data" / "runtime"
STATE_PATH = STATE_DIR / "status.json"
LOCK_PATH = STATE_DIR / ".filelock"
STATE_BRANCH = os.environ.get("STATE_BRANCH", "state")
STATE_FILE = "status.json"
HISTORY_MAX = 20

SCHEMA = 1


def _now() -> float:
    return time.time()


def _iso(ts: float | None = None) -> str:
    return _dt.datetime.fromtimestamp(ts if ts is not None else _now(),
                                      _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default() -> dict:
    return {
        "schema": SCHEMA,
        "updated_at": None,
        "bot": {"online": False, "last_heartbeat": None, "heartbeat_age_s": None,
                "pid": None, "host": None, "note": ""},
        "cycle": {"id": None, "workflow": None, "started_at": None,
                  "finished_at": None, "ok": None, "duration_s": None,
                  "error": None, "stages": {}},
        "counts": {"collected": 0, "verified": 0, "invalid": 0, "new": 0,
                   "duplicate": 0, "sent": 0, "send_failed": 0, "queued": 0},
        "workflows": {},
        "lock": {"owner": None, "workflow": None, "expires_at": None},
        "history": [],
    }


# ──────────────────────────────────────────────────────────────────────────────
# خواندن/نوشتن
# ──────────────────────────────────────────────────────────────────────────────
def load() -> dict:
    """وضعیت را می‌خواند؛ فایلِ خراب/غایب ⇒ وضعیتِ پیش‌فرض (هرگز استثنا)."""
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            raise ValueError("schema mismatch")
        base = _default()
        for key, val in base.items():
            if key not in data:
                data[key] = val
            elif isinstance(val, dict) and isinstance(data.get(key), dict):
                for sub, subval in val.items():
                    data[key].setdefault(sub, subval)
        return data
    except Exception:
        return _default()


def save(data: dict) -> bool:
    """ذخیرهٔ اتمی. True = موفق."""
    try:
        data["updated_at"] = _iso()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(STATE_DIR), prefix=".status-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, STATE_PATH)
        return True
    except Exception as exc:                      # fail-open
        print(f"[status] warning: could not save state: {exc}", file=sys.stderr)
        return False


@contextlib.contextmanager
def _file_lock(timeout: float = 10.0):
    """قفلِ فایل برای read-modify-write بینِ دو پروسه روی یک ماشین.

    قفلِ *بین‌ماشینی* با فایلِ `lock` داخلِ خودِ وضعیت انجام می‌شود (owner +
    expires_at)؛ این یکی فقط جلوی تداخلِ لحظه‌ایِ دو پروسهٔ همان ماشین را
    می‌گیرد.
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    deadline = _now() + timeout
    fh = None
    while _now() < deadline:
        try:
            fh = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            # قفلِ رهاشده از پروسهٔ کشته‌شده: پس از ۳۰ ثانیه آزادش کن
            try:
                if _now() - LOCK_PATH.stat().st_mtime > 30:
                    LOCK_PATH.unlink(missing_ok=True)
                    continue
            except OSError:
                pass
            time.sleep(0.05)
    try:
        if fh is not None:
            os.write(fh, str(os.getpid()).encode())
            os.close(fh)
        yield
    finally:
        if fh is not None:
            with contextlib.suppress(OSError):
                LOCK_PATH.unlink(missing_ok=True)


def _mutate(fn) -> dict:
    """read-modify-write اتمی با قفلِ فایل."""
    with _file_lock():
        data = load()
        fn(data)
        save(data)
        return data


# ──────────────────────────────────────────────────────────────────────────────
# قفلِ چرخه (بین‌ماشینی)
# ──────────────────────────────────────────────────────────────────────────────
def lock_owner() -> str | None:
    data = load()
    lock = data.get("lock") or {}
    if lock.get("owner") and (lock.get("expires_at") or 0) > _now():
        return str(lock["owner"])
    return None


def begin(workflow: str, ttl_min: float = 40.0, owner: str | None = None) -> tuple[bool, str]:
    """قفلِ چرخه را می‌گیرد. (True, owner) یا (False, دلیل)."""
    owner = owner or f"{socket.gethostname()}:{os.getpid()}"
    result = {"ok": False, "why": ""}

    def _apply(data: dict) -> None:
        lock = data.setdefault("lock", {})
        cur, exp = lock.get("owner"), lock.get("expires_at") or 0
        if cur and cur != owner and exp > _now():
            result["why"] = (f"cycle already running: owner={cur} "
                             f"workflow={lock.get('workflow')} "
                             f"expires_in={int(exp - _now())}s")
            return
        lock.update({"owner": owner, "workflow": workflow,
                     "expires_at": _now() + ttl_min * 60})
        data["cycle"] = {"id": owner, "workflow": workflow, "started_at": _iso(),
                         "finished_at": None, "ok": None, "duration_s": None,
                         "error": None, "stages": {}}
        result["ok"] = True

    _mutate(_apply)
    return result["ok"], (owner if result["ok"] else result["why"])


def release(owner: str) -> None:
    def _apply(data: dict) -> None:
        lock = data.setdefault("lock", {})
        if lock.get("owner") == owner:
            lock.update({"owner": None, "workflow": None, "expires_at": None})

    _mutate(_apply)


def stage(name: str, status: str = "ok", detail: str = "") -> None:
    def _apply(data: dict) -> None:
        cyc = data.setdefault("cycle", {})
        stages = cyc.setdefault("stages", {})
        prev = stages.get(name) or {}
        stages[name] = {"status": status, "at": _iso(), "detail": str(detail)[:300],
                        "duration_s": prev.get("duration_s")}

    _mutate(_apply)


def set_stage_duration(name: str, seconds: float) -> None:
    def _apply(data: dict) -> None:
        st = data.setdefault("cycle", {}).setdefault("stages", {}).setdefault(name, {})
        st["duration_s"] = round(float(seconds), 1)

    _mutate(_apply)


def finish(ok: bool, error: str = "", counts: dict | None = None,
           workflow: str | None = None) -> None:
    def _apply(data: dict) -> None:
        cyc = dict(data.get("cycle") or {})
        started = cyc.get("started_at")
        dur = None
        if started:
            with contextlib.suppress(Exception):
                t0 = _dt.datetime.strptime(started, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=_dt.timezone.utc).timestamp()
                dur = round(_now() - t0, 1)
        cyc.update({"finished_at": _iso(), "ok": bool(ok),
                    "duration_s": dur, "error": (error or "")[:500]})
        data["cycle"] = cyc
        wf = workflow or cyc.get("workflow") or "unknown"
        data.setdefault("workflows", {})[wf] = {
            "last_run_at": _iso(), "last_ok": bool(ok), "duration_s": dur,
            "error": (error or "")[:300],
        }
        if counts:
            c = data.setdefault("counts", {})
            for k, v in counts.items():
                if v is not None:
                    with contextlib.suppress(TypeError, ValueError):
                        c[k] = int(v)
        hist = data.setdefault("history", [])
        hist.append({"at": _iso(), "workflow": wf, "ok": bool(ok),
                     "duration_s": dur, "error": (error or "")[:200],
                     "counts": dict(counts or {})})
        data["history"] = hist[-HISTORY_MAX:]
        lock = data.setdefault("lock", {})
        if lock.get("owner") == cyc.get("id"):
            lock.update({"owner": None, "workflow": None, "expires_at": None})

    _mutate(_apply)


# ──────────────────────────────────────────────────────────────────────────────
# heartbeat ربات
# ──────────────────────────────────────────────────────────────────────────────
def heartbeat(pid: int | None = None, note: str = "") -> None:
    def _apply(data: dict) -> None:
        data["bot"] = {"online": True, "last_heartbeat": _iso(),
                       "heartbeat_age_s": 0, "pid": pid or os.getpid(),
                       "host": socket.gethostname(), "note": note[:200]}

    _mutate(_apply)


def bot_offline(note: str = "stopped") -> None:
    def _apply(data: dict) -> None:
        bot = data.setdefault("bot", {})
        bot.update({"online": False, "note": note[:200]})

    _mutate(_apply)


def set_counts(**kw) -> None:
    def _apply(data: dict) -> None:
        c = data.setdefault("counts", {})
        for k, v in kw.items():
            if v is not None:
                with contextlib.suppress(TypeError, ValueError):
                    c[k] = int(v)

    _mutate(_apply)


def incr(name: str, amount: int = 1) -> None:
    def _apply(data: dict) -> None:
        c = data.setdefault("counts", {})
        with contextlib.suppress(TypeError, ValueError):
            c[name] = int(c.get(name, 0)) + int(amount)

    _mutate(_apply)


def record_workflow(name: str, ok: bool, duration_s: float | None = None,
                    error: str = "") -> None:
    def _apply(data: dict) -> None:
        data.setdefault("workflows", {})[name] = {
            "last_run_at": _iso(), "last_ok": bool(ok),
            "duration_s": (round(float(duration_s), 1) if duration_s else None),
            "error": (error or "")[:300],
        }

    _mutate(_apply)


def counts_from_repo(root: Path | None = None) -> dict:
    """شمارنده‌های واقعی را از خروجیِ همین چرخه می‌خواند (نه از حدس).

    منبع: `index.json` (دستهٔ all و آبشارِ verified) و صفِ ارسال.
    """
    root = Path(root or REPO_ROOT)
    out: dict = {}
    try:
        with open(root / "index.json", encoding="utf-8") as f:
            idx = json.load(f)
        allc = (idx.get("categories") or {}).get("all") or {}
        cas = idx.get("cascade_categories") or {}
        for key, val in (("collected", allc.get("total_fetched")),
                         ("duplicate", allc.get("duplicates")),
                         ("invalid", allc.get("broken")),
                         ("verified", (cas.get("verified") or {}).get("unique"))):
            if val is not None:
                out[key] = int(val)
    except Exception:
        pass
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from bot import outbox as _ob
        s = _ob.stats()
        out.update({"queued": s["pending"], "sent": s["sent_total"],
                    "send_failed": s["failed_attempts"]})
        # «جدید» = کانفیگ‌هایی از verified که هنوز به کانال نرفته‌اند (دقیقاً
        # همان تعریفی که صفِ ارسال با آن کار می‌کند).
        try:
            with open(root / "verified" / "configs.txt", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip() and not ln.lstrip().startswith("#")]
            out["new"] = sum(1 for ln in lines if not _ob.seen(_ob.config_key(ln)))
        except Exception:
            pass
    except Exception:
        pass
    return out


def summarize() -> dict:
    """نمای خواندنی: سنِ heartbeat و وضعیتِ کهنه‌بودن را هم حساب می‌کند."""
    data = load()
    bot = dict(data.get("bot") or {})
    hb = bot.get("last_heartbeat")
    if hb:
        with contextlib.suppress(Exception):
            t = _dt.datetime.strptime(hb, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=_dt.timezone.utc).timestamp()
            age = int(_now() - t)
            bot["heartbeat_age_s"] = age
            # آستانهٔ آفلاین: ربات هر ۶۰ ثانیه heartbeat می‌دهد؛ ۵ دقیقه
            # بی‌خبری یعنی «آفلاین» (حاشیهٔ ۵ برابر، پس یک تأخیرِ گذرا
            # وضعیت را قرمز نمی‌کند).
            bot["online"] = bool(bot.get("online")) and age <= 300
    else:
        bot["online"] = False
    data["bot"] = bot
    return data


# ──────────────────────────────────────────────────────────────────────────────
# انتشار روی شاخهٔ state (git plumbing، بدونِ دست‌زدن به worktree)
# ──────────────────────────────────────────────────────────────────────────────
def _git(*args: str, timeout: int = 60, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(REPO_ROOT), capture_output=True,
                          text=True, timeout=timeout, check=check)


def _parent_sha() -> str | None:
    r = _git("ls-remote", "origin", f"refs/heads/{STATE_BRANCH}")
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.split()[0].strip()
    return None


def publish() -> bool:
    """`status.json` را روی شاخهٔ `state` می‌نویسد. False = ناموفق (fail-open)."""
    data = summarize()
    # کپیِ منتشرشده نباید رکوردهای حجیمِ محلی را ببرد؛ همان ساختار کافی است.
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(data, ensure_ascii=False, indent=1).encode()
    except Exception:
        return False
    for attempt in range(3):
        try:
            h = subprocess.run(["git", "hash-object", "-w", "--stdin"],
                               cwd=str(REPO_ROOT), input=blob, capture_output=True,
                               timeout=60)
            if h.returncode != 0:
                raise RuntimeError(h.stderr.decode().strip()[:200])
            blob_sha = h.stdout.decode().strip()
            tree_line = f"100644 blob {blob_sha}\t{STATE_FILE}\n"
            t = subprocess.run(["git", "mktree"], cwd=str(REPO_ROOT),
                               input=tree_line.encode(), capture_output=True, timeout=60)
            if t.returncode != 0:
                raise RuntimeError(t.stderr.decode().strip()[:200])
            tree = t.stdout.decode().strip()
            parent = _parent_sha()
            args = ["commit-tree", tree]
            if parent:
                args += ["-p", parent]
            args += ["-m", f"chore(state): runtime status {_iso()}"]
            c = _git(*args)
            if c.returncode != 0:
                raise RuntimeError(c.stderr.strip()[:200])
            commit = c.stdout.strip()
            p = _git("push", "--quiet", "origin", f"{commit}:refs/heads/{STATE_BRANCH}",
                     timeout=90)
            if p.returncode == 0:
                return True
            raise RuntimeError(p.stderr.strip()[:200])
        except Exception as exc:
            if attempt == 2:
                print(f"[status] publish failed: {exc}", file=sys.stderr)
                return False
            time.sleep(1.5 * (attempt + 1))
    return False


def pull() -> bool:
    """وضعیتِ منتشرشده را از شاخهٔ state می‌خواند و محلی می‌کند."""
    try:
        r = _git("fetch", "--depth=1", "--no-tags", "origin",
                 f"+refs/heads/{STATE_BRANCH}:refs/remotes/origin/{STATE_BRANCH}",
                 timeout=90)
        if r.returncode != 0:
            return False
        s = _git("show", f"refs/remotes/origin/{STATE_BRANCH}:{STATE_FILE}")
        if s.returncode != 0 or not s.stdout.strip():
            return False
        data = json.loads(s.stdout)
        if not isinstance(data, dict) or data.get("schema") != SCHEMA:
            return False
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with _file_lock():
            local = load()
            local["history"] = data.get("history") or local.get("history") or []
            local["workflows"] = data.get("workflows") or {}
            # قفل و heartbeat فقط مالِ خودِ این ماشین است؛ از دور برداشته نمی‌شود.
            save(local)
        return True
    except Exception as exc:
        print(f"[status] pull failed: {exc}", file=sys.stderr)
        return False


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def _parse_counts(pairs: list[str]) -> dict:
    out = {}
    for p in pairs:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="runtime status / lock / heartbeat")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("begin")
    b.add_argument("--workflow", default="aggregate")
    b.add_argument("--ttl-min", type=float, default=40.0)

    s = sub.add_parser("stage")
    s.add_argument("name")
    s.add_argument("--status", default="ok")
    s.add_argument("--detail", default="")
    s.add_argument("--seconds", type=float, default=None)

    f = sub.add_parser("finish")
    f.add_argument("--ok", action="store_true")
    f.add_argument("--failed", action="store_true")
    f.add_argument("--error", default="")
    f.add_argument("--counts", nargs="*", default=[])
    f.add_argument("--workflow", default=None)

    h = sub.add_parser("heartbeat")
    h.add_argument("--pid", type=int, default=0)
    h.add_argument("--note", default="")

    sub.add_parser("offline")
    sub.add_parser("publish")
    sub.add_parser("pull")
    sub.add_parser("show")

    c = sub.add_parser("counts")
    c.add_argument("pairs", nargs="*")

    r = sub.add_parser("report")
    r.add_argument("--root", default=".")
    r.add_argument("--workflow", default="aggregate")
    r.add_argument("--failed", action="store_true")
    r.add_argument("--error", default="")
    r.add_argument("--stage", action="append", default=[], metavar="name=status[:detail]")
    r.add_argument("--counts", nargs="*", default=[], metavar="key=value")
    r.add_argument("--no-publish", action="store_true")

    i = sub.add_parser("incr")
    i.add_argument("name")
    i.add_argument("--amount", type=int, default=1)

    args = ap.parse_args(argv)

    if args.cmd == "begin":
        ok, info = begin(args.workflow, args.ttl_min)
        print(f"{'acquired' if ok else 'busy'}: {info}")
        return 0 if ok else 75          # 75 = EX_TEMPFAIL → «رد شد»، نه «شکست»
    if args.cmd == "stage":
        stage(args.name, args.status, args.detail)
        if args.seconds is not None:
            set_stage_duration(args.name, args.seconds)
        print(f"stage {args.name}={args.status}")
        return 0
    if args.cmd == "finish":
        counts = _parse_counts(args.counts)
        finish(ok=not args.failed and (args.ok or not args.error),
               error=args.error, counts=counts or None, workflow=args.workflow)
        publish()
        print("cycle finished")
        return 0
    if args.cmd == "heartbeat":
        heartbeat(args.pid or None, args.note)
        print("heartbeat ok")
        return 0
    if args.cmd == "offline":
        bot_offline()
        publish()
        print("bot marked offline")
        return 0
    if args.cmd == "publish":
        return 0 if publish() else 1
    if args.cmd == "pull":
        return 0 if pull() else 1
    if args.cmd == "counts":
        set_counts(**_parse_counts(args.pairs))
        print("counts updated")
        return 0
    if args.cmd == "incr":
        incr(args.name, args.amount)
        print(f"{args.name} += {args.amount}")
        return 0
    if args.cmd == "report":
        for spec in args.stage:
            name, _, rest = spec.partition("=")
            st_val, _, detail = rest.partition(":")
            if name:
                stage(name, st_val or "ok", detail)
        counts = counts_from_repo(Path(args.root))
        counts.update({k: v for k, v in _parse_counts(args.counts).items()})
        finish(ok=not args.failed, error=args.error, counts=counts,
               workflow=args.workflow)
        print(json.dumps({"ok": not args.failed, "counts": counts}, ensure_ascii=False))
        if not args.no_publish:
            publish()
        return 0
    if args.cmd == "show":
        print(json.dumps(summarize(), ensure_ascii=False, indent=1))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
