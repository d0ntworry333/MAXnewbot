"""
Handlers for /start command and bot_started event.
Entry points into the bot.
"""

import logging
from maxapi import Dispatcher
from maxapi.types import MessageCreated, BotStarted, Command, CommandStart

from transport.max.keyboards import build_menu_keyboard
from transport.max.helpers import send_with_keyboard
from content.texts import TEXT_WELCOME, TEXT_ACHIEVEMENTS_STUB

logger = logging.getLogger(__name__)


def register(dp: Dispatcher) -> None:
    @dp.bot_started()
    async def on_bot_started(event: BotStarted):
        user_id = event.user.user_id
        logger.info("Bot started by user %d", user_id)
        kb = build_menu_keyboard()
        await send_with_keyboard(event.bot, user_id, TEXT_WELCOME, kb)

    @dp.message_created(CommandStart())
    async def on_start_command(event: MessageCreated):
        user_id = event.message.sender.user_id
        logger.info("/start from user %d", user_id)
        kb = build_menu_keyboard()
        await send_with_keyboard(event.bot, user_id, TEXT_WELCOME, kb)

    @dp.message_created(Command("achievements"))
    async def on_achievements(event: MessageCreated):
        user_id = event.message.sender.user_id
        kb = build_menu_keyboard()
        await send_with_keyboard(event.bot, user_id, TEXT_ACHIEVEMENTS_STUB, kb)
