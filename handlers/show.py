"""
User data display handlers.
Show profile, list all forms, delete forms.
"""

import logging
from maxapi import Dispatcher
from maxapi.types import MessageCreated, Command

from services import user_service
from content.texts import TEXT_NO_FORMS
from transport.max.keyboards import build_anketa_keyboard
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)


async def handle_show_callback(event, action: str, user_id: int, bot) -> None:
    """Handle show/clear actions triggered by callbacks."""
    kb = build_anketa_keyboard()

    if action == "show_me":
        profile = user_service.get_latest_profile(user_id)
        if not profile:
            await send_with_keyboard(bot, user_id, TEXT_NO_FORMS, kb)
            return
        text = user_service.format_profile(profile)
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])

    elif action == "my_forms":
        profiles = user_service.get_all_profiles(user_id)
        if not profiles:
            await send_with_keyboard(bot, user_id, TEXT_NO_FORMS, kb)
            return
        text = user_service.format_all_profiles(profiles)
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])

    elif action == "clear_last":
        deleted = user_service.delete_latest(user_id)
        if deleted:
            await send_with_keyboard(bot, user_id, "✅ Последняя анкета удалена.", kb)
        else:
            await send_with_keyboard(bot, user_id, TEXT_NO_FORMS, kb)

    elif action == "clear_all":
        count = user_service.delete_all(user_id)
        if count > 0:
            await send_with_keyboard(bot, user_id, f"✅ Удалено анкет: {count}", kb)
        else:
            await send_with_keyboard(bot, user_id, TEXT_NO_FORMS, kb)


def register(dp: Dispatcher) -> None:
    """Register slash commands for data display."""

    @dp.message_created(Command("show_me"))
    async def on_show_me(event: MessageCreated):
        user_id = event.message.sender.user_id
        await handle_show_callback(event, "show_me", user_id, event.bot)

    @dp.message_created(Command("my_forms"))
    async def on_my_forms(event: MessageCreated):
        user_id = event.message.sender.user_id
        await handle_show_callback(event, "my_forms", user_id, event.bot)

    @dp.message_created(Command("clear_last"))
    async def on_clear_last(event: MessageCreated):
        user_id = event.message.sender.user_id
        await handle_show_callback(event, "clear_last", user_id, event.bot)

    @dp.message_created(Command("clear_all"))
    async def on_clear_all(event: MessageCreated):
        user_id = event.message.sender.user_id
        await handle_show_callback(event, "clear_all", user_id, event.bot)
