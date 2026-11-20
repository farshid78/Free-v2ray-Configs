# PROJECT_STATUS.md — وضعیت فعلی پروژه (برند `@jojo_config`)

> راستی‌آزمایی‌شده روی یک clone تازه از `origin/main`، نه روی پوشهٔ کاری محلی.
> مخزن: `https://github.com/farshid78/Free-v2ray-Configs` · شاخه: `main`
> کامیتِ بررسی‌شده: `48961c3`
>
> ⚠️ شاخهٔ `main` با هر اجرای workflow یک کامیتِ `chore: update configs … [auto-output]`
> می‌گیرد، پس HEAD خودبه‌خود جلو می‌رود. اعدادِ این صفحه از همان کامیتِ بررسی‌شده
> است؛ برای دیدنِ HEAD فعلی: `git ls-remote https://github.com/farshid78/Free-v2ray-Configs refs/heads/main`.

---

## ۱. چه چیزی روی `main` نشست (این مرحله)

| کامیت | کار |
|---|---|
| `91a554d` | برندینگ در `scripts/brand.py` + بازتولید همهٔ سطوح تولیدی (`README`×۴، `docs/`، `dashboard-src/…/brand.generated.ts`، سبدها، `index.json`/`health.json`) |
| `eb094da` | مستندسازی: همین فایل + مقادیر برند در `PROJECT_ANALYSIS.md` |
| `6e535b3` | *(auto-output)* اجرای واقعیِ workflow با برند جدید: ۱۱۵۱۶ کانفیگ، همه با `@jojo_config` |
| `ab9722d` | تعمیر `scripts/test_categories.py`: هندلِ برند + پذیرشِ سرآیندِ واقعیِ `GOOGLE READY` |
| `48961c3` | `.gitattributes` با `* text=auto eol=lf` |

---

## ۲. مقادیر برند فعلی (خروجی `brand.py --json`)

| فیلد | مقدار |
|---|---|
| `brand` | `@jojo_config` |
| `brand_name` | `JoJo VPN` |
| `channel_url` / `support_url` | `https://t.me/jojo_config` |
| `bot` / `bot_docs` | `@jojo_config_bot` |
| `bot_name` → `generator` | `jojo-aggregator` → `jojo-aggregator aggregator` |
| `owner` / `repo` | `farshid78` / `Free-v2ray-Configs` (هویت مخزن، خارج از برندینگ) |
| `site` | `https://farshid78.github.io/Free-v2ray-Configs` |
| `group_url` | خالی (گروهی تعریف نشده) |

---

## ۳. گراف رابطهٔ فایل‌ها

```
.env / AGG_*  →  scripts/brand.py            (تنها منبع برند)
brand.py      →  scripts/core.py             (BRAND_CHANNEL, SUPPORT_URL, PROJECT_URL)
sources.py (+ data/sources_extra.json)
              →  scripts/aggregate.py        (fetch → dedup → brand_remark → نوشتن سبدها)
brand.py + core.py + state.py → scripts/aggregate.py
aggregate.py  →  all/ heavy/ light/ protocols/ archive/ + index.json + health.json + state.json
all/          →  scripts/pipeline.py         → verified/ fast/ secure/ top100.txt
verified/     →  scripts/countries.py + geo.py → Countries/
verified/     →  scripts/googleready.py      → google/
brand.py      →  docs-src/build.py           → docs/ + README×۴
brand.py      →  dashboard-src/src/brand.generated.ts
bot/          →  verified/ fast/ secure/ top100.txt + data/bot.db
bot/admin     →  GitHub API repository_dispatch (aggregate-now)
.github/workflows/aggregate.yml → brand + aggregate + pipeline + googleready + docs + test_pipeline
```

هماهنگ‌کنندهٔ کل زنجیره: `scripts/run_all.py` (`brand --check` → `aggregate` → `pipeline` → `googleready` → `docs`).

---

## ۴. منطق برنامه

1. **واکشی** منابع با ThreadPool، retry/backoff و ثبتِ سلامت هر منبع در `health.json`.
2. **استخراج** خطوط از لینک مستقیم یا بدنهٔ base64 (`core.extract_valid_lines`).
3. **پردازش دسته**: حذف خراب → دروازهٔ mihomo → dedup آگاه از CDN → **برندینگ `core.brand_remark`** (`{CC} {flag} | @jojo_config | {id}`) + دروازهٔ برند (retry و حذف خطِ بی‌برند).
4. **نوشتن**: `configs.txt`, `configs_base64.txt`, `clash.yaml`, `singbox.json` + سرآیند Hiddify (`#profile-title`, `#support-url`, `#profile-web-page-url`).
5. **پروتکل‌ها/آرشیو/متادیتا**: `protocols/*.txt`, `archive/*_broken|*_duplicates.txt`, `index.json`, `health.json`.
6. **آبشار کیفیت**: L0/L1 → L2 TCP → L3×۳ (xray-knife) → `verified/ fast/ secure/ top100.txt`.
7. **کشورها**: گروه‌بندی `verified/` با GeoIP.
8. **مستندات**: `docs-src/build.py` + `brand.py --render` (با `--check` برای دریفت).

