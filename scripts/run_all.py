#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اجرای **کلِ** پروژه با یک دستور — هماهنگ‌کنندهٔ مراحل، بدون تکرارِ منطقِ هیچ‌کدام.

هر مرحله همان اسکریپتِ رسمیِ خودش را اجرا می‌کند (نه بازنویسیِ آن):

    ۰) scripts/brand.py --check        دروازهٔ برند: صفر drift بین brand و خروجی‌ها
    ۱) scripts/aggregate.py            واکشی ۱۳ منبع → all/ heavy/ light/ protocols/
                                       archive/ index.json health.json state.json
    ۲) scripts/pipeline.py             آبشار L0→L3 روی all/configs.txt
                                       → verified/ fast/ secure/ top100.txt
    ۳) scripts/googleready.py          آزمونِ گوگل روی verified/configs.txt → google/
    ۴) docs-src/build.py               رندر README×۴ + docs/ (داشبورد، صفحات، sitemap)

ترتیب دقیقاً همان ترتیبِ `.github/workflows/aggregate.yml` است؛ این فایل فقط
«کجا و با چه آرگومانی» را می‌داند و «چه کاری» را به خودِ اسکریپت‌ها واگذار می‌کند.

⚠️ ابزارِ سنجشِ واقعی (`xray-knife`) لازم است
─────────────────────────────────────────────
لایه‌های L3 و «Google Ready» بدونِ این باینری **واقعاً** سنجیده نمی‌شوند؛
`realtest.resolve_binary` آن را از `L3_XK_BIN` یا `PATH` می‌گیرد. این اسکریپت
خودش هم در مسیرهای محلیِ مخزن می‌گردد (همان جایی که `.gitignore` پوشش می‌دهد):

    .cache/xray-knife/xray-knife[.exe]
    .cache/validators/xray-knife[.exe]

نسخهٔ pin‌شدهٔ CI همان `v10.1.1` است (`Xray-knife-windows-64.zip` روی ویندوز) و
checksumِ آرشیو با فایلِ `.dgst`ِ خودِ upstream باید بخواند؛ الزامِ آن در
`.github/workflows/aggregate.yml` گامِ «Install xray-knife» مستند شده است.

چند تصمیمِ عمدی
───────────────
۱) **Fail-fast فقط برای انباشت‌گر.** اگر `aggregate.py` شکست بخورد، مراحلِ بعدی
   روی دادهٔ کهنه کار می‌کنند و نتیجه‌شان گمراه‌کننده است ⇒ همان‌جا می‌ایستیم.
   شکستِ آبشار انتشار را نمی‌شکند: `googleready.py` با `--cascade-outcome failed`
   خودش را «skipped» می‌علامد (همان قراردادِ CI) و docs از دادهٔ موجود ساخته می‌شود.

۲) **rc صفر کافی نیست.** `pipeline.py` حتی وقتی هیچ کانفیگی تأیید نشود ۰
   برمی‌گرداند، و `googleready.py` برای وضعیت‌های `skipped`/`empty` هم ۰ می‌دهد.
   پس هر مرحله یک **پس‌شرطِ اندازه‌پذیر** دارد: وجودِ `verified/configs.txt`ِ
   ناتهی و `status == "published"` در خروجیِ JSONِ گوگل. چیزی که اجرا نشده یا
   خروجیِ خالی داده، ✅ گزارش نمی‌شود.

۳) **مرزِ زمانی: حالتِ نمونه‌ای (`--limit`).** یک دورِ کامل روی ~۱۱٬۵۰۰ کانفیگ
   چند دقیقه شبکه می‌خواهد. `--limit N` همان کدِ `pipeline.py`/`googleready.py`
   را روی یک نمونهٔ **قابلِ بازتولید** (شuffle با seedِ ثابت) از `all/configs.txt`
   اجرا می‌کند. پیش‌فرضِ rounds در این حالت ۱ است (هر دور یک اجرای واقعی است) تا
   بودجهٔ شبکه کوچک بماند؛ `--rounds` آن را بازنویسی می‌کند. خلاصهٔ پایانی
   **صریح** می‌گوید اجرا محدود بوده، وگرنه کسی آن را «تأییدِ کامل» می‌پندارد.

نمونه‌ها:

    python -X utf8 scripts/run_all.py                        # کل زنجیره
    python -X utf8 scripts/run_all.py --limit 2000 --rounds 1 # نمونهٔ محدودِ مستند
    python -X utf8 scripts/run_all.py --quick                 # بدونِ آبشار و گوگل
    python -X utf8 scripts/run_all.py --skip-fetch            # روی دادهٔ موجود
    python -X utf8 scripts/run_all.py --with-validate         # + دروازهٔ کلاینتِ واقعی
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PY = sys.executable

