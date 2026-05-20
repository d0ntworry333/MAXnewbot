from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class UserProfile:
    id: int
    user_id: int
    username: str
    height: float
    weight: float
    activity_level: str
    gender: str
    age: int
    bmr: float
    goal: str
    created_at: str
    updated_at: str


@dataclass
class TrainingSession:
    id: int
    user_id: int
    week_number: int
    training_days: str
    current_day: int
    completed_days: int
    session_active: bool
    check01_passed: bool
    check02_passed: bool
    created_at: str
    updated_at: str


@dataclass
class TrainingLog:
    id: int
    user_id: int
    session_id: int
    training_date: str
    training_type: str
    completed: Optional[bool]
    pain_feedback: Optional[str]
    created_at: str


@dataclass
class ExerciseWeight:
    id: int
    user_id: int
    session_id: int
    training_date: str
    exercise_id: int
    exercise_name: str
    weight: float
    week_number: int
    day_number: int
    created_at: str


@dataclass
class BodyWeight:
    id: int
    user_id: int
    weight: float
    recorded_at: str
    created_at: str


@dataclass
class Exercise:
    id: int
    name: str
    description: str
    muscle_groups: list[str]
    technique: str
