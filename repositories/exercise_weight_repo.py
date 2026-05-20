import logging
from core.models import ExerciseWeight
from repositories.database import get_connection

logger = logging.getLogger(__name__)


def save_exercise_weights(user_id: int, session_id: int, training_date: str,
                          week_number: int, day_number: int,
                          weights: list[tuple[int, str, float]]) -> None:
    """Save multiple exercise weights. weights = [(exercise_id, exercise_name, weight), ...]"""
    conn = get_connection()
    try:
        conn.executemany(
            """INSERT INTO exercise_weights (user_id, session_id, training_date,
               exercise_id, exercise_name, weight, week_number, day_number)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [(user_id, session_id, training_date, eid, ename, w, week_number, day_number)
             for eid, ename, w in weights],
        )
        conn.commit()
    finally:
        conn.close()
