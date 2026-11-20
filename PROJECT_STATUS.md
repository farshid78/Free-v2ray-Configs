# PROJECT_STATUS.md — وضعیت فعلی پروژه (برند `@jojo_config`)

> مخزن: `https://github.com/farshid78/Free-v2ray-Configs` · شاخه: `main`

### لنگرِ اعداد و هش‌ها (که به کدام کامیت تعلق دارند)

| نقش | کامیت | توضیح |
|---|---|---|
| دورِ دادهٔ منتشرشده | `551f74f` | `[auto-output]` ۲۰۲۶-۱۱-۲۰ · ۰۱:۰۵ UTC — همهٔ اعدادِ بخش ۹ (۱۱۴۰۶ کانفیگ) از این دور است؛ `index.json.updated_at = 2026-11-20T00:55:35.651685+00:00` |
| کدِ سنجیده‌شده | `faad62a` | رفعِ وابستگیِ `IPv4-mapped` به نسخهٔ پایتون؛ خروجی‌های همان دور با همین کد بازتولید شد |
| HEAD هنگام راستی‌آزمایی | `c00fdbe` | نسخهٔ پیشینِ همین سند |
| همین سند (نسخهٔ فعلی) | کامیتِ حاملِ این ویرایش | یک کامیت بعد از ردیفِ بالا؛ هیچ سند نمی‌تواند هشِ کامیتِ خودش را در متن داشته باشد، پس این ردیف عمداً بی‌هش است |

هر چهار ردیف به‌ترتیب روی `main` و ancestorِ HEAD هستند و بازهٔ `551f74f..HEAD` فقط تغییر کد (`faad62a`) و همین سند است — هیچ داده‌ای در آن بازه بازتولید نشده.

> ⚠️ شاخهٔ `main` با هر اجرای workflow یک کامیتِ `chore: update configs … [auto-output]`
> می‌گیرد و شمارش‌ها با هر اجرا کمی بالا/پایین می‌روند. اگر `origin/main` جلوتر از
> `551f74f` رفت، اعدادِ بخش ۹ مربوط به همان دورِ قدیمی‌ترند و باید از `index.json` تازه
> خوانده شوند. HEAD فعلی: `git ls-remote https://github.com/farshid78/Free-v2ray-Configs refs/heads/main`.

---

## ۱. کامیت‌های این مرحله روی `main`

| کامیت | کار |
|---|---|
| `91a554d` | برندینگ در `scripts/brand.py` + بازتولید همهٔ سطوح (README×۴، `docs/`، `brand.generated.ts`، سبدها، `index.json`/`health.json`) |
| `eb094da` | مستندسازی وضعیت |
| `6e535b3` | *(auto-output)* اجرای واقعی با برند جدید: ۱۱۵۱۶ کانفیگ |
| `ab9722d` | تعمیر `scripts/test_categories.py` (هندلِ برند + پذیرشِ سرآیندِ `GOOGLE READY`) |
| `48961c3` | `.gitattributes` = `* text=auto eol=lf` |
| `c641995` | بازنویسی گزارش با اعداد clone تازه |
| `551f74f` | *(auto-output)* اجرای بعدی: ۱۱۴۰۶ کانفیگ، همه با `@jojo_config` |
| `faad62a` | `converters._is_unroutable_server`: سنجشِ IPv4-mapped با قاعدهٔ IPv4 (رفعِ وابستگیِ خروجی به نسخهٔ پایتون) |

---

## ۲. مقادیر برند (خروجی `brand.py --json`)

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
3. **پردازش دسته**: حذف خراب → دروازهٔ mihomo → dedup آگاه از CDN → **برندینگ `core.brand_remark`** (`{CC} {flag} | @jojo_config | {id}`) + دروازهٔ برند (retry و حذفِ خطِ بی‌برند).
4. **نوشتن**: `configs.txt`, `configs_base64.txt`, `clash.yaml`, `singbox.json` + سرآیند Hiddify.
5. **پروتکل‌ها/آرشیو/متادیتا**: `protocols/*.txt`, `archive/*`, `index.json`, `health.json`.
6. **آبشار کیفیت**: L0/L1 → L2 TCP → L3×۳ (xray-knife) → `verified/ fast/ secure/ top100.txt`.
7. **کشورها**: گروه‌بندی `verified/` با GeoIP.
8. **مستندات**: `docs-src/build.py` + `brand.py --render` (هر دو `--check` دارند).

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