#: seedِ نمونه‌گیریِ محدود — ثابت است تا دو اجرا با `--limit` یکسان، همان
#: ورودی را بسنجند (بازتولیدپذیری، نه شانس).
BOUNDED_SEED = 1337

BRAND = "brand"
FETCH = "aggregate"
CASCADE = "pipeline"
GOOGLE = "google"
DOCS = "docs"
VALIDATE = "validate"
TESTS = "tests"

MAX_LABEL = 11


def _script(*parts: str) -> str:
    return os.path.join(REPO, *parts)


# ──────────────────────────────────────────────────────────────────────────────
# ابزارِ سنجش (xray-knife)
# ──────────────────────────────────────────────────────────────────────────────

def find_validator() -> Optional[str]:
    """
    مسیرِ باینریِ xray-knife، یا `None`.

    ترتیب عمدی است: اول تصمیمِ صریحِ کاربر (`L3_XK_BIN`)، بعد `PATH` (همان
    قراردادِ CI که باینری را در `~/.local/bin` نصب می‌کند)، و آخر مسیرهای
    محلیِ مخزن که `.gitignore` پوشش می‌دهد. هیچ‌کدام از این‌ها «حدس» نیست:
    هر سه در مستنداتِ خودِ پروژه آمده‌اند.
    """
    explicit = os.environ.get("L3_XK_BIN", "").strip()
    if explicit:
        if os.path.isfile(explicit):
            return os.path.abspath(explicit)
        found = shutil.which(explicit)
        if found:
            return found

    found = shutil.which("xray-knife")
    if found:
        return found

    for base in (".cache/xray-knife", ".cache/validators", ".cache/validators/extract"):
        for name in ("xray-knife", "xray-knife.exe"):
            candidate = os.path.join(REPO, *base.split("/"), name)
            if os.path.isfile(candidate):
                return candidate
    return None


PRESENT = "present"


def _env(validator: Optional[str]) -> Dict[str, str]:
    """
    محیطِ فرزند: UTF-8 اجباری (کنسولِ ویندوز cp1256 است)، بدونِ بافر، و
    `L3_XK_BIN` فقط وقتی خودمان باینری پیدا کرده باشیم.
    """
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    if validator:
        env["L3_XK_BIN"] = validator
    return env


# ──────────────────────────────────────────────────────────────────────────────
# نمونه‌گیریِ محدود
# ──────────────────────────────────────────────────────────────────────────────

def write_bounded_sample(src: str, limit: int, out: str) -> Tuple[str, int, int]:
    """
    نمونهٔ محدودِ قابلِ بازتولید از `src` → (مسیر، تعدادِ نمونه، تعدادِ کل).

    چرا shuffleِ seedدار و نه «اولین N سطر» یا «هر k-ام سطر»: فایل بر اساسِ
    منبع مرتب است، پس هر دو روشِ ساده به یک ناحیهٔ خاص از فایل چسب می‌زنند.
    اندازه‌گیری شد: نمونهٔ gام (`configs[::step][:1000]`) صفر کانفیگِ کارکن
    داد، در حالی که نمونهٔ تصادفیِ هم‌اندازه ۵۸ کانفیگِ کارکن داشت — یعنی
    روشِ نمونه‌گیری خودش نتیجه را تعیین می‌کرد. seed ثابت، همان نمونه را در
    هر اجرا بازمی‌گرداند.
    """
    with open(src, "r", encoding="utf-8", errors="replace") as handle:
        lines = [ln.strip() for ln in handle.read().splitlines()]
    configs = [ln for ln in lines if ln and not ln.startswith("#")]
    total = len(configs)
    if limit <= 0 or limit >= total:
        return src, total, total

    order = list(range(total))
    random.Random(BOUNDED_SEED).shuffle(order)
    picked = sorted(order[:limit])          # ترتیبِ فایل حفظ می‌شود
    sample = [configs[i] for i in picked]

    dest_dir = os.path.join(out, ".cache")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, f"run_all_sample_{limit}.txt")
    with open(dest, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(sample) + "\n")
    return dest, len(sample), total


# ──────────────────────────────────────────────────────────────────────────────
# اجرا و پس‌شرط‌ها
# ──────────────────────────────────────────────────────────────────────────────

