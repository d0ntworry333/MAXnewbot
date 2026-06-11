"""Пять контрольных чеков 8-недельного цикла."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CycleCheck:
    id: int
    title: str
    question: str
    fail_message: str
    """Неделя, на которую возвращаем при провале (None — без отката)."""
    fail_target_week: int | None
    after_week: int
    final: bool = False


# Чек после завершения недели N, перед переходом на N+1 (чек 5 — после нед. 8).
CHECK_AFTER_WEEK: dict[int, int] = {
    2: 1,
    4: 2,
    6: 3,
    7: 4,
    8: 5,
}

CYCLE_CHECKS: dict[int, CycleCheck] = {
    1: CycleCheck(
        id=1,
        title="Чек 1 — вводный этап",
        question=(
            "📋 Чек 1 — вводный этап (недели 1–2)\n\n"
            "Ответьте честно:\n"
            "• Освоились с техникой упражнений?\n"
            "• Получается соблюдать суточную калорийность?\n\n"
            "Если «Нет» — повторите неделю 2, пока не будет уверенности."
        ),
        fail_message=(
            "❌ Чек 1 не пройден.\n\n"
            "Возвращаемся на неделю 2: закрепите технику и калорийность, "
            "затем снова выполните все тренировки недели."
        ),
        fail_target_week=2,
        after_week=2,
    ),
    2: CycleCheck(
        id=2,
        title="Чек 2 — основной этап",
        question=(
            "📋 Чек 2 (после недель 3–4)\n\n"
            "Стабильно ли выходят тренировки в зале?\n"
            "Вы посещаете зал по плану без постоянных срывов?"
        ),
        fail_message=(
            "❌ Чек 2 не пройден.\n\n"
            "Повторите неделю 4: стабильность важнее спешки."
        ),
        fail_target_week=4,
        after_week=4,
    ),
    3: CycleCheck(
        id=3,
        title="Чек 3 — прогрессия",
        question=(
            "📋 Чек 3 (после недель 5–6)\n\n"
            "Стало ли получаться ставить больше силовой вес "
            "(или больше повторений при той же технике)?"
        ),
        fail_message=(
            "❌ Чек 3 не пройден.\n\n"
            "Возврат на неделю 5: закрепите прогрессию в знакомых упражнениях."
        ),
        fail_target_week=5,
        after_week=6,
    ),
    4: CycleCheck(
        id=4,
        title="Чек 4 — результат по весу",
        question=(
            "📋 Чек 4 (после недели 7)\n\n"
            "Есть ли результат по весу тела за цикл "
            "(снижение жира / рост массы — в зависимости от цели)?"
        ),
        fail_message=(
            "❌ Чек 4 не пройден.\n\n"
            "Возврат на неделю 5: пересоберите режим питания и тренировок, "
            "затем снова пройдите путь к финалу."
        ),
        fail_target_week=5,
        after_week=7,
    ),
    5: CycleCheck(
        id=5,
        title="Чек 5 — итоги цикла",
        question=(
            "🎉 Чек 5 — завершение 8-недельного цикла!\n\n"
            "Давайте проведём замер и посмотрим на ваш путь.\n\n"
            "Готовы подвести итоги?"
        ),
        fail_message="",
        fail_target_week=None,
        after_week=8,
        final=True,
    ),
}


def check_after_week(week: int) -> int | None:
    return CHECK_AFTER_WEEK.get(week)


def get_check(check_id: int) -> CycleCheck | None:
    return CYCLE_CHECKS.get(check_id)
