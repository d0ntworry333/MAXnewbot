import logging
from typing import Optional
from core.models import TrainingSession
from repositories.database import get_connection

logger = logging.getLogger(__name__)


def _row_to_session(row) -> TrainingSession:
    keys = row.keys()
    return TrainingSession(
        id=row["id"],
        user_id=row["user_id"],
        week_number=row["week_number"],
        training_days=row["training_days"],
        current_day=row["current_day"],
        completed_days=row["completed_days"],
        session_active=bool(row["session_active"]),
        check01_passed=bool(row["check01_passed"]),
        check02_passed=bool(row["check02_passed"]),
        check03_passed=bool(row["check03_passed"]) if "check03_passed" in keys else False,
        check04_passed=bool(row["check04_passed"]) if "check04_passed" in keys else False,
        check05_passed=bool(row["check05_passed"]) if "check05_passed" in keys else False,
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def get_active_session_by_id(session_id: int) -> Optional[TrainingSession]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM training_sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
        return _row_to_session(row) if row else None
    finally:
        conn.close()


def get_active_session(user_id: int) -> Optional[TrainingSession]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM training_sessions WHERE user_id = ? AND session_active = 1 ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return _row_to_session(row) if row else None
    finally:
        conn.close()


def get_all_active_sessions() -> list[TrainingSession]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM training_sessions WHERE session_active = 1"
        ).fetchall()
        return [_row_to_session(r) for r in rows]
    finally:
        conn.close()


def create_session(user_id: int, training_days: str) -> int:
    conn = get_connection()
    try:
        # Deactivate any existing active sessions
        conn.execute(
            "UPDATE training_sessions SET session_active = 0 WHERE user_id = ? AND session_active = 1",
            (user_id,),
        )
        cursor = conn.execute(
            "INSERT INTO training_sessions (user_id, training_days) VALUES (?, ?)",
            (user_id, training_days),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_session(session_id: int, **kwargs) -> None:
    if not kwargs:
        return
    conn = get_connection()
    try:
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [session_id]
        conn.execute(
            f"UPDATE training_sessions SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values,
        )
        conn.commit()
    finally:
        conn.close()


def advance_week(session_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE training_sessions SET
               week_number = week_number + 1,
               completed_days = 0,
               current_day = 0,
               updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()


def go_previous_week(session_id: int, current_week: int) -> bool:
    if current_week <= 1:
        return False
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE training_sessions SET
               week_number = week_number - 1,
               completed_days = 0,
               current_day = 0,
               updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (session_id,),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def rewind_to_week(session_id: int, week_number: int, clear_checks_from: int) -> None:
    """Откат на неделю и сброс прогресса; сбросить чек clear_checks_from и все последующие."""
    clears = {
        1: {"check01_passed": 0, "check02_passed": 0, "check03_passed": 0,
            "check04_passed": 0, "check05_passed": 0},
        2: {"check02_passed": 0, "check03_passed": 0, "check04_passed": 0, "check05_passed": 0},
        3: {"check03_passed": 0, "check04_passed": 0, "check05_passed": 0},
        4: {"check04_passed": 0, "check05_passed": 0},
        5: {"check05_passed": 0},
    }
    flags = clears.get(clear_checks_from, {})
    conn = get_connection()
    try:
        set_parts = [
            "week_number = ?",
            "completed_days = 0",
            "current_day = 0",
            "updated_at = CURRENT_TIMESTAMP",
        ]
        values: list = [week_number]
        for col, val in flags.items():
            set_parts.append(f"{col} = ?")
            values.append(val)
        values.append(session_id)
        conn.execute(
            f"UPDATE training_sessions SET {', '.join(set_parts)} WHERE id = ?",
            values,
        )
        conn.commit()
    finally:
        conn.close()


def deactivate_session(session_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE training_sessions SET session_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()
