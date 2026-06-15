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


def get_all_exercise_weights(user_id: int) -> list[ExerciseWeight]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM exercise_weights WHERE user_id = ?
               ORDER BY training_date ASC, week_number ASC, day_number ASC, id ASC""",
            (user_id,),
        ).fetchall()
        return [_row_to_exercise_weight(row) for row in rows]
    finally:
        conn.close()


def get_distinct_exercises(user_id: int) -> list[tuple[int, str]]:
    """Уникальные упражнения с записями весов: (exercise_id, exercise_name)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT exercise_id, exercise_name FROM exercise_weights
               WHERE user_id = ?
               GROUP BY exercise_id
               ORDER BY exercise_name ASC""",
            (user_id,),
        ).fetchall()
        return [(row["exercise_id"], row["exercise_name"]) for row in rows]
    finally:
        conn.close()


def get_weights_for_exercise(user_id: int, exercise_id: int) -> list[ExerciseWeight]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM exercise_weights
               WHERE user_id = ? AND exercise_id = ?
               ORDER BY training_date ASC, week_number ASC, day_number ASC, id ASC""",
            (user_id, exercise_id),
        ).fetchall()
        return [_row_to_exercise_weight(row) for row in rows]
    finally:
        conn.close()


def _row_to_exercise_weight(row) -> ExerciseWeight:
    return ExerciseWeight(
        id=row["id"],
        user_id=row["user_id"],
        session_id=row["session_id"],
        training_date=str(row["training_date"]),
        exercise_id=row["exercise_id"],
        exercise_name=row["exercise_name"],
        weight=row["weight"],
        week_number=row["week_number"],
        day_number=row["day_number"],
        created_at=str(row["created_at"]),
    )