---

## ۵. کنترل پروژه

| مکانیزم | جزئیات |
|---|---|
| CLI کل زنجیره | `python -X utf8 scripts/run_all.py` |
| واکشی/برند | `python -X utf8 scripts/aggregate.py` |
| آبشار | `python -X utf8 scripts/pipeline.py all/configs.txt --out . --rounds 1` |
| برند | `python -X utf8 scripts/brand.py --render/--check/--github-env/--json` |
| مستندات | `python -X utf8 docs-src/build.py [--check]` |
| ربات | `python -X utf8 -m bot.main` |
| زمان‌بندی | GitHub Actions: `0,15,30,45` + `5,20,35,50` + `10,25,40,55` + `*/5` (تواتر مؤثر ≈ ۱۵ دقیقه) |
| دستی | Actions → `aggregate` → Run workflow (`force`) |
| خارجی | `repository_dispatch` با `event_type: aggregate-now` |
| تست در CI | `python scripts/test_pipeline.py` (`.github/workflows/aggregate.yml`) |

---

## ۶. کنترل از طریق ربات تلگرام

**بله، ولی فقط عملیاتِ مدیریتی — نه اجرای خط لوله روی ماشین محلی.**

- کاربر: `/start`، ۲۰ تای آخر، دسته/کشور/پروتکل/تعداد — از فایل‌های محلیِ منتشرشده (`bot/utils.py:load_configs`).
- ادمین: `adm_stats`، `adm_trigger` (dispatch به GitHub)، `adm_broadcast` (به کاربران ربات، نه کانال)، `adm_addadmin`/`adm_removeadmin`، `adm_sources`/`adm_source_toggle`/`adm_source_remove`، `adm_addsource`.
- `bot/config.py`: `CHANNEL_USERNAME` پیش‌فرض `jojo_config` است، ولی هیچ کدی از آن برای پست در کانال استفاده نمی‌کند.
- `GITHUB_TOKEN` در `.env` خالی است ⇒ `adm_trigger` تا ست نشدنِ توکن با scope `actions:write`/`repo` کار نمی‌کند.

---

## ۷. برند روی کانفیگ‌ها و انتشار

| مرحله | وضعیت |
|---|---|
| ست شدن برند روی هر کانفیگ | ✅ در `aggregate.process_category` (`core.brand_remark`) — الان `@jojo_config` |
| انتشار در ربات خودم | ✅ ربات همان خطوطِ برندخورده را از `verified/`/`fast/`/`secure/` می‌فرستد |
| انتشار خودکار در کانال | ❌ وجود ندارد (نیاز به ادمین‌بودنِ ربات در کانال + شناسهٔ کانال + هندلر `send_document` بعد از aggregate) |

---

## ۸. کانفیگ‌ها از کجا می‌آیند و چطور منبع اضافه کنیم

- **۱۳ منبع فعال** در `scripts/sources.py`: ۸ منبع `LIGHT` + ۵ منبع `HEAVY` (همه اشتراک/مخزن عمومی).
- منابع افزوده از ربات در `data/sources_extra.json` ذخیره و merge می‌شوند.
- سلامت هر منبع در `health.json`؛ `state.py` منبعِ ضعیف را با چهار شرط ایمنی auto-disable می‌کند.

راه‌های افزودن:
1. **دائمی**: URL در `LIGHT_SOURCES`/`HEAVY_SOURCES` + به‌روزرسانی عددِ docstring (تست `test_source_docstring_count_matches_the_actual_list` قفلش کرده) + کامیت.
2. **از ربات (ادمین)**: پنل «منابع» → افزودن/روشن‌خاموش/حذف → `data/sources_extra.json`.
3. **PR** به مخزن برای لحاظ شدن در CI.
4. **بازاجرا**: `adm_trigger` یا محلی `python -X utf8 scripts/run_all.py` (بدون `--skip-fetch`).
5. پروتکل جدید خودکار پذیرفته می‌شود (لیست سیاه، نه allowlist).

---

## ۹. نتایج راستی‌آزمایی روی clone تازهٔ `48961c3`

