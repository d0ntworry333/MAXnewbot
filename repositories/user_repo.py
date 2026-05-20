import logging
from typing import Optional
from core.models import UserProfile
from repositories.database import get_connection

logger = logging.getLogger(__name__)


def _row_to_profile(row) -> UserProfile:
    return UserProfile(
        id=row["id"],
        user_id=row["user_id"],
        username=row["username"] or "",
        height=row["height"],
        weight=row["weight"],
        activity_level=row["activity_level"],
        gender=row["gender"],
        age=row["age"],
        bmr=row["bmr"],
        goal=row["goal"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def has_user_forms(user_id: int) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["cnt"] > 0
    finally:
        conn.close()


def add_user(user_id: int, username: str, height: float, weight: float,
             activity_level: str, gender: str, age: int, bmr: float, goal: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users (user_id, username, height, weight, activity_level,
               gender, age, bmr, goal) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, height, weight, activity_level, gender, age, bmr, goal),
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_profile(user_id: int) -> Optional[UserProfile]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return _row_to_profile(row) if row else None
    finally:
        conn.close()


def get_first_profile(user_id: int) -> Optional[UserProfile]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ? ORDER BY id ASC LIMIT 1",
            (user_id,),
        ).fetchone()
        return _row_to_profile(row) if row else None
    finally:
        conn.close()


def get_all_profiles(user_id: int) -> list[UserProfile]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM users WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        ).fetchall()
        return [_row_to_profile(r) for r in rows]
    finally:
        conn.close()


def delete_latest_profile(user_id: int) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if row:
            conn.execute("DELETE FROM users WHERE id = ?", (row["id"],))
            conn.commit()
            return True
        return False
    finally:
        conn.close()


def delete_all_profiles(user_id: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
