# PROJECT_ANALYSIS.md — تحلیل جامع Free-v2ray-Configs

> تاریخ: ۲۰۲۶-۱۱-۲۰ · بر اساس خواندن مستقیم سورس (نه خلاصه از حافظه).

---

## ۱. موجودی فایل‌ها (Inventory)

### ریشه
- `.github/workflows/aggregate.yml` (workflow اصلی)
- `.github/workflows/aggregate-fallback-a.yml`, `aggregate-fallback-b.yml` (fallbackهای زمان‌بندی)
- `scripts/` (موتور پایتون)
- `bot/` (ربات تلگرام اختیاری)
- `docs-src/`, `docs/`, `dashboard-src/`, `assets/`
- خروجی‌های commit‌شده: `all/`, `heavy/`, `light/`, `verified/`, `fast/`, `secure/`, `google/`, `protocols/`, `Countries/`, `archive/`, `index.json`, `health.json`, `top100.txt`, `state.json`

### scripts/
- `brand.py`, `core.py`, `aggregate.py`, `pipeline.py`, `sources.py`, `state.py`, `filters.py`, `reachability.py`, `realtest.py`, `converters.py`, `countries.py`, `geo.py`, `geoip_probe.py`, `googleready.py`, `mihomo_compat.py`, `validate.py`, `lkg.py`, `run_all.py`, `test_pipeline.py`, `test_categories.py`

### bot/
- `main.py`, `config.py`, `db.py`, `keyboards.py`, `utils.py`
- `handlers/user.py`, `handlers/admin.py`

---

## ۲. گراف رابطه (Dependency Graph)

```
.env / AGG_*  → scripts/brand.py (تنها بلوک برند)
brand.py      → scripts/core.py (BRAND_CHANNEL, SUPPORT_URL, PROJECT_URL)
scripts/sources.py (+ data/sources_extra.json) → scripts/aggregate.py
brand.py + core.py + state.py → scripts/aggregate.py
aggregate.py  → all/ heavy/ light/ protocols/ archive/ + index.json + health.json
all/...       → scripts/pipeline.py → verified/ fast/ secure/ top100.txt
verified/     → scripts/countries.py + geo.py → Countries/
verified/     → scripts/googleready.py → google/
brand.py      → docs-src/build.py → docs/ + README×4
brand.py      → dashboard-src/src/brand.generated.ts
bot/          → فایل‌های verified/fast/secure/top100 + data/bot.db
bot/admin     → GitHub API repository_dispatch: aggregate-now
.github/workflows/aggregate.yml → brand.py + aggregate.py + pipeline.py + googleready.py + docs
```

### Entry points
- کل زنجیره: `python -X utf8 scripts/run_all.py`
- واکشی/برند: `python -X utf8 scripts/aggregate.py`
- آبشار: `python -X utf8 scripts/pipeline.py all/configs.txt --out . --json pipeline.json --rounds 1`
- برند: `python -X utf8 scripts/brand.py --render/--check/--github-env/--json`
- مستندات: `python -X utf8 docs-src/build.py [--check]`
- ربات: `python -X utf8 -m bot.main`
- هر دو سرویس محلی: `start-local.cmd`

---

## ۳. منطق و جریان اجرایی

1. **ورودی منابع**: `scripts/sources.py` = ۸ LIGHT + ۵ HEAVY (بدون تکرار) — `scripts/sources.py:1-284` (`all_sources()` در خط ۲۸۴).
2. **واکشی**: `scripts/aggregate.py:222` (`fetch_all`) با ThreadPool (retry + backoff + گزارش سلامت).
3. **استخراج**: `core.extract_valid_lines` (direct یا base64).
4. **پردازش دسته**: `scripts/aggregate.py:311` (`process_category`):
   - حذف خراب (`is_dummy_config`) → `broken`
   - دروازهٔ mihomo (`mihomo_compat.fatal_reason`) → حذف
   - dedup CDN-aware (`dedup_key`) → `duplicates`
   - برندینگ `brand_remark` + دروازهٔ برند (retry یک بار، حذف خط بی‌برند)
   - مرتب‌سازی بر `dedup_key`، گرم‌کردن GeoIP
