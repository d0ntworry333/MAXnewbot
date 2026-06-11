"""Константы и утилиты 8-недельного цикла программы."""

MAX_PROGRAM_WEEKS = 8

# Недели с полным контентом от заказчика (остальные — заглушки).
WEEKS_WITH_FULL_CONTENT = frozenset({1, 2, 3, 4, 5, 6, 7, 8})

# Блоки методички основного этапа.
MAIN_STAGE_WEEKS_EARLY = frozenset({3, 4})
MAIN_STAGE_WEEKS_MID = frozenset({5, 6})
PEAK_WEEK = frozenset({7})
DELOAD_WEEK = frozenset({8})


def week_has_full_content_for_goal(goal: str, week: int) -> bool:
    """Есть ли методичка для цели и недели (профицит нед. 7 пока без контента)."""
    w = clamp_week(week)
    if w == 7 and goal == "профицит":
        return False
    return w in WEEKS_WITH_FULL_CONTENT


def clamp_week(week: int | None) -> int:
    """Нормализовать номер недели в диапазон 1…MAX_PROGRAM_WEEKS."""
    if week is None or week < 1:
        return 1
    return min(week, MAX_PROGRAM_WEEKS)


def week_has_full_content(week: int) -> bool:
    return clamp_week(week) in WEEKS_WITH_FULL_CONTENT


def week_header(week: int) -> str:
    return f"📅 Неделя {clamp_week(week)}"


def stub_text(section_title: str, goal: str, week: int) -> str:
    """Заглушка для разделов недель 3–8."""
    w = clamp_week(week)
    goal_label = "дефицит калорий" if goal == "дефицит" else "профицит калорий"
    return (
        f"{week_header(w)} · {section_title}\n\n"
        f"⏳ Методичка для недели {w} ({goal_label}) будет добавлена.\n"
        f"Пока ориентируйтесь на рекомендации предыдущих недель и общие правила цикла."
    )
