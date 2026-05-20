"""
Questionnaire (form) handlers.
Full form: height → weight → activity → gender → age → goal
Short form: weight → activity (for returning users)
"""

import logging
from maxapi import Dispatcher
from maxapi.types import MessageCreated, Command
from maxapi.context import MemoryContext

from handlers.states import FormStates
from handlers import session_store
from services import user_service
from core.validators import parse_height, parse_weight, parse_age
from content.texts import get_diet_text, TEXT_FORM_CANCELLED
from transport.max.keyboards import (
    build_activity_keyboard, build_gender_keyboard, build_goal_keyboard,
    build_cancel_keyboard, build_main_keyboard, build_anketa_keyboard,
)
from transport.max.helpers import send_with_keyboard, send_long_message

logger = logging.getLogger(__name__)


async def start_form_flow(user_id: int, bot, context: MemoryContext) -> None:
    """Entry point for the questionnaire. Chooses full or short form."""
    has_forms = user_service.has_forms(user_id)

    if has_forms:
        await context.set_state(FormStates.short_weight)
        session_store.put(user_id, "form_data", {})
        kb = build_cancel_keyboard()
        await send_with_keyboard(
            bot, user_id,
            "📝 Обновление анкеты\n\nВведите ваш текущий вес (кг):",
            kb,
        )
    else:
        await context.set_state(FormStates.height)
        session_store.put(user_id, "form_data", {})
        kb = build_cancel_keyboard()
        await send_with_keyboard(
            bot, user_id,
            "📝 Заполнение анкеты\n\nВведите ваш рост (см):",
            kb,
        )


async def handle_form_callback(event, payload: str, user_id: int, bot, context: MemoryContext) -> None:
    """Handle form-related callbacks (activity, gender, goal selections, cancel)."""
    parts = payload.removeprefix("form:").split(":", 1)
    field = parts[0]

    if field == "cancel":
        session_store.remove(user_id, "form_data")
        await context.set_state(None)
        kb = build_anketa_keyboard()
        await send_with_keyboard(bot, user_id, TEXT_FORM_CANCELLED, kb)
        return

    value = parts[1] if len(parts) > 1 else ""
    state = await context.get_state()

    if field == "activity":
        if state == FormStates.activity:
            form = session_store.get(user_id, "form_data", {})
            form["activity_level"] = value
            session_store.put(user_id, "form_data", form)
            await context.set_state(FormStates.gender)
            kb = build_gender_keyboard()
            await send_with_keyboard(bot, user_id, "Выберите ваш пол:", kb)

        elif state == FormStates.short_activity:
            form = session_store.get(user_id, "form_data", {})
            form["activity_level"] = value
            session_store.put(user_id, "form_data", form)
            await _finish_short_form(user_id, bot, context)

    elif field == "gender":
        if state == FormStates.gender:
            form = session_store.get(user_id, "form_data", {})
            form["gender"] = value
            session_store.put(user_id, "form_data", form)
            await context.set_state(FormStates.age)
            kb = build_cancel_keyboard()
            await send_with_keyboard(bot, user_id, "Введите ваш возраст:", kb)

    elif field == "goal":
        if state == FormStates.goal:
            form = session_store.get(user_id, "form_data", {})
            form["goal"] = value
            session_store.put(user_id, "form_data", form)
            await _finish_full_form(user_id, bot, context, event)


async def _finish_full_form(user_id: int, bot, context: MemoryContext, event) -> None:
    form = session_store.get(user_id, "form_data", {})
    username = ""
    try:
        username = event.callback.user.username or ""
    except AttributeError:
        pass

    bmr = user_service.create_full_profile(
        user_id=user_id,
        username=username,
        height=form["height"],
        weight=form["weight"],
        activity_level=form["activity_level"],
        gender=form["gender"],
        age=form["age"],
        goal=form["goal"],
    )

    text = (
        "✅ Анкета заполнена!\n\n"
        f"📏 Рост: {form['height']} см\n"
        f"⚖️ Вес: {form['weight']} кг\n"
        f"🏃 Активность: {form['activity_level']}\n"
        f"👤 Пол: {form['gender']}\n"
        f"🎂 Возраст: {form['age']}\n"
        f"🎯 Цель: {form['goal']}\n"
        f"🔥 Ваш БМР: {bmr} ккал\n\n"
        f"{get_diet_text(form['goal'])}"
    )

    session_store.remove(user_id, "form_data")
    await context.set_state(None)
    kb = build_main_keyboard()
    await send_long_message(bot, user_id, text, attachments=[kb.as_markup()])