def _display(cmd: Sequence[str]) -> str:
    """فرمانِ قابلِ کپی‌پیست — مسیرهای داخلِ مخزن نسبی می‌شوند."""
    out: List[str] = []
    for part in cmd:
        if part == PY:
            out.append("python")
        elif part.startswith(REPO + os.sep):
            out.append(os.path.relpath(part, REPO))
        else:
            out.append(part)
    return " ".join(out)


def _run(name: str, cmd: Sequence[str], note: str, env: Dict[str, str],
         capture: bool) -> Tuple[int, float, str]:
    """یک مرحله را اجرا می‌کند. `capture` فقط برای مراحلی است که خروجی‌شان
    باید تجزیه شود (pipeline/google)؛ بقیه زنده به ترمینال می‌روند."""
    print("\n" + "─" * 78)
    print(f"▶ {name}  —  {note}")
    print(f"  $ {_display(cmd)}")
    print("─" * 78, flush=True)
    t0 = time.time()
    try:
        if capture:
            proc = subprocess.run(list(cmd), cwd=REPO, env=env,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
            text = (proc.stdout or b"").decode("utf-8", errors="replace")
            if text.strip():
                print(text.rstrip(), flush=True)
            rc = proc.returncode
        else:
            rc = subprocess.run(list(cmd), cwd=REPO, env=env).returncode
            text = ""
    except FileNotFoundError as exc:
        print(f"❌ {name}: cannot start — {exc}", flush=True)
        return 127, time.time() - t0, ""
    dt = time.time() - t0
    print(f"\n{'✅ rc=0' if rc == 0 else f'❌ rc={rc}'}  ({name}, {dt:.1f}s)", flush=True)
    return rc, dt, text


def check_pipeline(out: str) -> Tuple[bool, str]:
    """پس‌شرطِ آبشار: کدِ ۰ کافی نیست؛ باید `verified/` واقعاً پر شده باشد."""
    stats_path = os.path.join(out, "pipeline.json")
    if not os.path.isfile(stats_path):
        return False, "pipeline.json was not written"
    try:
        with open(stats_path, encoding="utf-8") as handle:
            st = json.load(handle)
    except (OSError, ValueError) as exc:
        return False, f"pipeline.json unreadable: {type(exc).__name__}"

    verified = int(st.get("verified") or 0)
    detail = (f"verified={verified} fast={st.get('fast')} secure={st.get('secure')} "
              f"top={st.get('top')} rounds={st.get('rounds')}")
    targets = os.path.join(out, "verified", "configs.txt")
    non_empty = os.path.isfile(targets) and os.path.getsize(targets) > 0
    if verified < 1 or not non_empty:
        return False, (f"{detail} — no config survived L3 "
                       f"(network-side result, not a code fault)")
    return True, detail


def _last_json_object(text: str) -> Optional[Dict[str, Any]]:
    """آخرین شیءِ JSON در خروجیِ googleready (خطِ خلاصه)."""
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def check_google(out: str, text: str) -> Tuple[bool, str]:
    """
    پس‌شرطِ گوگل: `googleready.py` برای `skipped`/`empty` هم ۰ برمی‌گرداند،
    پس فقط `status == "published"` یعنی واقعاً اجرا شد و خروجی داد.
    """
    obj = _last_json_object(text)
    if obj is None:
        return False, "no JSON summary in googleready output"
    status = str(obj.get("status") or "?")
    detail = (f"status={status} input={obj.get('input')} ready={obj.get('ready')} "
              f"panel_ready={obj.get('panel_ready')} fail={obj.get('fail')} "
              f"unknown={obj.get('unknown')}")
    if status != "published":
        reason = str(obj.get("reason") or "").strip()
        return False, f"{detail}" + (f" — {reason}" if reason else "")
    targets = os.path.join(out, "google", "configs.txt")
    if not (os.path.isfile(targets) and os.path.getsize(targets) > 0):
        return False, f"{detail} — status says published but google/configs.txt is empty"
    return True, detail


# ──────────────────────────────────────────────────────────────────────────────
# نقشهٔ مراحل
# ──────────────────────────────────────────────────────────────────────────────

class Stage:
    def __init__(self, name: str, make: Callable[[], List[str]], note: str,
                 capture: bool = False,
                 check: Optional[Callable[[str], Tuple[bool, str]]] = None) -> None:
        self.name = name
        self.make = make
        self.note = note
        self.capture = capture
        self.check = check


def build_plan(args: argparse.Namespace, state: Dict[str, Any]) -> List[Stage]:
    """
    فهرستِ مرتبِ مراحل. `--quick` فقط آبشار/گوگل را حذف می‌کند، نه برند و نه
    docs را — چون docs همان چیزی است که کاربر می‌بیند.
    """
    out = os.path.abspath(args.out)
    plan: List[Stage] = []

    plan.append(Stage(
        BRAND,
        lambda: [PY, "-X", "utf8", _script("scripts", "brand.py"), "--check"],
        "brand drift gate (must be zero)"))

    if args.skip_fetch:
        print("⏭️  aggregate: skipped by --skip-fetch (using existing files on disk)")
    else:
        plan.append(Stage(
            FETCH,
            lambda: [PY, "-X", "utf8", _script("scripts", "aggregate.py"), "--out", out],
            "fetch 13 sources → all/ heavy/ light/ protocols/"))

    if args.quick:
        print("⏭️  pipeline + google: skipped by --quick")
    else:
        plan.append(Stage(
            CASCADE,
            lambda: [PY, "-X", "utf8", _script("scripts", "pipeline.py"),
                     state["input"], "--out", out,
                     "--json", os.path.join(out, "pipeline.json")]
            + (["--rounds", str(state["rounds"])] if state.get("rounds") else []),
            "L0→L3 cascade → verified/ fast/ secure/ top100.txt",
            capture=True,
            check=lambda text: check_pipeline(out)))

        plan.append(Stage(
            GOOGLE,
            lambda: [PY, "-X", "utf8", _script("scripts", "googleready.py"),
                     "--out", out,
                     "--cascade-outcome", state["cascade_outcome"]]
            + (["--rounds", str(state["rounds"])] if state.get("rounds") else []),
            "Google-Ready layer → google/",
            capture=True,
            check=lambda text: check_google(out, text)))

    if args.with_validate:
        plan.append(Stage(
            VALIDATE,
            lambda: [PY, "-X", "utf8", _script("scripts", "validate.py"), "--out", out],
            "real-client gate over produced subscriptions"))

    if args.with_tests:
        plan.append(Stage(
            TESTS,
            lambda: [PY, "-X", "utf8", _script("scripts", "test_pipeline.py")],
            "repository invariant suite"))

    plan.append(Stage(
        DOCS,
        lambda: [PY, "-X", "utf8", _script("docs-src", "build.py")],
        "render README×4 + docs/ (dashboard, pages, sitemap)"))
    return plan


# ──────────────────────────────────────────────────────────────────────────────
# خلاصه
# ──────────────────────────────────────────────────────────────────────────────

def _summary(rows: Sequence[Tuple[str, bool, int, float, str]], out: str,
             bounded: Optional[Tuple[int, int, int, Optional[int]]]) -> None:
    print("\n" + "═" * 78)
    print("خلاصهٔ اجرا")
    print("═" * 78)
    if bounded:
        sampled, total, rounds_used = bounded
        rounds_text = f"، L3 rounds={rounds_used}" if rounds_used else ""
        print(f"⚠️  اجرای محدود (BOUNDED): {sampled} از {total} کانفیگ{rounds_text} — "
              f"seed={BOUNDED_SEED}")
        print("   این یک اعتبارسنجیِ کامل نیست؛ فقط همان کدِ مراحل روی یک نمونه اجرا شد.")
        print("─" * 78)
    for name, ok, rc, dt, detail in rows:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {name:<{MAX_LABEL}} rc={rc:<3} {dt:>7.1f}s" +
              (f"   {detail}" if detail else ""))
    print("─" * 78)
    artifacts = [
        ("all/configs.txt", "همهٔ کانفیگ‌ها"),
        ("all/clash.yaml", "Clash"),
        ("all/singbox.json", "Sing-Box"),
        ("verified/configs.txt", "تأییدشده با آزمونِ واقعی"),
        ("fast/configs.txt", "سریع"),
        ("secure/configs.txt", "با محرمانگیِ پیشرو"),
        ("top100.txt", "۱۰۰ کانفیگِ برتر"),
        ("google/configs.txt", "Google-Ready"),
        ("index.json", "آمارِ انتشار"),
        ("health.json", "سلامتِ منابع"),
        ("docs/index.html", "صفحهٔ وب"),
    ]
    # docs همیشه در مخزن ساخته می‌شود (`docs-src/build.py` مسیر ثابت دارد)، حتی
    # وقتی `--out` جای دیگری باشد — پس نباید با `out` سنجیده شود.
    print("خروجی‌ها (اگر ساخته شده باشند):")
    for rel, label in artifacts:
        base = REPO if rel.startswith("docs/") else out
        path = os.path.join(base, *rel.split("/"))
        size = os.path.getsize(path) if os.path.isfile(path) else -1
        if size >= 0:
            print(f"  • {rel:<24} {size:>10,} B   {label}")
        else:
            print(f"  • {rel:<24} {'—':>10}     {label} (ساخته نشد)")
    print("─" * 78)
    print("پیش‌نمایشِ صفحه:  python -X utf8 -m http.server 8000 --directory docs")
    print("═" * 78)


