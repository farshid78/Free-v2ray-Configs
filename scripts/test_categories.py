# -*- coding: utf-8 -*-
"""
test_categories.py — آزمونِ دسته‌های **منتشرشده** با دادهٔ واقعی، نه ورودیِ مصنوعی.

چرا این فایل وجود دارد
──────────────────────
تست‌های `test_pipeline.py` منطق را با ورودیِ ساختگی می‌سنجند؛ ولی باگِ واقعیِ
این پروژه در **مرزِ فایل و کد** بود: `top100.txt` فقط سرآیندِ کامنت داشت،
`load_configs` همان خطوطِ `#` را کانفیگ می‌شمرد و عددِ «۹» به کاربر می‌رسید.
هیچ تستی فایلِ منتشرشده را در برابرِ تعریفش نمی‌گذاشت، پس باگ خاموش ماند.

این فایل همان مرز را می‌بندد: هر سبد با فایلِ واقعیِ همین مخزن سنجیده می‌شود.

اجرا:
    python -m pytest scripts/test_categories.py -q
    python scripts/test_categories.py
"""
from __future__ import annotations

import base64
import os
import re
import sys
from urllib.parse import parse_qs, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import core  # noqa: E402
import pipeline  # noqa: E402

BUCKETS = {
    "verified": os.path.join(ROOT, "verified", "configs.txt"),
    "fast": os.path.join(ROOT, "fast", "configs.txt"),
    "secure": os.path.join(ROOT, "secure", "configs.txt"),
    "all": os.path.join(ROOT, "all", "configs.txt"),
    "heavy": os.path.join(ROOT, "heavy", "configs.txt"),
    "light": os.path.join(ROOT, "light", "configs.txt"),
    "google": os.path.join(ROOT, "google", "configs.txt"),
}
TOP = os.path.join(ROOT, "top100.txt")
BRAND = "@farshid78"

#: قالب‌ها یکسان نیستند: «— VERIFIED — 12 configs» و «— TOP 12 — sorted …».
HEADER_COUNT = re.compile(
    r"—\s*(VERIFIED|FAST|SECURE|TOP|ALL|HEAVY|LIGHT|GOOGLE)\s*—?\s*(\d+)\b")


class _SkipTest(Exception):
    """محیطِ تست دادهٔ لازم را ندارد (مثلاً سبدِ google پیش از CI)."""


def _lines(path: str) -> list[str]:
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines()


def _real(path: str) -> list[str]:
    """خطوطی که واقعاً کانفیگ‌اند: نه خالی، نه سرآیندِ `#`."""
    return [ln.strip() for ln in _lines(path)
            if ln.strip() and not ln.lstrip().startswith("#")]


def _header(path: str) -> str:
    """خطِ شمارنده (نه نخستین کامنت، که سرآیندِ Hiddify است)."""
    for ln in _lines(path)[:30]:
        if ln.startswith("#") and HEADER_COUNT.search(ln):
            return ln
    return ""


def _declared(path: str) -> int | None:
    m = HEADER_COUNT.search(_header(path))
    return int(m.group(2)) if m else None


def _scheme(link: str) -> str:
    return link.split("://", 1)[0].strip().lower() if "://" in link else ""


def _tls_of(link: str) -> str:
    """همان مقداری که L3 به `is_secure` می‌دهد: برای vmess از JSONِ base64."""
    scheme = _scheme(link)
    if scheme == "vmess":
        try:
            import json
            raw = link.split("://", 1)[1].split("#", 1)[0].strip()
            raw += "=" * (-len(raw) % 4)
            obj = json.loads(base64.b64decode(raw).decode("utf-8", "replace"))
            return str(obj.get("tls") or obj.get("security") or "")
        except Exception:  # noqa: BLE001
            return ""
    try:
        q = parse_qs(urlsplit(link).query)
    except ValueError:
        return ""
    for key in ("security", "tls"):
        if q.get(key):
            return q[key][0]
    # trojan بدونِ پارامتر هم TLS اجباری دارد (RFCِ خودش)؛ بقیه بی‌پارامتر نه.
    return "tls" if scheme == "trojan" else ""


def test_every_published_line_is_a_config_not_a_header() -> None:
    """باگِ شمارش: هیچ خطِ `#` نباید کانفیگ حساب شود."""
    for name, path in BUCKETS.items():
        if not os.path.isfile(path):
            continue
        head = _header(path)
        assert head, f"{name}: the count header is missing"
        for ln in _real(path):
            assert "://" in ln, f"{name}: non-URI line leaked into the bucket: {ln[:80]!r}"


def test_header_count_matches_the_file_body() -> None:
    """عددی که در سرآیند می‌نویسیم باید همان تعدادِ خطِ معتبر باشد."""
    for name, path in BUCKETS.items():
        if not os.path.isfile(path):
            continue
        n = len(_real(path))
        declared = _declared(path)
        assert declared is not None, f"{name}: no '— <CAT> — N configs' header"
        assert declared == n, (
            f"{name}: header says {declared} configs but the file holds {n} real lines")


