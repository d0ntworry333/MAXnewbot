import logging
from datetime import date, timedelta
from typing import Optional
from core.models import BodyWeight
from repositories.database import get_connection

logger = logging.getLogger(__name__)


def add_body_weight(user_id: int, weight: float, recorded_at: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO weight_progress (user_id, weight, recorded_at) VALUES (?, ?, ?)",
            (user_id, weight, recorded_at),
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_body_weight(user_id: int) -> Optional[BodyWeight]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM weight_progress WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if row:
            return BodyWeight(
                id=row["id"],
                user_id=row["user_id"],
                weight=row["weight"],
                recorded_at=str(row["recorded_at"]),
                created_at=str(row["created_at"]),
            )
        return None
    finally:
        conn.close()


def get_all_body_weights(user_id: int) -> list[BodyWeight]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM weight_progress WHERE user_id = ? ORDER BY recorded_at ASC, id ASC",
            (user_id,),
        ).fetchall()
        return [
            BodyWeight(
                id=row["id"],
                user_id=row["user_id"],
                weight=row["weight"],
                recorded_at=str(row["recorded_at"]),
                created_at=str(row["created_at"]),
            )
            for row in rows
        ]
    finally:
        conn.close()


def needs_weigh_in(user_id: int) -> bool:
    """Returns True if user needs a weigh-in (no record or 7+ days since last)."""
    latest = get_latest_body_weight(user_id)
    if not latest:
        return True
    try:
        last_date = date.fromisoformat(latest.recorded_at)
        return (date.today() - last_date).days >= 7
    except (ValueError, TypeError):
        return True
