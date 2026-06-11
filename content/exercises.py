from __future__ import annotations
from dataclasses import dataclass

from content.weeks import MAX_PROGRAM_WEEKS, clamp_week


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
        name="Болгарские выпады",
        description="Выпады с опорой задней ноги на возвышение — квадрицепс и ягодицы",
        muscle_groups=["ноги"],
        technique=(
            "🔹 Техника — Болгарские выпады:\n\n"
            "1. Заднюю стопу поставьте на скамью или стул, передняя нога на полу\n"
            "2. Корпус прямой, руки на поясе или перед собой для баланса\n"
            "3. Опуститесь вниз до угла ~90° в переднем колене (2 секунды)\n"
            "4. Выжмите себя вверх через пятку передней ноги (2 секунды)\n"
            "5. Выполните все повторения на одну ногу, затем смените\n\n"
            "⚠️ Колено передней ноги не выходит далеко за носок."
        ),
    ),
    ExerciseDefinition(
        id=2,
        name="Отжимания",
        description="Классические отжимания от пола — грудь, плечи, трицепс",
        muscle_groups=["грудь", "руки"],
        technique=(
            "🔹 Техника — Отжимания:\n\n"
            "1. Упор лёжа, ладони на ширине плеч, корпус прямая линия\n"
            "2. Локти под углом ~45° к корпусу\n"
            "3. Опуститесь до лёгкого касания грудью пола (2 секунды)\n"
            "4. Отожмитесь вверх, полностью выпрямите руки (2 секунды)\n"
            "5. Не прогибайте поясницу и не поднимайте таз\n\n"
            "⚠️ При необходимости используйте резину для помощи в нижней точке."
        ),
    ),
    ExerciseDefinition(
        id=3,
        name="Австралийские подтягивания",
        description="Горизонтальная тяга к перекладине или столу — спина, бицепс",
        muscle_groups=["спина", "руки"],
        technique=(
            "🔹 Техника — Австралийские подтягивания:\n\n"
            "1. Лягте под перекладину, хват чуть шире плеч, тело прямое\n"
            "2. Пятки на полу, корпус напряжён\n"
            "3. Подтяните грудь к перекладине, сводя лопатки (2 секунды)\n"
            "4. Медленно опуститесь вниз, выпрямив руки (2 секунды)\n"
            "5. Чем выше перекладина — тем легче; чем ниже — тем сложнее\n\n"
            "⚠️ Не прогибайте поясницу вверх, работайте спиной."
        ),
    ),
    ExerciseDefinition(
        id=4,
        name="Негативные подтягивания",
        description="Медленное опускание с перекладины — сила спины и рук",
        muscle_groups=["спина", "руки"],
        technique=(
            "🔹 Техника — Негативные подтягивания:\n\n"
            "1. Запрыгните или подтянитесь на перекладину (можно с резиной)\n"
            "2. В верхней точке подбородок над перекладиной\n"
            "3. Медленно опускайтесь вниз 3–5 секунд, контролируя движение\n"
            "4. В нижней точке полностью выпрямите руки\n"
            "5. Помощь в подъёме допустима — акцент на медленном спуске\n\n"
            "⚠️ Не «падать» вниз — только контролируемое опускание."
        ),
    ),
    ExerciseDefinition(
        id=5,
        name="Скручивания в висе",
        description="Подъём коленей или ног к груди в висе — пресс и сгибатели бедра",
        muscle_groups=["кор"],
        technique=(
            "🔹 Техника — Скручивания в висе:\n\n"
            "1. Вис на перекладине, лопатки опущены, корпус стабилен\n"
            "2. Начните с подъёма коленей к груди (2 секунды вверх)\n"
            "3. Медленно опустите ноги вниз без раскачки (2 секунды)\n"
            "4. Не раскачивайтесь и не используйте инерцию\n"
            "5. По мере силы переходите к прямым ногам\n\n"
            "⚠️ Если не хватает силы — согните ноги в коленях."
        ),
    ),
    ExerciseDefinition(
        id=6,
        name="Приседания",
        description="Приседания с собственным весом — квадрицепс, ягодицы",
        muscle_groups=["ноги"],
        technique=(
            "🔹 Техника — Приседания:\n\n"
            "1. Ноги на ширине плеч, носки слегка развёрнуты\n"
            "2. Спина прямая, взгляд вперёд, вес на пятках и середине стопы\n"
            "3. Присядьте до параллели бёдер с полом (2 секунды)\n"
            "4. Встаньте, разгибая ноги и напрягая ягодицы (2 секунды)\n"
            "5. Колени направлены в сторону носков\n\n"
            "⚠️ При необходимости держите резину на плечах для сопротивления."
        ),
    ),
    ExerciseDefinition(
        id=7,
        name="Отжимания на брусьях",
        description="Отжимания на брусьях или параллельных опорах — грудь, трицепс",
        muscle_groups=["грудь", "руки"],
        technique=(
            "🔹 Техника — Отжимания на брусьях:\n\n"
            "1. Упор на брусьях, руки прямые, корпус вертикален\n"
            "2. Слегка наклонитесь вперёд для акцента на грудь\n"
            "3. Опуститесь до угла ~90° в локтях (2 секунды)\n"
            "4. Выжмите себя вверх, выпрямив руки (2 секунды)\n"
            "5. Не опускайтесь слишком глубоко, если болят плечи\n\n"
            "⚠️ Нет брусьев — используйте стулья или низкие опоры."
        ),
    ),
    ExerciseDefinition(
        id=8,
        name="Негативные подтягивания обратным хватом",
        description="Медленное опускание с обратным хватом — акцент на бицепс и широчайшие",
        muscle_groups=["спина", "руки"],
        technique=(
            "🔹 Техника — Негативные подтягивания обратным хватом:\n\n"
            "1. Хват ладонями к себе (обратный), руки на ширине плеч\n"
            "2. Поднимитесь в верхнюю точку с помощью прыжка или резины\n"
            "3. Медленно опускайтесь 3–5 секунд, локти ведите вдоль корпуса\n"
            "4. Внизу полностью выпрямите руки\n"
            "5. Не раскачивайтесь в нижней точке\n\n"
            "⚠️ Обратный хват сильнее нагружает бицепс — следите за локтями."
        ),
    ),
]