5. **نوشتن**: `configs.txt`, `configs_base64.txt`, `clash.yaml`, `singbox.json` + سرآیند Hiddify
6. **پروتکل‌ها**: `protocols/*.txt` روی دستهٔ ALL
7. **آرشیو**: `archive/*_broken.txt`, `*_duplicates.txt`
8. **متادیتا**: `index.json` (counts، CDN URLs، brand/generator) + `health.json`
9. **Countries**: گروه‌بندی verified بر اساس GeoIP
10. **آبشار (اختیاری)**: `pipeline.py` L0/L1 → L2 TCP → L3×۳ (xray-knife) → `verified/fast/secure/top100`
11. **state.json**: حافظهٔ منابع (بازده یکتا، auto-disable)
12. **lkg**: پشتیبان/بازیابی tiers در شکست
13. **مستندات**: `docs-src/build.py` + `brand.py --render`

---

## ۴. مکانیزم‌های کنترل

| مکانیزم | جزئیات |
|---|---|
| CLI کل زنجیره | `python -X utf8 scripts/run_all.py` |
| CLI واکشی/برند | `python -X utf8 scripts/aggregate.py` |
| CLI آبشار | `python -X utf8 scripts/pipeline.py` |
| CLI برند | `python -X utf8 scripts/brand.py --render/--check/--github-env/--json` |
| CLI docs | `python -X utf8 docs-src/build.py [--check]` |
| ربات | `python -X utf8 -m bot.main` |
| هر دو سرویس محلی | `start-local.cmd` |
| Scheduler | GitHub Actions cron `0,15,30,45` + `5,20,35,50` + `10,25,40,55` + `*/5` + freshness gate (۱۳ دقیقه) — `.github/workflows/aggregate.yml:21-30` |
| workflow_dispatch | force input |
| repository_dispatch | event `aggregate-now` (trigger خارجی) |
| push trigger | paths `scripts/**`, workflow |
| env کلیدی | `AGG_*`, `BOT_TOKEN`, `OWNER_ID`, `CHANNEL_USERNAME`, `GITHUB_TOKEN`, `GH_OWNER`, `GH_REPO`, `AGG_FETCH_TIMEOUT`, `AGG_MAX_WORKERS`, `AGG_FETCH_RETRIES` |

---

## ۵. کنترل از طریق ربات تلگرام

**بله، اما «کنترل عملیاتی محدود»، نه کنترل کامل خط لوله.**

- Entry point: `bot/main.py` (Application, handlers, `run_polling()`).
- Config: `bot/config.py` (env: `BOT_TOKEN`, `OWNER_ID`, `CHANNEL_USERNAME`, `GITHUB_TOKEN`, `GH_OWNER`, `GH_REPO`, `BOT_DB`, `MINI_APP_URL`, مسیرهای `verified/`, `fast/`, `secure/`).
- DB: `bot/db.py` (SQLite `users`, `admins`).
- Utils: `bot/utils.py:61` (`load_configs`) — خواندن از `verified/`/`fast/`/`secure/`/`top100.txt` (base64 fallback).
- User handlers: `bot/handlers/user.py` — `/start`, `latest20`, `categories`, `cat_selected`, `ask_country`, `ask_proto`, `ask_count`, `handle_text`, `proto_selected`, `back_main`.
- Admin handlers: `bot/handlers/admin.py` — `admin_panel`, `adm_stats`, `adm_trigger`, `adm_broadcast`, `adm_addadmin`, `adm_removeadmin`, `adm_sources`, `adm_source_toggle`, `adm_source_remove`, `adm_cats_help`, `adm_addsource`, `adm_addsource_cat`, `handle_admin_text`.
- Trigger aggregate: `bot/handlers/admin.py:57` (`_post_dispatch`) → `POST /repos/{GH_OWNER}/{GH_REPO}/dispatches` با `event_type: aggregate-now`.

| قابلیت | وضعیت |
|---|---|
| آمار (کاربران، counts) | ✅ `adm_stats` |
| همهٔ دسته‌ها | ✅ `user.cat_selected` + `utils.load_configs` |
| روشن/خاموش/حذف منابع | ✅ `adm_sources` / `adm_source_toggle` / `adm_source_remove` |
| افزودن منبع (light/heavy) | ✅ `adm_addsource` → `sources.add_extra_source` |
| broadcast به کاربران ربات | ✅ `adm_broadcast` |
| افزودن/حذف ادمین | ✅ `adm_addadmin` / `adm_removeadmin` |
| trigger به‌روزرسانی | ✅ `adm_trigger` → GitHub API |
| اجرای pipeline روی خود ماشین | ❌ ندارد |
| انتشار در کانال | ❌ ندارد (`CHANNEL_USERNAME` خوانده می‌شود ولی استفاده نمی‌شود) |
| VIP / Clean IP / اسکرپر تلگرامی | ❌ ندارد |

