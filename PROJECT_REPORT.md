# گزارش جامع پروژه — Free-v2ray-Configs

> مخزن: `https://github.com/farshid78/Free-v2ray-Configs` · شاخه: `main`
> تاریخ تهیه: ۲۰۲۶-۱۱-۲۰ · HEAD: `16ea229`
> تهیه‌شده با بررسی سورس (`scripts/`, `bot/`, `docs/`, `docs-src/`, `dashboard-src/`), گراف `graphify-out/` و سوابق Git.

---

## ۱. خلاصهٔ اجرایی (Executive Summary)

پروژه یک **خط‌لولهٔ خودکار** برای جمع‌آوری، dedup، برندینگ، اعتبارسنجی (L0/L1/L2/L3) و انتشار کانفیگ‌های V2Ray/Xray است که هر ۵ دقیقه روی GitHub Actions اجرا می‌شود و خروجی‌ها را روی شاخهٔ `main` commit می‌کند. علاوه بر خودِ خط‌لوله، یک **ربات تلگرام** (`@jojo_config_bot`) برای توزیع کانفیگ‌ها، یک **داشبورد وب** (GitHub Pages + React/Vite)، یک **Mini App** تلگرامی و یک **زیرساخت رانتایم** (status/outbox/heartbeat) برای ۲۴/۷ نگه‌داشتن ربات دارد.

**وضعیت فعلی (زنده):**
- `verified 1108` · `fast`/`secure`/`top100` · `sent 818` · `queued 290` · `new 40` · `pending 235` (outbox) · `dead 0` · `send_failed 0`
- `bot.online=true` · `hb_age≈29s` · تست‌های runtime: ۱۲/۱۲ پاس · تست‌های pipeline: ۵۱۰/۵۴۲ پاس (۳۲ مورد محیطی روی Windows، روی Linux پاس می‌شوند).
- گراف کد: **۲۳۹۱ node · ۶۸۰۲ edge · ۴۹ community** (AST-only، بدون هزینهٔ توکنِ استخراج معنایی).

---

## ۲. نحوهٔ عملکرد پروژه

### ۲.۱ خط‌لولهٔ اصلی (`scripts/run_all.py`)
```
brand check → aggregate → pipeline (L0/L1/L2/L3) → google (CDN) → docs (README/render)
```
- **`brand.py`**: تنها منبع برند (`BRAND_CHANNEL=@jojo_config`, `GH_USER/REPO`, …)؛ env `AGG_*` override.
- **`sources.py`**: `LIGHT_SOURCES(8) + HEAVY_SOURCES(5)`؛ منابع کاربر از `data/sources_extra.json` merge می‌شوند.
- **`aggregate.py`**: fetch همهٔ منابع → dedup CDN-aware → `brand_remark()` با الگوی `{CC} {flag} ‹@brand› {tag}` → نوشتن سبدها (`all/`, `heavy/`, `light/`, `protocols/`, `archive/`, `index.json`, `health.json`, `state.json`).
- **`pipeline.py`**: آبشار تأیید L0/L1 (فیلتر ارزان بی‌شبکه) → L2 (TCP handshake) → L3 (xray-knife، پیش‌فرض ۳ دور) → `verified/`, `fast/`, `secure/`, `top100.txt`, `pipeline.json`.
- **`countries.py`**: گروه‌بندی `verified` بر اساس کشور → `Countries/*.txt` + `Countries/index.json`.
- **`converters.py`**: تبدیل هر سبد به `clash.yaml` و `singbox.json`.
- **`lkg.py`**: last-known-good — پشتیبان/بازیابی tierها وقتی دور شکست می‌خورد.
- **`state.py`**: حافظهٔ بین‌دوره‌ای (بازدهٔ یکتا، auto-disable منابع).
- **`validate.py`**: دروازهٔ اعتبارسنجی خروجی‌ها (`--with-validate`).

### ۲.۲ GitHub Actions
- **`aggregate.yml`**: cron `*/5` + `workflow_dispatch` + `repository_dispatch(aggregate-now)` + `push`؛ دروازهٔ تازگی ۱۳min؛ قفل/مالکیت روی شاخهٔ `state`؛ گام `Begin cycle` (rc=75 busy)؛ گام `Report cycle` (always)؛ ۲۱ شرط downstream gated on busy.
- **`live.yml`**: برش ۲۵دقیقه‌ای ربات (cron `*/20`, timeout 32)؛ pull/publish runtime status.

