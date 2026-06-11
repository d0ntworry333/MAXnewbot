"""
Training process handlers.
Covers: day selection, exercise display, weight collection,
training completion, schedule, technique, week navigation.
"""

import logging
from datetime import date
from maxapi import Dispatcher
from maxapi.types import MessageCreated
from maxapi.context import MemoryContext

from handlers.states import TrainingStates
from handlers import session_store
from services import training_service, exercise_service, user_service
from core.validators import parse_exercise_weight, parse_body_weight
from content.texts import TEXT_NO_ACTIVE_SESSION, TEXT_TRAINING_COMPLETE, TEXT_ALL_WEIGHTS_RECORDED, TEXT_ALREADY_WEEK_1
from content.exercises import TRAINING_TYPES, EXERCISE_BY_ID
from transport.max.keyboards import (
    build_training_keyboard,
    build_health_keyboard,
    build_technique_keyboard,
    build_training_days_keyboard,
    build_next_week_keyboard,
    build_weighin_skip_keyboard,
    build_main_keyboard,
)
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)

DAYS_MAP = {
    "mon_wed_fri": "Пн-Ср-Пт",
    "tue_thu_sat": "Вт-Чт-Сб",
    "wed_fri_sun": "Ср-Пт-Вс",
}


def _user_goal(user_id: int) -> str:
    profile = user_service.get_latest_profile(user_id)
    return profile.goal if profile else "дефицит"


async def handle_days_selection(event, payload: str, user_id: int, bot) -> None:
    """Handle training days selection callback (days:mon_wed_fri, etc.)."""
    key = payload.removeprefix("days:")
    training_days = DAYS_MAP.get(key)
    if not training_days:
        return

    training_service.create_session(user_id, training_days)
    session = training_service.get_active_session(user_id)
    if not session:
        await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
        return
    text = training_service.get_training_status(session)
    kb = build_training_keyboard()
    await send_with_keyboard(bot, user_id, text, kb)


async def handle_training_nav(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """Handle training:* callbacks."""
    action = payload.removeprefix("training:")

    if action == "start":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        text = training_service.get_training_status(session)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)

    elif action == "status":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        text = training_service.get_training_status(session)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)

    elif action == "schedule":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        text = training_service.get_schedule_text(session)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)

    elif action == "exercises":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        session_store.put(user_id, "active_session_id", session.id)
        kb = build_health_keyboard()
        await send_with_keyboard(bot, user_id, "Как вы себя чувствуете?", kb)

    elif action == "complete":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        await _complete_training(user_id, bot, session, context)

    elif action == "technique":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        pain = session_store.get(user_id, "pain_type", "healthy")
        exercises, text = training_service.get_day_exercises(session, pain, _user_goal(user_id))
        if exercises:
            defs = [e.exercise for e in exercises]
            session_store.put(user_id, "technique_exercises", [e.id for e in defs])
            kb = build_technique_keyboard(defs)
            await send_with_keyboard(bot, user_id, "🧠 Выберите упражнение для просмотра техники:", kb)
        else:
            kb = build_training_keyboard()
            await send_with_keyboard(bot, user_id, text, kb)

    elif action == "back":
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, "🏋️ Тренировочное меню", kb)

    elif action == "next_week":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        training_service.advance_to_next_week(session.id)
        session = training_service.get_active_session(user_id)
        text = f"➡️ Переход на неделю {session.week_number}\n\n{training_service.get_training_status(session)}"
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)

    elif action == "prev_week":
        session = training_service.get_active_session(user_id)
        if not session:
            await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
            return
        if training_service.go_to_previous_week(session):
            session = training_service.get_active_session(user_id)
            text = f"⬅️ Возврат на неделю {session.week_number}\n\n{training_service.get_training_status(session)}"
            kb = build_training_keyboard()
            await send_with_keyboard(bot, user_id, text, kb)
        else:
            kb = build_training_keyboard()
            await send_with_keyboard(bot, user_id, TEXT_ALREADY_WEEK_1, kb)

    elif action == "skip_weighin":
        session_store.remove(user_id, "awaiting_weighin")
        await context.set_state(None)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, "⏭ Взвешивание пропущено.", kb)