# ──────────────────────────────────────────────────────────────────────────────

def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="run the whole project with one command",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=REPO, help="output directory (default: repo root)")
    ap.add_argument("--quick", action="store_true",
                    help="skip the network cascade (pipeline + google); keep fetch and docs")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="do not re-fetch sources; run downstream stages on existing files")
    ap.add_argument("--limit", type=int, default=0, metavar="N",
                    help="bounded run: run the same pipeline/google code on a seeded "
                         "sample of N configs from all/configs.txt (default rounds: 1)")
    ap.add_argument("--rounds", type=int, default=None,
                    help="L3/google rounds (default: pipeline's own constant; 1 with --limit)")
    ap.add_argument("--with-validate", action="store_true",
                    help="also run scripts/validate.py (needs sing-box/mihomo; else skipped)")
    ap.add_argument("--with-tests", action="store_true",
                    help="also run scripts/test_pipeline.py")
    args = ap.parse_args(argv)

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)

    state: Dict[str, Any] = {
        "input": os.path.join(out, "all", "configs.txt"),
        "cascade_outcome": "success",
        "rounds": args.rounds,
    }

    bounded: Optional[Tuple[int, int, int, Optional[int]]] = None
    if args.limit:
        src = os.path.join(out, "all", "configs.txt")
        if not os.path.isfile(src):
            print(f"❌ --limit needs {os.path.relpath(src, REPO)}; run without "
                  f"--skip-fetch first or fetch once.")
            return 2
        if args.rounds is None:
            state["rounds"] = 1
        dest, sampled, total = write_bounded_sample(src, args.limit, out)
        state["input"] = dest
        bounded = (sampled, total, state["rounds"] or 0)
        print(f"🔬 bounded run: {sampled} of {total} config lines "
              f"(seed={BOUNDED_SEED}, rounds={state['rounds']}) → "
              f"{os.path.relpath(dest, REPO)}")

    validator = find_validator()
    if validator:
        print(f"🧰 validator: {validator}")
    else:
        print("⚠️  validator: xray-knife not found (L3 and google cannot run for real)")
        print("   put it at .cache/xray-knife/xray-knife(.exe), on PATH, or set L3_XK_BIN")
    env = _env(validator)

    plan = build_plan(args, state)

    print("═" * 78)
    print(f"🚀 full project run → out={out}")
    print(f"   {len(plan)} stage(s), python={PY}")
    print("═" * 78)

    rows: List[Tuple[str, bool, int, float, str]] = []
    t0 = time.time()
    for stage in plan:
        rc, dt, text = _run(stage.name, stage.make(), stage.note, env, stage.capture)
        detail = ""
        if stage.check is not None:
            ok, detail = stage.check(text)
        else:
            ok = rc == 0
        rows.append((stage.name, ok, rc, dt, detail))
        if ok:
            continue

        # ── شکست: پیامِ عملی، و تصمیمِ درست برای بقیهٔ زنجیره ──────────────
        if stage.name == FETCH:
            print("\n⛔ aggregate failed — stopping here: the later stages would")
            print("   otherwise run on stale or partial data. Fix the fetch first")
            print("   (see health.json) or re-run with --skip-fetch.")
            _summary(rows, out, bounded)
            return rc if rc else 1
        if stage.name == CASCADE:
            # همان قراردادِ CI: بقیهٔ زنجیره ادامه می‌یابد، ولی «گوگل» صادقانه
            # skipped می‌شود — کدِ ۰ با صفر خروجی هم شکست حساب می‌شود.
            state["cascade_outcome"] = "failed"
            print("⚠️  cascade produced no verified configs — google stage becomes "
                  "'skipped' (cascade-outcome=failed)")
        if stage.name == GOOGLE:
            print("⚠️  google stage did not publish — see status/reason above")

    total_s = time.time() - t0
    _summary(rows, out, bounded)
    print(f"\n⏱️  total {total_s:.1f}s")
    return 0 if all(ok for _, ok, _, _, _ in rows) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