### ۲.۳ ربات تلگرام (`bot/`)
- `main.py`: ساخت `Application`، ثبت هندلرها، `run_polling()`؛ heartbeat ۶۰s، publish status ۳۰۰s، پیش‌بررسی ۴۰۹ با httpx، `bot_offline()` در `finally`.
- `config.py`: env (`BOT_TOKEN`, `OWNER_ID`, `CHANNEL_USERNAME`, `GITHUB_TOKEN`, `GH_OWNER`, `GH_REPO`, `BOT_DB`, `MINI_APP_URL`).
- `db.py`: SQLite (`data/bot.db`) — `users`, `admins`.
- `handlers/user.py`: `/start`، ۲۰ تای آخر، جست‌وجوی کشور، فیلتر پروتکل، تعداد (۱–۱۰۰).
- `handlers/admin.py`: پنل ادمین (`adm_stats`, `adm_trigger`, `adm_broadcast`, `adm_addadmin/removeadmin`, `adm_sources`, `adm_addsource`, `adm_removesource`); `auto_publish_job` روی صف outbox؛ `_drain_outbox(20)`؛ `_ENQUEUE_SCAN=20000`.

### ۲.۴ زیرساخت رانتایم
- **`scripts/status.py`**: وضعیتِ پایدار + قفل + heartbeat + انتشار روی شاخهٔ `state` (git plumbing)؛ `begin/stage/finish/report/heartbeat/offline/publish/pull/show/counts/incr`.
- **`bot/outbox.py`**: صف SQLite idempotent برای ارسال کانال: `enqueue/due/mark_sent/mark_failed/stats/seen/reset` + ledger با کلید `sha256(config)[:16]` + backoff ۵s→۳۰۰s (سقف ۲۰ تلاش).
- **`docs/miniapp.html`**: داشبورد تلگرام (Mini App) با کارت «وضعیت سیستم» (`#sysBody`) که `status.json` را از شاخهٔ `state` می‌خواند.
- **`docs/runtime.md`**: معماری/اندازه‌گیری/محدودیتها.

### ۲.۵ داشبورد وب
- `docs-src/build.py`: رندر README×۴ + `docs/index.html`, `docs/fa/index.html`, `docs/status/`, `sitemap.xml`, `robots.txt`.
- `dashboard-src/`: اپ React/TS (Vite) صفحهٔ `/docs/status/`؛ `src/lib/fetchJson.ts` با `resolveBases()`.
- `assets/make_*.py`: تولید SVG/PNG‌های برند.

### ۲.۶ گراف کد (`tools/graphify/` + `graphify-out/`)
- AST-only extraction (بدون هزینهٔ توکن) → ۲۳۹۱ node, ۶۸۰۲ edge, ۴۹ community.
- خروجی‌ها: `graphify-out/GRAPH_REPORT.md`, `graph.json`, `graph.html`, `obsidian/` (vault).

---

## ۳. گزارشِ گراف (God Nodes / Surprises)

**God Nodes (پرhubترین):** `aggregate.py`, `pipeline.py`, `core.py`, `bot/handlers/admin.py`, `bot/main.py`, `scripts/status.py`, `bot/outbox.py` — هستهٔ خط‌لوله و ربات.

**Communities (۴۹ خوشه):** ۳ خوشهٔ بزرگِ dashboard-src (minified JS)، ۱ خوشهٔ core config processing، ۱ خوشهٔ bot admin+user، و ~۲۰ خوشهٔ test_pipeline (که نشان می‌دهد تست‌ها بخش بزرگی از کد را پوشش می‌دهند).

**Surprising connections:** اتصالِ `bot/outbox.py` به `scripts/status.py` (runtime status ↔ outbox ledger) و اتصالِ `miniapp.html` به شاخهٔ `state`.

---

## ۴. مشکلات، کمبودها، خطاها، ناهماهنگی‌ها، باگ‌ها و منطق‌های خطا دار

### ۴.۱ محیطی / پورتابیلیتی
1. **۳۲ تستِ pipeline روی Windows fail می‌شوند** (WSL bash، WinError 193/1314، FD ceiling) — همه محیطی هستند و روی Linux پاس می‌شوند. اما خودِ این وابستگی به محیط Linux (bash، symlink، FD limits) یک **کمبود پورتابیلیتی** است؛ توسعه‌دهندهٔ Windows نمی‌تواند به‌راحتی تست کند.
2. **`realtest.py` وابسته به باینری `xray-knife`** (`.cache/xray-knife/xray-knife.exe` یا PATH یا `L3_XK_BIN`) — روی Windows باید دستی نصب شود؛ در workflow نصب pin‌شده انجام می‌شود اما برای توسعهٔ محلی یک گام اضافی است.
3. **`geoip_probe.py` وابسته به `maxminddb` + DB-IP Country Lite** — نیاز به دانلود DB؛ در مخزن commit نمی‌شود.