- کاربر: `/start`، ۲۰ تای آخر، دسته/کشور/پروتکل/تعداد — از فایل‌های منتشرشدهٔ محلی (`bot/utils.py:load_configs`).
- ادمین: `adm_stats`، `adm_trigger` (dispatch به GitHub)، `adm_broadcast` (به کاربران ربات، نه کانال)، `adm_addadmin`/`adm_removeadmin`، `adm_sources`/`adm_source_toggle`/`adm_source_remove`، `adm_addsource`.
- `bot/config.py`: `CHANNEL_USERNAME` پیش‌فرض `jojo_config`، ولی هیچ کدی از آن برای پست در کانال استفاده نمی‌کند.
- `GITHUB_TOKEN` در `.env` خالی است ⇒ `adm_trigger` تا ست نشدنِ توکن با scope `actions:write`/`repo` کار نمی‌کند.

---

## ۷. برند روی کانفیگ‌ها و انتشار

| مرحله | وضعیت |
|---|---|
| ست شدن برند روی هر کانفیگ | ✅ `aggregate.process_category` (`core.brand_remark`) — `@jojo_config` |
| انتشار در ربات خودم | ✅ ربات همان خطوطِ برندخورده را می‌فرستد |
| انتشار خودکار در کانال | ❌ وجود ندارد (نیاز به ادمین‌بودنِ ربات در کانال + شناسهٔ کانال + هندلر `send_document`) |

---

## ۸. منابع کانفیگ و راه‌های افزودن

- **۱۳ منبع فعال** در `scripts/sources.py`: ۸ منبع `LIGHT` + ۵ منبع `HEAVY`.
- منابع افزوده از ربات در `data/sources_extra.json` ذخیره و merge می‌شوند.
- سلامت هر منبع در `health.json`؛ `state.py` منبعِ ضعیف را با چهار شرط ایمنی auto-disable می‌کند.

1. **دائمی**: URL در `LIGHT_SOURCES`/`HEAVY_SOURCES` + به‌روزرسانی عددِ docstring (تست `test_source_docstring_count_matches_the_actual_list` قفلش کرده) + کامیت.
2. **از ربات (ادمین)**: پنل «منابع» → افزودن/روشن‌خاموش/حذف → `data/sources_extra.json`.
3. **PR** به مخزن برای لحاظ شدن در CI.
4. **بازاجرا**: `adm_trigger` یا محلی `python -X utf8 scripts/run_all.py` (بدون `--skip-fetch`).
5. پروتکل جدید خودکار پذیرفته می‌شود (لیست سیاه، نه allowlist).

---

## ۹. اعداد منتشرشده (دورِ دادهٔ `551f74f`)

| سطح | تعداد |
|---|---|
| `index.json.categories.all.unique` | ۱۱۴۰۶ |
| `index.json.categories.heavy.unique` | ۶۵۳۸ |
| `index.json.categories.light.unique` | ۶۱۳۶ |
| `verified/configs.txt` | ۱۵۰۰ |
| `fast/configs.txt` | ۱۱۲۲ |
| `secure/configs.txt` | ۹۵۱ |
| `google/configs.txt` (GOOGLE READY) | ۵۹۷ |
| `top100.txt` | ۱۰۰ |
| `Countries/*.txt` | ۵۱ فایل · ۱۲۴۶ خط واترمارک `| @jojo_config |` |
| `protocols/` | ۱۶ فایل |
| `archive/` | ۴ فایل |
| `index.json` | `brand=@jojo_config`، `generator=jojo-aggregator aggregator`، `updated_at=2026-11-20T00:55:35.651685+00:00` |

هر عددِ بالا با خط‌های واقعیِ همان فایل (بدون خطوط `#`) برابر است و `scripts/test_categories.py` همین را قفل می‌کند.

---

## ۱۰. خودسازگاریِ خروجی‌های کامیت‌شده (سنجیده، نه ادعا)

روی همان کامیت، با خودِ توابعِ تولیدِ پروژه:

1. `python -X utf8 scripts/brand.py --render` → هیچ فایلی بازنویسی نشد؛ `git status` پاک.
2. `python -X utf8 docs-src/build.py` → `docs/index.html` و `docs/fa/index.html` بازتولید شدند ولی **صفر بایت تغییر**؛ `git status` پاک.
3. بازتولیدِ ۱۲ خروجیِ سبدها از payload کامیت‌شدهٔ خودشان (`configs_base64.txt` → `configs.txt` + `configs_base64.txt` + `clash.yaml` + `singbox.json`) برای `all/`, `heavy/`, `light/` **بایت‌به‌بایت** برابر است.
4. `verified/`, `fast/`, `secure/`, `google/`, `Countries/` را `pipeline.py`/`countries.py`/`googleready.py` می‌سازند و ورودیِ خامشان (نتیجهٔ تستِ واقعیِ شبکه) در مخزن نیست؛ پس بازتولیدِ آفلاینِ آن‌ها ممکن نیست و در این سنجش نیامده‌اند. آن‌ها با `test_categories.py` (سرآیند/شمارش/زیرمجموعه‌بودن) سنجیده می‌شوند.

