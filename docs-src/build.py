#!/usr/bin/env python3
"""Build the GitHub Pages landing page from `docs-src/`.

    python3 docs-src/build.py            # writes docs/index.html and docs/fa/index.html
    python3 docs-src/build.py --check    # exit 1 if the committed pages are stale

Inputs
    docs-src/template.html   one template for both languages
    docs-src/i18n/en.json    English strings
    docs-src/i18n/fa.json    Persian strings (must carry exactly the same keys)
    docs/styles.css, docs/app.js, docs/vendor/*.js
                             hand-written runtime; their content hash becomes the
                             `?v=` cache-buster so a deploy never serves stale CSS/JS

Template syntax
    {{a.b}}      string from the language file, HTML-escaped
    {{{a.b}}}    string from the language file, inserted raw (keys end in `_html`)
    {{@x}}       build variable, HTML-escaped
    {{{@x}}}     build variable, inserted raw (pre-escaped JSON / generated HTML)

Only the Python standard library is used, so the page can be rebuilt anywhere.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DOCS = os.path.join(REPO, "docs")

#: The brand/repo/site identity lives in exactly one place.
sys.path.insert(0, os.path.join(REPO, "scripts"))
import brand  # noqa: E402

SITE = brand.SITE_URL + "/"
REPO_URL = brand.PROJECT_URL
RAW = brand.RAW_BASE
QR_VENDOR = "vendor/qrcode-generator-1.4.4.js"

LANGS = {
    "en": {
        "out": "index.html",
        "dir": "ltr",
        "base": "",
        "canonical": SITE,
        "og_locale": "en_US",
        "og_locale_alt": "fa_IR",
        "alt_href": "fa/",
        "alt_lang": "fa",
        "alt_label": "فارسی",
        "font_preload": "fonts/manrope-latin.woff2",
    },
    "fa": {
        "out": "fa/index.html",
        "dir": "rtl",
        "base": "../",
        "canonical": SITE + "fa/",
        "og_locale": "fa_IR",
        "og_locale_alt": "en_US",
        "alt_href": "../",
        "alt_lang": "en",
        "alt_label": "English",
        "font_preload": "fonts/estedad-arabic.woff2",
    },
}

_TOKEN = re.compile(r"\{\{\{(@?[\w.]+)\}\}\}|\{\{(@?[\w.]+)\}\}")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _short_hash(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:10]


def _flatten(obj, prefix: str = "") -> dict:
    out = {}
    for key, val in obj.items():
        name = f"{prefix}{key}"
        if isinstance(val, dict):
            out.update(_flatten(val, name + "."))
        else:
            out[name] = val
    return out


def _script_json(obj) -> str:
    """JSON that is safe inside <script>: no `</script>`, no `<!--`, no U+2028/9."""
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return (text.replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029"))


def _faq_html(items) -> str:
    rows = []
    for i, (q, a) in enumerate(items):
        rows.append(
            f'      <details class="faq-item" id="faq-{i + 1}">'
            f"<summary><span>{html.escape(q)}</span>"
            '<span class="faq-plus" aria-hidden="true"></span></summary>'
            f"<p>{html.escape(a)}</p></details>")
    return "\n".join(rows)


def _jsonld(strings: dict, lang: str, canonical: str) -> dict:
    faq = strings["faq"]["items"]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": SITE + "#website",
                "url": SITE,
                "name": brand.SITE_TITLE,
                "inLanguage": ["en", "fa"],
            },
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": strings["meta"]["title"],
                "description": strings["meta"]["desc"],
                "inLanguage": lang,
                "isPartOf": {"@id": SITE + "#website"},
            },
            {
                "@type": "SoftwareSourceCode",
                "name": brand.GH_REPO,
                "codeRepository": REPO_URL,
                "programmingLanguage": "Python",
                "license": "https://spdx.org/licenses/MIT.html",
                "creator": {"@type": "Person", "name": brand.GH_USER,
                            "url": f"https://github.com/{brand.GH_USER}"},
            },
            {
                "@type": "Dataset",
                "name": "Free V2Ray Configs (verified subscription)",
                "description": strings["meta"]["desc"],
                "url": canonical,
                "sameAs": REPO_URL,
                "isAccessibleForFree": True,
                "license": "https://spdx.org/licenses/MIT.html",
                "creator": {"@type": "Person", "name": brand.GH_USER},
                "distribution": [
                    {"@type": "DataDownload", "encodingFormat": "text/plain",
                     "contentUrl": f"{RAW}/verified/configs_base64.txt"},
                    {"@type": "DataDownload", "encodingFormat": "text/plain",
                     "contentUrl": f"{RAW}/verified/configs.txt"},
                    {"@type": "DataDownload", "encodingFormat": "application/yaml",
                     "contentUrl": f"{RAW}/verified/clash.yaml"},
                    {"@type": "DataDownload", "encodingFormat": "application/json",
                     "contentUrl": f"{RAW}/verified/singbox.json"},
                    {"@type": "DataDownload", "encodingFormat": "application/json",
                     "contentUrl": f"{RAW}/index.json"},
                ],
            },
            {
                "@type": "FAQPage",
                "inLanguage": lang,
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faq
                ],
            },
        ],
    }


def render(lang: str, template: str, strings: dict, hashes: dict) -> str:
    cfg = LANGS[lang]
    flat = _flatten(strings)
    build = {
        "lang": lang,
        "dir": cfg["dir"],
        "base": cfg["base"],
        "canonical": cfg["canonical"],
        "url_en": LANGS["en"]["canonical"],
        "url_fa": LANGS["fa"]["canonical"],
        "og_locale": cfg["og_locale"],
        "og_locale_alt": cfg["og_locale_alt"],
        "alt_href": cfg["alt_href"],
        "alt_lang": cfg["alt_lang"],
        "alt_label": cfg["alt_label"],
        "font_preload": cfg["font_preload"],
        # Brand identity for `{{@...}}` raw insertions — one config block.
        "brand": brand.BRAND_NAME,
        "brand_handle": brand.BRAND_CHANNEL.lstrip("@"),
        # The landing page's bot handle is its own legacy spelling
        # (`@ConfigExBot`); the READMEs say `@farshid78_bot`. Both defaults are
        # today's bytes — see the LEGACY note in `scripts/brand.py`.
        "bot": brand.BOT_HANDLE_DOCS,
        "bot_url": brand.BOT_URL_DOCS,
        "channel_url": brand.CHANNEL_URL,
        "group_url": brand.GROUP_URL,
        "repo_url": brand.PROJECT_URL,
        "raw": brand.RAW_BASE,
        "cdn": brand.CDN_BASE,
        "site": brand.SITE_URL,
        "owner": brand.GH_USER,
        "slug": brand.REPO_SLUG,
        "security_url": f"{brand.PROJECT_URL}/blob/{brand.GH_BRANCH}/SECURITY.md",
        "css_v": hashes["css"],
        "js_v": hashes["js"],
        "qr_v": hashes["qr"],
        "faq_html": _faq_html(strings["faq"]["items"]),
        "jsonld": _script_json(_jsonld(strings, lang, cfg["canonical"])),
        "i18n_json": _script_json({"lang": lang, "dir": cfg["dir"],
                                   **strings["js"]}),
    }
    missing = []

    def sub(m: re.Match) -> str:
        raw_key, esc_key = m.group(1), m.group(2)
        key = raw_key or esc_key
        if key.startswith("@"):
            val = build.get(key[1:])
        else:
            val = flat.get(key)
        if not isinstance(val, str):
            missing.append(key)
            return ""
        if raw_key is not None:
            if not key.startswith("@") and not key.endswith("_html"):
                raise SystemExit(f"build: raw insertion of non-_html key {key!r}")
            return val
        return html.escape(val, quote=True)

    out = _TOKEN.sub(sub, template)
    if missing:
        raise SystemExit(f"build[{lang}]: unresolved template keys: {sorted(set(missing))}")
    if "{{" in out or "}}" in out.replace("}}]}", ""):
        leftover = re.findall(r"\{\{.{0,40}", out)
        if leftover:
            raise SystemExit(f"build[{lang}]: leftover template syntax: {leftover[:3]}")
    return out


def _check_parity(en: dict, fa: dict) -> None:
    a, b = set(_flatten(en)), set(_flatten(fa))
    if a != b:
        raise SystemExit(f"build: en/fa key mismatch: only-en={sorted(a - b)} "
                         f"only-fa={sorted(b - a)}")
    if len(en["faq"]["items"]) != len(fa["faq"]["items"]):
        raise SystemExit("build: en/fa FAQ item count differs")
    for lang, s in (("en", en), ("fa", fa)):
        for key, val in _flatten(s["js"]).items():
            ref = _flatten(en["js"])[key]
            if set(re.findall(r"\{\w+\}", val)) != set(re.findall(r"\{\w+\}", ref)):
                raise SystemExit(f"build[{lang}]: placeholder mismatch in js.{key}")


def _apply_brand(obj):
    """Expand `{{brand}}`-style tokens in every i18n string.

    The language files carry no literal handle/URL: `docs-src/i18n/*.json` say
    `{{brand}}` / `{{channel_url}}` / `{{owner}}`, and the values come from the
    single config block in `scripts/brand.py`. Done before rendering so the
    template engine never sees a leftover `{{`.
    """
    if isinstance(obj, dict):
        return {key: _apply_brand(val) for key, val in obj.items()}
    if isinstance(obj, list):
        return [_apply_brand(val) for val in obj]
    if isinstance(obj, str):
        return brand.render(obj)
    return obj


#: Hand-written docs files that still carry the site URL. They are templates so a
#: rename of the repo/handle does not leave a stale sitemap behind.
SIDECARS = {"robots.txt": "robots.txt.in", "sitemap.xml": "sitemap.xml.in"}

#: Hand-written runtime/styles that carry brand strings (page-title prefix, raw
#: and CDN bases, the sister-site host in a comment). They are templates so a
#: brand switch cannot leave a stale literal behind, while the default render
#: reproduces the shipped bytes exactly.
ASSET_TEMPLATES = {"app.js": "app.js.in", "styles.css": "styles.css.in"}


def _render_assets(check: bool) -> list:
    """Render `docs/app.js` and `docs/styles.css` from their templates.

    Must run **before** `_short_hash()`: the `<script src="app.js?v=…">` and
    `<link href="styles.css?v=…">` cache-busters are hashes of exactly these
    files, so rendering late would leave the page pointing at a stale digest.
    """
    values = (("{{@brand}}", brand.BRAND_NAME),
              ("{{@raw}}", brand.RAW_BASE),
              ("{{@cdn}}", brand.CDN_BASE))
    stale = []
    for out_name, tpl_name in ASSET_TEMPLATES.items():
        text = _read(os.path.join(HERE, tpl_name))
        for token, value in values:
            text = text.replace(token, value)
        path = os.path.join(DOCS, out_name)
        current = _read(path) if os.path.exists(path) else None
        if current == text:
            continue
        if check:
            stale.append(f"docs/{out_name}")
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"build: docs/{out_name}  {len(text.encode('utf-8')):,} B")
    return stale


def _render_sidecars(check: bool) -> list:
    values = (("{{site}}", brand.SITE_URL),
              ("{{raw}}", brand.RAW_BASE),
              ("{{repo_url}}", brand.PROJECT_URL))
    stale = []
    for out_name, tpl_name in SIDECARS.items():
        text = _read(os.path.join(HERE, tpl_name))
        for token, value in values:
            text = text.replace(token, value)
        path = os.path.join(DOCS, out_name)
        current = _read(path) if os.path.exists(path) else None
        if current == text:
            continue
        if check:
            stale.append(out_name)
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"build: docs/{out_name}  {len(text.encode('utf-8')):,} B")
    return stale


def main(argv) -> int:
    check = "--check" in argv
    template = _read(os.path.join(HERE, "template.html"))
    strings = {lang: _apply_brand(json.loads(_read(os.path.join(HERE, "i18n", f"{lang}.json"))))
               for lang in LANGS}
    _check_parity(strings["en"], strings["fa"])
    stale = _render_assets(check)
    hashes = {
        "css": _short_hash(os.path.join(DOCS, "styles.css")),
        "js": _short_hash(os.path.join(DOCS, "app.js")),
        "qr": _short_hash(os.path.join(DOCS, QR_VENDOR)),
    }
    for lang, cfg in LANGS.items():
        page = render(lang, template, strings[lang], hashes)
        path = os.path.join(DOCS, cfg["out"])
        if check:
            current = _read(path) if os.path.exists(path) else None
            if current != page:
                stale.append(cfg["out"])
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(page)
        print(f"build: docs/{cfg['out']}  {len(page.encode('utf-8')):,} B")
    stale += _render_sidecars(check)
    if stale:
        print(f"build --check: stale, rebuild with `python3 docs-src/build.py`: {stale}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
