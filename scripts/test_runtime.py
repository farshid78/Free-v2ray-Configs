#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تست‌های لایهٔ رانتایم: قفلِ چرخه، وضعیتِ ماندگار، صفِ ارسال و idempotency.

هر تست به یک نقصِ واقعی گره خورده است (نه پوششِ تزئینی):

• `test_second_cycle_is_refused`  — دو چرخهٔ هم‌زمان نباید هم‌پوشانی کنند.
• `test_lock_expires_after_ttl`    — اجرای کشته‌شده نباید قفل را برای همیشه
                                     نگه دارد (راه‌اندازیِ خودکار باید ممکن باشد).
• `test_corrupt_state_recovers`    — فایلِ وضعیتِ خراب نباید چرخهٔ سالم را بشکند.
• `test_stage_and_history`         — گزارشِ هر مرحله و تاریخچهٔ چرخه‌ها ذخیره شود.
• `test_outbox_never_resends`      — یک کانفیگ دو بار به کانال نرود.
• `test_outbox_backoff_grows`      — Retry با تأخیرِ افزایشی، و پیام در صف بماند.
• `test_outbox_survives_restart`   — اتصالِ دوباره به دیتابیس، صف را از دست ندهد
                                     (شبیه‌سازیِ ری‌استارتِ برش).

