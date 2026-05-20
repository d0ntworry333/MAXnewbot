def parse_height(text: str) -> float | None:
    """Parse height in cm. Valid: 50-250."""
    try:
        value = float(text.replace(",", ".").strip())
        if 50 <= value <= 250:
            return value
    except (ValueError, AttributeError):
        pass
    return None


def parse_weight(text: str) -> float | None:
    """Parse weight in kg. Valid: 20-300."""
    try:
        value = float(text.replace(",", ".").strip())
        if 20 <= value <= 300:
            return value
    except (ValueError, AttributeError):
        pass
    return None


def parse_age(text: str) -> int | None:
    """Parse age. Valid: 1-120."""
    try:
        value = int(text.strip())
        if 1 <= value <= 120:
            return value
    except (ValueError, AttributeError):
        pass
    return None


def parse_exercise_weight(text: str) -> float | None:
    """Parse exercise weight in kg. Valid: >= 0."""
    try:
        value = float(text.replace(",", ".").strip())
        if value >= 0:
            return value
    except (ValueError, AttributeError):
        pass
    return None


def parse_body_weight(text: str) -> float | None:
    """Parse body weight. Valid: 20-300."""
    return parse_weight(text)


VALID_ACTIVITIES = {"Очень высокая", "Высокая", "Средняя", "Низкая"}


def validate_activity(text: str) -> str | None:
    text = text.strip()
    if text in VALID_ACTIVITIES:
        return text
    return None


GENDER_MAP = {"мужской": "Мужской", "женский": "Женский"}


def normalize_gender(text: str) -> str | None:
    return GENDER_MAP.get(text.strip().lower())


GOAL_MAP = {
    "снизить вес (дефицит)": "дефицит",
    "набрать вес (профицит)": "профицит",
}


def normalize_goal(text: str) -> str | None:
    return GOAL_MAP.get(text.strip().lower())