| بررسی | نتیجه |
|---|---|
| `git status --porcelain` | خالی (working tree پاک) |
| `python -X utf8 scripts/brand.py --check` | rc=0 |
| `python -X utf8 docs-src/build.py --check` | rc=0 |
| `python -X utf8 scripts/test_categories.py` | 9/9 passed |
| `python -X utf8 -m pytest scripts/test_pipeline.py` | 508 passed، ۳۴ failed — همه محیطی (پایین توضیح داده شده) |
| هندلِ قدیمی در سبدهای کانفیگ/خروجی‌های تولیدی | ۰ فایل |
| `#profile-title: @jojo_config` | ۷۳ فایل (سبدها + کشورها + پروتکل‌ها + top100) |
| `index.json` | `brand=@jojo_config`، `generator=jojo-aggregator aggregator`، `updated_at=2026-11-20T00:38:43Z` |
| شمارش‌ها | all=۱۱۵۱۶، heavy=۶۵۲۴، light=۶۱۳۶، verified=۱۳۹۴، fast=۹۹۲، secure=۸۵۲، google=۶۲۷، top100=۱۰۰ |
| خطوطِ واترمارک `| @jojo_config |` در `Countries/` | ۱۱۳۱ خط در ۴۹ فایل |
| `protocols/` | ۱۸ فایل (txt + base64) |
| `archive/` | ۴ فایل |

### دربارهٔ ۳۴ تستِ ناموفق (محیطی، نه رگرسیون)

مجموعهٔ همان ۳۴ تست روی کامیتِ **قبل از تغییرات** (`eb094da`) هم عیناً fail می‌شود
(مقایسهٔ مجموعه‌ها: `same set: True`). دلیل‌ها، همه مخصوصِ ویندوز/این ماشین:

- `OSError: [WinError 1314] A required privilege is not held` → ساختِ symlink نیاز به Developer Mode/ادمین دارد.
- `OSError: [WinError 193] %1 is not a valid Win32 application` → تست‌هایی که یک باینریِ bash/اجراییِ لینوکسی را صدا می‌زنند.
- ۳ تستِ نامِ کشور (`Germany.txt` در برابر `DE.txt`) به پایگاهِ GeoIP در `.cache/` نیاز دارند که در clone تازه وجود ندارد (`countries.resolve_names` → `geo.database_available()`).

شاهدِ اینکه در محیطِ درست پاس می‌شوند: اجرای workflow روی `91a554d` با نتیجهٔ **success**، در حالی که همان workflow `python scripts/test_pipeline.py` را اجرا می‌کند.

---

## ۱۰. سرنوشتِ تغییراتِ `scripts/test_categories.py`

در پوشِ قبلی این فایل از کامیت کنار گذاشته شد. حالا روشن و کامیت‌شده است:

- نسخهٔ کنارگذاشته‌شده یک کپیِ **خراب** از همان فایل بود: هر خط با خطِ خالی و CRLF تکراری، ۱۱۷۲ خط در برابر ۲۴۷ خط. تنها محتوای معنایی‌اش یک خط بود: `BRAND = "@jojo_config"`.
- آن تغییرِ معتبر حالا در `ab9722d` درست و بدون خرابیِ خطوط کامیت شده است (`BRAND`، assertion هویت، و پیام/docstring مربوط).
- به‌علاوه یک باگِ **از قبل موجود** در همان تست تعمیر شد: الگوی `HEADER_COUNT` سرآیندِ واقعیِ `# @jojo_config — GOOGLE READY — 627 configs` را رد می‌کرد و ۳ تست روی `eb094da` شکست می‌خورد. الگو اکنون یک کلمهٔ اضافی و داشِ اختیاری قبل از عدد را می‌پذیرد و ۹/۹ تست پاس می‌شود.

هیچ تغییری بی‌صدا دور ریخته نشد: نسخهٔ خراب در تاریخِ گیت (`3c43917`) باقی است و محتوای معتبرش کامیت شده.

---

## ۱۱. یک نکتهٔ زیرساختی (`48961c3`)

روی ویندوز، `core.autocrlf` فایل‌ها را با CRLF check-out می‌کند در حالی که مخزن LF ذخیره می‌کند. دو بررسیِ خودکار بایت‌محور بودند (`brand.py --check` و هشِ `?v=` در `docs-src/build.py`) و در نتیجه **هر clone تازه** دریفتِ غیرواقعی نشان می‌داد. `.gitattributes` با `* text=auto eol=lf` این را قطعی کرد؛ الان clone تازه بدون هیچ بازتولیدی هر دو `--check` را پاس می‌کند.

---

## ۱۲. باقی‌مانده‌ها

1. **انتشار در کانال** پیاده‌سازی نشده (بخش ۷) — عمداً در این مرحله اضافه نشد.
2. **`GITHUB_TOKEN`** در `.env` خالی است ⇒ trigger از ربات غیرفعال.
3. هندلِ قدیمی فقط در سه جای **هویتی** مانده و عمداً دست‌نخورده است: `ACCESSIBILITY.md:89`، `GOVERNANCE.md:26` (نگه‌دارندهٔ مخزن)، `PHASE_A_REPORT.md:594` (امضای گزارشِ تاریخی).
4. کامیت‌های `[auto-output]` هر ~۱۵ دقیقه اضافه می‌شوند؛ اعدادِ بخش ۹ مربوط به کامیتِ ذکرشده است.