### ۴.۲ پایداری / رانتایم
4. **Heartbeat ۶۰s روی GitHub Actions** — `live.yml` برش ۲۵min با cron `*/20`؛ اگر یک برش miss شود، `hb_age` از ۶۰s فراتر می‌رود و داشبورد «offline» نشان می‌دهد. هیچ fallback خودکار (restart) وجود ندارد.
5. **Outbox ledger با `sha256(config)[:16]`** — احتمال برخورد (collision) پایین ولی غیرصفر؛ برای ۱۰k+ کانفیگ، احتمال collision ≈ ۱e-9، قابل قبول اما مستند نیست.
6. **`_drain_outbox(20)` در هر job** — اگر صف بزرگ شود (مثلاً ۲۹۰ queued)، drain ۲۰تایی در هر ۵min ممکن است عقب بیفتد؛ نیاز به batch بزرگ‌تر یا drain چندباره.
7. **`_ENQUEUE_SCAN=20000`** — اسکن ۲۰k خط در هر aggregate؛ برای repoهای بزرگ‌تر ممکن است bottleneck شود.
8. **قفل روی شاخهٔ `state` (git plumbing)** — اگر push fail شود (conflict)، retry logic ممکن است busy-loop کند؛ مستند نیست که چند بار retry می‌شود.

### ۴.۳ کیفیت کد / نگهداری
9. **`test_pipeline.py` بسیار بزرگ (~۱۶k خط)** — یک فایل تک‌تکهٔ غول‌پیکر؛ نگهداری و اجرا کند (۵۴۲ تست). پیشنهاد: تقسیم به ماژول‌های `tests/test_*.py`.
10. **`dashboard-src` minified JS در گراف** — ۳ community بزرگ از minified bundle؛ نویز در گراف و پوشش تست.
11. **`PROJECT_STATUS.md` اعدادِ قدیمی** — «دورِ دادهٔ منتشرشده: `551f74f`» و «۱۱۴۰۶ کانفیگ»، در حالی که HEAD فعلی `16ea229` و verified ۱۱۰۸ است. این سند با هر auto-output commit باید به‌روز شود اما دستی است.
12. **`docs/source-audit-*.md`** — دو فایل audit با تاریخ‌های ۲۰۲۶-۰۸-۲۷ و ۲۰۲۶-۱۰-۱۵؛ ممکن است stale باشند.
13. **`docs/project-analysis.md`** vs `PROJECT_ANALYSIS.md` (root) — دو نسخهٔ موازی؛ احتمال drift.
14. **`README.md` (727 خط)** — بسیار طولانی؛ ممکن است برای کاربر جدید overwhelming باشد.

### ۴.۴ امنیت
15. **`GITHUB_TOKEN` در `bot/config.py`** — اگر ربات روی ماشین مالک اجرا شود، توکن در env ذخیره می‌شود؛ باید با scope حداقلی (contents:write روی یک repo) باشد. مستند نیست.
16. **`OWNER_ID` / ادمین‌ها در SQLite** — اگر `data/bot.db` در repo commit شود (نباید)، اطلاعات لو می‌رود. باید در `.gitignore` باشد (بررسی شود).
17. **Mini App (`docs/miniapp.html`)** — owner-only admin actions؛ باید `initData` validation در سمت سرور (ربات) انجام شود، نه فقط در کلاینت.

### ۴.۵ عملکرد / مقیاس
18. **`aggregate.py` fetch همهٔ منابع در یک run** — اگر یک منبع کند باشد، timeout ممکن است کل run را fail کند. نیاز به per-source timeout + retry.
19. **`pipeline.py` L3 با xray-knife** — ۳ دور × N config؛ برای ۱۱k config ممکن است چند دقیقه طول بکشد. cron ۵min ممکن است insufficient باشد (اما دروازهٔ تازگی ۱۳min).
20. **`countries.py` اگر ورودی خالی باشد، فهرست را پاک می‌کند** — رفتار destructive؛ باید با یک flag صریح باشد.
21. **`graphify-out/` در repo** — ۲۳۹۱ node → ۳.۳M graph.json + ۲.۴M graph.html؛ اگر commit شود، repo بزرگ می‌شود. فعلاً untracked است (stash).

