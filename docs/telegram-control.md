# کنترل این پروژه از طریق تلگرام — راهنمای گام‌به‌گام

این پروژه **خودش ربات تلگرام نیست**. یک *تجمیع‌کننده* است: کانفیگ‌ها را از منابع عمومی می‌گیرد، تست می‌کند، تگ برند رویشان می‌گذارد و خروجی‌ها را به GitHub (`main`) منتشر می‌کند. ربات تلگرام و کانال، *مصرف‌کنندهٔ downstream* هستند: از URLهای raw گیت‌هاب می‌خوانند و پست می‌کنند.

> فرض: شما این ریپو را fork کرده‌اید و می‌خواهید با برند خودتان (`@YourBrand`) اجرا شود.

---

## ۱. آماده‌سازی (یک‌بار)

```bash
git clone https://github.com/<شما>/<repo>.git
cd <repo>
python -m venv .venv && source .venv/bin/activate   # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt
```

پایتون ۳.۱۱+ لازم است (`pyproject.toml` را ببینید).

---

## ۲. برندینگ (فیلدهای دقیق)

همهٔ مقادیر در **یک بلوک واحد**: `scripts/brand.py` (تابع `_compute()`). هر فیلد با پیشوند `AGG_` قابل override است.

| فیلد env | مقدار پیش‌فرض (امروز) | کجا مصرف می‌شود |
|---|---|---|
| `AGG_BRAND_CHANNEL` | `@jojo_config` | تگ روی کانفیگ (`#profile-title: …`)، گروه‌های Clash، `index.json.brand` |
| `AGG_BRAND_NAME` | `JoJo VPN` | عنوان docs، JSON-LD، توضیح generator |
| `AGG_BOT_NAME` | `jojo-aggregator` | `index.json.generator` («… aggregator») |
| `AGG_BOT_HANDLE` | `@jojo_config_bot` | READMEها |
| `AGG_BOT_HANDLE_DOCS` | `@jojo_config_bot` | صفحهٔ فرود (`docs`) — هم‌راستا با README |
| `AGG_GROUP_URL` | (خالی — گروهی تعریف نشده) | دکمهٔ گروه حذف شد |
| `AGG_GH_USER` | `farshid78` | `PROJECT_URL`, `RAW/CDN/SITE`, badges |
| `AGG_GH_REPO` | `Free-v2ray-Configs` | همان |
| `AGG_PUBLISH_BRANCH` / `PUBLISH_BRANCH` | `main` | شاخهٔ انتشار |
| `AGG_CHANNEL_URL` | `https://t.me/jojo_config` | دکمه‌های README و docs |
| `AGG_SUPPORT_URL` | `https://t.me/jojo_config` | Hiddify `support-url` |
| `AGG_SITE_URL` | `https://farshid78.github.io/Free-v2ray-Configs` | GitHub Pages |
| `AGG_COMMIT_NAME` | `jojo_config-bot[actions]` | هویتِ کامیتِ خودکار انتشار |

**روش ۱ (دائمی)**: defaults را در `scripts/brand.py` ویرایش کنید، سپس:

```bash
PYTHONUTF8=1 python scripts/brand.py --render
PYTHONUTF8=1 python docs-src/build.py
```

**روش ۲ (CI)**: در `.github/workflows/aggregate.yml` بخش `env:` مقدارها را بگذارید یا در GitHub → Settings → Secrets and variables → Actions → Variables اضافه کنید.

بررسی بایت‌یکسانی:

```bash
PYTHONUTF8=1 python scripts/brand.py --check      # باید rc=0
PYTHONUTF8=1 python docs-src/build.py --check      # باید rc=0
```

خروجی `brand.py --github-env` مقادیر را به‌صورت `KEY=value` چاپ می‌کند (برای گام‌های workflow).

---

## ۳. فعال‌سازی GitHub Pages

Settings → Pages → Source = `Deploy from a branch` → Branch `main` → Folder `/docs`.  
آدرس نهایی: `https://<user>.github.io/<repo>/` (این را در `AGG_SITE_URL` بگذارید).

---

## ۴. اجرای workflow (دستی و زمان‌بندی)

فایل: `.github/workflows/aggregate.yml`

- **زمان‌بندی**: `cron: "*/5 * * * *"` (تأثیر واقعی ≈ هر ۱۵ دقیقه، به‌خاطر gateی تازگی).
- **دستی**: تب Actions → `aggregate` → Run workflow → `force` (اختیاری، gate را نادیده می‌گیرد).
- **از ربات/سرور**: `repository_dispatch` با `event_type: aggregate-now` (برای trigger خارجی).

