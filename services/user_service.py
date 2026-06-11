import logging
from typing import Optional
from core.models import UserProfile
from core.calculations import calculate_bmr, calculate_bmi
from repositories import user_repo

logger = logging.getLogger(__name__)


def create_full_profile(user_id: int, username: str, height: float, weight: float,
                        activity_level: str, gender: str, age: int, goal: str) -> float:
    """Create a full user profile. Returns calculated BMR."""
    bmr = calculate_bmr(weight, height, age, gender, activity_level, goal)
    user_repo.add_user(user_id, username, height, weight, activity_level, gender, age, bmr, goal)
    logger.info("Created full profile for user %d, BMR=%.2f", user_id, bmr)
    return bmr


def create_short_profile(user_id: int, username: str, weight: float, activity_level: str) -> Optional[float]:
    """Create a short profile update using first profile's inherited fields. Returns BMR or None if no first profile."""
    first = user_repo.get_first_profile(user_id)
    if not first:
        return None
    bmr = calculate_bmr(weight, first.height, first.age, first.gender, activity_level, first.goal)
    user_repo.add_user(user_id, username, first.height, weight, activity_level,
                       first.gender, first.age, bmr, first.goal)
    logger.info("Created short profile for user %d, BMR=%.2f", user_id, bmr)
    return bmr


def get_target_calories(profile: UserProfile, week: int = 1) -> float:
    """Суточная норма калорий с учётом цели, активности и номера недели цикла."""
    return calculate_bmr(
        profile.weight,
        profile.height,
        profile.age,
        profile.gender,
        profile.activity_level,
        profile.goal,
        week=week,
    )


def get_latest_profile(user_id: int) -> Optional[UserProfile]:
    return user_repo.get_latest_profile(user_id)


def get_first_profile(user_id: int) -> Optional[UserProfile]:
    return user_repo.get_first_profile(user_id)


def get_all_profiles(user_id: int) -> list[UserProfile]:
    return user_repo.get_all_profiles(user_id)


def has_forms(user_id: int) -> bool:
    return user_repo.has_user_forms(user_id)


def delete_latest(user_id: int) -> bool:
    return user_repo.delete_latest_profile(user_id)


def delete_all(user_id: int) -> int:
    return user_repo.delete_all_profiles(user_id)


def format_profile(profile: UserProfile) -> str:
    bmi = calculate_bmi(profile.weight, profile.height)
    return (
        f"📊 Ваш профиль:\n\n"
        f"📏 Рост: {profile.height} см\n"
        f"⚖️ Вес: {profile.weight} кг\n"
        f"📐 ИМТ: {bmi}\n"
        f"🏃 Активность: {profile.activity_level}\n"
        f"👤 Пол: {profile.gender}\n"
        f"🎂 Возраст: {profile.age}\n"
        f"🔥 Калории (БМР): {profile.bmr} ккал\n"
        f"🎯 Цель: {profile.goal}\n"
        f"📅 Дата заполнения: {profile.created_at}"
    )


def format_all_profiles(profiles: list[UserProfile]) -> str:
    if not profiles:
        return "У вас нет заполненных анкет."

    lines = []
    for i, p in enumerate(profiles):
        if i == 0:
            lines.append(
                f"📋 Анкета #{i+1}:\n"
                f"  📏 Рост: {p.height} см\n"
                f"  ⚖️ Вес: {p.weight} кг\n"
                f"  🏃 Активность: {p.activity_level}\n"
                f"  👤 Пол: {p.gender}\n"
                f"  🎂 Возраст: {p.age}\n"
                f"  🎯 Цель: {p.goal}\n"
                f"  🔥 БМР: {p.bmr} ккал\n"
                f"  📅 Дата: {p.created_at}"
            )
        else:
            prev = profiles[i - 1]
            changes = []
            if p.weight != prev.weight:
                diff = p.weight - prev.weight
                sign = "+" if diff > 0 else ""
                changes.append(f"  ⚖️ Вес: {p.weight} кг ({sign}{diff:.1f})")
            if p.activity_level != prev.activity_level:
                changes.append(f"  🏃 Активность: {p.activity_level}")
            if p.bmr != prev.bmr:
                changes.append(f"  🔥 БМР: {p.bmr} ккал")
            if not changes:
                changes.append("  Без изменений")
            lines.append(
                f"\n📋 Анкета #{i+1} ({p.created_at}):\n" + "\n".join(changes)
            )

    return "\n".join(lines)