async def _finish_short_form(user_id: int, bot, context: MemoryContext) -> None:
    form = session_store.get(user_id, "form_data", {})

    bmr = user_service.create_short_profile(
        user_id=user_id,
        username="",
        weight=form["weight"],
        activity_level=form["activity_level"],
    )

    if bmr is None:
        await bot.send_message(user_id=user_id, text="❌ Не найдена первая анкета. Заполните полную анкету.")
        await context.set_state(None)
        kb = build_anketa_keyboard()
        await send_with_keyboard(bot, user_id, "📝 Меню анкеты", kb)
        return

    text = (
        "✅ Анкета обновлена!\n\n"
        f"⚖️ Вес: {form['weight']} кг\n"
        f"🏃 Активность: {form['activity_level']}\n"
        f"🔥 Ваш БМР: {bmr} ккал"
    )

    session_store.remove(user_id, "form_data")
    await context.set_state(None)
    kb = build_main_keyboard()
    await send_with_keyboard(bot, user_id, text, kb)


def register(dp: Dispatcher) -> None:
    """Register text input handlers for form states."""

    @dp.message_created(FormStates.height)
    async def on_height_input(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        height = parse_height(text)
        if height is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите рост от 50 до 250 см (например: 175):",
            )
            return

        form = session_store.get(user_id, "form_data", {})
        form["height"] = height
        session_store.put(user_id, "form_data", form)
        await context.set_state(FormStates.weight)
        kb = build_cancel_keyboard()
        await send_with_keyboard(event.bot, user_id, "Введите ваш вес (кг):", kb)

    @dp.message_created(FormStates.weight)
    async def on_weight_input(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        weight = parse_weight(text)
        if weight is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите вес от 20 до 300 кг (например: 75.5):",
            )
            return

        form = session_store.get(user_id, "form_data", {})
        form["weight"] = weight
        session_store.put(user_id, "form_data", form)
        await context.set_state(FormStates.activity)
        kb = build_activity_keyboard()
        await send_with_keyboard(event.bot, user_id, "Выберите уровень активности:", kb)

    @dp.message_created(FormStates.age)
    async def on_age_input(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        age = parse_age(text)
        if age is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите возраст от 1 до 120 (например: 25):",
            )
            return

        form = session_store.get(user_id, "form_data", {})
        form["age"] = age
        session_store.put(user_id, "form_data", form)
        await context.set_state(FormStates.goal)
        kb = build_goal_keyboard()
        await send_with_keyboard(event.bot, user_id, "Выберите вашу цель:", kb)

    @dp.message_created(FormStates.short_weight)
    async def on_short_weight_input(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        text = event.message.body.text or ""

        if text.startswith("/"):
            return

        weight = parse_weight(text)
        if weight is None:
            await event.bot.send_message(
                user_id=user_id,
                text="⚠️ Введите вес от 20 до 300 кг (например: 75.5):",
            )
            return

        form = session_store.get(user_id, "form_data", {})
        form["weight"] = weight
        session_store.put(user_id, "form_data", form)
        await context.set_state(FormStates.short_activity)
        kb = build_activity_keyboard()
        await send_with_keyboard(event.bot, user_id, "Выберите уровень активности:", kb)

    @dp.message_created(Command("form"))
    async def on_form_command(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        await start_form_flow(user_id, event.bot, context)

    @dp.message_created(Command("cancel"))
    async def on_cancel_command(event: MessageCreated, context: MemoryContext):
        user_id = event.message.sender.user_id
        session_store.remove(user_id, "form_data")
        await context.set_state(None)
        kb = build_main_keyboard()
        await send_with_keyboard(event.bot, user_id, TEXT_FORM_CANCELLED, kb)
