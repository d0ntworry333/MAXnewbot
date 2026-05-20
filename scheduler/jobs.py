"""
APScheduler cron jobs for automated training checks.

Jobs:
  1. Evening check (23:00) — ask users if they trained today
  2. Next-day reminder (16:00) — remind about unanswered yesterday's check
  3. Session reset (23:59) — deactivate sessions with 2-day-old unanswered checks
"""

import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone as pytz_timezone

from maxapi import Bot
from services import schedule_service
from transport.max.keyboards import build_scheduled_check_keyboard
from transport.max.helpers import send_with_keyboard

logger = logging.getLogger(__name__)

_bot: Bot | None = None


def set_bot(bot: Bot) -> None:
    global _bot
    _bot = bot


async def evening_check_job() -> None:
    """23:00 — Check if users trained today, send Yes/No prompt."""
    if not _bot:
        logger.error("Bot not set for evening check job")
        return

    today = date.today()
    users = schedule_service.get_users_needing_evening_check(today)

    for u in users:
        try:
            from repositories import training_log_repo
            pending = training_log_repo.get_pending_log(u["user_id"], u["session_id"], today.isoformat())
            log_id = pending.id if pending else 0

            kb = build_scheduled_check_keyboard(log_id)
            await send_with_keyboard(
                _bot,
                u["user_id"],
                f"🕐 Вечерняя проверка\n\nСегодня у вас запланирована: {u['training_type']}\n\nВыполнили ли вы тренировку сегодня?",
                kb,
            )
        except Exception:
            logger.exception("Failed to send evening check to user %d", u["user_id"])


async def reminder_job() -> None:
    """16:00 — Remind users about unanswered yesterday check."""
    if not _bot:
        logger.error("Bot not set for reminder job")
        return

    today = date.today()
    users = schedule_service.get_users_needing_reminder(today)

    for u in users:
        try:
            kb = build_scheduled_check_keyboard(u["log_id"])
            await send_with_keyboard(
                _bot,
                u["user_id"],
                "⏰ Напоминание\n\nВы ещё не ответили на вчерашнюю проверку тренировки.\nВыполнили ли вы тренировку?",
                kb,
            )
        except Exception:
            logger.exception("Failed to send reminder to user %d", u["user_id"])


async def reset_job() -> None:
    """23:59 — Deactivate sessions with old unanswered checks."""
    if not _bot:
        logger.error("Bot not set for reset job")
        return

    today = date.today()
    sessions = schedule_service.get_sessions_to_deactivate(today)

    for s in sessions:
        try:
            await _bot.send_message(
                user_id=s["user_id"],
                text="⚠️ Ваша тренировочная сессия деактивирована из-за отсутствия ответа.\n\n"
                     "Чтобы начать заново, перейдите в раздел «Тренировки».",
            )
        except Exception:
            logger.exception("Failed to notify user %d about session deactivation", s["user_id"])


def create_scheduler(
    tz_name: str = "Europe/Moscow",
    evening_hour: int = 23,
    evening_minute: int = 0,
    reminder_hour: int = 16,
    reminder_minute: int = 0,
    reset_hour: int = 23,
    reset_minute: int = 59,
) -> AsyncIOScheduler:
    """Create and configure the scheduler with all cron jobs."""
    tz = pytz_timezone(tz_name)
    scheduler = AsyncIOScheduler(timezone=tz)

    scheduler.add_job(
        evening_check_job,
        CronTrigger(hour=evening_hour, minute=evening_minute, timezone=tz),
        id="evening_check",
        replace_existing=True,
    )

    scheduler.add_job(
        reminder_job,
        CronTrigger(hour=reminder_hour, minute=reminder_minute, timezone=tz),
        id="reminder",
        replace_existing=True,
    )

    scheduler.add_job(
        reset_job,
        CronTrigger(hour=reset_hour, minute=reset_minute, timezone=tz),
        id="reset_sessions",
        replace_existing=True,
    )

    logger.info(
        "Scheduler configured: evening=%02d:%02d, reminder=%02d:%02d, reset=%02d:%02d, tz=%s",
        evening_hour, evening_minute, reminder_hour, reminder_minute, reset_hour, reset_minute, tz_name,
    )

    return scheduler
