from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .config import MINI_APP_URL


def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = []
    # تلگرام Web App را فقط با HTTPS می‌پذیرد؛ اگر آدرس خالی/غیرِHTTPS باشد
    # دکمه حذف می‌شود. دلیلش تجربهٔ واقعی است: یک `MINI_APP_URL=` تهی باعث
    # می‌شد تلگرام کلِ پیامِ /start را با «URL host is empty» رد کند و کاربر
    # هیچ پاسخی نبیند — یک دکمهٔ کم، بهتر از یک منوی مرده است.
    if MINI_APP_URL.startswith("https://"):
        rows.append([InlineKeyboardButton("🌐 پنل گلس (Mini App)",
                                          web_app=WebAppInfo(url=MINI_APP_URL))])
    rows += [
        [InlineKeyboardButton("📥 دریافت لینک‌های ساب", callback_data="sub_link")],
        [InlineKeyboardButton("📦 آخرین 20 کانفیگ", callback_data="latest20")],
        [InlineKeyboardButton("📚 دسته‌بندی‌ها", callback_data="categories"),
         InlineKeyboardButton("🌍 فیلتر کشور", callback_data="ask_country")],
        [InlineKeyboardButton("⚙️ فیلتر پروتکل", callback_data="ask_proto"),
         InlineKeyboardButton("🔢 تعداد سفارشی", callback_data="ask_count")],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton("🛡️ پنل ادمین", callback_data="admin_panel")])
    return InlineKeyboardMarkup(rows)


def categories_menu() -> InlineKeyboardMarkup:
    from .utils import CATEGORY_LABELS
    rows = []
    keys = ["top100", "verified", "fast", "secure", "google", "all", "heavy", "light"]
    for k in keys:
        rows.append([InlineKeyboardButton(CATEGORY_LABELS[k], callback_data=f"cat:{k}")])
    rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 آمار", callback_data="adm_stats"),
         InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")],
        [InlineKeyboardButton("📢 انتشار در کانال (dry-run/live)", callback_data="adm_publish")],
        [InlineKeyboardButton("📤 انتشارِ تکیِ کانفیگ‌ها (۵ تایی)", callback_data="adm_publish_configs")],
        [InlineKeyboardButton("🔄 Trigger aggregate", callback_data="adm_trigger")],
        [InlineKeyboardButton("📋 منابع و مدیریت", callback_data="adm_sources")],
        [InlineKeyboardButton("🔍 اسکن/استخراج از URL", callback_data="adm_scan")],
        [InlineKeyboardButton("➕ افزودن ادمین", callback_data="adm_addadmin"),
         InlineKeyboardButton("➖ حذف ادمین", callback_data="adm_removeadmin")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
    ])


def protocols_menu() -> InlineKeyboardMarkup:
    protos = ["vless", "vmess", "trojan", "ss", "hysteria"]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(p.upper(), callback_data=f"proto:{p}") for p in protos[:3]],
        [InlineKeyboardButton(p.upper(), callback_data=f"proto:{p}") for p in protos[3:]],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
    ])
