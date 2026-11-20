import asyncio
import html as _html
import json as _json_mod
import logging
import os
import random
import sys
import time

import httpx
from telegram import Update
from telegram.error import BadRequest, NetworkError, RetryAfter, TimedOut
from telegram.ext import ContextTypes

from ..config import (GITHUB_TOKEN, GH_OWNER, GH_REPO, GH_BRANCH,
                      CHANNEL_USERNAME, CHANNEL_PUBLISH, BRAND_CHANNEL,
                      is_owner, REPO_ROOT)
from ..db import add_admin, remove_admin, is_admin, user_count
from ..keyboards import admin_menu

sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger(__name__)


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


async def _post_dispatch() -> str:
    """Trigger the aggregate workflow (non-blocking, async HTTP). Returns a short status string."""
    if not (GITHUB_TOKEN and GH_OWNER and GH_REPO):
        return "GITHUB_TOKEN/GH_OWNER/GH_REPO تنظیم نشده."
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/dispatches",
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github+json"},
                json={"event_type": "aggregate-now"},
            )
        return "Triggered ✅" if r.status_code == 204 else f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"


async def _trigger_aggregate() -> str:
    return await _post_dispatch()


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
           f"Import: `{raw_url}`")
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
        await context.bot.send_message(chat_id=channel, text=msg, parse_mode="Markdown")
        await q.edit_message_text(preview + "\n✅ در کانال منتشر شد.", reply_markup=admin_menu())
    except Exception as e:
        await q.edit_message_text(
            preview + f"\n❌ ارسال ناموفق: {type(e).__name__}: {e}\n"
            "بررسی کنید بات ادمین کانال باشد و CHANNEL_USERNAME درست باشد.",
            reply_markup=admin_menu(),
        )


def _country_map() -> dict:
    """نقشهٔ base-config → (flag, country name) از پوشهٔ Countries/."""
    import json as _json
    from pathlib import Path
    result = {}
    try:
        idx = _json.loads((REPO_ROOT / "Countries" / "index.json").read_text(encoding="utf-8"))
    except Exception:
        idx = {"countries": []}
    code2flag = {c.get("code"): c.get("flag", "") for c in idx.get("countries", [])}
    code2name = {c.get("code"): c.get("name", "") for c in idx.get("countries", [])}
    cdir = REPO_ROOT / "Countries"
    if not cdir.exists():
        return result
    for f in cdir.glob("*.txt"):
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                base = line.split("#", 1)[0].strip()
                remark = line.split("#", 1)[1] if "#" in line else ""
                code = remark.split("|")[0].strip().split()[0] if remark else ""
                if base and code and code in code2flag:
                    result[base] = (code2flag[code], code2name.get(code, code))
        except OSError:
            continue
    return result


def _proto_of(line: str) -> str:
    scheme = line.split("://", 1)[0].lower() if "://" in line else ""
    return {
        "vless": "VLESS", "vmess": "VMESS", "trojan": "TROJAN",
        "ss": "SHADOWSOCKS", "shadowsocks": "SHADOWSOCKS",
        "hysteria": "HYSTERIA2", "hysteria2": "HYSTERIA2", "hy2": "HYSTERIA2",
        "tuic": "TUIC",
    }.get(scheme, scheme.upper() or "CONFIG")


#: سقفِ امنِ متنِ پیام تلگرام ۴۰۹۶ کاراکتر است؛ کانفیگ‌های بلندتر (بعضی
#: vmessها) کلِ پیام را رد می‌کردند و ارسال قطع می‌شد.
_MAX_TEXT = 3800


def _format_channel_msg(line: str, cmap: dict) -> str:
    base = line.split("#", 1)[0].strip()
    flag, cname = cmap.get(base, ("", ""))
    proto = _proto_of(line)
    if flag and cname:
        header = f"🈳🈱 {flag} {cname} ┃ ⚙️ {proto}"
    else:
        header = f"🈳🈱 ⚙️ {proto}"
    body = line.strip()
    if len(body) > _MAX_TEXT:
        body = body[:_MAX_TEXT] + "…"
    # HTML parse mode: کانفیگ را در <code> می‌گذاریم تا monospace شود و
    # کاراکترهای خاصِ Markdown (مانند `_` یا backtick) باعث خطای parse نشوند.
    safe_line = _html.escape(body)
    return (f"{header}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<code>{safe_line}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 t.me/{CHANNEL_USERNAME.lstrip('@')}")


