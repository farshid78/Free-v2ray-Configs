# PROJECT_STATUS.md — وضعیت فعلی پروژه (پس از برندینگ `@jojo_config`)

> تاریخ: ۲۰۲۶-۱۱-۲۰ · بر اساس خواندن مستقیم کد و بررسی فایل‌های روی دیسک، نه از حافظه.
> مخزن: `https://github.com/farshid78/Free-v2ray-Configs` · شاخه: `main`
> آخرین کامیتِ پوش‌شده: `91a554d` — Rebrand the channel identity to @jojo_config and refresh generated outputs

---

## ۱. کاری که در این مرحله انجام شد

| مورد | وضعیت |
|---|---|
| تغییر برند در تک‌منبع (`scripts/brand.py`) | ✅ انجام شد |
| بازتولید سطوح تولیدی (`brand.py --render`, `docs-src/build.py`) | ✅ انجام شد |
| تغییر برند روی خروجی‌های کانفیگ (`Countries/`, `protocols/`, `archive/`, `verified/`, …) | ✅ انجام شد |
| به‌روزرسانی مستندات `.md` با مقادیر جدید | ✅ انجام شد |
| پوش به `origin/main` | ✅ انجام شد (`9a87ef6..91a554d`) |

---

## ۲. مقادیر برند فعلی (خروجی واقعی `brand.py --json`)

| فیلد | مقدار |
|---|---|
| `brand` (هندل کانال) | `@jojo_config` |
| `brand_name` | `JoJo VPN` |
| `brand_slug` | `jojo_config` |
| `channel_url` | `https://t.me/jojo_config` |
| `support_url` | `https://t.me/jojo_config` |
| `bot` / `bot_docs` | `@jojo_config_bot` |
| `bot_url` | `https://t.me/jojo_config_bot` |
| `bot_name` (generator) | `jojo-aggregator` |
| `owner` / `repo` | `farshid78` / `Free-v2ray-Configs` (بدون تغییر — هویت مخزن) |
| `site` | `https://farshid78.github.io/Free-v2ray-Configs` |
| `raw` | `https://raw.githubusercontent.com/farshid78/Free-v2ray-Configs/main` |
| `cdn` | `https://cdn.jsdelivr.net/gh/farshid78/Free-v2ray-Configs@main` |
| `group_url` | خالی (گروهی تعریف نشده — دکمهٔ گروه حذف است) |

`index.json` → `"brand": "@jojo_config"`, `"generator": "jojo-aggregator aggregator"`.
`health.json` → `"brand": "@jojo_config"`.

---

## ۳. گراف رابطهٔ فایل‌ها (خلاصه)

```
.env / AGG_*  →  scripts/brand.py            (تنها منبع برند)
brand.py      →  scripts/core.py             (BRAND_CHANNEL, SUPPORT_URL, PROJECT_URL)
sources.py (+ data/sources_extra.json)
              →  scripts/aggregate.py        (fetch + dedup + brand_remark + نوشتن سبدها)
brand.py + core.py + state.py
              →  scripts/aggregate.py
aggregate.py  →  all/ heavy/ light/ protocols/ archive/ + index.json + health.json + state.json
all/          →  scripts/pipeline.py         → verified/ fast/ secure/ top100.txt
verified/     →  scripts/countries.py + geo.py → Countries/
verified/     →  scripts/googleready.py      → google/
brand.py      →  docs-src/build.py           → docs/ + README×۴
brand.py      →  dashboard-src/src/brand.generated.ts
bot/          →  verified/ fast/ secure/ top100.txt + data/bot.db
bot/admin     →  GitHub API repository_dispatch (aggregate-now)
.github/workflows/aggregate.yml → brand + aggregate + pipeline + googleready + docs
```

`scripts/run_all.py` هماهنگ‌کنندهٔ کل زنجیره است: `brand --check` → `aggregate` → `pipeline` → `googleready` → `docs`.

---

## ۴. منطق برنامه (جریان اجرا)

1. **واکشی**: `aggregate.fetch_all` با ThreadPool، retry/backoff و ثبت سلامت هر منبع.
2. **استخراج**: `core.extract_valid_lines` (لینک مستقیم یا base64).
3. **پردازش دسته**: حذف خراب (`is_dummy_config`) → دروازهٔ mihomo → dedup آگاه از CDN (`dedup_key`) → **برندینگ `core.brand_remark`** (`{CC} {flag} | @jojo_config | {id}`) + دروازهٔ برند (retry یک بار، حذف خط بی‌برند) → مرتب‌سازی.
4. **نوشتن**: `configs.txt`, `configs_base64.txt`, `clash.yaml`, `singbox.json` + سرآیند Hiddify (`#profile-title`, `#support-url`, `#profile-web-page-url`).
5. **پروتکل‌ها / آرشیو / متادیتا**: `protocols/*.txt`, `archive/*_broken.txt|*_duplicates.txt`, `index.json`, `health.json`.
6. **آبشار کیفیت (اختیاری)**: L0/L1 → L2 TCP → L3×۳ با xray-knife → `verified/ fast/ secure/ top100.txt`.
7. **کشورها**: گروه‌بندی `verified/` بر اساس GeoIP.
8. **مستندات**: `docs-src/build.py` + `brand.py --render`.

---

## ۵. نحوهٔ کنترل پروژه

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

---

## ۶. کنترل از طریق ربات تلگرام

**بله، اما محدود به عملیات مدیریتی — نه اجرای خط لوله روی ماشین محلی.**

