import asyncio
import sys

import requests
from telegram import Update
from telegram.ext import ContextTypes

from ..config import (GITHUB_TOKEN, GH_OWNER, GH_REPO, GH_BRANCH,
                      CHANNEL_USERNAME, CHANNEL_PUBLISH, BRAND_CHANNEL,
                      is_owner, REPO_ROOT)
from ..db import add_admin, remove_admin, is_admin, user_count
from ..keyboards import admin_menu

sys.path.insert(0, str(REPO_ROOT))


def _is_admin(user_id: int) -> bool:
    return is_admin(user_id) or is_owner(user_id)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        await q.edit_message_text("دسترسی ندارید.")
        return
    await q.edit_message_text("پنل ادمین:", reply_markup=admin_menu())


async def adm_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    user = q.from_user if q else update.effective_user
    if not user or not _is_admin(user.id):
        if q:
            await q.answer()
        else:
            await update.message.reply_text("دسترسی ندارید.")
        return
    if q:
        await q.answer()
    from ..utils import load_configs, CATEGORY_LABELS
    rows = []
    for key in ("top100", "verified", "fast", "secure", "google",
                "all", "heavy", "light"):
        rows.append(f"{CATEGORY_LABELS[key]} → {len(load_configs(key))}")
    try:
        from scripts.sources import all_sources, list_disabled_sources
        nsrc = f"{len(all_sources())} فعال / {len(list_disabled_sources())} خاموش"
    except Exception:
        nsrc = "?"
    text = ("📊 آمار\n" + f"کاربران: {user_count()}\nمنابع: {nsrc}\n"
            + "\n".join(rows))
    if q:
        await q.edit_message_text(text, reply_markup=admin_menu())
    else:
        await update.message.reply_text(text)


def _post_dispatch() -> str:
    """Trigger the aggregate workflow (blocking). Returns a short status string."""
    if not (GITHUB_TOKEN and GH_OWNER and GH_REPO):
        return "GITHUB_TOKEN/GH_OWNER/GH_REPO تنظیم نشده."
    try:
        r = requests.post(
            f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/dispatches",
            headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json"},
            json={"event_type": "aggregate-now"}, timeout=20,
        )
        return "Triggered ✅" if r.status_code == 204 else f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"


async def _trigger_aggregate() -> str:
    # requests.post بلاک می‌کند؛ در ترد جدا تا polling ربات قطع نشود.
    return await asyncio.to_thread(_post_dispatch)


async def adm_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    await q.edit_message_text("در حال ارسال درخواست…")
    status = await _trigger_aggregate()
    await q.edit_message_text(status, reply_markup=admin_menu())


async def adm_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    context.user_data["mode"] = "broadcast"
    await q.edit_message_text("متن broadcast را بفرستید:")


async def adm_addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not is_owner(q.from_user.id):
        await q.edit_message_text("فقط مالک.")
        return
    context.user_data["mode"] = "addadmin"
    await q.edit_message_text("user_id عددی را بفرستید:")


async def adm_removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not is_owner(q.from_user.id):
        await q.edit_message_text("فقط مالک.")
        return
    context.user_data["mode"] = "removeadmin"
    await q.edit_message_text("user_id عددی برای حذف ادمین را بفرستید:")


def _flat_sources():
    """فهرست تخت و پایدار برای دکمه‌های پنل: [(url, برچسب, فعال؟, اضافه‌شده؟)]

    ترتیب تصادفی نمی‌شود، چون callback فقط ایندکس را حمل می‌کند.
    """
    from scripts.sources import list_all_sources
    d = list_all_sources()
    off = set(d["disabled"])
    out = []
    for key, label, is_extra in (("light", "⭐ Light", False),
                                 ("heavy", "📦 Heavy", False),
                                 ("extra_light", "➕ Light", True),
                                 ("extra_heavy", "➕ Heavy", True)):
        for url in d[key]:
            out.append((url, label, url not in off, is_extra))
    return out


