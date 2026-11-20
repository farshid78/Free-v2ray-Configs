import logging
import re

from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

from .config import BOT_TOKEN
from .db import add_admin
from .handlers import user, admin
from .keyboards import main_menu


logging.basicConfig(level=logging.INFO)

# httpx logs every request URL and the bot's URLs carry the token in the path.
# Masking happens in the formatter, not in a filter on record.args: httpx passes
# an httpx.URL object (not a str) as an argument, so a filter would leave it
# untouched while the formatter rendered the raw secret.
_TOKEN_RE = re.compile(r"bot\d+:[A-Za-z0-9_-]{20,}")


class _MaskFormatter(logging.Formatter):
    """Replace `bot<id>:<secret>` with `bot<TOKEN>` in the rendered line."""

    def format(self, record: logging.LogRecord) -> str:
        return _TOKEN_RE.sub("bot<TOKEN>", super().format(record))


for _handler in logging.getLogger().handlers:
    _handler.setFormatter(_MaskFormatter())


async def _route_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # admin text modes take priority
    if context.user_data.get("mode") in ("broadcast", "addadmin", "removeadmin") or (context.user_data.get("mode") or "").startswith("addsource_"):
        await admin.handle_admin_text(update, context)
        return
    if context.user_data.get("mode") in ("country", "count"):
        await user.handle_text(update, context)
        return
    # default: try country search
    await user.handle_text(update, context)


def build_app() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", user.start))
    app.add_handler(CommandHandler("sub", user.sub_link))
    app.add_handler(CommandHandler("health", admin.adm_stats))

    # callback routing
    app.add_handler(CallbackQueryHandler(user.latest20, pattern="^latest20$"))
    app.add_handler(CallbackQueryHandler(user.categories, pattern="^categories$"))
    app.add_handler(CallbackQueryHandler(user.cat_selected, pattern="^cat:"))
    app.add_handler(CallbackQueryHandler(user.ask_country, pattern="^ask_country$"))
    app.add_handler(CallbackQueryHandler(user.ask_proto, pattern="^ask_proto$"))
    app.add_handler(CallbackQueryHandler(user.ask_count, pattern="^ask_count$"))
    app.add_handler(CallbackQueryHandler(user.proto_selected, pattern="^proto:"))
    app.add_handler(CallbackQueryHandler(user.back_main, pattern="^back_main$"))
    app.add_handler(CallbackQueryHandler(admin.admin_panel, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(admin.adm_stats, pattern="^adm_stats$"))
    app.add_handler(CallbackQueryHandler(admin.adm_trigger, pattern="^adm_trigger$"))
    app.add_handler(CallbackQueryHandler(admin.adm_broadcast, pattern="^adm_broadcast$"))
    app.add_handler(CallbackQueryHandler(admin.adm_addadmin, pattern="^adm_addadmin$"))
    app.add_handler(CallbackQueryHandler(admin.adm_removeadmin, pattern="^adm_removeadmin$"))
    app.add_handler(CallbackQueryHandler(admin.adm_sources, pattern="^adm_sources$"))
    app.add_handler(CallbackQueryHandler(admin.adm_source_toggle, pattern="^src:"))
    app.add_handler(CallbackQueryHandler(admin.adm_source_remove, pattern="^srcrm:"))
    app.add_handler(CallbackQueryHandler(admin.adm_cats_help, pattern="^adm_cats_help$"))
    app.add_handler(CallbackQueryHandler(admin.adm_addsource, pattern="^adm_addsource$"))
    app.add_handler(CallbackQueryHandler(admin.adm_addsource_cat, pattern="^addsrc:"))
    app.add_handler(CallbackQueryHandler(admin.adm_scan, pattern="^adm_scan$"))
    app.add_handler(CallbackQueryHandler(admin.adm_scan_cat, pattern="^scancat:"))
    app.add_handler(CallbackQueryHandler(user.sub_link, pattern="^sub_link$"))
    app.add_handler(CallbackQueryHandler(admin.adm_publish, pattern="^adm_publish$"))
    app.add_handler(CallbackQueryHandler(admin.adm_publish_configs, pattern="^adm_publish_configs$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _route_text))
    return app


def main() -> None:
    app = build_app()
    # انتشارِ خودکار: هر ۳۰ ثانیه ۲۰ کانفیگ (با فاصلهٔ تصادفی) + trigger ساعتی
    # workflow. خطای زمان‌بندی قبلاً بی‌صدا بلعیده می‌شد و هیچ کانفیگی به کانال
    # نمی‌رسید؛ الان در لاگ دیده می‌شود.
    try:
        from .handlers import admin as _admin
        app.job_queue.run_repeating(_admin.auto_publish_job,
                                    interval=_admin._PUBLISH_CYCLE_SECONDS, first=10)
        app.job_queue.run_repeating(_admin.trigger_aggregate_job, interval=3600, first=300)
        logging.info("انتشار خودکار فعال شد: ۲۰ کانفیگ در هر ۳۰ ثانیه")
    except Exception:
        logging.exception("زمان‌بندیِ انتشار خودکار فعال نشد — کانفیگی به کانال نمی‌رود")
    try:
        app.run_polling()
    except (TimedOut, NetworkError) as exc:
        # شبکهٔ ایران معمولاً به api.telegram.org نمی‌رسد. این خطای محیط است،
        # نه باگِ ربات؛ یک خطِ روشن به‌جای tracebackِ چندصفحه‌ای.
        print(f"[warn] telegram API unreachable ({type(exc).__name__}); "
              f"bot did not start polling", flush=True)
        raise SystemExit(3)


if __name__ == "__main__":
    main()
