from telegram import Update
from telegram.ext import ContextTypes

from ..config import is_owner
from ..db import add_user, is_admin
from ..keyboards import main_menu, protocols_menu, categories_menu
from ..utils import (load_configs, filter_by_protocol, filter_by_country,
                     chunk_text, subscription_urls)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        add_user(user.id, user.username)
    admin = bool(user and (is_admin(user.id) or is_owner(user.id)))
    await update.message.reply_text(
        "خوش آمدید! کانفیگ معتبر را انتخاب کنید:",
        reply_markup=main_menu(admin),
    )


async def latest20(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    lines = load_configs("verified", 20)
    if not lines:
        await q.edit_message_text("کانفیگی موجود نیست. ابتدا pipeline را اجرا کنید.")
        return
    for chunk in chunk_text(lines):
        await q.message.reply_text(chunk)


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("دسته‌بندی را انتخاب کنید:", reply_markup=categories_menu())


async def cat_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    bucket = q.data.split(":", 1)[1]
    lines = load_configs(bucket)
    if not lines:
        hint = {
            "google": (
                "این دسته فقط با آزمونِ واقعیِ گوگل ساخته می‌شود: "
                "pipeline → googleready با xray-knife و ۲ دورِ "
                "gstatic/YouTube/Play/generate_204/Maven/Gemini. "
                "در رانرِ CI ساخته و همان‌جا منتشر می‌شود؛ در اجرای محلی "
                "تا وقتی googleready اجرا نشود خالی است."
            ),
            "top100": "این فایل با pipeline و آزمونِ سه‌دوره‌ای ساخته می‌شود.",
        }.get(bucket, "این دسته پس از اجرای pipeline پُر می‌شود.")
        await q.edit_message_text(
            f"دستهٔ {bucket} خالی است.\n{hint}",
            reply_markup=categories_menu(),
        )
        return
    await q.edit_message_text(f"{len(lines)} کانفیگ در دستهٔ {bucket}:")
    for chunk in chunk_text(lines[:100]):
        await q.message.reply_text(chunk)
    await q.message.reply_text("بازگشت:", reply_markup=categories_menu())


async def ask_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    context.user_data["mode"] = "country"
    await q.edit_message_text("نام/کد کشور را بفرستید (مثلاً NL یا Netherlands):")


async def ask_proto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("پروتکل را انتخاب کنید:", reply_markup=protocols_menu())


async def ask_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    context.user_data["mode"] = "count"
    await q.edit_message_text("تعداد مورد نظر (1-100) را بفرستید:")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mode = context.user_data.get("mode")
    text = (update.message.text or "").strip()
    if mode == "country":
        context.user_data.pop("mode", None)
        lines = filter_by_country(load_configs("verified"), text)
        if not lines:
            await update.message.reply_text("چیزی یافت نشد.")
            return
        for chunk in chunk_text(lines[:50]):
            await update.message.reply_text(chunk)
    elif mode == "count":
        context.user_data.pop("mode", None)
        try:
            n = max(1, min(100, int(text)))
        except ValueError:
            await update.message.reply_text("عدد نامعتبر.")
            return
        lines = load_configs("verified", n)
        for chunk in chunk_text(lines):
            await update.message.reply_text(chunk)
    else:
        # treat as free-text country search fallback
        lines = filter_by_country(load_configs("verified"), text)
        if lines:
            for chunk in chunk_text(lines[:20]):
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text("برای شروع /start را بزنید.")


async def proto_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    proto = q.data.split(":", 1)[1]
    lines = filter_by_protocol(load_configs("verified"), proto)
    if not lines:
        await q.edit_message_text(f"کانفیگ {proto} یافت نشد.")
        return
    await q.edit_message_text(f"{len(lines)} کانفیگ {proto.upper()}:")
    for chunk in chunk_text(lines[:50]):
        await q.message.reply_text(chunk)


async def sub_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ارسال لینک‌های ساب‌سکریپشنِ برندشده (فایل‌های واقعیِ موجود)."""
    q = update.callback_query
    if q:
        await q.answer()
        reply = q.message.reply_text
    else:
        reply = update.message.reply_text
    lines = ["📥 لینک‌های ساب‌سکریپشن (برندشده — همهٔ کانفیگ‌ها remark/نامِ برند دارند):", ""]
    for title, url, desc in subscription_urls():
        lines.append(f"{title}")
        lines.append(f"`{url}`")
        lines.append(f"_{desc}_")
        lines.append("")
    lines.append("کپی کنید یا در کلاینت import کنید. تعداد و پروتکل با index.json می‌خواند.")
    await reply("\n".join(lines), parse_mode="Markdown")
    if q:
        u = q.from_user
        await q.message.reply_text("بازگشت:", reply_markup=main_menu(
            bool(u and (is_admin(u.id) or is_owner(u.id)))))


async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    user = q.from_user
    admin = bool(user and (is_admin(user.id) or is_owner(user.id)))
    await q.edit_message_text("منوی اصلی:", reply_markup=main_menu(admin))