async def handle_health_selection(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """Handle health status selection (health:healthy, health:arm, etc.)."""
    pain_type = payload.removeprefix("health:")
    session_store.put(user_id, "pain_type", pain_type)

    session = training_service.get_active_session(user_id)
    if not session:
        await bot.send_message(user_id=user_id, text=TEXT_NO_ACTIVE_SESSION)
        return

    exercises, text = training_service.get_day_exercises(session, pain_type, _user_goal(user_id))
    if not exercises:
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, text, kb)
        return

    header = f"📋 Упражнения дня — {TRAINING_TYPES.get(session.current_day, '')}:\n\n"
    await bot.send_message(user_id=user_id, text=header + text)

    session_store.put(
        user_id,
        "weight_queue",
        [(item.exercise.id, item.exercise.name) for item in exercises],
    )
    session_store.put(user_id, "weight_index", 0)
    session_store.put(user_id, "collected_weights", [])

    first_ex = exercises[0].exercise
    await context.set_state(TrainingStates.collecting_exercise_weight)
    await bot.send_message(
        user_id=user_id,
        text=f"🏋️ Упражнение 1/{len(exercises)}: {first_ex.name}\nВведите вес (кг):",
    )


async def handle_technique_selection(event, payload: str, user_id: int, bot) -> None:
    """Handle technique:N callback."""
    try:
        exercise_id = int(payload.removeprefix("technique:"))
    except ValueError:
        return

    text = exercise_service.get_technique_text(exercise_id)
    exercises_ids = session_store.get(user_id, "technique_exercises", [])
    exercises = [EXERCISE_BY_ID[eid] for eid in exercises_ids if eid in EXERCISE_BY_ID]

    kb = build_technique_keyboard(exercises) if exercises else build_training_keyboard()
    await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])


async def _complete_training(user_id: int, bot, session, context: MemoryContext) -> None:
    collected = session_store.get(user_id, "collected_weights", [])
    pain = session_store.get(user_id, "pain_type")

    weights_tuples = [(eid, ename, w) for eid, ename, w in collected] if collected else None

    result = training_service.complete_training(
        user_id=user_id,
        session=session,
        collected_weights=weights_tuples,
        pain_feedback=pain,
    )

    session_store.remove(user_id, "weight_queue")
    session_store.remove(user_id, "weight_index")
    session_store.remove(user_id, "collected_weights")
    session_store.remove(user_id, "pain_type")

    if result["week_complete"]:
        from handlers.training_check import handle_week_completion
        await handle_week_completion(user_id, bot, context)
    elif result["needs_weighin"]:
        await context.set_state(TrainingStates.collecting_body_weight)
        session_store.put(user_id, "awaiting_weighin", True)
        kb = build_weighin_skip_keyboard()
        await send_with_keyboard(
            bot, user_id,
            f"{TEXT_TRAINING_COMPLETE}\n\n⚖️ Пора взвеситься! Введите ваш текущий вес (кг):",
            kb,
        )
    else:
        await context.set_state(None)
        kb = build_training_keyboard()
        await send_with_keyboard(bot, user_id, TEXT_TRAINING_COMPLETE, kb)


def register(dp: Dispatcher) -> None:
    """Register text input handlers for training states."""

    @dp.message_created(TrainingStates.collecting_exercise_weight)
    async def on_exercise_weight(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        weight = parse_exercise_weight(text)
        if weight is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите вес (число ≥ 0, например: 12.5):",
            )
            return

        queue = session_store.get(user_id, "weight_queue", [])
        index = session_store.get(user_id, "weight_index", 0)
        collected = session_store.get(user_id, "collected_weights", [])

        eid, ename = queue[index]
        collected.append((eid, ename, weight))
        session_store.put(user_id, "collected_weights", collected)

        next_index = index + 1
        if next_index >= len(queue):
            summary_lines = [f"  {name}: {w} кг" for _, name, w in collected]
            summary = "\n".join(summary_lines)
            await context.set_state(None)
            session_store.put(user_id, "weight_index", next_index)
            kb = build_training_keyboard()
            await send_with_keyboard(
                event.bot, user_id,
                f"{TEXT_ALL_WEIGHTS_RECORDED}\n\n{summary}",
                kb,
            )
        else:
            session_store.put(user_id, "weight_index", next_index)
            next_eid, next_ename = queue[next_index]
            await event.bot.send_message(
                user_id=user_id,
                text=f"🏋️ Упражнение {next_index + 1}/{len(queue)}: {next_ename}\nВведите вес (кг):",
            )

    @dp.message_created(TrainingStates.collecting_body_weight)
    async def on_body_weight(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        weight = parse_body_weight(text)
        if weight is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите вес от 20 до 300 кг:",
            )
            return

        training_service.save_body_weight(user_id, weight)
        session_store.remove(user_id, "awaiting_weighin")
        await context.set_state(None)
        kb = build_training_keyboard()
        await send_with_keyboard(
            event.bot, user_id,
            f"✅ Вес {weight} кг записан!",
            kb,
        )