def test_top100_is_between_1_and_100_and_matches_its_lines() -> None:
    """Done-when: top100 بین ۱ و ۱۰۰ و برابرِ خطوطِ معتبرِ همان فایل."""
    n = len(_real(TOP))
    declared = _declared(TOP)
    assert declared is not None, "top100.txt has no '— TOP N' header"
    assert declared == n, f"top100.txt header says {declared} but holds {n} lines"
    assert 1 <= n <= 100, f"top100.txt must hold 1..100 configs, holds {n}"
    assert len(set(_real(TOP))) == n, "top100.txt contains duplicates"


def _keys(path: str) -> set[str]:
    """کلیدِ dedup، نه رشتهٔ خام: ریمارکِ هر سبد عمداً متفاوت است."""
    return {core.dedup_key(ln) for ln in _real(path) if core.dedup_key(ln)}


def test_categories_are_subsets_of_their_source() -> None:
    """هر سبد باید از سبدِ مادرش بیاید، نه از فایلِ دیگر."""
    top = _keys(TOP)
    verified = _keys(BUCKETS["verified"])
    allcfg = _keys(BUCKETS["all"])
    assert top <= verified, f"top100 has {len(top - verified)} config(s) outside verified/"
    for name in ("fast", "secure"):
        bucket = _keys(BUCKETS[name])
        assert bucket <= verified, (
            f"{name}/ has {len(bucket - verified)} config(s) outside verified/")
    if os.path.isfile(BUCKETS["google"]):
        google = _keys(BUCKETS["google"])
        assert google <= verified, (
            f"google/ has {len(google - verified)} config(s) outside verified/")
    for name in ("heavy", "light"):
        bucket = _keys(BUCKETS[name])
        assert bucket <= allcfg, f"{name}/ has {len(bucket - allcfg)} config(s) outside all/"


def test_fast_is_not_larger_than_verified() -> None:
    """تعریفِ fast: verified + میانهٔ تأخیر < ۸۰۰ms ⇒ هرگز بزرگ‌تر از verified نیست."""
    fast = _real(BUCKETS["fast"])
    verified = _real(BUCKETS["verified"])
    assert len(fast) <= len(verified), (
        f"fast ({len(fast)}) is larger than verified ({len(verified)})")
    assert pipeline.FAST_THRESHOLD_MS == 800, (
        f"FAST_THRESHOLD_MS drifted to {pipeline.FAST_THRESHOLD_MS}")


def test_secure_entries_really_have_forward_secrecy() -> None:
    """تعریفِ secure: verified + forward secrecy + گواهی غیرفعال‌نشده."""
    for ln in _real(BUCKETS["secure"]):
        assert pipeline.is_secure(ln, _tls_of(ln)), (
            f"secure/ contains a link without forward secrecy: {ln[:90]!r}")


def test_published_headers_carry_this_repo_identity() -> None:
    """هویت: هیچ سرآیند/بدنه‌ای نباید هندل یا ریپوی پروژهٔ دیگر را داشته باشد."""
    files = [TOP] + [p for p in BUCKETS.values() if os.path.isfile(p)]
    for path in files:
        text = "\n".join(_lines(path))
        assert "jojo_vpn" not in text and "jojo_config" not in text, (
            f"{os.path.relpath(path, ROOT)} still carries the old identity")
        head = _header(path)
        assert BRAND in head, (
            f"{os.path.relpath(path, ROOT)} header lacks {BRAND}: {head!r}")


def test_bot_counts_match_the_published_files() -> None:
    """درخواستِ کاربر با عددِ فایل یکی باشد — همان باگی که این تست را ساخت."""
    try:
        from bot.utils import load_configs  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        raise _SkipTest(f"bot package is not importable here: {type(exc).__name__}: {exc}")
    for name, path in BUCKETS.items():
        if name == "google" and not os.path.isfile(path):
            assert load_configs(name) == [], "load_configs('google') must return [] when absent"
            continue
        if not os.path.isfile(path):
            raise _SkipTest(f"{name}/ is not published in this checkout")
        assert len(load_configs(name)) == len(_real(path)), (
            f"bot reports {len(load_configs(name))} for {name}/ but the file holds "
            f"{len(_real(path))} real lines")
    assert len(load_configs("top100")) == len(_real(TOP)), (
        "bot's top100 count differs from top100.txt")


def test_brand_defaults_come_from_the_repo_identity() -> None:
    """پیش‌فرضِ برند از GH_OWNER می‌آید، نه از پروژهٔ دیگر."""
    import brand
    b = brand.values()
    assert b["brand"] == BRAND, f"default brand is {b['brand']!r}, expected {BRAND}"
    assert b["repo"] == "Free-v2ray-Configs"
    assert b["raw"] == "https://raw.githubusercontent.com/farshid78/Free-v2ray-Configs/main"


def _run_all() -> int:
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ✅ {name}")
        except _SkipTest as e:
            skipped += 1
            print(f"  ⏭️ {name}\n       {e}")
        except AssertionError as e:
            failed += 1
            print(f"  ❌ {name}\n       {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  💥 {name}\n       {type(e).__name__}: {e}")
    tail = f"\n{len(tests) - failed - skipped}/{len(tests)} passed"
    if skipped:
        tail += f", {skipped} skipped (environment)"
    print(tail)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
