"""
Week completion checks (check01, check02) and scheduled check response handlers.
"""

import logging
from maxapi.context import MemoryContext

from handlers.states import TrainingStates
from handlers import session_store
from services import training_service, schedule_service
from content.texts import TEXT_WEEK_COMPLETE
from transport.max.keyboards import (
    build_check01_keyboard, build_training_keyboard,
    build_next_week_keyboard, build_main_keyboard,
)
from transport.max.helpers import send_with_keyboard

logger = logging.getLogger(__name__)


async def handle_week_completion(user_id: int, bot, context: MemoryContext) -> None:
    """Called when a user completes 3/3 trainings in a week."""
    session = training_service.get_active_session(user_id)
    if not session:
        return

    week = session.week_number

    if week == 1:
        kb = build_next_week_keyboard()
        await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)

    elif week == 2:
        if training_service.needs_check01(session):
            session_store.put(user_id, "check_step", "check01")
            session_store.put(user_id, "check_session_id", session.id)
            kb = build_check01_keyboard()
            await send_with_keyboard(
                bot, user_id,
                "📋 Проверка недели 2\n\nВыполнили ли вы все тренировки?",
                kb,
            )
        elif training_service.needs_check02(session):
            await _start_check02(user_id, bot, session, context)
        else:
            kb = build_next_week_keyboard()
            await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)

    else:  # week 3+
        if training_service.needs_check02(session):
            await _start_check02(user_id, bot, session, context)
        else:
            kb = build_next_week_keyboard()
            await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)


async def _start_check02(user_id: int, bot, session, context: MemoryContext) -> None:
    session_store.put(user_id, "check_step", "check02")
    session_store.put(user_id, "check_session_id", session.id)
    await context.set_state(TrainingStates.collecting_calories)
    await bot.send_message(
        user_id=user_id,
        text="📊 Введите вашу среднюю калорийность за неделю:",
    )


async def handle_check_callback(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """Handle check:* callbacks (check01 yes/no, check02 skip)."""
    action = payload.removeprefix("check:")

    if action == "check01_yes":
        session_id = session_store.get(user_id, "check_session_id")
        if session_id:
            training_service.handle_check01_yes(session_id)
            logger.info("User %d passed check01", user_id)

        session = training_service.get_active_session(user_id)
        if session and training_service.needs_check02(session):
            await _start_check02(user_id, bot, session, context)
        else:
            session_store.remove(user_id, "check_step")
            session_store.remove(user_id, "check_session_id")
            kb = build_next_week_keyboard()
            await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)

    elif action == "check01_no":
        session_id = session_store.get(user_id, "check_session_id")
        if session_id:
            training_service.handle_check01_no(session_id)
            logger.info("User %d failed check01 — week reset", user_id)

        session_store.remove(user_id, "check_step")
        session_store.remove(user_id, "check_session_id")
        kb = build_training_keyboard()
        await send_with_keyboard(
            bot, user_id,
            "❌ Неделя сброшена. Выполните все тренировки заново.",
            kb,
        )

    elif action == "check02_skip":
        session_id = session_store.get(user_id, "check_session_id")
        if session_id:
            training_service.handle_check02_pass(session_id)

        session_store.remove(user_id, "check_step")
        session_store.remove(user_id, "check_session_id")
        await context.set_state(None)
        kb = build_next_week_keyboard()
        await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)


async def handle_scheduled_callback(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """Handle sched:yes:N or sched:no:N callbacks from scheduled evening checks."""
    parts = payload.removeprefix("sched:").split(":")
    if len(parts) < 2:
        return

    response = parts[0]
    try:
        log_id = int(parts[1])
    except ValueError:
        return

    completed = response == "yes"

    session = training_service.get_active_session(user_id)
    session_id = session.id if session else 0

    result = schedule_service.handle_scheduled_check_response(
        log_id=log_id,
        session_id=session_id,
        user_id=user_id,
        completed=completed,
    )

    if completed:
        text = "✅ Отлично! Тренировка засчитана."
        if result.get("week_complete"):
            await handle_week_completion(user_id, bot, context)
            return
        elif result.get("needs_weighin"):
            await context.set_state(TrainingStates.collecting_body_weight)
            session_store.put(user_id, "awaiting_weighin", True)
            from transport.max.keyboards import build_weighin_skip_keyboard
            kb = build_weighin_skip_keyboard()
            await send_with_keyboard(
                bot, user_id,
                f"{text}\n\n⚖️ Пора взвеситься! Введите ваш текущий вес (кг):",
                kb,
            )
            return
    else:
        text = "📌 Тренировка отложена. Постарайтесь наверстать!"

    await bot.send_message(user_id=user_id, text=text)


def register(dp):
    """Register text input handler for calorie collection (check02)."""
    from maxapi import Dispatcher
    from maxapi.types import MessageCreated

    @dp.message_created(TrainingStates.collecting_calories)
    async def on_calories_input(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = (event.message.body.text or "").strip()

        if text.startswith("/"):
            return

        session_id = session_store.get(user_id, "check_session_id")
        if session_id:
            training_service.handle_check02_pass(session_id)
            logger.info("User %d passed check02 with input: %s", user_id, text[:50])

        session_store.remove(user_id, "check_step")
        session_store.remove(user_id, "check_session_id")
        await context.set_state(None)
        kb = build_next_week_keyboard()
        await send_with_keyboard(event.bot, user_id, TEXT_WEEK_COMPLETE, kb)