---

## ۶. آیا می‌توان برندِ کاربر را روی کانفیگ‌ها ست کرد و در ربات/کانال خودش منتشر کرد؟

**برند: بله (از پیش پیاده‌سازی شده، تک‌منبع). انتشار در ربات: بله (با فایل‌های محلی). انتشار خودکار در کانال: نه، باید اضافه شود.**

### برندینگ
- تک‌منبع: `scripts/brand.py` → `_compute()` با defaults و env override (`AGG_*`).
- مصرف: `core.BRAND_CHANNEL = brand.BRAND_CHANNEL` (alias) — `scripts/core.py:1256` (`brand_remark`).
- تزریق روی کانفیگ: `core.brand_remark(line, idx)` → فرمت `{CC} {flag} | @brand | {idx}`.
- در `aggregate.process_category` روی هر خط یکتا اعمال می‌شود + دروازهٔ برند (retry + drop + count در `health.json`).
- Hiddify header: `core.hiddify_profile_header` → `#profile-title`, support-url, profile-web-page-url.

### متغیرهای لازم (env)
- `AGG_BRAND_CHANNEL` / `CHANNEL_USERNAME` → تگ روی کانفیگ
- `AGG_BRAND_NAME` → عنوان docs، JSON-LD
- `AGG_BOT_HANDLE` / `AGG_BOT_HANDLE_DOCS` → README/docs
- `AGG_GH_USER` / `AGG_GH_REPO` / `AGG_PUBLISH_BRANCH` → URLها
- `AGG_CHANNEL_URL` / `AGG_SUPPORT_URL` / `AGG_SITE_URL` → لینک‌ها
- `BOT_TOKEN`, `OWNER_ID`, `GITHUB_TOKEN`, `GH_OWNER`, `GH_REPO` → ربات

### انتشار در ربات
- ربات از فایل‌های محلی (`verified/`, `fast/`, `secure/`, `top100.txt`) می‌خواند (`bot/utils.py:61`).
- تغییر `BOT_TOKEN` و `OWNER_ID` در `.env` کافی است؛ ربات از همان `verified/` محلی می‌خواند.
- اگر ربات روی ماشین دیگری باشد، فایل‌های سبد باید همگام شوند (ربات خودش دانلود نمی‌کند).

### انتشار در کانال (نیاز به افزودن کد)
- هیچ کدی امروز پیام/فایل در کانال نمی‌گذارد.
- لازم: (۱) ربات در کانال ادمین باشد، (۲) شناسهٔ کانال (`@…` یا `-100…`) در env، (۳) هندلر که فایل‌های `verified/*.txt` یا `index.json` را با `send_document` بفرستد و پس از `aggregate` صدا زده شود.

---

## ۷. کانفیگ‌های فعلی از کجا استخراج می‌شوند؟

از **۱۳ منبع فعال** در `scripts/sources.py`:
- **۸ LIGHT** (دست‌چین/تست‌شده)
- **۵ HEAVY** (انبوه)

همگی مخازن/subscriptionهای عمومی گیت‌هاب هستند. منابع اضافه‌شده از ربات در `data/sources_extra.json` ذخیره و merge می‌شوند. وضعیت زندهٔ هر منبع در `health.json` منتشر می‌شود و `state.py` منبع ضعیف را با ۴ شرط ایمنی auto-disable می‌کند.

---

## ۸. راه‌های افزودن/تعریف منبع جدید

