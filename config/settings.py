from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass
class Settings:
    max_bot_token: str
    database_path: str
    timezone: str
    log_level: str
    check_hour_evening: int
    check_minute_evening: int
    reminder_hour: int
    reminder_minute: int
    reset_hour: int
    reset_minute: int
    max_message_length: int

    @classmethod
    def from_env(cls) -> Settings:
        token = os.environ.get("MAX_BOT_TOKEN")
        if not token:
            raise ValueError("MAX_BOT_TOKEN is required")
        return cls(
            max_bot_token=token,
            database_path=os.environ.get("DATABASE_PATH", "data/bot.db"),
            timezone=os.environ.get("TIMEZONE", "Europe/Moscow"),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            check_hour_evening=int(os.environ.get("CHECK_HOUR_EVENING", "23")),
            check_minute_evening=int(os.environ.get("CHECK_MINUTE_EVENING", "0")),
            reminder_hour=int(os.environ.get("REMINDER_HOUR", "16")),
            reminder_minute=int(os.environ.get("REMINDER_MINUTE", "0")),
            reset_hour=int(os.environ.get("RESET_HOUR", "23")),
            reset_minute=int(os.environ.get("RESET_MINUTE", "59")),
            max_message_length=int(os.environ.get("MAX_MESSAGE_LENGTH", "4000")),
        )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


# Lazy singleton — accessed after load_dotenv() is called in main.py
class _SettingsProxy:
    def __getattr__(self, name: str):
        return getattr(get_settings(), name)


settings = _SettingsProxy()  # type: ignore[assignment]
