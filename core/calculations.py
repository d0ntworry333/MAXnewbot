ACTIVITY_MULTIPLIERS = {
    "Очень высокая": 1.725,
    "Высокая": 1.55,
    "Средняя": 1.375,
    "Низкая": 1.2,
}

# Вводный этап (недели 1–2): активность из анкеты × множитель цели.
GOAL_MULTIPLIERS_INTRO = {
    "дефицит": {"Мужской": 0.95, "Женский": 0.95},
    "профицит": {"Мужской": 1.15, "Женский": 1.1},
}

# Основной этап (недели 3+): фиксированная «Средняя» активность 1.375 × множитель цели.
MAIN_STAGE_ACTIVITY = 1.375
GOAL_MULTIPLIERS_MAIN = {
    "дефицит": {"Мужской": 0.9, "Женский": 0.95},
    "профицит": {"Мужской": 1.25, "Женский": 1.15},
}


def _mifflin_base(weight: float, height: float, age: int, gender: str) -> float:
    if gender == "Мужской":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_bmr(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str | None = None,
    week: int = 1,
) -> float:
    """Суточная норма калорий по формуле Миффлина — Сан Жеора."""
    base = _mifflin_base(weight, height, age, gender)
    if week >= 3 and goal:
        tdee = base * MAIN_STAGE_ACTIVITY
        goal_mult = GOAL_MULTIPLIERS_MAIN.get(goal, {}).get(gender, 1.0)
        return round(tdee * goal_mult, 2)
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    tdee = base * multiplier
    if goal:
        goal_mult = GOAL_MULTIPLIERS_INTRO.get(goal, {}).get(gender, 1.0)
        tdee *= goal_mult
    return round(tdee, 2)


def calculate_bmi(weight: float, height: float) -> float:
    """BMI = weight_kg / (height_m)^2"""
    height_m = height / 100
    if height_m <= 0:
        return 0.0
    return round(weight / (height_m ** 2), 1)
