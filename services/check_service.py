"""Логика 5 чеков цикла: прохождение, блокировка перехода, откат недель."""

import logging

from content.checks import check_after_week, get_check
from core.models import TrainingSession
from repositories import session_repo

logger = logging.getLogger(__name__)

_CHECK_FIELDS = {
    1: "check01_passed",
    2: "check02_passed",
    3: "check03_passed",
    4: "check04_passed",
    5: "check05_passed",
}


def is_check_passed(session: TrainingSession, check_id: int) -> bool:
    field = _CHECK_FIELDS.get(check_id)
    if not field:
        return False
    return bool(getattr(session, field, False))


def pending_check_before_next_week(session: TrainingSession) -> int | None:
    """Какой чек нужно пройти перед переходом с текущей недели на следующую."""
    check_id = check_after_week(session.week_number)
    if not check_id:
        return None
    if is_check_passed(session, check_id):
        return None
    return check_id


def mark_check_passed(session_id: int, check_id: int) -> None:
    field = _CHECK_FIELDS.get(check_id)
    if field:
        session_repo.update_session(session_id, **{field: True})
        logger.info("Session %d passed check %d", session_id, check_id)


def apply_check_failure(session_id: int, check_id: int) -> str:
    """Откат недели при провале чека. Возвращает сообщение пользователю."""
    check = get_check(check_id)
    if not check or check.fail_target_week is None:
        return "❌ Чек не пройден."

    field = _CHECK_FIELDS[check_id]
    session_repo.rewind_to_week(
        session_id,
        week_number=check.fail_target_week,
        clear_checks_from=check_id,
    )
    logger.info(
        "Session %d failed check %d — rewind to week %d",
        session_id, check_id, check.fail_target_week,
    )
    return check.fail_message


def can_advance_week(session: TrainingSession) -> bool:
    if session.week_number >= 8:
        return False
    return pending_check_before_next_week(session) is None
