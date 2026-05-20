from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ExerciseDefinition:
    id: int
    name: str
    description: str
    muscle_groups: list[str]
    technique: str


EXERCISES: list[ExerciseDefinition] = [
    ExerciseDefinition(
        id=1,
        name="Отжимания с резиной",
        description="Отжимания от пола с резиновым эспандером на спине",
        muscle_groups=["грудь", "руки"],
        technique=(
            "🔹 Техника выполнения — Отжимания с резиной:\n\n"
            "1. Закрепите резинку за спиной, концы держите в ладонях\n"
            "2. Примите упор лёжа, руки на ширине плеч\n"
            "3. Опуститесь, сгибая руки в локтях (2 секунды)\n"
            "4. Отожмитесь вверх, разгибая руки (2 секунды)\n"
            "5. В верхней точке полностью выпрямите руки\n\n"
            "⚠️ Держите корпус прямым, не прогибайте поясницу."
        ),
    ),
    ExerciseDefinition(
        id=2,
        name="Подтягивания с резиной",
        description="Подтягивания на турнике с помощью резинового эспандера",
        muscle_groups=["спина", "руки"],
        technique=(
            "🔹 Техника выполнения — Подтягивания с резиной:\n\n"
            "1. Закрепите резинку на турнике, встаньте ногой в петлю\n"
            "2. Возьмитесь за перекладину хватом чуть шире плеч\n"
            "3. Подтянитесь, подводя грудь к перекладине (2 секунды)\n"
            "4. Медленно опуститесь вниз (2 секунды)\n"
            "5. В нижней точке полностью выпрямите руки\n\n"
            "⚠️ Не раскачивайтесь, работайте мышцами спины."
        ),
    ),
    ExerciseDefinition(
        id=3,
        name="Приседания с резиной",
        description="Приседания с резиновым эспандером на плечах",
        muscle_groups=["ноги"],
        technique=(
            "🔹 Техника выполнения — Приседания с резиной:\n\n"
            "1. Встаньте на резинку, концы держите на плечах\n"
            "2. Ноги на ширине плеч, носки слегка развёрнуты\n"
            "3. Присядьте до параллели бёдер с полом (2 секунды)\n"
            "4. Встаньте, разгибая ноги (2 секунды)\n"
            "5. В верхней точке напрягите ягодицы\n\n"
            "⚠️ Колени не должны выходить за носки."
        ),
    ),
    ExerciseDefinition(
        id=4,
        name="Тяга резины к поясу",
        description="Тяга резинового эспандера к поясу в наклоне",
        muscle_groups=["спина", "руки"],
        technique=(
            "🔹 Техника выполнения — Тяга резины к поясу:\n\n"
            "1. Встаньте на резинку, наклонитесь вперёд на 45°\n"
            "2. Возьмите концы резинки в руки\n"
            "3. Потяните резинку к поясу, сводя лопатки (2 секунды)\n"
            "4. Медленно отпустите вниз (2 секунды)\n"
            "5. Держите спину прямой на протяжении всего движения\n\n"
            "⚠️ Не округляйте спину, смотрите вперёд."
        ),
    ),
    ExerciseDefinition(
        id=5,
        name="Ягодичный мостик с резиной",
        description="Ягодичный мостик с резиновым эспандером на бёдрах",
        muscle_groups=["ноги", "спина"],
        technique=(
            "🔹 Техника выполнения — Ягодичный мостик с резиной:\n\n"
            "1. Лягте на спину, согните ноги в коленях\n"
            "2. Разместите резинку чуть выше колен\n"
            "3. Поднимите таз вверх, напрягая ягодицы (2 секунды)\n"
            "4. Медленно опустите таз вниз (2 секунды)\n"
            "5. В верхней точке разведите колени в стороны против резинки\n\n"
            "⚠️ Не перегибайте поясницу, работайте ягодицами."
        ),
    ),
]

EXERCISE_BY_ID: dict[int, ExerciseDefinition] = {e.id: e for e in EXERCISES}

# Weekly training plans: week_number -> day_number (0,1,2) -> list of exercise IDs
# Only week 1 is populated (same as original bot)
WEEKLY_PLANS: dict[int, dict[int, list[int]]] = {
    1: {
        0: [1, 4],      # Day 1 (Push): Отжимания, Тяга резины
        1: [2, 4],      # Day 2 (Pull): Подтягивания, Тяга резины
        2: [3, 5],      # Day 3 (Legs): Приседания, Ягодичный мостик
    },
}

TRAINING_TYPES: dict[int, str] = {
    0: "День 1: Грудь, Плечи, Трицепс",
    1: "День 2: Спина, Бицепс",
    2: "День 3: Ноги и Кор",
}

DAYS_MAPPING: dict[str, list[int]] = {
    "Пн-Ср-Пт": [0, 2, 4],    # Monday=0, Wednesday=2, Friday=4
    "Вт-Чт-Сб": [1, 3, 5],    # Tuesday=1, Thursday=3, Saturday=5
    "Ср-Пт-Вс": [2, 4, 6],    # Wednesday=2, Friday=4, Sunday=6
}

PAIN_FILTER: dict[str, str] = {
    "arm": "руки",
    "back": "спина",
    "legs": "ноги",
}


def get_exercises_for_day(week: int, day: int) -> list[ExerciseDefinition]:
    """Return exercises for given week and day. Empty list if not defined."""
    week_plan = WEEKLY_PLANS.get(week, {})
    exercise_ids = week_plan.get(day, [])
    return [EXERCISE_BY_ID[eid] for eid in exercise_ids if eid in EXERCISE_BY_ID]


def filter_exercises_by_pain(exercises: list[ExerciseDefinition], pain_type: str) -> list[ExerciseDefinition]:
    """Filter out exercises targeting the painful muscle group."""
    excluded_group = PAIN_FILTER.get(pain_type)
    if not excluded_group:
        return exercises
    return [e for e in exercises if excluded_group not in e.muscle_groups]


def format_exercise_list(exercises: list[ExerciseDefinition]) -> str:
    """Format exercise list for display."""
    if not exercises:
        return "Нет упражнений."
    lines = []
    for i, ex in enumerate(exercises, 1):
        lines.append(f"{i}. {ex.name}\n   {ex.description}")
    return "\n\n".join(lines)


def is_training_day(training_days: str, weekday: int) -> bool:
    """Check if given weekday (0=Monday) is a training day for the schedule."""
    days = DAYS_MAPPING.get(training_days, [])
    return weekday in days