```bash
curl -X POST \
  -H "Authorization: Bearer <GITHUB_TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/<owner>/<repo>/dispatches \
  -d '{"event_type":"aggregate-now"}'
```

نیاز به token با scope `repo` (یا `actions:write`) دارد. نکته: پس از هر اجرا، خروجی‌ها به `main` کامیت می‌شوند (commit identity از `BRAND_COMMIT_NAME/EMAIL`).

---

## ۵. کجا منتشر می‌شود؟ (URLهای خروجی)

Base raw: `https://raw.githubusercontent.com/<owner>/<repo>/main/`

| فایل | URL |
|---|---|
| verified (base64) | `…/verified/configs_base64.txt` |
| verified (plain) | `…/verified/configs.txt` |
| fast | `…/fast/configs.txt` |
| secure | `…/secure/configs.txt` |
| google | `…/google/configs.txt` |
| top100 | `…/top100.txt` |
| index | `…/index.json` |
| health | `…/health.json` |
| صفحهٔ فرود | `https://<user>.github.io/<repo>/` |

CDN (jsdelivr): `https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/...`

---

## ۶. مصرف در تلگرام (کانال/ربات)

پروژه خودش پست نمی‌کند. ربات شما باید:
1. یکی از URLهای بالا را بخواند (مثلاً `verified/configs_base64.txt`).
2. در کانال پست کند (ربات باید admin کانال باشد).
3. (اختیاری) دکمهٔ «Run now» که `repository_dispatch` را صدا بزند.

### اسنیپت حداقلی (Python)

```bash
pip install python-telegram-bot requests
```

```python
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]          # scope: repo / actions:write
OWNER = os.environ["GH_OWNER"]
REPO = os.environ["GH_REPO"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]          # مثلاً @yourchannel
RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Run now", callback_data="run")],
        [InlineKeyboardButton("Latest verified", callback_data="latest")],
    ]
    await update.message.reply_text("Panel", reply_markup=InlineKeyboardMarkup(kb))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "run":
        r = requests.post(
            f"https://api.github.com/repos/{OWNER}/{REPO}/dispatches",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json"},
            json={"event_type": "aggregate-now"}, timeout=20)
        await q.edit_message_text("Triggered ✅" if r.status_code == 204 else f"Error {r.status_code}")
    elif q.data == "latest":
        r = requests.get(f"{RAW}/verified/configs_base64.txt", timeout=20)
        lines = [x for x in r.text.strip().splitlines() if x][:5]
        await q.edit_message_text("\n".join(lines) if lines else "empty")

def main():
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling()

if __name__ == "__main__":
    main()
```

متغیرهای محیطی: `TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`, `GH_OWNER`, `GH_REPO`, `TELEGRAM_CHANNEL`. هرگز token را در ریپو commit نکنید (`.env` + `.gitignore`).

برای پست خودکار در کانال، ربات را admin کانال کنید و از `context.bot.send_message(chat_id=CHANNEL, text=...)` استفاده کنید. برای پست دوره‌ای، یا `job_queue` بات را استفاده کنید یا یک cron خارجی که این اسکریپت را اجرا می‌کند.

---

## ۷. افزودن / غیرفعال‌کردن منابع کانفیگ

فایل: `scripts/sources.py`

- `LIGHT_SOURCES` = ۸ منبعِ دست‌چین/تست‌شده
- `HEAVY_SOURCES` = ۵ منبعِ انبوه

**افزودن**: URL را به لیست مناسب append کنید. قبل از افزودن، URL را با یک درخواست HTTP واقعی بررسی کنید و تعداد کانفیگ معتبرش را بشمارید.

**غیرفعال‌کردن**: URL را کامنت کنید (حذف نکنید — دانش دلیلِ حذف بماند). منابع کامنت‌شده در شمارش `all_sources()` نمی‌آیند.

**هشدار**: عددِ شمارش در docstring بالای فایل (مثلاً «۸ منبع فعال») باید به‌روز شود — تست `test_source_docstring_count_matches_the_actual_list` آن را قفل کرده و در غیر این صورت fail می‌شود.

**غیرفعال‌سازی خودکار**: `state.py` بازدهِ یکتا (نه تعداد کانفیگ) را دوربه‌دور به یاد می‌آورد و `disable_candidates()` با چهار شرط ایمنی منابع ضعیف را غیرفعال می‌کند.

---

## ۸. خلاصهٔ معماری

```
sources.py (URLها)
   ↓
aggregate.py (واکشی + L0/L1/L2/L3×3)
   ↓
core.brand_remark (تگ @YourBrand)
   ↓
buckets: verified / fast / secure / google / heavy / light / all / protocols / Countries
   ↓
index.json + top100.txt + health.json  →  commit به main
   ↓
raw.githubusercontent.com / cdn.jsdelivr.net  →  کانال/ربات تلگرام
```

