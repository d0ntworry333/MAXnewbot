"""
In-memory per-user session data store.
Replaces Telegram's context.user_data for transient state
(weight collection queue, form data, pain type, etc.).

This data is lost on restart — same behavior as the original Telegram bot.
"""

from typing import Any

_sessions: dict[int, dict[str, Any]] = {}


def get(user_id: int, key: str, default: Any = None) -> Any:
    return _sessions.get(user_id, {}).get(key, default)


def put(user_id: int, key: str, value: Any) -> None:
    if user_id not in _sessions:
        _sessions[user_id] = {}
    _sessions[user_id][key] = value


def remove(user_id: int, key: str) -> None:
    if user_id in _sessions:
        _sessions[user_id].pop(key, None)


def clear(user_id: int) -> None:
    _sessions.pop(user_id, None)


def get_all(user_id: int) -> dict[str, Any]:
    return _sessions.get(user_id, {})
