import logging
from datetime import date
from typing import Optional
from core.models import TrainingLog
from repositories.database import get_connection

logger = logging.getLogger(__name__)


def _row_to_log(row) -> TrainingLog:
    return TrainingLog(
        id=row["id"],
        user_id=row["user_id"],
        session_id=row["session_id"],
        training_date=str(row["training_date"]),
        training_type=row["training_type"] or "",
        completed=row["completed"] if row["completed"] is not None else None,
        pain_feedback=row["pain_feedback"],
        created_at=str(row["created_at"]),
    )


def add_training_log(user_id: int, session_id: int, training_date: str,
                     training_type: str, completed: Optional[bool] = None,
                     pain_feedback: Optional[str] = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO training_log (user_id, session_id, training_date,
               training_type, completed, pain_feedback) VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, session_id, training_date, training_type, completed, pain_feedback),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_training_log(log_id: int, completed: bool) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE training_log SET completed = ? WHERE id = ?",
            (completed, log_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_pending_log(user_id: int, session_id: int, training_date: str) -> Optional[TrainingLog]:
    conn = get_connection()
    try:
        row = conn.execute(
            """SELECT * FROM training_log WHERE user_id = ? AND session_id = ?
               AND training_date = ? AND completed IS NULL LIMIT 1""",
            (user_id, session_id, training_date),
        ).fetchone()
        return _row_to_log(row) if row else None
    finally:
        conn.close()


def get_pending_logs_for_date(training_date: str) -> list[TrainingLog]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM training_log WHERE training_date = ? AND completed IS NULL",
            (training_date,),
        ).fetchall()
        return [_row_to_log(r) for r in rows]
    finally:
        conn.close()


def get_old_pending_logs(before_date: str) -> list[TrainingLog]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM training_log WHERE training_date <= ? AND completed IS NULL",
            (before_date,),
        ).fetchall()
        return [_row_to_log(r) for r in rows]
    finally:
        conn.close()


def has_log_for_date(user_id: int, session_id: int, training_date: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM training_log WHERE user_id = ? AND session_id = ? AND training_date = ?",
            (user_id, session_id, training_date),
        ).fetchone()
        return row["cnt"] > 0
    finally:
        conn.close()
