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


def _tech(name: str, body: str) -> str:
    return f"🔹 Техника — {name}:\n\n{body}"


EXERCISES: list[ExerciseDefinition] = [
    ExerciseDefinition(
        id=1,
        name="Болгарские выпады",
        description="Выпады с опорой задней ноги на возвышение — квадрицепс и ягодицы",
        muscle_groups=["ноги"],
        technique=_tech(
            "Болгарские выпады",
            "Задняя нога на скамье, передняя стопа впереди (для девушек дальше, для мужчин ближе), "
            "спина прямая, согните переднее колено, вернитесь вверх усилием передней ноги.",
        ),
    ),
    ExerciseDefinition(
        id=2,
        name="Отжимания",
        description="Классические отжимания от пола — грудь, плечи, трицепс",
        muscle_groups=["грудь", "руки"],
        technique=_tech(
            "Отжимания",
            "Упор лёжа, лопатки сведены, тело прямое, опустите грудь к полу локти назад-в стороны, "
            "руками давите будто сжимая землю внутрь, вернитесь в исходное положение.",
        ),
    ),
    ExerciseDefinition(
        id=3,
        name="Австралийские подтягивания",
        description="Горизонтальная тяга к перекладине или столу — спина, бицепс",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Австралийские подтягивания",
            "Возьмитесь за перекладину на уровне пояса, тело прямое, пятки на полу, "
            "подтянитесь к перекладине сводя лопатки (касание низом груди), "
            "задержитесь и плавно вернитесь.",
        ),
    ),
    ExerciseDefinition(
        id=4,
        name="Негативные подтягивания",
        description="Медленное опускание с перекладины — сила спины и рук",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Негативные подтягивания",
            "Из верхней точки медленно опускайтесь вниз на прямые руки, грудь смотрит вверх.",
        ),
    ),
    ExerciseDefinition(
        id=5,
        name="Скручивания в висе",
        description="Подъём коленей или ног к груди в висе — пресс и сгибатели бедра",
        muscle_groups=["кор"],
        technique=_tech(
            "Скручивания в висе",
            "Вис на перекладине, спина/ягодицы прижаты к стене/упору. Ноги согнуты — "
            "скрутите таз вверх. Задача не поднять ноги, а именно скрутить таз, "
            "без раскачки, медленно опустите обратно.",
        ),
    ),
    ExerciseDefinition(
        id=6,
        name="Приседания",
        description="Приседания с собственным весом — квадрицепс, ягодицы",
        muscle_groups=["ноги"],
        technique=_tech(
            "Приседания",
            "Ноги немного уже ширины плеч, стопы слегка наружу, спина ровная, таз назад, "
            "максимально опуститесь, колени по направлению стоп — подъём в изначальное положение.",
        ),
    ),
    ExerciseDefinition(
        id=7,
        name="Отжимания на брусьях",
        description="Отжимания на брусьях или параллельных опорах — грудь, трицепс",
        muscle_groups=["грудь", "руки"],
        technique=_tech(
            "Отжимания на брусьях",
            "На прямых руках, тело наклонено вперёд, опуститесь сгибая локти в стороны, "
            "выжмите корпус вверх.",
        ),
    ),
    ExerciseDefinition(
        id=8,
        name="Негативные подтягивания обратным хватом",
        description="Медленное опускание с обратным хватом — акцент на бицепс и широчайшие",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Негативные подтягивания обратным хватом",
            "Хват ладонями к себе, из верхней точки медленно опускайтесь, "
            "внизу полностью разогните руки, грудь направлена вверх.",
        ),
    ),
    # ── Основной этап (недели 3+), тренажёрный зал ──
    ExerciseDefinition(
        id=9, name="Бабочка",
        description="Сведение рук в тренажёре «бабочка» — грудные мышцы",
        muscle_groups=["грудь"],
        technique=_tech(
            "Бабочка",
            "Сидя в тренажёре: сведите лопатки, прижмите спину, локти минимально согнуты, "
            "сведите руки перед грудью, медленно вернитесь, "
            "сделайте паузу в момент максимального растяжения грудных.",
        ),
    ),
    ExerciseDefinition(
        id=10, name="Подтягивания",
        description="Подтягивания на перекладине — спина, бицепс",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Подтягивания",
            "Вис параллельным хватом, на выдохе сведите лопатки и подтянитесь к перекладине, "
            "грудь смотрит вверх, плавно опуститесь.",
        ),
    ),
    ExerciseDefinition(
        id=11, name="Жим гантелей сидя",
        description="Жим гантелей сидя — передние дельты",
        muscle_groups=["плечи", "руки"],
        technique=_tech(
            "Жим гантелей сидя",
            "Сидя с опорой спины, ладони вперёд выжмите вверх полностью распрямляя руки, "
            "гантели почти соприкасаются, медленно опустите.",
        ),
    ),
    ExerciseDefinition(
        id=12, name="Махи гантелей в стороны",
        description="Разведение гантелей в стороны — средние дельты",
        muscle_groups=["плечи"],
        technique=_tech(
            "Махи гантелей в стороны",
            "Стоя, гантели в опущенных руках, локти минимально согнуты, "
            "разведите руки чуть выше уровня ушей, медленно опустите.",
        ),
    ),
    ExerciseDefinition(
        id=13, name="Строгий подъём на бицепс сидя",
        description="Сгибание рук с гантелями сидя — бицепс",
        muscle_groups=["руки"],
        technique=_tech(
            "Строгий подъём на бицепс сидя",
            "Сидя в наклоне, гантели в руках ладони немного в стороны, локти прижаты к лавке, "
            "согните руки поднимая гантели к плечам, опустите разгибая руки.",
        ),
    ),
    ExerciseDefinition(
        id=14, name="Разгибания ног",
        description="Разгибание ног в тренажёре — квадрицепс",
        muscle_groups=["ноги"],
        technique=_tech(
            "Разгибания ног",
            "Спинку тренажёра максимально отклоните назад. Прижмите ягодицы к сиденью. "
            "В стартовом положении вы должны чувствовать небольшое натяжение в квадрицепсе. "
            "Полностью разогните ноги, медленно опустите.",
        ),
    ),
    ExerciseDefinition(
        id=15, name="Сгибания ног лёжа",
        description="Сгибание ног лёжа — бицепс бедра",
        muscle_groups=["ноги"],
        technique=_tech(
            "Сгибания ног лёжа",
            "Натяните носки на себя, согните ноги пытаясь достать пятками до ягодиц, плавно опустите.",
        ),
    ),
    ExerciseDefinition(
        id=16, name="Разведение ног в тренажёре",
        description="Разведение ног сидя — средняя ягодичная",
        muscle_groups=["ноги"],
        technique=_tech(
            "Разведение ног в тренажёре",
            "Колени упираются в подушки, максимально разведите ноги, медленно сведите обратно.",
        ),
    ),
    ExerciseDefinition(
        id=17, name="Сведение ног в тренажёре",
        description="Сведение ног сидя — приводящие мышцы",
        muscle_groups=["ноги"],
        technique=_tech(
            "Сведение ног в тренажёре",
            "Ноги широко разведены, сведите бёдра, медленно разведите обратно.",
        ),
    ),
    ExerciseDefinition(
        id=18, name="Румынская тяга",
        description="Румынская тяга — бицепс бедра, ягодицы",
        muscle_groups=["ноги", "спина"],
        technique=_tech(
            "Румынская тяга",
            "Стоя, штанга в опущенных руках (лямки), колени чуть согнуты, спина прямая, "
            "без сгибания ног наклонитесь скользя штангой вдоль ног, "
            "сконцентрируйтесь на том, чтобы максимально отвести таз назад. "
            "Разгонитесь в положение стоя.",
        ),
    ),
    ExerciseDefinition(
        id=19, name="Подъёмы на носки",
        description="Подъёмы на икры стоя или сидя",
        muscle_groups=["ноги"],
        technique=_tech(
            "Подъёмы на носки",
            "Стоя носками на возвышении, пятки на весу, опустите пятки растягивая икры, "
            "немного задержитесь в этом положении, поднимитесь до параллели с носками.",
        ),
    ),
    ExerciseDefinition(
        id=20, name="Жим гантелей в наклоне",
        description="Жим гантелей на наклонной скамье — верх груди",
        muscle_groups=["грудь", "руки"],
        technique=_tech(
            "Жим гантелей в наклоне",
            "Лежа на наклонной скамье (30 градусов), гантели в руках, вверх по дуге почти касаясь их, "
            "на вдохе плавно опустите максимально растягивая грудные в нижней точке движения.",
        ),
    ),
    ExerciseDefinition(
        id=21, name="Y-разводка",
        description="Разведение рук в плоскости Y — задние дельты",
        muscle_groups=["плечи", "спина"],
        technique=_tech(
            "Y-разводка",
            "Лежа на наклонной скамье (20 градусов), гантели в руках. "
            "Чуть приподнимите грудь, оторвав верхнюю часть спины от спинки. "
            "Разведите руки в стороны (немного вперёд) до уровня чуть выше ушей, медленно опустите.",
        ),
    ),
    ExerciseDefinition(
        id=22, name="Тяга штанги к поясу",
        description="Тяга штанги в наклоне к поясу — спина",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Тяга штанги к поясу",
            "Наклон корпуса параллельно полу на протяжении всего упражнения, спина прямая (пояс, лямки), "
            "подтяните штангу к середине живота отводя локти назад, "
            "немного задержитесь, медленно опустите обратно.",
        ),
    ),
    ExerciseDefinition(
        id=23, name="Пуловер в кроссовере",
        description="Пуловер в блочном тренажёре — грудь, широчайшие",
        muscle_groups=["грудь", "спина"],
        technique=_tech(
            "Пуловер в кроссовере",
            "Лицом к кроссоверу, рукоять над головой, локти чуть согнуты, немного сведя лопатки, "
            "выгните спину грудь поднимая вверх, тяните вниз к бёдрам по дуге напрягая широчайшие, "
            "медленно вернитесь вверх.",
        ),
    ),
    ExerciseDefinition(
        id=24, name="Разгибание рук в кроссовере",
        description="Разгибание рук на блоке — трицепс",
        muscle_groups=["руки"],
        technique=_tech(
            "Разгибание рук в кроссовере",
            "Лицом к кроссоверу, прямая рукоять, локти прижаты к корпусу и не уходят в стороны, "
            "разогните руки вниз, медленно согните.",
        ),
    ),
    ExerciseDefinition(
        id=25, name="Французский жим",
        description="Разгибание рук из-за головы — трицепс",
        muscle_groups=["руки"],
        technique=_tech(
            "Французский жим",
            "Лёжа на скамье: штанга на выпрямленных руках над грудью, на вдохе согните локти "
            "опуская вес за голову (локти неподвижны и направлены вперёд), разогните руки.",
        ),
    ),
    ExerciseDefinition(
        id=26, name="Рычажная тяга",
        description="Тяга в рычажном тренажёре — спина",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Рычажная тяга",
            "Сидя в тренажёре, потяните рукояти к животу сводя лопатки, "
            "немного отклоняясь назад, плавно вернитесь в изначальное положение.",
        ),
    ),
    ExerciseDefinition(
        id=27, name="Ягодичный мостик",
        description="Ягодичный мостик — ягодицы, задняя поверхность бедра",
        muscle_groups=["ноги"],
        technique=_tech(
            "Ягодичный мостик",
            "Лёжа на спине, колени согнуты, стопы на полу, штанга на поясе, "
            "поднимите таз до прямой линии, плавно опуститесь не касаясь штангой пола.",
        ),
    ),
    ExerciseDefinition(
        id=28, name="Тяга верхнего блока к груди",
        description="Вертикальная тяга на блоке — широчайшие, бицепс",
        muscle_groups=["спина", "руки"],
        technique=_tech(
            "Тяга верхнего блока к груди",
            "Сидя, бёдра зафиксированы, нейтральный хват, корпус чуть назад, "
            "потяните рукоять к низу груди сводя лопатки, плавно верните вверх.",
        ),
    ),
]