اجرا:  python -X utf8 scripts/test_runtime.py
"""

from __future__ import annotations

import asyncio
import contextlib
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.status as st          # noqa: E402
import bot.outbox as ob              # noqa: E402


def _isolate(case: unittest.TestCase) -> tempfile.TemporaryDirectory:
    """وضعیت و صف را به یک پوشهٔ موقت منتقل می‌کند تا تست روی دادهٔ واقعی ننویسد."""
    tmp = tempfile.TemporaryDirectory()
    d = Path(tmp.name)
    case.addCleanup(tmp.cleanup)
    st.STATE_DIR = d
    st.STATE_PATH = d / "status.json"
    st.LOCK_PATH = d / ".filelock"
    ob.OUTBOX_DB = d / "outbox.db"
    return tmp


class StatusTests(unittest.TestCase):
    def setUp(self) -> None:
        _isolate(self)

    def test_second_cycle_is_refused(self) -> None:
        ok, owner = st.begin("aggregate", ttl_min=5)
        self.assertTrue(ok)
        ok2, why = st.begin("aggregate", ttl_min=5, owner="other-machine:1")
        self.assertFalse(ok2, "چرخهٔ دوم نباید هم‌زمان شروع شود")
        self.assertIn("already running", why)
        st.release(owner)
        ok3, _ = st.begin("aggregate", ttl_min=5, owner="other-machine:1")
        self.assertTrue(ok3, "پس از آزادکردنِ قفل باید بتواند شروع کند")

    def test_lock_expires_after_ttl(self) -> None:
        ok, owner = st.begin("aggregate", ttl_min=0.02)   # ~۱.۲ ثانیه
        self.assertTrue(ok)
        ok2, _ = st.begin("aggregate", ttl_min=5, owner="restarted:2")
        self.assertFalse(ok2)
        time.sleep(1.4)
        ok3, _ = st.begin("aggregate", ttl_min=5, owner="restarted:2")
        self.assertTrue(ok3, "قفلِ رهاشده پس از TTL باید آزاد شود")

    def test_corrupt_state_recovers(self) -> None:
        st.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        st.STATE_PATH.write_text("{ this is not json", encoding="utf-8")
        data = st.load()
        self.assertEqual(data["schema"], st.SCHEMA)
        ok, _ = st.begin("aggregate", ttl_min=1)
        self.assertTrue(ok, "وضعیتِ خراب باید fail-open رفتار کند")

    def test_stage_and_history(self) -> None:
        st.begin("aggregate", ttl_min=5)
        st.stage("collection", "ok", "11495 configs")
        st.set_stage_duration("collection", 41.5)
        st.finish(ok=True, counts={"collected": 11495, "verified": 1139})
        data = st.load()
        self.assertEqual(data["cycle"]["stages"]["collection"]["duration_s"], 41.5)
        self.assertTrue(data["cycle"]["ok"])
        self.assertEqual(data["counts"]["verified"], 1139)
        self.assertEqual(len(data["history"]), 1)
        self.assertIsNone(data["lock"]["owner"], "پایانِ چرخه باید قفل را آزاد کند")

    def test_bot_online_flag_follows_heartbeat_age(self) -> None:
        st.heartbeat(pid=1234, note="test")
        self.assertTrue(st.summarize()["bot"]["online"])
        data = st.load()
        data["bot"]["last_heartbeat"] = "2020-01-01T00:00:00Z"
        st.save(data)
        self.assertFalse(st.summarize()["bot"]["online"], "heartbeatِ کهنه = آفلاین")


class OutboxTests(unittest.TestCase):
    def setUp(self) -> None:
        _isolate(self)

    def test_outbox_never_resends(self) -> None:
        items = [(ob.config_key("vless://a@h:443#x"), "<code>vless://a@h:443#x</code>")]
        self.assertEqual(ob.enqueue(items), 1)
        rows = ob.due(limit=5)
        self.assertEqual(len(rows), 1)
        ob.mark_sent(rows[0]["key"])
        self.assertEqual(ob.due(limit=5), [], "پیامِ ارسال‌شده نباید دوباره در صف بیاید")
        # تلاشِ دوباره برای صف‌کردنِ همان کانفیگ (مثلاً برشِ بعدی) باید بی‌اثر باشد
        self.assertEqual(ob.enqueue(items), 0)
        self.assertTrue(ob.seen(items[0][0]))

    def test_outbox_backoff_grows(self) -> None:
        key = ob.config_key("vmess://abc")
        ob.enqueue([(key, "<code>vmess://abc</code>")])
        a1 = ob.mark_failed(key, "network")
        self.assertEqual(a1, 1)
        self.assertEqual(ob.due(limit=5), [],
                         "پس از شکست، پیام باید در صف بماند ولی فوراً دوباره تلاش نشود")
        # اتصالِ دستی باید بسته شود، وگرنه روی ویندوز فایلِ tmp قفل می‌ماند
        # (همین تست با نشتِ اتصال، cleanup را می‌شکست).
        with contextlib.closing(ob._conn()) as c:
            row = c.execute("SELECT attempts, last_error FROM outbox WHERE key=?",
                            (key,)).fetchone()
            self.assertEqual(row["attempts"], 1)
            self.assertEqual(row["last_error"], "network")
            # انقضای backoff را برای تست جلو می‌اندازیم
            c.execute("UPDATE outbox SET next_at=? WHERE key=?", (time.time() - 1, key))
            c.commit()
        self.assertEqual(len(ob.due(limit=5)), 1, "بعد از پنجرهٔ backoff باید دوباره تلاش شود")

    def test_outbox_survives_restart(self) -> None:
        key = ob.config_key("trojan://pw@h:443")
        ob.enqueue([(key, "<code>trojan://pw@h:443</code>")])
        # ری‌استارت: هیچ حالتِ درون‌حافظه‌ای وجود ندارد؛ صف باید از دیسک بیاید
        self.assertEqual(ob.stats()["pending"], 1)
        self.assertEqual(len(ob.due(limit=1)), 1)

    def test_stats_reports_queue_depth(self) -> None:
        ob.enqueue([(ob.config_key(f"ss://{i}"), f"<code>ss://{i}</code>") for i in range(3)])
        s = ob.stats()
        self.assertEqual(s["pending"], 3)
        self.assertEqual(s["sent_total"], 0)
        self.assertGreaterEqual(s["oldest_age_s"], 0)


class DrainTests(unittest.TestCase):
    """رفتارِ ارسال: خطای کانال نباید پیام را دور بریزد و نباید دوباره بفرستد."""

    def setUp(self) -> None:
        _isolate(self)
        from bot.handlers import admin as A
        self.A = A
        A._gap_base = 0.01
        A._min_gap = 0.01
        A._deadline = 0.0            # بدونِ مهلت: کلِ صف در تست در دسترس باشد

    def test_failed_send_stays_queued(self) -> None:
        from telegram.error import BadRequest

        key = ob.config_key("vless://fail@h:443")
        ob.enqueue([(key, "<code>vless://fail@h:443</code>")])

        class BadBot:
            async def send_message(self, **kw):
                raise BadRequest("not enough rights to send text messages")

        sent = asyncio.run(self.A._drain_outbox(BadBot(), "@test"))
        self.assertEqual(sent, 0)
        st = ob.stats()
        self.assertEqual(st["pending"], 1, "پیامِ ناموفق باید در صف بماند")
        self.assertEqual(st["sent_total"], 0)

    def test_success_sends_exactly_once(self) -> None:
        key = ob.config_key("vless://ok@h:443")
        ob.enqueue([(key, "<code>vless://ok@h:443</code>")])

        class OkBot:
            n = 0

            async def send_message(self, **kw):
                OkBot.n += 1
                return object()

        self.assertEqual(asyncio.run(self.A._drain_outbox(OkBot(), "@test")), 1)
        self.assertEqual(ob.stats()["pending"], 0)
        # دورِ بعد (مثل برشِ تازهٔ CI): هیچ چیزِ تکراری نمی‌رود
        self.assertEqual(asyncio.run(self.A._drain_outbox(OkBot(), "@test")), 0)
        self.assertEqual(OkBot.n, 1)

    def test_flood_stops_the_batch(self) -> None:
        import datetime
        from telegram.error import RetryAfter

        ob.enqueue([(ob.config_key(f"ss://{i}"), f"<code>ss://{i}</code>") for i in range(3)])

        class FloodBot:
            calls = 0

            async def send_message(self, **kw):
                FloodBot.calls += 1
                raise RetryAfter(datetime.timedelta(seconds=600))

        sent = asyncio.run(self.A._drain_outbox(FloodBot(), "@test"))
        self.assertEqual(sent, 0)
        self.assertEqual(ob.stats()["pending"], 3, "جریمه نباید صف را پاک کند")
        self.assertEqual(FloodBot.calls, 1, "پس از جریمهٔ سنگین نباید بقیهٔ صف را بکوبد")


if __name__ == "__main__":
    unittest.main(verbosity=2)
