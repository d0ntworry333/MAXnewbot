"""
Контрольные чеки цикла (1–5) и ответы на вечерние напоминания.
"""

import logging

from maxapi.context import MemoryContext

from handlers.states import TrainingStates
from handlers import session_store
from services import training_service, schedule_service, check_service, user_service
from content.checks import get_check
from content.texts import TEXT_WEEK_COMPLETE, get_week_transition_text
from transport.max.keyboards import (
    build_check_keyboard,
    build_training_keyboard,
    build_next_week_keyboard,
    build_main_keyboard,
    build_weighin_skip_keyboard,
)
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)

TEXT_CYCLE_COMPLETE = (
    "🏆 Поздравляем! 8-недельный цикл завершён.\n\n"
    "Давайте зафиксируем замер и посмотрим на ваш путь."
)

TEXT_CHECK_PASSED = "✅ Чек пройден!"


async def prompt_pending_check(user_id: int, bot, context: MemoryContext) -> bool:
    """Показать чек, блокирующий переход на след. неделю. True если чек показан."""
    session = training_service.get_active_session(user_id)
    if not session:
        return False
    check_id = check_service.pending_check_before_next_week(session)
    if not check_id:
        return False
    await _start_check(user_id, bot, context, session.id, check_id)
    return True


async def try_advance_week_or_check(user_id: int, bot, context: MemoryContext) -> None:
    """След. неделя: сначала чек (если нужен), затем переход."""
    session = training_service.get_active_session(user_id)
    if not session:
        await bot.send_message(user_id=user_id, text="❌ Нет активной тренировочной сессии.")
        return

    if session.week_number >= 8:
        await bot.send_message(
            user_id=user_id,
            text="✅ Вы на финальной неделе цикла. Пройдите чек 5 после всех тренировок.",
        )
        return

    if await prompt_pending_check(user_id, bot, context):
        return

    if not training_service.advance_to_next_week(session.id):
        await bot.send_message(user_id=user_id, text="⚠️ Не удалось перейти на следующую неделю.")
        return

    await _send_week_transition(user_id, bot)


async def _send_week_transition(user_id: int, bot) -> None:
    session = training_service.get_active_session(user_id)
    if not session:
        return
    profile = user_service.get_latest_profile(user_id)
    gender = profile.gender if profile else "Мужской"
    goal = profile.goal if profile else "дефицит"
    parts = [f"➡️ Переход на неделю {session.week_number}"]
    transition = get_week_transition_text(goal, session.week_number, gender)
    if transition:
        parts.append(transition)
    parts.append(training_service.get_training_status(session, gender))
    kb = build_training_keyboard()
    await send_long_message(bot, user_id, "\n\n".join(parts), attachments=[kb.as_markup()])


async def handle_week_completion(user_id: int, bot, context: MemoryContext) -> None:
    """После 3/3 (или 2/2 на нед. 8) тренировок."""
    session = training_service.get_active_session(user_id)
    if not session:
        return

    check_id = check_service.pending_check_before_next_week(session)
    if check_id:
        await _start_check(user_id, bot, context, session.id, check_id)
        return

    if session.week_number >= 8:
        kb = build_main_keyboard()
        await send_with_keyboard(bot, user_id, TEXT_CYCLE_COMPLETE, kb)
        return

    kb = build_next_week_keyboard()
    await send_with_keyboard(bot, user_id, TEXT_WEEK_COMPLETE, kb)


async def _start_check(
    user_id: int, bot, context: MemoryContext, session_id: int, check_id: int,
) -> None:
    check = get_check(check_id)
    if not check:
        return
    session_store.put(user_id, "check_step", str(check_id))
    session_store.put(user_id, "check_session_id", session_id)
    kb = build_check_keyboard(check_id, final=check.final)
    await send_with_keyboard(bot, user_id, check.question, kb)


async def handle_check_callback(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """check:N:yes | check:N:no"""
    parts = payload.removeprefix("check:").split(":")
    if len(parts) != 2:
        return

    try:
        check_id = int(parts[0])
    except ValueError:
        return

    answer = parts[1]
    session_id = session_store.get(user_id, "check_session_id")

    if answer == "no":
        if session_id:
            msg = check_service.apply_check_failure(session_id, check_id)
        else:
            msg = "❌ Чек не пройден."
        session_store.remove(user_id, "check_step")
        session_store.remove(user_id, "check_session_id")
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, msg, kb)
        return

    if answer != "yes":
        return

    if session_id:
        check_service.mark_check_passed(session_id, check_id)
        logger.info("User %d passed check %d", user_id, check_id)

    session_store.remove(user_id, "check_step")
    session_store.remove(user_id, "check_session_id")

    check = get_check(check_id)
    if check and check.final:
        await context.set_state(TrainingStates.collecting_body_weight)
        session_store.put(user_id, "awaiting_weighin", True)
        kb = build_weighin_skip_keyboard()
        await send_with_keyboard(
            bot, user_id,
            f"{TEXT_CHECK_PASSED}\n\n{TEXT_CYCLE_COMPLETE}\n\n"
            "⚖️ Введите текущий вес (кг) для итогового замера:",
            kb,
        )
        return

    kb = build_next_week_keyboard()
    await send_with_keyboard(
        bot, user_id,
        f"{TEXT_CHECK_PASSED}\n\n{TEXT_WEEK_COMPLETE}",
        kb,
    )


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
    """Регистрация не требуется — чеки через callback, без ввода текста."""
    pass
