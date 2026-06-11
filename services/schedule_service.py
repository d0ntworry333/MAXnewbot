import logging
from datetime import date, timedelta
from content.exercises import is_training_day, TRAINING_TYPES
from repositories import session_repo, training_log_repo

logger = logging.getLogger(__name__)


def get_users_needing_evening_check(today: date) -> list[dict]:
    """Return list of {user_id, session_id, training_type} for users who need evening check."""
    weekday = today.weekday()
    today_str = today.isoformat()
    sessions = session_repo.get_all_active_sessions()
    result = []

    for s in sessions:
        if not is_training_day(s.training_days, weekday):
            continue
        if training_log_repo.has_log_for_date(s.user_id, s.id, today_str):
            continue
        training_type = TRAINING_TYPES.get(s.current_day, "Тренировка")
        training_log_repo.add_training_log(
            user_id=s.user_id,
            session_id=s.id,
            training_date=today_str,
            training_type=training_type,
            completed=None,
        )
        result.append({
            "user_id": s.user_id,
            "session_id": s.id,
            "training_type": training_type,
        })

    logger.info("Evening check: %d users need notification", len(result))
    return result


def get_users_needing_reminder(today: date) -> list[dict]:
    """Return list of {user_id, session_id, log_id} for users with pending yesterday logs."""
    yesterday_str = (today - timedelta(days=1)).isoformat()
    pending = training_log_repo.get_pending_logs_for_date(yesterday_str)
    result = [{"user_id": l.user_id, "session_id": l.session_id, "log_id": l.id} for l in pending]
    logger.info("Reminder check: %d users need reminder", len(result))
    return result


def get_sessions_to_deactivate(today: date) -> list[dict]:
    """Return list of {user_id, session_id, log_id} for sessions with 2-day-old pending logs."""
    cutoff_str = (today - timedelta(days=2)).isoformat()
    old_pending = training_log_repo.get_old_pending_logs(cutoff_str)
    result = []
    for log in old_pending:
        session_repo.deactivate_session(log.session_id)
        result.append({"user_id": log.user_id, "session_id": log.session_id, "log_id": log.id})
    logger.info("Reset check: %d sessions deactivated", len(result))
    return result


def handle_scheduled_check_response(log_id: int, session_id: int, user_id: int, completed: bool) -> dict:
    """Handle user response to scheduled training check. Returns status info."""
    from repositories import session_repo as sr
    from repositories import body_weight_repo

    training_log_repo.update_training_log(log_id, completed)

    if completed:
        session = sr.get_active_session(user_id)
        if session:
            from content.exercises import trainings_per_week
            total = trainings_per_week(session.week_number)
            new_completed = session.completed_days + 1
            new_day = (session.current_day + 1) % total
            sr.update_session(session.id, completed_days=new_completed, current_day=new_day)
            week_complete = new_completed >= total
            needs_weighin = body_weight_repo.needs_weigh_in(user_id)
            return {
                "completed": True,
                "week_complete": week_complete,
                "needs_weighin": needs_weighin,
                "completed_days": new_completed,
            }
    return {"completed": False}