1. **دائمی و نسخه‌دار**: URL را در `LIGHT_SOURCES` یا `HEAVY_SOURCES` در `scripts/sources.py` اضافه کنید. قاعدهٔ فایل: قبل از افزودن با HTTP واقعی تست و تعداد کانفیگ معتبر شمرده شود؛ عددِ مستندِ شمارش در docstring هم به‌روز شود (تست `test_source_docstring_count_matches_the_actual_list` آن را قفل کرده).
2. **از داخل ربات (ادمین)**: پنل ادمین → «منابع و مدیریت» → روشن/خاموش یا حذف هر منبع، و «افزودن منبع» → `data/sources_extra.json`. مناسب تست سریع؛ فقط روی همان ماشینی که `aggregate` اجرا می‌شود اثر دارد.
3. **PR به همین مخزن**: برای لحاظ در CI، تغییر `sources.py` باید کامیت شود.
4. **بازاجرا**: پس از افزودن، یا `adm_trigger` (dispatch) یا محلی `python -X utf8 scripts/run_all.py` (برای منابع جدید باید fetch انجام شود، پس بدون `--skip-fetch`).
5. **پروتکل‌های جدید** خودکار پذیرفته می‌شوند (`is_proxy_config` با لیست سیاه، نه allowlist).

---

## ۹. نقاط تماس برندینگ (Touchpoints)

| مکان | چه چیزی |
|---|---|
| `scripts/brand.py` | defaults + env overrides (`AGG_*`) — تنها منبع |
| `scripts/core.py` | `BRAND_CHANNEL = brand.BRAND_CHANNEL` (alias) + `brand_remark` |
| `core.hiddify_profile_header` | `#profile-title`, support-url, profile-web-page-url |
| `scripts/aggregate.py` / `pipeline.py` | مصرف `brand.*` |
| `docs-src/readme/*.in` + `README*.md` | rendered از template |
| `docs-src/i18n/en.json`, `fa.json` | رشته‌های دوزبانه |
| `docs-src/build.py` | رندر docs |
| `dashboard-src/src/brand.generated.ts` | AUTO-GENERATED |
| `assets/make_*.py` + تصاویر | علامت، social preview، promo |
| `.github/workflows/aggregate.yml` | brand→env، commit identity، publish |
| `.env` | `CHANNEL_USERNAME`, `PROJECT_NAME`, `GH_OWNER`, `GH_REPO` |
| `bot/config.py` / `bot/handlers/*.py` / `bot/keyboards.py` | متن‌های فارسی و منوها |
| خروجی‌ها | header روی `configs.txt`، `index.json.brand/generator`، `health.json` |

---

## ۱۰. نقشهٔ راه برندینگ (Branding Roadmap)

1. **ورودی‌های کاربر**: نام/هندل کانال، نام برند، هندل ربات، GitHub owner/repo/branch، لینک‌های کانال/پشتیبانی/سایت/گروه، Bot Token، Owner ID، GitHub Token، شناسهٔ کانال (برای انتشار خودکار)، لوگو/تصاویر، پیام‌های دلخواه.
2. **ویرایش تک‌منبع**: defaults را در `scripts/brand.py` ویرایش کنید یا env vars ست کنید.
3. **برند روی کانفیگ**: `core.brand_remark` خودکار اعمال می‌شود؛ دروازهٔ برند (retry + drop + count) در `health.json`.
4. **ربات**: `BOT_TOKEN` و `OWNER_ID` را در `.env` عوض کنید؛ ربات از `verified/` محلی می‌خواند.
5. **کانال**: کد انتشار خودکار در کانال را اضافه کنید (هندلر `send_document` + trigger پس از aggregate).
6. **مستندات**: `python -X utf8 scripts/brand.py --render` و `python -X utf8 docs-src/build.py`.
7. **بررسی**: `python -X utf8 scripts/brand.py --check` و `python -X utf8 docs-src/build.py --check` (باید rc=0).
8. **push**: commit و push به `main`.

---

## ۱۱. وضعیت فعلی داده

- `all/configs.txt`: ۱۱٬۳۸۲ کانفیگ یکتا
- `verified/`, `fast/`, `secure/`, `top100.txt`: **۰** (اجرای محلی)
- `Countries/index.json`: فهرست خالی
- تست‌ها: `test_pipeline.py` ۵۱۳/۵۴۲؛ `test_categories.py` ۹/۹
- کامیت: `ef0858c` (push شده)

---

## ۱۲. محدودیت‌ها

- Branch protection از این محیط قابل فعال‌سازی نیست (بدون `gh` و بدون token).
- `google/` به‌خاطر شبکه منتشر نشده.
- انتشار خودکار در کانال نیاز به کد اضافی دارد.
- GitHub Actions cron best-effort است؛ برای تضمین بیشتر از cron خارجی/PAT استفاده کنید.