async def adm_publish_configs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """انتشارِ دستیِ یک دور کامل (۲۰ کانفیگ) در کانال، با فاصلهٔ تصادفی."""
    q = update.callback_query
    await q.answer()
    if not _is_admin(q.from_user.id):
        await q.edit_message_text("دسترسی ندارید.")
        return
    from ..utils import load_configs
    lines = load_configs("verified")
    if not lines:
        await q.edit_message_text("هیچ کانفیگی در verified نیست.", reply_markup=admin_menu())
        return
    cmap = _country_map()
    offset = context.user_data.get("publish_offset", _load_auto_offset())
    batch = _PUBLISH_PER_CYCLE
    chunk = lines[offset:offset + batch]
    if not chunk:
        context.user_data["publish_offset"] = 0
        await q.edit_message_text("همهٔ کانفیگ‌ها منتشر شدند. offset صفر شد.", reply_markup=admin_menu())
        return
    msgs = [_format_channel_msg(ln, cmap) for ln in chunk]
    channel = "@" + CHANNEL_USERNAME.lstrip("@")
    dry = (CHANNEL_PUBLISH != "live")
    preview = (f"📤 انتشارِ دستی در کانال\nکانال: {channel}\n"
               f"offset {offset} → {offset + len(chunk)} از {len(lines)}\n\n"
               + "\n\n".join(m for m in msgs[:3]))
    if len(msgs) > 3:
        preview += f"\n\n… و {len(msgs) - 3} کانفیگِ دیگر در این دسته."
    if dry:
        preview += ("\n\nحالت: DRY-RUN. برای post واقعی CHANNEL_PUBLISH=live تنظیم کنید "
                    "و بات را ادمین کانال کنید.")
        await q.edit_message_text(preview, reply_markup=admin_menu(), parse_mode="HTML")
        return
    sent = await _send_batch(context.bot, channel, msgs)
    context.user_data["publish_offset"] = (
        0 if offset + sent >= len(lines) else offset + sent
    )
    if sent == len(msgs):
        await q.edit_message_text(
            preview + f"\n\n✅ {sent} کانفیگ در کانال منتشر شد.",
            reply_markup=admin_menu(), parse_mode="HTML",
        )
    else:
        await q.edit_message_text(
            preview + f"\n\n⚠️ {sent} از {len(msgs)} ارسال شد؛ بقیه رد شدند "
            "(FloodWait یا خطای شبکه — لاگِ ربات را ببینید).",
            reply_markup=admin_menu(), parse_mode="HTML",
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
            async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
                r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                text = r.text
            from scripts.core import extract_valid_lines
            lines = extract_valid_lines(text)
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


# ──────────────────────────────────────────────────────────────────────────────
# انتشارِ خودکار (بدونِ دخالتِ دستی)
# ──────────────────────────────────────────────────────────────────────────────
_AUTO_STATE_PATH = REPO_ROOT / "data" / "auto_publish_state.json"

#: ۲۰ کانفیگ در هر دور، با فاصلهٔ تصادفی بین هر دو ارسال.
_PUBLISH_PER_CYCLE = 30
_PUBLISH_CYCLE_SECONDS = 40
#: فاصلهٔ پایه. تلگرام برای هر کانال حدود ۲۰ پیام در دقیقه اجازه می‌دهد؛
#: با اندازه‌گیریِ واقعی، ۴۰ و ۲۵ پیام در دقیقه هر دو «Flood control» دادند
#: (یک‌بار ۵۱۴ ثانیه قفل شد). ۳.۳ ثانیه ⇒ ~۱۸ پیام در دقیقه، پایین‌تر از
#: سقف، پس یک دورِ ۲۰تایی ~۶۵ ثانیه طول می‌کشد و پایدار می‌ماند.
_GAP_BASE = 1.0
_GAP_FLOOR = 1.0
_GAP_CEIL = 30.0
#: فلود‌کنترلِ تلگرام روی همهٔ متدها اعمال می‌شود؛ تا پایانش هیچ ارسالی
#: نمی‌کنیم تا جریمه تمدید نشود.
_flood_until = 0.0
_gap_base = _GAP_BASE
#: زمانی که این نمونه باید خاموش شود (epoch). صفر = بی‌نهایت.
#: در CI عمرِ هر برش محدود است؛ بدونِ این، یک دستهٔ ۲۰تایی می‌تواند از
#: لحظهٔ خاموشی رد شود و shutdown را قفل کند.
_deadline = 0.0


def set_run_deadline(epoch: float | None) -> None:
    global _deadline
    _deadline = float(epoch or 0.0)


def _time_left() -> float:
    return float("inf") if _deadline <= 0 else _deadline - time.time()
#: کفِ امن: کوچک‌ترین فاصله‌ای که تا حالا باعث جریمه شده؛ دیگر از آن پایین‌تر
#: نمی‌رویم تا هر چند دور یک‌بار دوباره به دیوارِ فلود نخوریم.
_min_gap = _GAP_FLOOR


def _load_auto_state() -> dict:
    try:
        with open(_AUTO_STATE_PATH, encoding="utf-8") as f:
            d = _json_mod.load(f)
        return {"offset": int(d.get("offset", 0)),
                "gap": float(d.get("gap", _GAP_BASE)),
                "min_gap": float(d.get("min_gap", _GAP_FLOOR))}
    except Exception:
        return {"offset": 0, "gap": _GAP_BASE, "min_gap": _GAP_FLOOR}


def _load_auto_offset() -> int:
    """offset ذخیره‌شده؛ در CI (هر برش یک ماشینِ تازه) از ساعت مشتق می‌شود.

    بدونِ این، هر برشِ Actions بی‌حافظه شروع می‌شد و همان ۲۰ کانفیگِ اول را
    دوباره به کانال می‌فرستاد. commitِ فایلِ وضعیت هم گزینه نبود: workflowِ
    تجمیع با force-push منتشر می‌کند و این فایل را پاک می‌کرد. پس نقطهٔ شروع
    را از زمان می‌گیریم؛ در هر برش هم به‌اندازهٔ ارسال‌ها جلو می‌رود.
    """
    if _AUTO_STATE_PATH.exists():
        return _load_auto_state()["offset"]
    if os.environ.get("GITHUB_ACTIONS"):
        return int(time.time() // _PUBLISH_CYCLE_SECONDS) * _PUBLISH_PER_CYCLE
    return 0


def _save_auto_offset(off: int) -> None:
    _save_auto_state(offset=off)


def _save_auto_state(offset: int | None = None, gap: float | None = None,
                     min_gap: float | None = None) -> None:
    try:
        cur = _load_auto_state()
        data = {
            "offset": int(cur["offset"] if offset is None else offset),
            "gap": round(float(cur["gap"] if gap is None else gap), 2),
            "min_gap": round(float(cur["min_gap"] if min_gap is None else min_gap), 2),
        }
        _AUTO_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_AUTO_STATE_PATH, "w", encoding="utf-8") as f:
            _json_mod.dump(data, f)
    except Exception:
        logger.warning("ذخیرهٔ وضعیتِ انتشار خودکار ناموفق بود", exc_info=True)


def _sync_gap() -> None:
    """فاصله و کفِ امنِ یادگرفته‌شده را از فایلِ وضعیت برمی‌دارد."""
    global _gap_base, _min_gap
    st = _load_auto_state()
    _min_gap = _clamp_gap(st["min_gap"])
    _gap_base = max(_min_gap, _clamp_gap(st["gap"]))


def _clamp_gap(g: float) -> float:
    try:
        return max(_GAP_FLOOR, min(_GAP_CEIL, float(g)))
    except (TypeError, ValueError):
        return _GAP_BASE


def _retry_seconds(exc: RetryAfter) -> float:
    """مقدارِ انتظارِ FloodWait را به ثانیه تبدیل می‌کند.

    در python-telegram-bot نسخهٔ ۲۰ به بعد `retry_after` یک `timedelta` است،
    نه عدد؛ `float(timedelta)` خطا می‌دهد و همان خطا کلِ ارسالِ خودکار را
    متوقف می‌کرد.
    """
    ra = getattr(exc, "retry_after", 0)
    try:
        return max(1.0, float(ra))
    except (TypeError, ValueError):
        return max(1.0, float(getattr(ra, "total_seconds", lambda: 5.0)()))


class _FloodStop(Exception):
    """جریمهٔ طولانیِ تلگرام: دورِ فعلی باید همین‌جا تمام شود."""


def _gap() -> float:
    """فاصلهٔ تصادفی دور و برِ فاصلهٔ یادگرفته‌شده (±۲۵٪)."""
    return random.uniform(_gap_base * 0.75, _gap_base * 1.25)


async def _send_one(bot, channel: str, text: str, attempts: int = 3) -> bool:
    """یک پیام را می‌فرستد و در برابر FloodWait/شبکه مقاوم است.

    خطاها لاگ می‌شوند؛ قبلاً بی‌صدا بلعیده می‌شدند و معلوم نبود چرا هیچ
    کانفیگی به کانال نمی‌رسد.
    """
    global _flood_until, _gap_base
    for attempt in range(attempts):
        try:
            await bot.send_message(chat_id=channel, text=text, parse_mode="HTML",
                                   disable_web_page_preview=True)
            return True
        except RetryAfter as exc:
            wait = _retry_seconds(exc)
            if wait > 20:
                # جریمهٔ سنگین: ادامه دادن، جریمه را تمدید می‌کند. کلِ دور را
                # متوقف می‌کنیم و فاصله را برای دورهای بعدی زیاد می‌کنیم.
                _flood_until = time.time() + wait + 3
                _min_gap = _clamp_gap(_gap_base * 1.6)
                _gap_base = _min_gap
                _save_auto_state(gap=_gap_base, min_gap=_min_gap)
                logger.warning("تلگرام %.0f ثانیه قفل کرد؛ فاصله به %.1fs زیاد شد",
                               wait, _gap_base)
                raise _FloodStop
            logger.warning("FloodWait %.0fs (تلاش %d/%d) — صبر می‌کنیم",
                           wait, attempt + 1, attempts)
            await asyncio.sleep(wait + 1)
        except TimedOut:
            logger.warning("TimedOut در ارسال (تلاش %d/%d)", attempt + 1, attempts)
            await asyncio.sleep(2.0 * (attempt + 1))
        except NetworkError as exc:
            logger.warning("NetworkError در ارسال: %s (تلاش %d/%d)",
                           exc, attempt + 1, attempts)
            await asyncio.sleep(3.0 * (attempt + 1))
        except BadRequest as exc:
            logger.error("BadRequest در ارسال به کانال: %s", exc)
            return False
    logger.error("ارسال یک کانفیگ پس از %d تلاش ناموفق ماند", attempts)
    return False


async def _send_batch(bot, channel: str, msgs: list[str]) -> int:
    """پیام‌ها را با فاصلهٔ تصادفی می‌فرستد؛ تعدادِ ارسال‌شده را برمی‌گرداند.

    اگر عمرِ این نمونه در حال تمام شدن باشد، دسته را نیمه‌کاره نمی‌گذارد ولی
    از شروعِ دستهٔ بعدی هم خودداری می‌کند (به `auto_publish_job` نگاه کنید).
    """
    sent = 0
    for i, m in enumerate(msgs):
        try:
            if await _send_one(bot, channel, m):
                sent += 1
        except _FloodStop:
            break
        if i < len(msgs) - 1:
            await asyncio.sleep(_gap())
    return sent


_AUTO_PUBLISH_LOCK = asyncio.Lock()


#: کلِ فهرستِ verified اسکن می‌شود، نه یک برشِ ثابت از ابتدای آن. با برشِ
#: ثابت (۴۰۰ خط) پس از مهاجرتِ دفترِ idempotency هیچ چیزِ تازه‌ای پیدا نمی‌شد و
#: صف برای همیشه خالی می‌ماند — با اجرای واقعی دیده شد. `enqueue` روی کلید،
#: «درج یا نادیده‌گرفتن» است، پس اسکنِ کامل هزینه‌اش ناچیز است.
_ENQUEUE_SCAN = 20000


async def _drain_outbox(bot, channel: str, limit: int = _PUBLISH_PER_CYCLE) -> int:
    """صف را تا سقفِ `limit` پیام خالی می‌کند؛ تعدادِ ارسال را برمی‌گرداند.

    سقف عمدی است: بدونِ سقف، یک فراخوانی می‌تواند صدها پیام (چند ساعت) قفل را
    نگه دارد و هیچ لاگ/عددی به وضعیت نرسد. با سقفِ ۲۰، هر دور یک خطِ لاگ و
    یک به‌روزرسانیِ شمارنده دارد و انسدادِ قفل کوتاه می‌ماند.
    """
    from ..outbox import due, mark_failed, mark_sent

    sent = 0
    while sent < limit:
        if _time_left() < 8:
            logger.info("وقتِ این برش تمام است؛ صف برای دورِ بعد می‌ماند")
            break
        rows = due(limit=1)
        if not rows:
            break
        row = rows[0]
        try:
            ok = await _send_one(bot, channel, row["text"])
        except _FloodStop:
            break                     # جریمهٔ تلگرام: بقیه در صف می‌مانند
        if ok:
            mark_sent(row["key"])     # بی‌درنگ، بدونِ کارِ دیگر در این میان
            sent += 1
        else:
            attempts = mark_failed(row["key"], "send failed")
            logger.warning("ارسال ناموفق (تلاش %d) — پیام در صف می‌ماند", attempts)
        await asyncio.sleep(_gap())
    return sent


async def auto_publish_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """صفِ کانال را با کانفیگ‌های *جدید* پر می‌کند و با فاصلهٔ تصادفی خالی می‌کند.

    هر کانفیگ با فاصلهٔ تصادفی حدودِ ۲.۵ تا ۴ ثانیه از کانفیگِ قبلی
    فرستاده می‌شود تا ارسال یکنواخت و شبیهِ اسپم به نظر نرسد. فاصله در
    `data/auto_publish_state.json` ذخیره می‌شود و اگر تلگرام جریمه کند
    خودکار بزرگ‌تر می‌ماند. اگر دورِ قبلی هنوز تمام نشده، این اجرا رد
    می‌شود تا ارسال‌ها روی هم نیفتند.
    """
    global _gap_base
    if CHANNEL_PUBLISH != "live":
        return
    remaining = _flood_until - time.time()
    if remaining > 0:
        logger.info("جریمهٔ تلگرام فعال است؛ %.0f ثانیهٔ دیگر ادامه می‌دهیم", remaining)
        return
    if _AUTO_PUBLISH_LOCK.locked():
        logger.info("دورِ قبلی انتشار خودکار هنوز تمام نشده؛ این دور رد شد")
        return
    if _time_left() < 25:
        logger.info("عمرِ این برش برای ارسال کافی نیست (%.0fs) — دورِ بعد", _time_left())
        return
    _sync_gap()
    async with _AUTO_PUBLISH_LOCK:
        try:
            from ..outbox import enqueue, stats
            from ..utils import load_configs
            lines = load_configs("verified")
        except Exception:
            logger.warning("خواندنِ کانفیگ‌ها برای انتشار خودکار ناموفق بود", exc_info=True)
            return
        if not lines:
            logger.warning("هیچ کانفیگِ verified برای انتشار نیست")
            return
        channel = "@" + CHANNEL_USERNAME.lstrip("@")
        cmap = _country_map()
        # هر کانفیگ یک کلیدِ محتوایی دارد؛ صف و دفترِ idempotency تضمین می‌کنند
        # یک کانفیگ با هیچ ری‌استارت/برشی دو بار به کانال نرود.
        from ..outbox import config_key
        scan = min(_ENQUEUE_SCAN, max(1, 2 * len(lines)))
        added = enqueue([(config_key(ln), _format_channel_msg(ln, cmap))
                         for ln in lines[:scan]])
        sent = await _drain_outbox(context.bot, channel)
        st = stats()
        try:
            from scripts import status as rt
            rt.set_counts(queued=st["pending"], sent=st["sent_total"],
                          send_failed=st["failed_attempts"])
        except Exception:
            pass
        if sent and st["pending"] == 0:
            # صف خالی شد: کمی سرعت را به هدفِ اصلی نزدیک کن (ولی هرگز زیرِ کفِ
            # امنی که تلگرام تحمیل کرده).
            _gap_base = max(_min_gap, _clamp_gap(_gap_base * 0.96))
            _save_auto_state(gap=_gap_base)
        logger.info("انتشار: +%d صف، %d ارسال، %d در صف، %d کل (فاصله %.1fs)",
                    added, sent, st["pending"], st["sent_total"], _gap_base)


async def trigger_aggregate_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """هر ساعت workflowِ aggregate را از طریق repository_dispatch trigger می‌کند (async)."""
    if not GITHUB_TOKEN:
        return
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(
                f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/dispatches",
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github+json"},
                json={"event_type": "aggregate-now"},
            )
    except Exception:
        pass
