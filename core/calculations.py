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
GOAL_MULTIPLIERS_MAIN_W34 = {
    "дефицит": {"Мужской": 0.9, "Женский": 0.95},
    "профицит": {"Мужской": 1.25, "Женский": 1.15},
}
GOAL_MULTIPLIERS_MAIN_W56 = {
    "дефицит": {"Мужской": 0.9, "Женский": 0.95},
    "профицит": {"Мужской": 1.1, "Женский": 1.05},
}
GOAL_MULTIPLIERS_MAIN_W7_DEFICIT = {
    "Мужской": 0.85,
    "Женский": 0.9,
}

# Разгрузочная неделя 8: корректировка углеводов (ккал).
DELOAD_DEFICIT_CARB_KCAL = 350   # +75–100 г углеводов
DELOAD_SURPLUS_CARB_KCAL = 250   # −50–75 г углеводов от поддержки


def _main_stage_goal_multiplier(goal: str, gender: str, week: int) -> float:
    if week >= 7 and goal == "дефицит":
        return GOAL_MULTIPLIERS_MAIN_W7_DEFICIT.get(gender, 0.9)
    if week >= 5:
        return GOAL_MULTIPLIERS_MAIN_W56.get(goal, {}).get(gender, 1.0)
    return GOAL_MULTIPLIERS_MAIN_W34.get(goal, {}).get(gender, 1.0)


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
    if week == 8 and goal:
        maintenance = base * MAIN_STAGE_ACTIVITY
        if goal == "дефицит":
            w7 = maintenance * GOAL_MULTIPLIERS_MAIN_W7_DEFICIT.get(gender, 0.9)
            return round(w7 + DELOAD_DEFICIT_CARB_KCAL, 2)
        return round(maintenance - DELOAD_SURPLUS_CARB_KCAL, 2)
    if week >= 3 and goal:
        tdee = base * MAIN_STAGE_ACTIVITY
        goal_mult = _main_stage_goal_multiplier(goal, gender, week)
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
