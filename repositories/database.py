import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

_db_path: str = "data/bot.db"


def set_db_path(path: str) -> None:
    global _db_path
    _db_path = path


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                height REAL,
                weight REAL,
                activity_level TEXT,
                gender TEXT,
                age INTEGER,
                bmr REAL,
                goal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id);

            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_number INTEGER DEFAULT 1,
                training_days TEXT,
                current_day INTEGER DEFAULT 0,
                completed_days INTEGER DEFAULT 0,
                session_active BOOLEAN DEFAULT 1,
                check01_passed BOOLEAN DEFAULT 0,
                check02_passed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_training_user_id ON training_sessions(user_id);

            CREATE TABLE IF NOT EXISTS training_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER,
                training_date DATE,
                training_type TEXT,
                completed BOOLEAN,
                pain_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_training_log_user_id ON training_log(user_id);

            CREATE TABLE IF NOT EXISTS exercise_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER,
                training_date DATE,
                exercise_id INTEGER,
                exercise_name TEXT,
                weight REAL,
                week_number INTEGER,
                day_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_exercise_weights_user ON exercise_weights(user_id);

            CREATE TABLE IF NOT EXISTS weight_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight REAL,
                recorded_at DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_weight_progress_user ON weight_progress(user_id);
        """)
        conn.commit()
        logger.info("Database initialized at %s", _db_path)
    finally:
        conn.close()
