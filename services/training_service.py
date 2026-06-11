import logging
from datetime import date
from typing import Optional
from core.models import TrainingSession
from content.exercises import (
    TRAINING_TYPES,
    get_exercises_for_day,
    filter_exercises_by_pain,
    format_exercise_list,
    week_has_training_plan,
)
from content.texts import TEXT_EXERCISES_WEEK_STUB
from content.weeks import clamp_week
from repositories import session_repo, training_log_repo, exercise_weight_repo, body_weight_repo

logger = logging.getLogger(__name__)


def get_active_session(user_id: int) -> Optional[TrainingSession]:
    return session_repo.get_active_session(user_id)


def resolve_user_week(user_id: int) -> int:
    """Текущая неделя цикла: из активной сессии или 1 по умолчанию."""
    session = session_repo.get_active_session(user_id)
    if session:
        return clamp_week(session.week_number)
    return 1


def create_session(user_id: int, training_days: str) -> int:
    session_id = session_repo.create_session(user_id, training_days)
    logger.info("Created training session %d for user %d, days=%s", session_id, user_id, training_days)
    return session_id


def get_training_status(session: TrainingSession) -> str:
    return (
        f"📊 Статус тренировок:\n\n"
        f"📅 Неделя: {session.week_number}\n"
        f"🗓 Дни тренировок: {session.training_days}\n"
        f"✅ Выполнено: {session.completed_days}/3\n"
        f"📌 Текущий день: {TRAINING_TYPES.get(session.current_day, 'N/A')}"
    )


def get_schedule_text(session: TrainingSession) -> str:
    lines = [
        f"📅 Расписание — Неделя {session.week_number}",
        f"🗓 Дни: {session.training_days}\n",
    ]
    for day_idx in range(3):
        status = "✅" if day_idx < session.completed_days else ("⏳" if day_idx == session.completed_days else "⭕")
        day_name = TRAINING_TYPES.get(day_idx, f"День {day_idx + 1}")
        lines.append(f"{status} {day_name}")
    return "\n".join(lines)


def get_day_exercises(
    session: TrainingSession,
    pain_type: Optional[str] = None,
    goal: Optional[str] = None,
):
    """Returns (exercises_list, formatted_text) or (None, error_text)."""
    goal_key = goal or "дефицит"
    week = session.week_number
    if not week_has_training_plan(goal_key, week):
        return None, TEXT_EXERCISES_WEEK_STUB.format(week=week)
    exercises = get_exercises_for_day(goal_key, week, session.current_day)
    if not exercises:
        return None, f"❌ Упражнения для недели {week}, день {session.current_day + 1} не заполнены."
    if pain_type and pain_type != "healthy":
        exercises = filter_exercises_by_pain(exercises, pain_type)
    text = format_exercise_list(exercises)
    return exercises, text


def complete_training(user_id: int, session: TrainingSession,
                      collected_weights: list[tuple[int, str, float]] | None = None,
                      pain_feedback: str | None = None) -> dict:
    """Mark training complete. Returns dict with status info."""
    today_str = date.today().isoformat()
    training_type = TRAINING_TYPES.get(session.current_day, "")

    training_log_repo.add_training_log(
        user_id=user_id,
        session_id=session.id,
        training_date=today_str,
        training_type=training_type,
        completed=True,
        pain_feedback=pain_feedback,
    )

    if collected_weights:
        exercise_weight_repo.save_exercise_weights(
            user_id=user_id,
            session_id=session.id,
            training_date=today_str,
            week_number=session.week_number,
            day_number=session.current_day + 1,
            weights=collected_weights,
        )

    new_completed = session.completed_days + 1
    new_day = (session.current_day + 1) % 3

    session_repo.update_session(
        session.id,
        completed_days=new_completed,
        current_day=new_day,
    )

    week_complete = new_completed >= 3
    needs_weighin = body_weight_repo.needs_weigh_in(user_id)

    logger.info("User %d completed training day %d, total=%d/3, week_complete=%s",
                user_id, session.current_day, new_completed, week_complete)

    return {
        "week_complete": week_complete,
        "needs_weighin": needs_weighin,
        "completed_days": new_completed,
        "week_number": session.week_number,
    }


def advance_to_next_week(session_id: int) -> None:
    session_repo.advance_week(session_id)


def go_to_previous_week(session: TrainingSession) -> bool:
    return session_repo.go_previous_week(session.id, session.week_number)


def handle_check01_yes(session_id: int) -> None:
    session_repo.update_session(session_id, check01_passed=True)


def handle_check01_no(session_id: int) -> None:
    session_repo.update_session(session_id, completed_days=0, current_day=0)


def handle_check02_pass(session_id: int) -> None:
    session_repo.update_session(session_id, check02_passed=True)


def needs_check01(session: TrainingSession) -> bool:
    return session.week_number == 2 and not session.check01_passed


def needs_check02(session: TrainingSession) -> bool:
    return session.week_number >= 2 and not session.check02_passed


def save_body_weight(user_id: int, weight: float) -> None:
    body_weight_repo.add_body_weight(user_id, weight, date.today().isoformat())
    logger.info("Saved body weight %.1f for user %d", weight, user_id)