def _sources_view() -> tuple[str, object]:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    flat = _flat_sources()
    on = sum(1 for row in flat if row[2])
    text = (f"📋 منابع: {len(flat)} کل · {on} فعال · {len(flat) - on} خاموش\n"
            "برای روشن/خاموش کردن، روی هر منبع بزنید.")
    rows = []
    for i, (url, label, enabled, is_extra) in enumerate(flat):
        mark = "✅" if enabled else "⛔"
        short = url.replace("https://", "").replace("http://", "")[:38]
        row = [InlineKeyboardButton(f"{mark} {label} {short}", callback_data=f"src:{i}")]
        if is_extra:
            row.append(InlineKeyboardButton("🗑", callback_data=f"srcrm:{i}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("➕ افزودن منبع", callback_data="adm_addsource")])
    rows.append([InlineKeyboardButton("🧭 راهنمای دسته‌ها", callback_data="adm_cats_help")])
    rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")])
    return text, InlineKeyboardMarkup(rows)


async def adm_sources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        await q.edit_message_text("دسترسی ندارید.")
        return
    try:
        text, kb = _sources_view()
    except Exception as e:  # noqa: BLE001
        text, kb = f"خطا در خواندن منابع: {e}", admin_menu()
    await q.edit_message_text(text, reply_markup=kb)


async def adm_source_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    from scripts.sources import set_source_enabled
    idx = int(q.data.split(":", 1)[1])
    flat = _flat_sources()
    if not 0 <= idx < len(flat):
        await q.edit_message_text("فهرست تغییر کرده؛ دوباره باز کنید.", reply_markup=admin_menu())
        return
    url, _label, enabled, _extra = flat[idx]
    set_source_enabled(url, not enabled)
    text, kb = _sources_view()
    await q.edit_message_text(text, reply_markup=kb)


async def adm_source_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    from scripts.sources import remove_source
    idx = int(q.data.split(":", 1)[1])
    flat = _flat_sources()
    if not 0 <= idx < len(flat):
        await q.edit_message_text("فهرست تغییر کرده؛ دوباره باز کنید.", reply_markup=admin_menu())
        return
    result = remove_source(flat[idx][0])
    text, kb = _sources_view()
    prefix = {"removed": "حذف شد ✅", "disabled": "خاموش شد ⛔",
              "notfound": "یافت نشد."}[result]
    await q.edit_message_text(prefix + "\n\n" + text, reply_markup=kb)


async def adm_cats_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    await q.edit_message_text(
        "🧭 تعریف دسته‌ها (همان معیارِ pipeline)\n"
        "🏆 top100 — verified، مرتب بر میانهٔ تأخیر، فقط ۱۰۰ موردِ اول.\n"
        "🏆 verified — در هر ۳ دور، یک درخواستِ واقعی از داخل پروکسی موفق.\n"
        "⚡ fast — verified با میانهٔ تأخیر < ۸۰۰ms.\n"
        "🔐 secure — verified + forward secrecy و بدون allowInsecure/\n"
        "   skip-cert-verify.\n"
        "🟢 google — verified + در هر دو دور: gstatic/YouTube/Play (۲۰۴)،\n"
        "   Maven POM (۲xx)، gemini robots (۲xx) و کشورِ خروج در فهرستِ Gemini.\n"
        "🌐 all — همهٔ کانفیگ‌های dedup، تست‌نشده.\n"
        "📦 heavy — فقط ۵ منبعِ پرحجم.\n"
        "⭐ light — فقط ۸ منبعِ گزیده.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_sources")]]),
    )


async def adm_addsource(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("سبک (Light)", callback_data="addsrc:light"),
         InlineKeyboardButton("انبوه (Heavy)", callback_data="addsrc:heavy")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_sources")],
    ])
    await q.edit_message_text("دستهٔ منبع را انتخاب کنید:", reply_markup=kb)


async def adm_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        await q.edit_message_text("دسترسی ندارید.")
        return
    context.user_data["mode"] = "scanurl"
    await q.edit_message_text(
        "🔍 URL را بفرستید (وب‌صفحه، raw لینک، یا t.me/channel):\n"
        "پس از اسکن، تعداد کانفیگ‌های استخراج‌شده و نمونه نشان داده می‌شود "
        "و می‌توانید آن را به منابع اضافه کنید."
    )


async def adm_scan_cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    cat = q.data.split(":", 1)[1]
    url = context.user_data.pop("scan_url", None)
    if not url:
        await q.edit_message_text("چیزی برای افزودن نیست. دوباره اسکن کنید.", reply_markup=admin_menu())
        return
    from scripts.sources import add_extra_source
    ok = add_extra_source(cat, url)
    if ok:
        trig = await _trigger_aggregate()
        await q.edit_message_text(f"منبع افزوده شد ✅ ({cat})\n{trig}", reply_markup=admin_menu())
    else:
        await q.edit_message_text("این منبع قبلاً وجود داشت.", reply_markup=admin_menu())


async def adm_addsource_cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        return
    cat = q.data.split(":", 1)[1]
    context.user_data["mode"] = f"addsource_{cat}"
    await q.edit_message_text(f"URL منبع ({cat}) را بفرستید:")





