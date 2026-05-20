ACTIVITY_MULTIPLIERS = {
    "Очень высокая": 1.725,
    "Высокая": 1.55,
    "Средняя": 1.375,
    "Низкая": 1.2,
}


def calculate_bmr(weight: float, height: float, age: int, gender: str, activity_level: str) -> float:
    """Mifflin-St Jeor equation adjusted by activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    if gender == "Мужской":
        base = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        base = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return round(base * multiplier, 2)


def calculate_bmi(weight: float, height: float) -> float:
    """BMI = weight_kg / (height_m)^2"""
    height_m = height / 100
    if height_m <= 0:
        return 0.0
    return round(weight / (height_m ** 2), 1)