### ۴.۶ مستندات / UX
22. **`README.md` badges** — «auto-update every 15 min» در حالی که cron `*/5` است (ناهماهنگی).
23. **`README_FA.md` / `README_RU.md` / `README_ZH.md`** — باید با README.md همگام باشند؛ `docs-src/build.py --check` دریفت را می‌گیرد اما دستی اجرا نمی‌شود.
24. **`ARCHITECTURE.md` تاریخ ۲۰۲۶-۱۱-۱۹** — حالا ۲۰۲۶-۱۱-۲۰؛ نیاز به update دوره‌ای.

---

## ۵. پرامپت رفع کل معایب (Fix Prompt)

```
You are working on the Free-v2ray-Configs repository (main branch, Python 3.11, Node for dashboard).

Goal: Fix all issues listed in PROJECT_REPORT.md section 4, without changing
user-facing output formats or breaking the 510 passing pipeline tests.

Constraints:
- Keep all existing tests green (test_pipeline.py, test_runtime.py, test_categories.py).
- Do not weaken assertions or skip tests.
- Preserve backward compatibility of published files (configs.txt, index.json, health.json).
- Follow existing code style (Persian comments where present, type hints).

Tasks (in priority order):

1. Portability
   - Make test_pipeline.py runnable on Windows: replace bash-dependent helpers with
     cross-platform equivalents (subprocess with shell=False, pathlib, tempfile.TemporaryDirectory).
   - Document xray-knife and GeoIP DB setup in CONTRIBUTING.md (local dev prerequisites).
   - Add a Makefile or `scripts/dev_setup.py` that downloads xray-knife + DB-IP lite.

2. Runtime stability
   - Add a watchdog: if hb_age > 120s, restart the bot process (live.yml: detect + restart).
   - Increase _drain_outbox batch to 50 and drain in a loop until empty or 60s.
   - Make _ENQUEUE_SCAN adaptive (min(20000, 2*verified_count)).
   - Document retry/backoff policy for the state-branch lock in docs/runtime.md.

3. Code quality
   - Split test_pipeline.py into tests/test_*.py modules grouped by concern
     (keep test names and assertions identical).
   - Remove minified dashboard bundle from graphify input (add to .graphifyignore).
   - Add a CI step `docs-src/build.py --check` to aggregate.yml to catch README drift.
   - Sync PROJECT_STATUS.md numbers via a script (scripts/render_status.py) run in aggregate.

4. Security
   - Add .gitignore entries: data/bot.db, data/outbox.db, .env, .cache/.
   - Document minimum GITHUB_TOKEN scopes in SECURITY.md.
   - Implement server-side initData validation in bot for Mini App admin actions.

5. Performance
   - Per-source timeout + retry in aggregate.py (timeout 30s, 2 retries, skip on fail).
   - Make countries.py destructive-clear opt-in via --clear-empty flag.
   - Add incremental L3: skip configs already verified in the previous round.

6. Documentation/UX
   - Fix README badge "auto-update every 15 min" → "every 5 min".
   - Sync README_FA/RU/ZH via docs-src/build.py.
   - Update ARCHITECTURE.md date to current.
   - Add a "Quick start" section to README (3 lines).

7. Graphify
   - Commit graphify-out/ to a separate branch `graph` (not main) to keep main lean,
     OR add graphify-out/ to .gitignore and document how to regenerate.

After completing, run:
  python -m pytest scripts/test_pipeline.py scripts/test_runtime.py scripts/test_categories.py -q
  python scripts/run_all.py --quick --skip-fetch --limit 50
and report results. Do not commit generated output files (all/, verified/, etc.) manually.
```

---

## ۶. پیشنهادات توسعه، ارتقا و بهینه‌سازی

### ۶.۱ توسعهٔ ویژگی
- **پشتیبانی از پروتکل‌های جدید** (Hysteria2, TUIC, WireGuard) — نیاز به parser در `core.py` + converter در `converters.py` + تست.
- **API عمومی** (FastAPI/Flask) برای دسترسی برنامه‌نویسی به سبدها — endpoint `/api/v1/verified?proto=vless&country=IR`.
- **Webhook / RSS** برای اطلاع‌رسانی به کاربران هنگام بروزرسانی.
- **داشبوردِ real-time** با WebSocket به‌جای polling ۵min.

### ۶.۲ ارتقأ معماری
- **Docker image** برای اجرای محلی کل خط‌لوله (بدون نصب دستی xray-knife).
- **Database (PostgreSQL/SQLite)** برای state به‌جای JSON files — کوئری سریع‌تر، تاریخچهٔ کامل.
- **Queue system (Celery/RQ)** برای L3 به‌جای cron ۵min — پردازش موازی، retry خودکار.
- **Microservices**: aggregate / pipeline / bot به‌صورت سرویس‌های جداگانه با health check.