### چرا این خودسازگاری قبلاً برقرار نبود — و چه شد

`converters._is_unroutable_server` روی پایتونِ ۳٫۱۱ نشانی‌های `::ffff:1.2.3.4` را «reserved» می‌دید و حذف می‌کرد، ولی CI (پایتونِ ۳٫۱۲) نگه می‌داشت؛ یعنی یک ورودی، دو خروجیِ متفاوت، فقط به‌خاطرِ نسخهٔ مفسر. حالا آدرسِ map‌شده با قاعدهٔ IPv4 سنجیده می‌شود (`faad62a`) و بازتولیدِ محلی دقیقاً همان بایت‌های منتشرشده است.

---

## ۱۱. تست‌ها

| اجرا | نتیجه |
|---|---|
| `python -X utf8 scripts/test_categories.py` | **9/9 passed** |
| `python -X utf8 -m pytest scripts/test_pipeline.py` روی این ماشین (با `.cache/` موجود) | ۵۱۱ passed، ۳۱ failed |
| همان، روی clone تازه (بدون پایگاهِ GeoIP) | ۵۰۸ passed، ۳۴ failed |

۳۴ موردِ clone تازه همه محیطی‌اند و روی کامیتِ **قبل از تغییرات** (`eb094da`) هم عیناً fail می‌شدند (مجموعهٔ یکسان):

- `WinError 1314` → ساختِ symlink نیاز به Developer Mode/ادمین دارد.
- `WinError 193` → تست‌هایی که باینریِ bash/لینوکسی را اجرا می‌کنند.
- ۳ تستِ نامِ کشور (`Germany.txt` در برابر `DE.txt`) که به پایگاهِ GeoIP در `.cache/` نیاز دارند.

شاهدِ پاس‌شدن در محیطِ درست: workflow روی `91a554d` با نتیجهٔ **success**، در حالی که همان workflow `python scripts/test_pipeline.py` را اجرا می‌کند.

---

## ۱۲. سرنوشتِ `scripts/test_categories.py`

- نسخه‌ای که در پوشِ قبلی کنار گذاشته شد، کپیِ **خرابِ** همان فایل بود (هر خط با خطِ خالی + CRLF؛ ۱۱۷۲ خط در برابر ۲۴۷). تنها محتوای معنایی‌اش `BRAND = "@jojo_config"` بود.
- همان تغییر در `ab9722d` **درست** کامیت شد: `BRAND`، assertion هویت (ممنوعیتِ هندلِ قدیمی به‌جای ممنوعیتِ هندلِ جدید) و پیام/docstring.
- باگِ از پیش موجود هم تعمیر شد: `HEADER_COUNT` سرآیندِ واقعیِ `# @jojo_config — GOOGLE READY — 597 configs` را رد می‌کرد و ۳ تست روی `eb094da` شکست می‌خورد.

---

## ۱۳. `.gitattributes` (چرا لازم بود)

ویندوز با `core.autocrlf` فایل‌ها را CRLF check-out می‌کند ولی مخزن LF است؛ `brand.py --check` و هشِ `?v=` در `docs-src/build.py` بایت‌محورند، پس هر clone تازه دریفتِ غیرواقعی نشان می‌داد. `* text=auto eol=lf` این را قطعی کرد.

---

## ۱۴. باقی‌مانده‌ها

1. **انتشار در کانال** پیاده نشده (بخش ۷) — عمداً در این مرحله اضافه نشد.
2. **`GITHUB_TOKEN`** در `.env` خالی است ⇒ trigger از ربات غیرفعال.
3. هندلِ قدیمی فقط در سه جای **هویتی** مانده و عمداً دست‌نخورده است: `ACCESSIBILITY.md:89`، `GOVERNANCE.md:26` (نگه‌دارندهٔ مخزن)، `PHASE_A_REPORT.md:594` (امضای گزارشِ تاریخی).
4. کامیت‌های `[auto-output]` هر ~۱۵ دقیقه اضافه می‌شوند و شمارش‌ها را کمی جابه‌جا می‌کنند؛ اعدادِ بخش ۹ مربوط به دورِ `551f74f` است.
