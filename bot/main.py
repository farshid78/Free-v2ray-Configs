import asyncio
import logging
import re
import time

import httpx

from telegram import Update
from telegram.error import Conflict, NetworkError, TimedOut
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

from .config import BOT_TOKEN, RUN_MINUTES
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


async def _another_instance_polls(token: str) -> bool:
    """آیا نمونهٔ دیگری با همین توکن در حال poll است؟

    تلگرام برای هر ربات فقط یک `getUpdates` هم‌زمان اجازه می‌دهد و به دومی
    `409 Conflict` می‌دهد. این بررسی پیش از start_polling انجام می‌شود چون
    خودِ کتابخانه ۴۰۹ را در حلقهٔ شبکه‌اش می‌گیرد و فقط لاگ می‌کند؛ نتیجه در
    عمل یک برشِ ۲۵ دقیقه‌ایِ بی‌کار بود که تا تایم‌اوت job زنده می‌ماند.

    `limit=1` و `timeout=0` هیچ updateای را حذف نمی‌کند: تا وقتی offset تأیید
    نشود، آپدیت‌ها در صفِ تلگرام می‌مانند و poll بعدی دوباره می‌گیردشان.
    """
    # ⚠️ عمداً `app.bot` استفاده نمی‌شود: کلاینتِ HTTPِ آن به loop فعلی گره
    # می‌خورد و وقتی probe را در یک loop جداگانه اجرا می‌کنیم، همان کلاینت در
    # اولین ارسال با «Event loop is closed» می‌ترکد (با اجرای واقعی دیده شد).
    # یک کلاینتِ مستقل که در همین loop بسته می‌شود، این نشتی را ندارد.
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                f"https://api.telegram.org/bot{token}/getUpdates",
                params={"timeout": 0, "limit": 1},
            )
        return r.status_code == 409
    except Exception:      # شبکه/توکن: اجازه بده start_polling خودش تصمیم بگیرد
        return False


async def heartbeat_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """هر دقیقه وضعیتِ «آنلاین» را با زمانِ زنده مینویسد و منتشر می‌کند.

    داشبورد با همین heartbeat سنِ آخرین تماس را نشان می‌دهد؛ نبودِ آن یعنی
    ربات آفلاین است — نه این‌که «آخرین workflow سبز بود».
    """
    try:
        from scripts import status as rt
        rt.heartbeat(note=f"run_minutes={RUN_MINUTES}")
        await asyncio.get_event_loop().run_in_executor(None, rt.publish)
    except Exception:
        pass


async def status_publish_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """وضعیت را هر چند دقیقه روی شاخهٔ state منتشر می‌کند (fail-open)."""
    try:
        from scripts import status as rt
        await asyncio.get_event_loop().run_in_executor(None, rt.publish)
    except Exception:
        pass


def _schedule_lifetime(app: Application) -> None:
    """ربات را پس از `BOT_RUN_MINUTES` تمیز خاموش می‌کند.

    چرا لازم است: روی GitHub Actions هر برش باید خودش پیش از سقفِ job تمام
    شود. اگر منتظر kill شدنِ job بمانیم، خاموشی ناگهانی است و آخرین ارسال‌ها
    و offset ذخیره نمی‌شوند.
    """
    if RUN_MINUTES <= 0:
        return

    async def _stop(context: ContextTypes.DEFAULT_TYPE) -> None:
        # `stop_running()` (نه `stop()`): خودِ `run_polling` بعد از این پرچم
        # به‌ترتیب updater و job_queue را می‌بندد. فراخوانیِ مستقیمِ `stop()`
        # از داخلِ یک job، loop را زیرِ پای همان job می‌بندد — با اجرای واقعی
        # دیده شد که پروسه تا تایم‌اوت زنده ماند و `Event loop is closed` داد.
        logging.info("⏹️ عمرِ این برش تمام شد (%.1f دقیقه) — خاموشیِ تمیز", RUN_MINUTES)
        context.application.stop_running()

    app.job_queue.run_once(_stop, when=RUN_MINUTES * 60)
    logging.info("عمرِ این نمونه: %.1f دقیقه", RUN_MINUTES)