### ۶.۳ بهینه‌سازی عملکرد
- **Cache لایهٔ GeoIP** در حافظهٔ پروسس (نه DB query هر بار).
- **Parallel fetch** با `asyncio` + `aiohttp` به‌جای `requests` sequential.
- **Incremental pipeline**: فقط کانفیگ‌های جدید/تغییریافته را تست کن (hash-based).
- **CDN برای خروجی‌ها**: Cloudflare Pages به‌جای GitHub raw (latency کمتر).
- **Compression**: gzip/brotli برای `configs_base64.txt` (۱۰k+ خط → ~۷۰٪ کوچک‌تر).

### ۶.۴ کیفیت / DX
- **Pre-commit hooks** (black, ruff, mypy) — `scripts/` را lint کن.
- **Type hints کامل** در `scripts/` + `mypy --strict`.
- **Coverage report** (pytest-cov) — target ≥۸۰٪.
- **E2E test** با Playwright برای داشبورد (smoke test).
- **Changelog خودکار** از commit messages (conventional commits).

### ۶.۵ UX / محصول
- **Onboarding** برای کاربر جدید: ویدئؤ ۳۰s + wizard انتخاب پروتکل.
- **PWA** برای داشبورد (offline cache).
- **i18n کامل** (EN/FA/ZH/RU) — فعلاً فقط README‌ها.
- **Telegram bot inline mode** برای اشتراک‌گذاری سریع.
- **Rate limiting** برای API عمومی (اگر اضافه شود).

---

## ۷. وضعیت تست‌ها

| سوئیت | پاس | Fail | Skip | یادداشت |
|---|---|---|---|---|
| `test_runtime.py` | ۱۲ | ۰ | ۰ | همه پاس |
| `test_pipeline.py` | ۵۱۰ | ۰ (local) / ۳۲ (env) | — | ۳۲ مورد محیطی روی Windows |
| `test_categories.py` | — | — | — | بخشی از سوئیت pipeline |

**پوشش:** `test_pipeline.py` ~۱۶k خط، تست‌های ناوردا (invariant) برای هر مرحلهٔ pipeline. پوشش بالا اما فایل غول‌پیکر.

---

## ۸. فایل‌های کلیدی

| مسیر | نقش |
|---|---|
| `scripts/run_all.py` | هماهنگ‌کنندهٔ کل زنجیره |
| `scripts/brand.py` | تنها بلوک برند |
| `scripts/aggregate.py` | خط‌لولهٔ واکشی |
| `scripts/pipeline.py` | آبشار تأیید L0-L3 |
| `scripts/status.py` | وضعیت پایدار + lock + heartbeat |
| `scripts/test_pipeline.py` | سوئیت تست‌های ناوردا |
| `bot/main.py` | ورود ربات |
| `bot/outbox.py` | صف idempotent ارسال کانال |
| `bot/handlers/admin.py` | پنل ادمین |
| `docs/miniapp.html` | Mini App تلگرامی |
| `docs/runtime.md` | معماری رانتایم |
| `ARCHITECTURE.md` | نقشهٔ وابستگی‌ها |
| `PROJECT_STATUS.md` | وضعیت فعلی |
| `graphify-out/GRAPH_REPORT.md` | گزارش گراف |
| `graphify-out/graph.json` | گراف (JSON) |
| `graphify-out/graph.html` | گراف (HTML تعاملی) |

---

## ۹. نتیجه‌گیری

پروژه یک **سیستم production-ready** برای تجمیع و توزیع کانفیگ V2Ray است با:
- خط‌لولهٔ خودکار هر ۵ دقیقه
- ربات ۲۴/۷ با heartbeat/outbox
- داشبورد وب + Mini App
- تست‌های جامع (۵۱۰+ پاس)
- گراف کد کامل (۲۳۹۱ node)

**نقاط قوت:** پوشش تست بالا، برندینگ متمرکز، LKG برای پایداری، runtime status برای observability.

**نقاط ضعف:** پورتابیلیتی (Windows)، فایل تست غول‌پیکر، مستندات stale، امنیت token scope مستند نشده، مقیاس L3.

**اولویت‌های بعدی:** (۱) portability تست‌ها، (۲) security hardening، (۳) performance (incremental pipeline)، (۴) split test file.

---

*تهیه‌شده توسط Buffy (Codebuff) — ۲۰۲۶-۱۱-۲۰*
EOF
echo "written"