کنترل: GitHub Actions (`aggregate.yml`) با `cron` و `workflow_dispatch`/`repository_dispatch`. هیچ ربات داخلی وجود ندارد.

---

## ۹. ربات تلگرام داخلی (اختیاری)

یک اسکلت حداقلی در پوشه `bot/` اضافه شده که ویژگی‌های کاربر (دریافت کانفیگ بر اساس کشور/پروتکل/تعداد) و ادمین (آمار، broadcast، trigger aggregate) را از فایل‌های تولیدشده می‌خواند.

```bash
pip install -r requirements-bot.txt
cp .env.example .env   # BOT_TOKEN, OWNER_ID, CHANNEL_USERNAME, GITHUB_TOKEN, GH_OWNER, GH_REPO, MINI_APP_URL
python -X utf8 -m bot.main
```

یا همهٔ سرویس‌های محلی با هم: `start-local.cmd` (وب‌سرور + ربات، لاگ در `.cache/logs/`).

- **اجرا فقط با long-polling است**؛ تا وقتی این پروسه روی یک ماشین/سرور زنده نیست، `/start` هیچ پاسخی نمی‌دهد. GitHub Actions ربات را اجرا نمی‌کند.
- **پنل ادمین** در `config.py` با `OWNER_ID` باز می‌شود (آیدیِ عددی از `@userinfobot`). ادمین‌های دیگر با `adm_addadmin` اضافه می‌شوند.
- **پنل گلس (Mini App)** — `docs/miniapp.html` (تک‌فایل، بدون وابستگیِ خارجی). با Pages روی شاخهٔ **`main`** و پوشهٔ **`/docs`**، آدرس عمومی‌اش دقیقاً همان پیش‌فرضِ `MINI_APP_URL` در `bot/config.py` است: `https://farshid78.github.io/Free-v2ray-Configs/miniapp.html`. اگر پوشهٔ Pages را `/ (root)` بگذارید آدرس به `/docs/miniapp.html` تغییر می‌کند و دکمهٔ ربات ۴۰۴ می‌شود — پوشه باید `/docs` باشد. آدرسِ غیرِHTTPS/تهی عمداً از منو حذف می‌شود، چون تلگرام کلِ پیامِ `/start` را با `URL host is empty` رد می‌کرد.
- **دادهٔ پنل** از `raw.githubusercontent.com` خوانده می‌شود و اگر شکست خورد از آینهٔ `cdn.jsdelivr.net` — چون `index.json`/`health.json`/`Countries/index.json` در **ریشهٔ مخزن** ساخته می‌شوند ولی Pages ریشه را روی `docs/` می‌گذارد (مسیر نسبی همیشه ۴۰۴ بود). عددهای پنل همان عددهای `index.json` است (all / verified / fast / secure / google / top100 / کشورها / منابع). پارامترهای اختیاری: `?data=<base>` برای ریشهٔ دادهٔ دیگر (تست آفلاین) و `?bot=<handle>` برای دکمه‌های ادمین. اگر همهٔ مسیرها شکست بخورند، کارتِ خطا با «تلاش دوباره» و لینک `index.json` نمایش داده می‌شود، نه صفحهٔ خالی.
- **هندلِ ربات در دکمه‌ها**: `@jojo_config_bot` در تلگرام ثبت نشده (`getChat` → «chat not found»)، پس پنل به رباتِ زندهٔ `@jojo_np_bot` لینک می‌دهد تا دکمه‌ای به صفحهٔ مرده نرود. بعد از ساختِ آن هندل در BotFather، با `?bot=jojo_config_bot` یا تغییرِ `BOT` در `docs/miniapp.html` عوض می‌شود.
- **تبِ ادمینِ پنل** فقط‌خواندنی است (آمار، منابع، لینک به ربات)؛ اقداماتِ نوشتاری مثل اجرای تجمیع، broadcast و مدیریتِ منابع/ادمین فقط در ربات انجام می‌شوند.
- **دکمهٔ «Trigger aggregate»** به `GITHUB_TOKEN` با دسترسی `Actions: write` نیاز دارد؛ بقیهٔ پنل بدون آن کار می‌کند.
- **Broadcast** به کاربرانِ ثبت‌شده در `data/bot.db` می‌فرستد، نه به کانال؛ ربات برای این کار لازم نیست ادمینِ کانال باشد. انتشار در کانال در این پروژه پیاده نشده است.
- اگر دو نسخهٔ ربات هم‌زمان اجرا شوند، تلگرام `409 Conflict` می‌دهد؛ `stop-local.cmd` نسخه‌های قبلیِ همین پروژه را می‌بندد.