def main() -> None:
    # runtime watchdog: exit the process if heartbeat goes stale (>120s) so the
    # runner/supervisor can restart it instead of leaving a zombie.
    try:
        from . import watchdog as _watchdog
        _watchdog.start()
    except Exception:
        pass
    app = build_app()
    # انتشارِ خودکار: هر ۳۰ ثانیه ۲۰ کانفیگ (با فاصلهٔ تصادفی) + trigger ساعتی
    # workflow. خطای زمان‌بندی قبلاً بی‌صدا بلعیده می‌شد و هیچ کانفیگی به کانال
    # نمی‌رسید؛ الان در لاگ دیده می‌شود.
    try:
        from .handlers import admin as _admin
        if RUN_MINUTES > 0:
            _admin.set_run_deadline(time.time() + RUN_MINUTES * 60)
        app.job_queue.run_repeating(_admin.auto_publish_job,
                                    interval=_admin._PUBLISH_CYCLE_SECONDS, first=10)
        app.job_queue.run_repeating(_admin.trigger_aggregate_job, interval=900, first=300)
        app.job_queue.run_repeating(heartbeat_job, interval=60, first=1)
        # انتشارِ وضعیت هر ۵ دقیقه: داشبورد باید «آنلاین/آفلاین» را واقعی ببیند.
        app.job_queue.run_repeating(status_publish_job, interval=120, first=30)
        logging.info("انتشار خودکار فعال شد: صفِ ۲۰تایی با فاصلهٔ تصادفی")
    except Exception:
        logging.exception("زمان‌بندیِ انتشار خودکار فعال نشد — کانفیگی به کانال نمی‌رود")
    _schedule_lifetime(app)
    # بررسیِ ۴۰۹ روی یک loop مستقل؛ بعدش یک loop تازه به‌عنوانِ current
    # می‌گذاریم، چون `asyncio.run` آن را پاک می‌کند و `run_polling` بعدی
    # `RuntimeError: There is no current event loop` می‌دهد.
    # انتشارِ فوری تا داشبورد از همان ابتدای برش «آنلاین» ببیند.
    try:
        from scripts import status as _rt
        _rt.heartbeat(note=f"run_minutes={RUN_MINUTES}")
        _rt.publish()
    except Exception:
        pass

    probe = asyncio.new_event_loop()
    try:
        busy = probe.run_until_complete(_another_instance_polls(BOT_TOKEN))
    finally:
        probe.close()
    asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        if busy:
            logging.warning(
                "نمونهٔ دیگری از همین ربات در حال poll است (409) — این برش "
                "بدونِ ارسالِ هیچ پیامی کنار می‌رود. اگر ربات را روی کامپیوترِ "
                "خودتان هم روشن گذاشته‌اید، همان کافی است.")
            return
        app.run_polling()
    except Conflict:
        # دو نمونه با یک توکن نمی‌توانند هم‌زمان getUpdates بزنند. در زنجیرهٔ
        # Actions این حالت نباید رخ بدهد (concurrency سریالی می‌کند)، ولی اگر
        # رباتِ محلیِ کاربر هم روشن باشد، برشِ CI باید بی‌سروصدا کنار برود،
        # نه این‌که با traceback بترکد.
        logging.warning("نمونهٔ دیگری از همین ربات در حال poll است (409 Conflict) — "
                        "این نمونه کنار می‌رود")
        return
    except (TimedOut, NetworkError) as exc:  # noqa: BLE001
        # شبکهٔ ایران معمولاً به api.telegram.org نمی‌رسد. این خطای محیط است،
        # نه باگِ ربات؛ یک خطِ روشن به‌جای tracebackِ چندصفحه‌ای.
        print(f"[warn] telegram API unreachable ({type(exc).__name__}); "
              f"bot did not start polling", flush=True)
        raise SystemExit(3)
    finally:
        # خروج (خواه عمرِ برش تمام شده باشد، خواه ۴۰۹/قطعیِ شبکه): وضعیت
        # آنلاین را پاک کن تا داشبورد واقعیت را نشان دهد، نه وضعیتِ کهنه.
        try:
            from scripts import status as rt
            rt.bot_offline("stopped")
            rt.publish()
        except Exception:
            pass


if __name__ == "__main__":
    main()