- کاربر: `/start`، `latest20`، دسته‌ها، انتخاب کشور/پروتکل/تعداد — همه از فایل‌های محلی (`bot/utils.py:load_configs`).
- ادمین: `adm_stats`، `adm_trigger` (dispatch به GitHub)، `adm_broadcast` (به کاربران ربات، نه کانال)، `adm_addadmin`/`adm_removeadmin`، `adm_sources`/`adm_source_toggle`/`adm_source_remove`، `adm_addsource`.
- `bot/config.py` → `CHANNEL_USERNAME` پیش‌فرض اکنون `jojo_config` است، ولی **هنوز هیچ کدی از آن برای پست در کانال استفاده نمی‌کند**.
- `GITHUB_TOKEN` در `.env` خالی است ⇒ `adm_trigger` تا وقتی توکن با scope `actions:write`/`repo` ست نشود کار نمی‌کند.

---

## ۷. برند من روی کانفیگ‌ها و انتشار در ربات/کانال

| مرحله | وضعیت |
|---|---|
| ست شدن برند روی هر کانفیگ | ✅ پیاده‌سازی شده (`core.brand_remark` در `aggregate.process_category`)، اکنون `@jojo_config` |
| انتشار در ربات خودم | ✅ ربات همان خطوط برندخورده را از `verified/`/`fast/`/`secure/` می‌فرستد |
| انتشار خودکار در کانال | ❌ وجود ندارد — نیاز به: ربات ادمین کانال + شناسهٔ کانال در env + هندلر `send_document` بعد از `aggregate` |

---

## ۸. کانفیگ‌های فعلی از کجا استخراج می‌شوند؟

- **۱۳ منبع فعال** در `scripts/sources.py`: ۸ منبع `LIGHT` (دست‌چین/تست‌شده) + ۵ منبع `HEAVY` (انبوه).
- منابع اضافه‌شده از داخل ربات در `data/sources_extra.json` ذخیره و merge می‌شوند.
- سلامت هر منبع در `health.json` منتشر می‌شود؛ `state.py` منبع ضعیف را با چهار شرط ایمنی خودکار غیرفعال می‌کند.
- منابعِ کامنت‌شده در `all_sources()` شمرده نمی‌شوند (دانشِ دلیلِ حذف در فایل می‌ماند).

### راه‌های افزودن منبع
1. **دائمی**: افزودن URL به `LIGHT_SOURCES`/`HEAVY_SOURCES` در `scripts/sources.py` + به‌روزرسانی عددِ docstring (تست `test_source_docstring_count_matches_the_actual_list` آن را قفل کرده) + کامیت.
2. **از ربات (ادمین)**: «منابع و مدیریت» → افزودن/روشن-خاموش/حذف → `data/sources_extra.json` (فقط روی ماشینی که `aggregate` اجرا می‌شود اثر دارد).
3. **PR به مخزن** برای لحاظ شدن در CI.
4. **بازاجرا**: `adm_trigger` یا محلی `python -X utf8 scripts/run_all.py` (بدون `--skip-fetch`).
5. پروتکل‌های جدید خودکار پذیرفته می‌شوند (لیست سیاه، نه allowlist).

---

## ۹. نتایج راستی‌آزمایی این مرحله

| بررسی | نتیجه |
|---|---|
| `python -X utf8 scripts/brand.py --check` | rc=0 (بدون دریفت) |
| `python -X utf8 docs-src/build.py --check` | rc=0 |
| `@farshid78` در `Countries/`, `protocols/`, `archive/`, `verified/`, `fast/`, `secure/`, `google/`, `heavy/`, `light/`, `all/`, `top100.txt` | ۰ مورد |
| خطوط واترمارک `@jojo_config` در `Countries/` | ۱۱۰۶ خط |
| اعتبار JSON: `index.json`, `health.json`, `state.json`, `*/singbox.json` | همه معتبر |
| `index.json` counts | all=11496, heavy=6533, light=6107 |
| outbounds در singbox | verified=1138, fast=756, secure=710, google=465, all=10912 |
| `git status` پس از پوش | پاک (clean) |
| `HEAD` == `origin/main` == `refs/heads/main` | `91a554d` |

`@farshid78` باقی‌مانده فقط در سه جای هویتی (نه کانال) است:
`ACCESSIBILITY.md:89`، `GOVERNANCE.md:26` (نگه‌دارندهٔ مخزن) و `PHASE_A_REPORT.md:594` (امضای گزارش تاریخی). این‌ها عمداً تغییر نکردند.

---

## ۱۰. نکات و کارهای باقی‌مانده

1. **یک چرخهٔ دادهٔ خودکار عقب‌تر**: مخزن پیش از پوش یک اجرای auto-output جدیدتر داشت (۱۱۴۹۷ کانفیگ). چون خروجی‌های محلی از وضعیت ۱۱۴۹۶ بازتولید شده بودند، پوش یک چرخه دادهٔ خودکار را عقب برد؛ اجرای بعدی workflow (≈۱۵ دقیقه) آن را با برند جدید بازتولید می‌کند.
2. **انتشار در کانال** هنوز پیاده‌سازی نشده (بخش ۷).
3. **`GITHUB_TOKEN`** در `.env` خالی است ⇒ trigger از ربات غیرفعال است تا توکن ست شود.
4. **`generator`** به شکل `jojo-aggregator aggregator` است (الگوی قبلی `{bot_name} aggregator`)؛ اگر نام تمیزتر می‌خواهید، `AGG_BOT_NAME` را عوض کنید و `index.json` را بازتولید کنید.
