"""
Inline keyboard builders for the MAX fitness bot.

MAX does not have persistent reply keyboards like Telegram.
All menus use inline keyboards attached to messages.
Button types:
  - CallbackButton: triggers message_callback event with payload
  - MessageButton: sends button text as a user message
"""

from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def build_menu_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="📋 Основное меню", payload="nav:main"))
    b.row(CallbackButton(text="🏆 Достижения", payload="nav:achievements"))
    return b


def build_main_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="📝 Анкета", payload="nav:anketa"),
        CallbackButton(text="🎯 Цель и рацион", payload="nav:diet"),
    )
    b.row(
        CallbackButton(text="💪 Восстановление", payload="nav:recovery"),
        CallbackButton(text="🏋️ Тренировки", payload="nav:training"),
    )
    b.row(CallbackButton(text="🏠 Главное меню", payload="nav:menu"))
    return b


def build_anketa_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="📝 Заполнить анкету", payload="action:form"),
        CallbackButton(text="↩️ Назад", payload="nav:main"),
    )
    b.row(
        CallbackButton(text="📋 Мои анкеты", payload="action:my_forms"),
        CallbackButton(text="👤 Мой профиль", payload="action:show_me"),
    )
    b.row(
        CallbackButton(text="🗑 Удалить последнюю", payload="action:clear_last"),
        CallbackButton(text="🗑 Удалить все", payload="action:clear_all"),
    )
    return b


def build_training_hub_keyboard() -> InlineKeyboardBuilder:
    """Меню раздела «Тренировки» перед рабочим меню сессии."""
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="📖 Правила тренировки", payload="nav:training_rules"))
    b.row(CallbackButton(text="🚀 Начать тренировку", payload="nav:training_begin"))
    b.row(CallbackButton(text="↩️ Основное меню", payload="nav:main"))
    return b


def build_training_rules_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура после показа правил — возврат в раздел тренировок."""
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="↩️ Назад", payload="nav:training"))
    return b


def build_training_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="📋 Упражнения дня", payload="training:exercises"),
        CallbackButton(text="📅 Расписание", payload="training:schedule"),
    )
    b.row(
        CallbackButton(text="✅ Я выполнил тренировку", payload="training:complete"),
        CallbackButton(text="📊 Статус", payload="training:status"),
    )
    b.row(
        CallbackButton(text="🧠 Техника", payload="training:technique"),
        CallbackButton(text="📋 Основное меню", payload="nav:main"),
    )
    b.row(
        CallbackButton(text="⬅️ Пред. неделя", payload="training:prev_week"),
        CallbackButton(text="➡️ След. неделя", payload="training:next_week"),
    )
    return b


def build_training_days_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="Пн-Ср-Пт", payload="days:mon_wed_fri"))
    b.row(CallbackButton(text="Вт-Чт-Сб", payload="days:tue_thu_sat"))
    b.row(CallbackButton(text="Ср-Пт-Вс", payload="days:wed_fri_sun"))
    return b


def build_start_training_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="🚀 Начать тренировки", payload="training:start"))
    return b


def build_health_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="✅ Здоров", payload="health:healthy"),
        CallbackButton(text="🤕 Болит рука", payload="health:arm"),
    )
    b.row(
        CallbackButton(text="🤕 Болит спина", payload="health:back"),
        CallbackButton(text="🤕 Болят ноги", payload="health:legs"),
    )
    return b


def build_activity_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="Очень высокая", payload="form:activity:Очень высокая"),
        CallbackButton(text="Высокая", payload="form:activity:Высокая"),
    )
    b.row(
        CallbackButton(text="Средняя", payload="form:activity:Средняя"),
        CallbackButton(text="Низкая", payload="form:activity:Низкая"),
    )
    b.row(CallbackButton(text="❌ Отмена", payload="form:cancel"))
    return b


def build_gender_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="Мужской", payload="form:gender:Мужской"),
        CallbackButton(text="Женский", payload="form:gender:Женский"),
    )
    b.row(CallbackButton(text="❌ Отмена", payload="form:cancel"))
    return b


def build_goal_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="Снизить вес (дефицит)", payload="form:goal:дефицит"))
    b.row(CallbackButton(text="Набрать вес (профицит)", payload="form:goal:профицит"))
    b.row(CallbackButton(text="❌ Отмена", payload="form:cancel"))
    return b


def build_cancel_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="❌ Отмена", payload="form:cancel"))
    return b


def build_check01_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="✅ Да", payload="check:check01_yes"),
        CallbackButton(text="❌ Нет", payload="check:check01_no"),
    )
    return b


def build_check02_prompt_keyboard() -> InlineKeyboardBuilder:
    """Shown before check02 text input to provide context."""
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="❌ Пропустить", payload="check:check02_skip"))
    return b


def build_scheduled_check_keyboard(log_id: int) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(
        CallbackButton(text="✅ Да, выполнил", payload=f"sched:yes:{log_id}"),
        CallbackButton(text="❌ Нет, не выполнил", payload=f"sched:no:{log_id}"),
    )
    return b


def build_technique_keyboard(exercises: list) -> InlineKeyboardBuilder:
    """Build keyboard with exercise names for technique browsing."""
    b = InlineKeyboardBuilder()
    for ex in exercises:
        b.row(CallbackButton(text=f"📋 {ex.name}", payload=f"technique:{ex.id}"))
    b.row(CallbackButton(text="↩️ Назад", payload="training:back"))
    return b


def build_next_week_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="➡️ Следующая неделя", payload="training:next_week"))
    b.row(CallbackButton(text="📋 Основное меню", payload="nav:main"))
    return b


def build_weighin_skip_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.row(CallbackButton(text="⏭ Пропустить", payload="training:skip_weighin"))
    return b
