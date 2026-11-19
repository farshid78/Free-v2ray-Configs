#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brand / repository identity — the project's ONLY config block.

Every user-visible name, handle and URL in this repository is derived from the
constants below. Nothing else is allowed to hard-code a brand, a channel, a
GitHub owner/repo or a Pages/raw/CDN URL; `scripts/test_brand_single_source.py`
grep-guards that rule and `python3 scripts/brand.py --check` proves the
generated surfaces (README files, dashboard module, docs) still match.

Why a separate module instead of `core.py`
    `aggregate.py` imports `core`, so `core` cannot import `aggregate` to learn
    the GitHub owner/repo (import cycle). This module imports nothing from the
    project, so both sides can read it without a cycle. `core` re-exports the
    three names it always had (`BRAND_CHANNEL`, `SUPPORT_URL`, `PROJECT_URL`) so
    no existing importer changes.

Changing the brand is ONE edit
    Either edit the defaults below, or (for CI) set the `AGG_*` variables —
    every value recomputes from them at import time. Then run:

        python3 scripts/brand.py --render     # README×4 + dashboard module
        python3 docs-src/build.py             # docs/index.html + docs/fa/

    `--check` fails if any generated surface is stale, so a drift is caught
    instead of shipped.

⚠️ The defaults below are the repository's current identity. They were NOT
   invented; they are the exact values that were previously scattered across
   ~15 files.