EXERCISE_BY_ID: dict[int, ExerciseDefinition] = {e.id: e for e in EXERCISES}


@dataclass
class DayExercise:
    """Упражнение дня с подходами и повторениями."""
    exercise: ExerciseDefinition
    sets: int
    reps: int

    @property
    def prescription(self) -> str:
        return f"{self.sets}×{self.reps}"


def _plan(*items: tuple[int, int, int]) -> list[DayExercise]:
    """(exercise_id, sets, reps) → список DayExercise."""
    result: list[DayExercise] = []
    for eid, sets, reps in items:
        ex = EXERCISE_BY_ID.get(eid)
        if ex:
            result.append(DayExercise(exercise=ex, sets=sets, reps=reps))
    return result


# Недели 1–2: одинаковый план для дефицита и профицита (по методичке заказчика).
_WEEKS_1_2: dict[int, dict[int, list[DayExercise]]] = {
    1: {
        0: _plan((1, 2, 10), (2, 3, 8), (3, 4, 10), (4, 2, 8), (5, 2, 8)),
        1: _plan((6, 3, 18), (7, 3, 8), (3, 4, 10), (8, 2, 8), (5, 2, 8)),
        2: _plan((1, 2, 10), (2, 3, 8), (3, 4, 10), (4, 2, 8), (5, 2, 8)),
    },
    2: {
        0: _plan((1, 4, 12), (2, 4, 10), (3, 3, 12), (4, 2, 10), (5, 3, 10)),
        1: _plan((6, 4, 20), (7, 4, 10), (3, 3, 12), (8, 2, 10), (5, 3, 10)),
        2: _plan((1, 4, 12), (2, 4, 10), (3, 3, 12), (4, 2, 10), (5, 3, 10)),
    },
}

# Недели 3–8: заглушки (пустые планы — контент добавит заказчик).
_WEEKS_STUB: dict[int, dict[int, list[DayExercise]]] = {
    week: {} for week in range(3, MAX_PROGRAM_WEEKS + 1)
}

_ALL_WEEKS: dict[int, dict[int, list[DayExercise]]] = {**_WEEKS_1_2, **_WEEKS_STUB}

WEEKLY_PLANS_BY_GOAL: dict[str, dict[int, dict[int, list[DayExercise]]]] = {
    "дефицит": _ALL_WEEKS,
    "профицит": _ALL_WEEKS,
}

DEFAULT_GOAL = "дефицит"

TRAINING_TYPES: dict[int, str] = {
    0: "День 1: Грудь, Плечи, Трицепс",
    1: "День 2: Спина, Бицепс",
    2: "День 3: Ноги и Кор",
}

DAYS_MAPPING: dict[str, list[int]] = {
    "Пн-Ср-Пт": [0, 2, 4],
    "Вт-Чт-Сб": [1, 3, 5],
    "Ср-Пт-Вс": [2, 4, 6],
}

PAIN_FILTER: dict[str, str] = {
    "arm": "руки",
    "back": "спина",
    "legs": "ноги",
}


def week_has_training_plan(goal: str, week: int) -> bool:
    """Есть ли заполненная программа тренировок на неделю."""
    goal_key = goal if goal in WEEKLY_PLANS_BY_GOAL else DEFAULT_GOAL
    week_plan = WEEKLY_PLANS_BY_GOAL[goal_key].get(clamp_week(week), {})
    return bool(week_plan)


def get_exercises_for_day(goal: str, week: int, day: int) -> list[DayExercise]:
    """Упражнения на день с учётом цели (дефицит / профицит) и номера недели."""
    goal_key = goal if goal in WEEKLY_PLANS_BY_GOAL else DEFAULT_GOAL
    week_plan = WEEKLY_PLANS_BY_GOAL[goal_key].get(clamp_week(week), {})
    return list(week_plan.get(day, []))


def filter_exercises_by_pain(exercises: list[DayExercise], pain_type: str) -> list[DayExercise]:
    """Исключить упражнения на зону с болью."""
    excluded_group = PAIN_FILTER.get(pain_type)
    if not excluded_group:
        return exercises
    return [e for e in exercises if excluded_group not in e.exercise.muscle_groups]


def format_exercise_list(exercises: list[DayExercise]) -> str:
    """Форматированный список упражнений с подходами."""
    if not exercises:
        return "Нет упражнений."
    lines = []
    for i, item in enumerate(exercises, 1):
        ex = item.exercise
        lines.append(f"{i}. {ex.name} — {item.prescription}\n   {ex.description}")
    return "\n\n".join(lines)


def is_training_day(training_days: str, weekday: int) -> bool:
    """Check if given weekday (0=Monday) is a training day for the schedule."""
    days = DAYS_MAPPING.get(training_days, [])
    return weekday in days
