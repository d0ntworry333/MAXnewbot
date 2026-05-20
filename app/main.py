"""
Application entry point for the MAX Fitness Bot.
Initializes all components and starts long polling.
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from config.settings import settings
from repositories.database import init_db, set_db_path
from transport.max.helpers import set_max_message_length
from scheduler.jobs import create_scheduler, set_bot
from maxapi import Bot, Dispatcher


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)


def register_handlers(dp: Dispatcher) -> None:
    from handlers import start, form, training, training_check, show, navigation

    start.register(dp)
    form.register(dp)
    training.register(dp)
    training_check.register(dp)
    show.register(dp)
    navigation.register(dp)


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting MAX Fitness Bot...")
    logger.info("Database: %s", settings.database_path)
    logger.info("Timezone: %s", settings.timezone)

    set_db_path(settings.database_path)
    init_db()

    set_max_message_length(settings.max_message_length)

    bot = Bot(settings.max_bot_token)
    dp = Dispatcher()

    register_handlers(dp)

    set_bot(bot)
    scheduler = create_scheduler(
        tz_name=settings.timezone,
        evening_hour=settings.check_hour_evening,
        evening_minute=settings.check_minute_evening,
        reminder_hour=settings.reminder_hour,
        reminder_minute=settings.reminder_minute,
        reset_hour=settings.reset_hour,
        reset_minute=settings.reset_minute,
    )
    scheduler.start()
    logger.info("Scheduler started with %d jobs", len(scheduler.get_jobs()))

    logger.info("Starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
