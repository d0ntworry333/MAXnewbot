"""Раздел «Достижения»: вес тела и силовые показатели."""

import logging

from services import achievements_service
from transport.max.keyboards import (
    build_achievements_menu_keyboard,
    build_achievements_body_keyboard,
    build_achievements_strength_keyboard,
    build_achievements_exercises_keyboard,
    build_achievements_back_keyboard,
)
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)

TEXT_ACHIEVEMENTS_MENU = (
    "🏆 Достижения\n\n"
    "Здесь собран ваш прогресс за цикл тренировок:\n"
    "вес тела и силовые показатели по упражнениям."
)


async def show_achievements_menu(user_id: int, bot) -> None:
    kb = build_achievements_menu_keyboard()
    await send_with_keyboard(bot, user_id, TEXT_ACHIEVEMENTS_MENU, kb)


async def handle_achievements_callback(
    payload: str, user_id: int, bot,
) -> None:
    """achieve:menu | achieve:body | achieve:body:before_after | ..."""
    action = payload.removeprefix("achieve:")

    if action == "menu":
        await show_achievements_menu(user_id, bot)
        return

    if action == "body":
        kb = build_achievements_body_keyboard()
        await send_with_keyboard(
            bot, user_id,
            "⚖️ Ваш вес на протяжении тренировок\n\nВыберите формат отчёта:",
            kb,
        )
        return

    if action == "body:before_after":
        text = achievements_service.format_body_before_after(user_id)
        kb = build_achievements_back_keyboard("achieve:body")
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])
        return

    if action == "body:changes":
        text = achievements_service.format_body_changes(user_id)
        kb = build_achievements_back_keyboard("achieve:body")
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])
        return

    if action == "strength":
        kb = build_achievements_strength_keyboard()
        await send_with_keyboard(
            bot, user_id,
            "🏋️ Ваш силовой вес на протяжении тренировок\n\nВыберите формат:",
            kb,
        )
        return

    if action == "strength:avg":
        text = achievements_service.format_strength_average(user_id)
        kb = build_achievements_back_keyboard("achieve:strength")
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])
        return

    if action == "strength:exercises":
        exercises = achievements_service.get_exercises_for_menu(user_id)
        if not exercises:
            kb = build_achievements_back_keyboard("achieve:strength")
            await send_with_keyboard(
                bot, user_id,
                "❌ Нет записей силовых весов. Вводите веса после упражнений в тренировках.",
                kb,
            )
            return
        text = achievements_service.format_strength_exercises_list(user_id)
        kb = build_achievements_exercises_keyboard(exercises)
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])
        return

    if action.startswith("ex:"):
        try:
            exercise_id = int(action.removeprefix("ex:"))
        except ValueError:
            return
        text = achievements_service.format_exercise_history(user_id, exercise_id)
        kb = build_achievements_back_keyboard("achieve:strength:exercises")
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])
        return

    logger.warning("Unknown achievements action: %s", action)
