from content.exercises import EXERCISE_BY_ID, ExerciseDefinition
from typing import Optional


def get_exercise_by_id(exercise_id: int) -> Optional[ExerciseDefinition]:
    return EXERCISE_BY_ID.get(exercise_id)


def get_technique_text(exercise_id: int) -> str:
    ex = EXERCISE_BY_ID.get(exercise_id)
    if not ex:
        return "❌ Упражнение не найдено."
    return ex.technique
