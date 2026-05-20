"""
Bot states for the FSM (finite state machine).
Uses maxapi's State/StatesGroup for compatibility with the dispatcher's state filtering.
"""

from maxapi.context import State, StatesGroup


class FormStates(StatesGroup):
    height = State()
    weight = State()
    activity = State()
    gender = State()
    age = State()
    goal = State()
    short_weight = State()
    short_activity = State()


class TrainingStates(StatesGroup):
    collecting_exercise_weight = State()
    collecting_body_weight = State()
    collecting_calories = State()