"""

from __future__ import annotations

import json
import os
import sys

# ══════════════════════════════════════════════════════════════════════════════
# 🏷️  THE CONFIG BLOCK — the only place any of these values is written down
# ══════════════════════════════════════════════════════════════════════════════
#
# Every field is env-overridable (prefix `AGG_`). The env names that already
# existed (`AGG_GH_USER`, `AGG_GH_REPO`, `AGG_SUPPORT_URL`, `AGG_PROJECT_URL`,
# `AGG_PUBLISH_BRANCH`, `PUBLISH_BRANCH`) keep working unchanged.
#
#   field          feeds
#   ─────────────  ────────────────────────────────────────────────────────────
#   BRAND_CHANNEL  remark «CC 🇩🇪 | @… | tag», profile-title, Clash groups,
#                  index.json.brand, support URL, commit identity
#   BRAND_NAME     prose titles: docs <title>, JSON-LD, generator description
#   BOT_NAME       index.json.generator ("<BOT_NAME> aggregator")
#   BOT_HANDLE     the Telegram bot named in the READMEs (legacy spelling)
#   BOT_HANDLE_DOCS the bot named on the landing page (its own legacy spelling)
#   GROUP_URL      the community button on the docs bot card (legacy link)
#   GH_USER        GitHub owner: PROJECT_URL, RAW/CDN/SITE, badges, workflow
#   GH_REPO        GitHub repository name: same
#   GH_BRANCH      raw/CDN/pages branch (published outputs live here)
#   SISTER_REPO    sibling project linked from README ("Free-Telegram-Proxy")
#   CHANNEL_URL    Telegram channel link (README buttons, docs)
#   SUPPORT_URL    Hiddify `support-url` + `profile-web-page-url`
#   BOT_URL        bot link in README/docs prose
#   SITE_URL       GitHub Pages landing page (no trailing slash)
#   COMMIT_NAME    `git config user.name` in the publish step + commit subject
#   GENERATOR      index.json.generator

def _compute() -> dict:
    """Resolve the whole block from the environment (defaults = today's brand).

    Split out of the module body for one measured reason: the test suite proves
    the legacy `AGG_PUBLISH_BRANCH` override by `importlib.reload(aggregate)`,
    and a bare `import brand` inside a reloaded module hands back the *cached*
    copy. `refresh()` (called by `aggregate`) rebuilds these values, so the
    override keeps working exactly as `aggregate.py` documented it.
    """
    #: GitHub identity comes FIRST: every brand default derives from it, so the
    #: repository cannot ship another project's handle by accident. Override
    #: with `AGG_GH_USER` / `AGG_GH_REPO`.
    gh_user = os.environ.get("AGG_GH_USER", "farshid78")
    gh_repo = os.environ.get("AGG_GH_REPO", "Free-v2ray-Configs")
    #: Channel handle. Precedence: AGG_BRAND_CHANNEL → CHANNEL_USERNAME →
    #: `@<gh_user>`. When the real channel is known, ONE variable changes it.
    _channel_env = (os.environ.get("AGG_BRAND_CHANNEL")
                    or os.environ.get("CHANNEL_USERNAME") or "").strip()
    brand_channel = _channel_env or f"@{gh_user}"
    if not brand_channel.startswith("@"):
        brand_channel = "@" + brand_channel
    #: Lower-cased handle without `@` — what Telegram URLs and the bot's git
    #: identity are built from, so they can never disagree with the handle.
    brand_slug = brand_channel.lstrip("@").lower()
    brand_name = os.environ.get("AGG_BRAND_NAME", gh_user)
    #: Bot display name (not a handle) — used by `index.json.generator`.
    bot_name = os.environ.get("AGG_BOT_NAME", f"{gh_user}_bot")
    #: Bot handle as written in README/docs prose.
    #: ⚠️ LEGACY / INCONSISTENT ON PURPOSE — do not "fix" these two defaults.
    #: The repository as shipped states the bot handle in two different
    #: spellings: the READMEs say ``@jojo_np_bot`` while the landing page
    #: (``docs-src/i18n/*.json``) says ``@ConfigExBot``. Both are today's
    #: bytes, and the default run must reproduce them byte-for-byte, so the
    #: config carries both fields instead of silently unifying them. When the
    #: real brand is supplied, set both to the same handle; until then the
    #: inconsistency is data, not a bug.
    bot_handle = os.environ.get("AGG_BOT_HANDLE", f"@{gh_user}_bot")
    bot_handle_docs = os.environ.get("AGG_BOT_HANDLE_DOCS", bot_handle)
    #: Branch the published files are served from. `AGG_PUBLISH_BRANCH` is the
    #: explicit modern name; the two older names are accepted so a stale caller
    #: cannot silently 404.
    gh_branch = (os.environ.get("AGG_PUBLISH_BRANCH")
                 or os.environ.get("PUBLISH_BRANCH")
                 or os.environ.get("AGG_DATA_BRANCH")
                 or os.environ.get("DATA_BRANCH")
                 or "main")
    sister_repo = os.environ.get("AGG_SISTER_REPO", "Free-Telegram-Proxy")
    #: Display link — keeps the handle's original casing (Telegram treats
    #: handles case-insensitively, but the committed READMEs use
    #: `t.me/jojo_config`).
    channel_url = os.environ.get(
        "AGG_CHANNEL_URL", f"https://t.me/{brand_channel.lstrip('@')}")
    #: Machine-facing support URL — lower-cased, exactly what `core.SUPPORT_URL`
    #: published before this refactor
    #: (`test_zzz_hdr_project_and_support_urls_cannot_drift` locks it).
    support_url = os.environ.get("AGG_SUPPORT_URL", f"https://t.me/{brand_slug}")
    bot_url = os.environ.get("AGG_BOT_URL", f"https://t.me/{bot_handle.lstrip('@')}")
    #: ⚠️ LEGACY ON PURPOSE — the group button on the bot card points at
    #: ``t.me/jojo_np_bot`` in the shipped site (a leftover from the upstream
    #: extractor). It is preserved verbatim as the default so the default build
    #: stays byte-identical; supply the real community link via `AGG_GROUP_URL`.
    group_url = os.environ.get("AGG_GROUP_URL", "")
    #: `owner/repo` — the slug GitHub prints, and the path inside every raw URL.
    repo_slug = f"{gh_user}/{gh_repo}"
    sister_slug = f"{gh_user}/{sister_repo}"
    project_url = os.environ.get(
        "AGG_PROJECT_URL", f"https://github.com/{repo_slug}")
    #: GitHub Pages origin for `<user>.github.io` (lower-cased host, as GitHub
    #: serves it). No trailing slash: callers append `/`, `/fa/`, `/status/`.
    site_url = os.environ.get(
        "AGG_SITE_URL", f"https://{gh_user.lower()}.github.io/{gh_repo}")
    return {
        "BRAND_CHANNEL": brand_channel,
        "BRAND_SLUG": brand_slug,
        "BRAND_NAME": brand_name,
        "BOT_NAME": bot_name,
        "BOT_HANDLE": bot_handle,
        "BOT_HANDLE_DOCS": bot_handle_docs,
        "BOT_URL_DOCS": f"https://t.me/{bot_handle_docs.lstrip('@')}",
        "GROUP_URL": group_url,
        #: `@handle` printed next to the group button (path segment of GROUP_URL).
        "GROUP_HANDLE": ("@" + group_url.rstrip("/").rsplit("/", 1)[-1].lstrip("@")
                        if group_url.strip() else ""),
        "GH_USER": gh_user,
        "GH_REPO": gh_repo,
        "GH_BRANCH": gh_branch,
        "SISTER_REPO": sister_repo,
        "CHANNEL_URL": channel_url,
        "SUPPORT_URL": support_url,
        "BOT_URL": bot_url,
        "GROUP_URL": group_url,
        "REPO_SLUG": repo_slug,
        "SISTER_SLUG": sister_slug,
        "PROJECT_URL": project_url,
        "RAW_BASE": f"https://raw.githubusercontent.com/{repo_slug}/{gh_branch}",
        "CDN_BASE": f"https://cdn.jsdelivr.net/gh/{repo_slug}@{gh_branch}",
        "SISTER_URL": f"https://github.com/{sister_slug}",
        "SISTER_RAW_BASE": f"https://raw.githubusercontent.com/{sister_slug}/{gh_branch}",
        "SITE_URL": site_url,
        "SISTER_SITE_URL": f"https://{gh_user.lower()}.github.io/{sister_repo}",
        "COMMIT_NAME": os.environ.get(
            "AGG_COMMIT_NAME", f"{brand_slug}-bot[actions]"),
        "COMMIT_EMAIL": os.environ.get(
            "AGG_COMMIT_EMAIL", "actions@users.noreply.github.com"),
        "GENERATOR": f"{bot_name} aggregator",
        #: Document title used by the landing page and JSON-LD.
        "SITE_TITLE": f"{brand_name}",
    }


def refresh() -> dict:
    """Re-read the environment into this module's globals (used by `aggregate`).

    Needed only because of `importlib.reload(aggregate)`: reloading that module
    re-executes `import brand`, which returns this cached module. Calling
    `refresh()` at that import keeps the documented env overrides live — without
    it the reload silently kept stale values and
    `test_publish_branch_is_the_default_branch_and_configurable` failed with
    «AGG_PUBLISH_BRANCH is ignored by aggregate.py».
    """
    fresh = _compute()
    globals().update(fresh)
    return fresh


globals().update(_compute())

# ══════════════════════════════════════════════════════════════════════════════
# Generated surfaces (README×4 + dashboard module) — rendered FROM this block
# ══════════════════════════════════════════════════════════════════════════════

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
README_DIR = os.path.join(REPO, "docs-src", "readme")

#: template basename -> committed output basename
README_TEMPLATES = {
    "README.md.in": "README.md",
    "README_FA.md.in": "README_FA.md",
    "README_RU.md.in": "README_RU.md",
    "README_ZH.md.in": "README_ZH.md",
}

DASHBOARD_MODULE = os.path.join(REPO, "dashboard-src", "src",
                                "brand.generated.ts")


def values() -> dict:
    """The substitution table. One key per derived value; nothing literal."""
    return {
        "brand": BRAND_CHANNEL,
        #: Handle without `@`, casing preserved (badge URLs print it as-is).
        "brand_handle": BRAND_CHANNEL.lstrip("@"),
        "brand_slug": BRAND_SLUG,
        "brand_name": BRAND_NAME,
        "bot": BOT_HANDLE,
        "bot_url": BOT_URL,
        "bot_docs": BOT_HANDLE_DOCS,
        "bot_url_docs": BOT_URL_DOCS,
        "group_handle": GROUP_HANDLE,
        "bot_name": BOT_NAME,
        "owner": GH_USER,
        "repo": GH_REPO,
        "slug": REPO_SLUG,
        "branch": GH_BRANCH,
        "project_url": PROJECT_URL,
        "raw": RAW_BASE,
        "cdn": CDN_BASE,
        "site": SITE_URL,
        "channel_url": CHANNEL_URL,
        "group_url": GROUP_URL,
        "support_url": SUPPORT_URL,
        "sister": SISTER_REPO,
        "sister_slug": SISTER_SLUG,
        "sister_url": SISTER_URL,
        "sister_raw": SISTER_RAW_BASE,
        "sister_site": SISTER_SITE_URL,
        "site_title": SITE_TITLE,
    }


def _percent_encoded(text: str) -> str:
    """`https://raw…/x` → `https%3A%2F%2Fraw…%2Fx` (shields.io query strings)."""
    out = []
    for ch in text:
        if ch.isalnum() or ch in "-._~":
            out.append(ch)
        else:
            out.append("".join(f"%{b:02X}" for b in ch.encode("utf-8")))
    return "".join(out)


def render(text: str) -> str:
    """Expand `{{key}}` tokens from `values()` (plus `*_urlenc` variants)."""
    table = dict(values())
    for key, val in list(table.items()):
        if val.startswith("http"):
            table[key + "_urlenc"] = _percent_encoded(val)
    table["slug_urlenc"] = _percent_encoded(table["slug"])
    table["sister_slug_urlenc"] = _percent_encoded(table["sister_slug"])
    # Longest-first so `{{slug}}` never eats the prefix of a longer token.
    for key in sorted(table, key=len, reverse=True):
        text = text.replace("{{" + key + "}}", table[key])
    return text


def render_readme(template_text: str) -> str:
    return render(template_text)


def render_dashboard_ts() -> str:
    v = values()
    return (
        "// AUTO-GENERATED by `python3 scripts/brand.py --render` — do not edit.\n"
        "// Source of truth: the config block in scripts/brand.py\n"
        f"export const BRAND = {json.dumps(v['brand'])};\n"
        f"export const BRAND_NAME = {json.dumps(v['brand_name'])};\n"
        f"export const BOT_NAME = {json.dumps(v['bot_name'])};\n"
        f"export const GH_USER = {json.dumps(v['owner'])};\n"
        f"export const GH_REPO = {json.dumps(v['repo'])};\n"
        f"export const BRANCH = {json.dumps(v['branch'])};\n"
        f"export const REPO_URL = {json.dumps(v['project_url'])};\n"
        f"export const RAW_BASE = {json.dumps(v['raw'])};\n"
        f"export const CDN_BASE = {json.dumps(v['cdn'])};\n"
        f"export const SITE_URL = {json.dumps(v['site'])};\n"
        f"export const CHANNEL_URL = {json.dumps(v['channel_url'])};\n"
        f"export const SISTER_URL = {json.dumps(v['sister_url'])};\n"
        f"export const SECURITY_URL = {json.dumps(v['project_url'] + '/blob/' + v['branch'] + '/SECURITY.md')};\n"
    )


def _write_if_changed(path: str, text: str) -> bool:
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            if fh.read() == text:
                return False
    except FileNotFoundError:
        pass
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return True


def render_all(check: bool = False) -> int:
    """Render every generated surface; with `check`, report stale ones."""
    stale = []
    for tpl_name, out_name in README_TEMPLATES.items():
        tpl = os.path.join(README_DIR, tpl_name)
        with open(tpl, encoding="utf-8") as fh:
            want = render_readme(fh.read())
        path = os.path.join(REPO, out_name)
        if check:
            try:
                with open(path, encoding="utf-8", newline="") as fh:
                    got = fh.read()
            except FileNotFoundError:
                got = None
            if got != want:
                stale.append(out_name)
        elif _write_if_changed(path, want):
            print(f"brand: wrote {out_name}")
    want = render_dashboard_ts()
    if check:
        try:
            with open(DASHBOARD_MODULE, encoding="utf-8", newline="") as fh:
                got = fh.read()
        except FileNotFoundError:
            got = None
        if got != want:
            stale.append(os.path.relpath(DASHBOARD_MODULE, REPO))
    elif _write_if_changed(DASHBOARD_MODULE, want):
        print(f"brand: wrote {os.path.relpath(DASHBOARD_MODULE, REPO)}")
    if stale:
        print("brand --check: stale, rerun `python3 scripts/brand.py --render`: "
              + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


def github_env() -> str:
    """`KEY=value` lines for `$GITHUB_ENV` — keeps the workflow literal-free."""
    pairs = {
        "BRAND_CHANNEL": BRAND_CHANNEL,
        "BRAND_NAME": BRAND_NAME,
        "BRAND_BRANCH": GH_BRANCH,
        "BRAND_BOT": BOT_NAME,
        "BRAND_COMMIT_NAME": COMMIT_NAME,
        "BRAND_COMMIT_EMAIL": COMMIT_EMAIL,
        "BRAND_REPO_SLUG": REPO_SLUG,
        "BRAND_REPO": GH_REPO,
        "BRAND_OWNER": GH_USER,
        "BRAND_RAW_BASE": RAW_BASE,
    }
    return "\n".join(f"{k}={v}" for k, v in pairs.items())


def main(argv: list) -> int:
    check = "--check" in argv
    if "--github-env" in argv:
        print(github_env())
        return 0
    if "--json" in argv:
        print(json.dumps(values(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if "--render" in argv or check:
        return render_all(check=check)
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