EXERCISE_BY_ID: dict[int, ExerciseDefinition] = {e.id: e for e in EXERCISES}


@dataclass
class DayExercise:
    """Упражнение дня с подходами и повторениями."""
    exercise: ExerciseDefinition
    sets: int
    reps: int | str

    @property
    def prescription(self) -> str:
        return f"{self.sets}×{self.reps}"


def _plan(*items: tuple[int, int, int | str]) -> list[DayExercise]:
    """(exercise_id, sets, reps) → список DayExercise."""
    result: list[DayExercise] = []
    for eid, sets, reps in items:
        ex = EXERCISE_BY_ID.get(eid)
        if ex:
            result.append(DayExercise(exercise=ex, sets=sets, reps=reps))
    return result


# Недели 1–2: одинаковый план для дефицита и профицита (по методичке заказчика).
WEEKLY_PLANS_INTRO: dict[int, dict[int, list[DayExercise]]] = {
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

# Недели 3–4 профицит (мужчины) — методичка 3–4.
_MEN_SURPLUS_W34 = {
    0: _plan((9, 2, 10), (10, 3, 10), (11, 2, "6-8"), (7, 3, 8), (12, 3, "10-12"), (13, 2, 10), (5, 2, "10-15")),
    1: _plan((14, 4, 10), (15, 3, 10), (16, 2, 10), (17, 2, "10-12"), (1, 2, 10), (18, 2, 10), (19, 2, "12-15")),
    2: _plan((20, 2, 10), (21, 3, "10-12"), (22, 2, 10), (23, 2, 10), (7, 3, 10), (13, 2, 10), (24, 2, 10)),
}
# Недели 5–6–7 профицит (мужчины) — методичка нед. 7.
_MEN_SURPLUS_W567 = {
    0: _plan((9, 2, 10), (10, 3, 10), (11, 2, "6-8"), (7, 3, 8), (12, 3, "10-12"), (13, 2, 10), (5, 2, "10-15")),
    1: _plan((14, 4, 10), (15, 3, 10), (16, 2, 10), (17, 2, "10-12"), (1, 2, 10), (18, 2, 10), (19, 2, "12-15")),
    2: _plan((20, 2, 10), (21, 3, "10-12"), (22, 2, 10), (23, 2, 10), (7, 3, 10), (13, 2, 10), (24, 2, 10)),
}
_MEN_DEFICIT_W34 = {
    0: _plan((7, 3, "10-12"), (10, 3, "8-10"), (12, 3, "10-12"), (13, 2, 10), (25, 2, 10), (5, 3, "10-15")),
    1: _plan((14, 3, 10), (15, 3, 10), (17, 2, "10-12"), (1, 2, 10), (19, 3, "12-15")),
    2: _plan((20, 3, 10), (21, 3, "10-12"), (23, 3, 10), (7, 2, 10), (13, 2, 10), (26, 3, 10)),
}
_WOMEN_LOWER_UPPER_W34 = {
    0: _plan((14, 2, 10), (16, 3, 10), (15, 2, 10), (27, 2, 10), (19, 2, "12-15")),
    1: _plan((3, 2, "10-12"), (12, 3, 10), (23, 2, 10), (7, 2, 10), (13, 2, 10), (5, 2, "10-12")),
    2: _plan((1, 2, 10), (15, 2, 10), (16, 3, 10), (17, 2, 10), (27, 2, 10)),
}
# Недели 3–7 профицит (женщины) — программа недель 3–4.
_WOMEN_SURPLUS_W34 = _WOMEN_LOWER_UPPER_W34


def _weeks_bundle(
    week_numbers: tuple[int, ...],
    plan: dict[int, list[DayExercise]],
) -> dict[int, dict[int, list[DayExercise]]]:
    return {w: plan for w in week_numbers}


def _merge_week_plans(*parts: dict[int, dict[int, list[DayExercise]]]) -> dict[int, dict[int, list[DayExercise]]]:
    merged: dict[int, dict[int, list[DayExercise]]] = {}
    for part in parts:
        merged.update(part)
    return merged


# Неделя 8: разгрузка, 2 тренировки фулбади.
_MEN_DEFICIT_W8 = {
    0: _plan((14, 2, 10), (28, 2, 10), (20, 2, 10), (12, 2, 12), (13, 2, 10), (5, 2, 12)),
    1: _plan((15, 2, 10), (26, 2, 10), (2, 2, 10), (21, 2, 12), (25, 2, 10)),
}
_WOMEN_DEFICIT_W8 = {
    0: _plan((27, 2, 10), (3, 2, 10), (16, 2, 12), (12, 2, 12), (5, 2, 12)),
    1: _plan((18, 2, 10), (23, 2, 10), (17, 2, 12), (2, 2, 10), (19, 2, 15)),
}
_MEN_SURPLUS_W8 = {
    0: _plan((14, 2, 10), (28, 2, 10), (20, 2, 10), (12, 2, 12), (13, 2, 10), (5, 2, 12)),
    1: _plan((15, 2, 10), (26, 2, 10), (20, 2, 12), (21, 2, 12), (25, 2, 10)),
}
_WOMEN_SURPLUS_W8 = {
    0: _plan((27, 2, 10), (3, 2, 10), (16, 2, 12), (12, 2, 12), (5, 2, 12)),
    1: _plan((18, 2, 10), (23, 2, 10), (17, 2, 12), (2, 2, 10), (19, 2, 15)),
}

WEEKLY_PLANS_MAIN_STAGE: dict[str, dict[str, dict[int, dict[int, list[DayExercise]]]]] = {
    "дефицит": {
        "Мужской": _merge_week_plans(
            _weeks_bundle((3, 4, 5, 6, 7), _MEN_DEFICIT_W34),
            {8: _MEN_DEFICIT_W8},
        ),
        "Женский": _merge_week_plans(
            _weeks_bundle((3, 4, 5, 6, 7), _WOMEN_LOWER_UPPER_W34),
            {8: _WOMEN_DEFICIT_W8},
        ),
    },
    "профицит": {
        "Мужской": _merge_week_plans(
            _weeks_bundle((3, 4), _MEN_SURPLUS_W34),
            _weeks_bundle((5, 6, 7), _MEN_SURPLUS_W567),
            {8: _MEN_SURPLUS_W8},
        ),
        "Женский": _merge_week_plans(
            _weeks_bundle((3, 4, 5, 6, 7), _WOMEN_SURPLUS_W34),
            {8: _WOMEN_SURPLUS_W8},
        ),
    },
}

DEFAULT_GOAL = "дефицит"
DEFAULT_GENDER = "Мужской"

TRAINING_TYPES_INTRO: dict[int, str] = {
    0: "День 1: Грудь, Плечи, Трицепс",
    1: "День 2: Спина, Бицепс",
    2: "День 3: Ноги и Кор",
}

TRAINING_TYPES_MALE_MAIN: dict[int, str] = {
    0: "День 1: Верх",
    1: "День 2: Низ",
    2: "День 3: Верх",
}

TRAINING_TYPES_FEMALE_MAIN: dict[int, str] = {
    0: "День 1: Низ",
    1: "День 2: Верх",
    2: "День 3: Низ",
}

TRAINING_TYPES_DELOAD: dict[int, str] = {
    0: "День 1: Фулбади",
    1: "День 2: Фулбади",
}

# Обратная совместимость
TRAINING_TYPES = TRAINING_TYPES_INTRO


def trainings_per_week(week: int) -> int:
    """Сколько тренировок в неделе (на 8-й — разгрузка, 2 дня)."""
    return 2 if clamp_week(week) == 8 else 3


def _normalize_gender(gender: str | None) -> str:
    if gender in ("Мужской", "Женский"):
        return gender
    return DEFAULT_GENDER


def get_training_day_label(week: int, day: int, gender: str | None = None) -> str:
    w = clamp_week(week)
    if w == 8:
        return TRAINING_TYPES_DELOAD.get(day, f"День {day + 1}")
    if w <= 2:
        return TRAINING_TYPES_INTRO.get(day, f"День {day + 1}")
    g = _normalize_gender(gender)
    types = TRAINING_TYPES_FEMALE_MAIN if g == "Женский" else TRAINING_TYPES_MALE_MAIN
    return types.get(day, f"День {day + 1}")

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


def _week_plan(goal: str, week: int, gender: str | None) -> dict[int, list[DayExercise]]:
    goal_key = goal if goal in WEEKLY_PLANS_MAIN_STAGE else DEFAULT_GOAL
    w = clamp_week(week)
    if w <= 2:
        return WEEKLY_PLANS_INTRO.get(w, {})
    g = _normalize_gender(gender)
    return WEEKLY_PLANS_MAIN_STAGE[goal_key][g].get(w, {})


def week_has_training_plan(goal: str, week: int, gender: str | None = None) -> bool:
    """Есть ли заполненная программа тренировок на неделю."""
    return bool(_week_plan(goal, week, gender))


def get_exercises_for_day(
    goal: str,
    week: int,
    day: int,
    gender: str | None = None,
) -> list[DayExercise]:
    """Упражнения на день: цель, неделя, день, пол (для недель 3+)."""
    return list(_week_plan(goal, week, gender).get(day, []))


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
