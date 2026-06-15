"""
Central callback handler for all navigation and action callbacks.
Routes message_callback events based on payload prefix.
"""

import logging
from maxapi import Dispatcher
from maxapi.types import MessageCallback
from maxapi.context import MemoryContext

from handlers import session_store
from handlers.form import start_form_flow, handle_form_callback
from handlers.training import (
    handle_training_nav,
    handle_days_selection,
    handle_health_selection,
    handle_technique_selection,
)
from handlers.training_check import handle_check_callback, handle_scheduled_callback
from handlers.show import handle_show_callback
from handlers.achievements import show_achievements_menu, handle_achievements_callback

from services import user_service, training_service
from content.texts import (
    TEXT_NO_ACTIVE_SESSION,
    TEXT_NO_FORMS,
    get_nutrition_text,
    get_recovery_text,
    get_training_rules_text,
)
from transport.max.keyboards import (
    build_menu_keyboard,
    build_main_keyboard,
    build_anketa_keyboard,
    build_training_hub_keyboard,
    build_training_rules_keyboard,
    build_training_keyboard,
    build_training_days_keyboard,
)
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)


def register(dp: Dispatcher) -> None:

    @dp.message_callback()
    async def on_callback(event: MessageCallback, context: MemoryContext):
        payload = event.callback.payload or ""
        user_id = event.callback.user.user_id
        bot = event.bot

        logger.debug("Callback from user %d: %s", user_id, payload)

        try:
            if payload.startswith("nav:"):
                await _handle_nav(event, payload, user_id, bot, context)
            elif payload.startswith("action:"):
                await _handle_action(event, payload, user_id, bot, context)
            elif payload.startswith("form:"):
                await handle_form_callback(event, payload, user_id, bot, context)
            elif payload.startswith("days:"):
                await handle_days_selection(event, payload, user_id, bot)
            elif payload.startswith("training:"):
                await handle_training_nav(event, payload, user_id, bot, context)
            elif payload.startswith("health:"):
                await handle_health_selection(event, payload, user_id, bot, context)
            elif payload.startswith("technique:"):
                await handle_technique_selection(event, payload, user_id, bot)
            elif payload.startswith("check:"):
                await handle_check_callback(event, payload, user_id, bot, context)
            elif payload.startswith("sched:"):
                await handle_scheduled_callback(event, payload, user_id, bot, context)
            elif payload.startswith("achieve:"):
                await handle_achievements_callback(payload, user_id, bot)
            else:
                logger.warning("Unknown callback payload: %s", payload)
        except Exception:
            logger.exception("Error handling callback %s for user %d", payload, user_id)
            await bot.send_message(user_id=user_id, text="⚠️ Произошла ошибка. Попробуйте ещё раз.")


async def _handle_nav(event, payload: str, user_id: int, bot, context: MemoryContext):
    dest = payload.removeprefix("nav:")

    if dest == "menu":
        await context.set_state(None)
        kb = build_menu_keyboard()
        await send_with_keyboard(bot, user_id, "🏠 Главное меню", kb)

    elif dest == "main":
        await context.set_state(None)
        kb = build_main_keyboard()
        await send_with_keyboard(bot, user_id, "📋 Основное меню", kb)

    elif dest == "anketa":
        await context.set_state(None)
        kb = build_anketa_keyboard()
        await send_with_keyboard(bot, user_id, "📝 Меню анкеты", kb)

    elif dest == "diet":
        profile = user_service.get_latest_profile(user_id)
        if profile:
            week = training_service.resolve_user_week(user_id)
            calories = user_service.get_target_calories(profile, week)
            text = (
                f"🎯 Ваша цель: {profile.goal}\n"
                f"📅 Неделя: {week}\n\n"
                f"{get_nutrition_text(profile.goal, week, calories)}"
            )
        else:
            text = f"❌ {TEXT_NO_FORMS}"
        kb = build_main_keyboard()
        await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])

    elif dest == "recovery":
        profile = user_service.get_latest_profile(user_id)
        if profile:
            week = training_service.resolve_user_week(user_id)
            text = get_recovery_text(profile.goal, week)
        else:
            text = "❌ Сначала заполните анкету, чтобы получить рекомендации по восстановлению."
        kb = build_main_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)

    elif dest == "training":
        kb = build_training_hub_keyboard()
        await send_with_keyboard(
            bot,
            user_id,
            "🏋️ Раздел тренировок\n\nВыберите действие:",
            kb,
        )

    elif dest == "training_rules":
        profile = user_service.get_latest_profile(user_id)
        rules_text = (
            get_training_rules_text(profile.goal, training_service.resolve_user_week(user_id))
            if profile
            else "❌ Сначала заполните анкету, чтобы увидеть правила тренировок для вашей цели."
        )
        kb = build_training_rules_keyboard()
        await send_long_message(
            bot,
            user_id,
            rules_text,
            attachments=[kb.as_markup()],
        )

    elif dest == "training_begin":
        await _show_training_workspace(user_id, bot)

    elif dest == "achievements":
        await show_achievements_menu(user_id, bot)


async def _show_training_workspace(user_id: int, bot) -> None:
    """Меню активной сессии или выбор дней, если сессии ещё нет."""
    session = training_service.get_active_session(user_id)
    if session:
        profile = user_service.get_latest_profile(user_id)
        gender = profile.gender if profile else None
        text = training_service.get_training_status(session, gender)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)
    else:
        kb = build_training_days_keyboard()
        await send_with_keyboard(bot, user_id, "🏋️ Выберите дни тренировок:", kb)


async def _handle_action(event, payload: str, user_id: int, bot, context: MemoryContext):
    action = payload.removeprefix("action:")

    if action == "form":
        await start_form_flow(user_id, bot, context)

    elif action == "show_me":
        await handle_show_callback(event, "show_me", user_id, bot)

    elif action == "my_forms":
        await handle_show_callback(event, "my_forms", user_id, bot)

    elif action == "clear_last":
        await handle_show_callback(event, "clear_last", user_id, bot)

    elif action == "clear_all":
        await handle_show_callback(event, "clear_all", user_id, bot)
