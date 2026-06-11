"""Константы и утилиты 8-недельного цикла программы."""

MAX_PROGRAM_WEEKS = 8

# Недели с полным контентом от заказчика (остальные — заглушки).
WEEKS_WITH_FULL_CONTENT = frozenset({1, 2, 3, 4})

# Недели 3–4 — один блок методички «основной этап».
MAIN_STAGE_WEEKS = frozenset({3, 4})


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