async def adm_publish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """انتشار در کانال: پیش‌نمایش (dry-run) یا post واقعی.

    به‌طور پیش‌فرض dry-run است (CHANNEL_PUBLISH تنظیم نشده) تا در تست محلی
    هیچ post واقعی به تلگرام نرود. برای post واقعی: CHANNEL_PUBLISH=live و
    بات باید ادمین کانال باشد. همیشه به فایلِ واقعیِ موجود (verified/configs_base64.txt)
    اشاره می‌کند؛ اگر فایل نباشد، پیامِ راهنما می‌دهد نه خطای مرده.
    """
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        await q.edit_message_text("دسترسی ندارید.")
        return
    from ..utils import subscription_urls
    sub_path = REPO_ROOT / "verified" / "configs_base64.txt"
    raw_url = f"https://raw.githubusercontent.com/{GH_OWNER}/{GH_REPO}/{GH_BRANCH}/verified/configs_base64.txt"
    if not sub_path.exists():
        await q.edit_message_text(
            "فایلِ ساب‌سکریپشنِ برندشده یافت نشد (verified/configs_base64.txt).\n"
            "ابتدا pipeline/aggregate را اجرا کنید.\n\n"
            "مسیرِ انتظار: " + str(sub_path),
            reply_markup=admin_menu(),
        )
        return
    try:
        size = sub_path.stat().st_size
        import base64
        raw = base64.b64decode("".join(sub_path.read_text(encoding="utf-8").split()))
        ncfg = sum(1 for ln in raw.decode("utf-8", errors="replace").splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#"))
    except Exception as e:
        await q.edit_message_text(f"خواندنِ فایل ناموفق: {e}", reply_markup=admin_menu())
        return
    channel = "@" + CHANNEL_USERNAME.lstrip("@")
    msg = (f"JoJo VPN — ساب‌سکریپشنِ برندشده\n"
           f"{ncfg} کانفیگ · verified\n"
           f"Import: {raw_url}")
    dry = (CHANNEL_PUBLISH != "live")
    preview = ("📢 پیش‌نمایشِ انتشار در کانال\n"
               f"کانال: {channel}\n"
               f"فایل: verified/configs_base64.txt ({ncfg} کانفیگ، {size} بایت)\n"
               f"برند: همهٔ remarkها «{BRAND_CHANNEL}» دارند\n"
               f"URL: {raw_url}\n\n"
               f"پیامی که ارسال می‌شود:\n{msg}\n\n")
    if dry:
        preview += ("حالت: DRY-RUN (پیش‌فرض). هیچ post واقعی ارسال نشد.\n"
                    "برای post واقعی: CHANNEL_PUBLISH=live تنظیم کنید و بات را "
                    "ادمین کانال کنید، سپس دوباره بزنید.")
        await q.edit_message_text(preview, reply_markup=admin_menu())
        return
    # live mode: attempt to post
    try:
        await context.bot.send_message(chat_id=channel, text=msg)
        await q.edit_message_text(preview + "\n✅ در کانال منتشر شد.", reply_markup=admin_menu())
    except Exception as e:
        await q.edit_message_text(
            preview + f"\n❌ ارسال ناموفق: {type(e).__name__}: {e}\n"
            "بررسی کنید بات ادمین کانال باشد و CHANNEL_USERNAME درست باشد.",
            reply_markup=admin_menu(),
        )


async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mode = context.user_data.get("mode")
    text = (update.message.text or "").strip()
    user = update.effective_user
    if not user or not _is_admin(user.id):
        return
    if mode == "broadcast":
        context.user_data.pop("mode", None)
        from ..db import _conn
        c = _conn()
        ids = [r[0] for r in c.execute("SELECT user_id FROM users").fetchall()]
        c.close()
        sent = 0
        for uid in ids:
            try:
                await context.bot.send_message(chat_id=uid, text=text)
                sent += 1
            except Exception:
                pass
        await update.message.reply_text(f"ارسال شد به {sent} کاربر.")
    elif mode == "addadmin":
        context.user_data.pop("mode", None)
        if not is_owner(user.id):
            return
        try:
            uid = int(text)
        except ValueError:
            await update.message.reply_text("عدد نامعتبر.")
            return
        add_admin(uid)
        await update.message.reply_text(f"ادمین {uid} اضافه شد.")
    elif mode == "removeadmin":
        context.user_data.pop("mode", None)
        if not is_owner(user.id):
            return
        try:
            uid = int(text)
        except ValueError:
            await update.message.reply_text("عدد نامعتبر.")
            return
        remove_admin(uid)
        await update.message.reply_text(f"ادمین {uid} حذف شد.")
    elif mode == "scanurl":
        context.user_data.pop("mode", None)
        url = text.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            await update.message.reply_text("URL نامعتبر (باید با http/https شروع شود).")
            return
        await update.message.reply_text("در حال اسکن…")
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            from scripts.core import extract_valid_lines
            lines = extract_valid_lines(r.text)
        except Exception as e:
            await update.message.reply_text(f"اسکن ناموفق: {type(e).__name__}: {e}")
            return
        if not lines:
            await update.message.reply_text("هیچ کانفیگ معتبری در این صفحه یافت نشد.")
            return
        context.user_data["scan_url"] = url
        sample = "\n".join(lines[:5])
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Light", callback_data="scancat:light"),
             InlineKeyboardButton("➕ Heavy", callback_data="scancat:heavy")],
            [InlineKeyboardButton("❌ انصراف", callback_data="back_main")],
        ])
        await update.message.reply_text(
            f"✅ {len(lines)} کانفیگ استخراج شد.\nنمونه:\n{sample}\n\n"
            "برای انتشار، این URL را به منابع اضافه کنید:",
            reply_markup=kb,
        )
    elif mode and mode.startswith("addsource_"):
        context.user_data.pop("mode", None)
        cat = mode.split("_", 1)[1]
        url = text.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            await update.message.reply_text("URL نامعتبر (باید با http/https شروع شود).")
            return
        from scripts.sources import add_extra_source
        ok = add_extra_source(cat, url)
        if ok:
            trig = await _trigger_aggregate()
            await update.message.reply_text(f"منبع افزوده شد ✅\n{trig}")
        else:
            await update.message.reply_text("این منبع قبلاً وجود داشت.")
    else:
        return
