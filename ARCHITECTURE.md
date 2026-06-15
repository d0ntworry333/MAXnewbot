# Architecture: МАКС-бот «Твой тренер»

> **Date:** 2026-04-01
> **Platform:** MAX Messenger
> **Runtime:** Python 3.10+ / asyncio
> **Transport:** Long polling via `maxapi` library

---

## 1. Project Structure

```
max-fitness-bot/
├── app/
│   ├── __init__.py
│   └── main.py                        # Application entry point
├── config/
│   ├── __init__.py
│   └── settings.py                    # Environment-based configuration
├── core/
│   ├── __init__.py
│   ├── models.py                      # Domain dataclasses
│   ├── calculations.py                # BMR/BMI pure functions
│   └── validators.py                  # Input validation pure functions
├── content/
│   ├── __init__.py
│   ├── texts.py                       # Static Russian text content
│   └── exercises.py                   # Exercise catalog + weekly plans
├── repositories/
│   ├── __init__.py
│   ├── database.py                    # SQLite connection management
│   ├── user_repo.py                   # users table CRUD
│   ├── session_repo.py                # training_sessions table CRUD
│   ├── training_log_repo.py           # training_log table CRUD
│   ├── exercise_weight_repo.py        # exercise_weights table CRUD
│   └── body_weight_repo.py            # weight_progress table CRUD
├── services/
│   ├── __init__.py
│   ├── user_service.py                # User profile business logic
│   ├── training_service.py            # Training session orchestration
│   ├── exercise_service.py            # Exercise catalog operations
│   └── schedule_service.py            # Scheduled check business logic
├── transport/
│   └── max/
│       ├── __init__.py
│       ├── keyboards.py               # Inline keyboard builders
│       └── helpers.py                 # Message splitting, formatting
├── handlers/
│   ├── __init__.py
│   ├── start.py                       # /start, bot_started, top-level menu
│   ├── navigation.py                  # Menu navigation callbacks
│   ├── form.py                        # Questionnaire FSM handlers
│   ├── training.py                    # Training process handlers
│   ├── training_check.py              # Week completion + check flows
│   └── show.py                        # Data display handlers
├── scheduler/
│   ├── __init__.py
│   └── jobs.py                        # APScheduler cron job definitions
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
├── MIGRATION_PLAN.md
└── ARCHITECTURE.md
```

---

## 2. Module Boundaries

### Dependency Rules (strict)

```
handlers/  →  services/  →  repositories/
    ↓             ↓              ↓
transport/     core/         database.py
    ↓
  maxapi
```

- **`core/`** has ZERO imports from any other project module (except standard library).
- **`content/`** has ZERO imports from any other project module.
- **`repositories/`** imports only from `core/models.py` and `config/`.
- **`services/`** imports from `core/`, `content/`, and `repositories/`.
- **`handlers/`** imports from `services/`, `transport/`, and `config/`.
- **`transport/`** imports only from `maxapi` and `config/`.
- **`scheduler/`** imports from `services/` and `transport/`.
- **`app/main.py`** wires everything together.

### What each layer owns

| Layer | Responsibility | Does NOT do |
|-------|---------------|-------------|
| `core/` | Domain models, calculations, validation | I/O, messaging, DB access |
| `content/` | Static text, exercise data | Logic, I/O |
| `repositories/` | SQL queries, row↔model mapping | Business logic, messaging |
| `services/` | Business rules, orchestration | Messaging, HTTP, UI |
| `transport/` | Keyboard building, message formatting | Business logic, DB |
| `handlers/` | Event→service call→response mapping | Direct DB access, calculations |
| `scheduler/` | Job scheduling, job execution | Direct DB access (uses services) |

---

## 3. Transport Layer Design

### 3.1 MAX API Client

The `maxapi.Bot` class wraps all HTTP calls to `platform-api.max.ru`:
- `bot.send_message(user_id=..., text=..., attachments=[...])` — send messages
- `bot.edit_message(message_id=..., text=..., attachments=[...])` — edit messages
- `bot.get_updates()` — long polling
- `bot.get_me()` — bot identity

### 3.2 Keyboard System

All keyboards are inline keyboards (MAX has no reply keyboards).

Two button types used:
- **`CallbackButton(text, payload)`** — triggers `message_callback` event. Used for navigation, selections, confirmations.
- **`MessageButton(text)`** — sends button text as a message. Used where we want the user to "type" a value (alternative to free text).

Keyboard builders in `transport/max/keyboards.py` provide factory functions:
- `build_menu_keyboard()` → Main menu
- `build_main_keyboard()` → Core features menu
- `build_anketa_keyboard()` → Questionnaire submenu
- `build_training_keyboard()` → Active training menu
- `build_health_keyboard()` → Health status selection
- `build_activity_keyboard()` → Activity level selection
- `build_gender_keyboard()` → Gender selection
- `build_goal_keyboard()` → Goal selection
- `build_check01_keyboard()` → Yes/No for check01
- `build_scheduled_check_keyboard()` → Yes/No for scheduled evening check
- `build_technique_keyboard(exercises)` → Dynamic exercise list
- `build_training_days_keyboard()` → Day schedule selection
- `build_cancel_keyboard()` → Cancel button (for forms)

### 3.3 Message Helpers

- `send_long_message(bot, user_id, text, ...)` — splits text at 4000 chars
- Message formatting uses markdown where supported

---

## 4. Handler / Event Flow

### 4.1 Event Types Handled

| MAX Event | Handler Module | Trigger |
|-----------|---------------|---------|
| `bot_started` | `handlers/start.py` | User opens bot chat for first time |
| `message_created` + `Command('start')` | `handlers/start.py` | User sends `/start` |
| `message_created` + `Command('form')` | `handlers/form.py` | User sends `/form` |
| `message_created` + `Command('show_me')` | `handlers/show.py` | User sends `/show_me` |
| `message_created` + `Command('my_forms')` | `handlers/show.py` | User sends `/my_forms` |
| `message_created` + `Command('clear_last')` | `handlers/show.py` | User sends `/clear_last` |
| `message_created` + `Command('clear_all')` | `handlers/show.py` | User sends `/clear_all` |
| `message_created` + `Command('cancel')` | `handlers/form.py` | User sends `/cancel` |
| `message_created` + `Command('achievements')` | `handlers/start.py` | Stub command |
| `message_created` (text, in FSM state) | `handlers/form.py`, `handlers/training.py` | Free text input during forms or weight collection |
| `message_callback` | `handlers/navigation.py` | Any inline button press |

### 4.2 Callback Payload Convention

All callback payloads follow a namespaced pattern:

```
nav:{destination}          — Navigation between menus
action:{action_name}       — Performing an action
form:{field}:{value}       — Form field selection
training:{action}          — Training-specific actions
days:{schedule}            — Training day selection
health:{status}            — Health status selection
check:{response}           — Check01/check02 responses
technique:{exercise_id}    — Exercise technique view
sched:{response}           — Scheduled check responses
```

Examples:
- `nav:main` → Navigate to main menu
- `nav:training` → Navigate to training
- `action:complete_training` → Mark training complete
- `form:activity:high` → Select activity level "high"
- `days:mon_wed_fri` → Select Mon-Wed-Fri schedule
- `health:healthy` → Select "healthy" status
- `check:yes` → Check01 "yes" response
- `technique:3` → View technique for exercise ID 3
- `sched:yes` → Scheduled check "yes, I trained"

### 4.3 Request Flow

```
MAX Server
  │
  ├─── GET /updates (long poll) ───→ maxapi.Dispatcher
  │                                       │
  │                                  Parse update
  │                                       │
  │                              Match handler by:
  │                              - update_type
  │                              - filters (Command, F, state)
  │                                       │
  │                              Call handler function
  │                                       │
  │                              handler/  │
  │                              ┌─────────┴──────────┐
  │                              │  Extract user_id    │
  │                              │  Parse payload/text │
  │                              │  Call service layer │
  │                              └─────────┬──────────┘
  │                                        │
  │                              services/ │
  │                              ┌─────────┴──────────┐
  │                              │  Business logic     │
  │                              │  Call repositories  │
  │                              │  Return result      │
  │                              └─────────┬──────────┘
  │                                        │
  │                              handler formats response
  │                              builds keyboard
  │                                        │
  ├─── POST /messages ──────────────────── │
  │    (or POST /answers)                  │
  │                                        ▼
  │                                    User sees
  │                                    response
```

---

## 5. Core Business Layer

### 5.1 Domain Models (`core/models.py`)

```python
@dataclass
class UserProfile:
    id: int
    user_id: int
    username: str
    height: float
    weight: float
    activity_level: str
    gender: str
    age: int                # Renamed from years_experience
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
    completed: Optional[bool]   # None = pending
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
```

### 5.2 Calculations (`core/calculations.py`)

Pure functions, zero dependencies:
- `calculate_bmr(weight, height, age, gender, activity_level) → float`
- `calculate_bmi(weight, height) → float`
- Activity multiplier lookup

### 5.3 Validators (`core/validators.py`)

Pure functions:
- `parse_height(text) → float | None` — 50–250 cm
- `parse_weight(text) → float | None` — 20–300 kg
- `parse_age(text) → int | None` — 1–120
- `parse_exercise_weight(text) → float | None` — ≥0
- `validate_activity(text) → str | None`
- `normalize_gender(text) → str | None`

---

## 6. Repositories / Persistence Layer

### 6.1 Database Management (`repositories/database.py`)

- SQLite with WAL journal mode
- Schema creation via `CREATE TABLE IF NOT EXISTS` on startup
- Connection-per-operation pattern (simple, same as original)
- `Row` factory set to `sqlite3.Row` for named access (no more tuple indexing)
- DB path configurable via `DATABASE_PATH` env var

### 6.2 Schema (5 tables)

Same as original with one fix: `years_experience` → `age`.

Each repository module provides typed CRUD functions that return domain model instances.

---

## 7. Integrations Layer

### 7.1 APScheduler

- `AsyncIOScheduler` with configurable timezone
- 3 cron jobs: 23:00, 16:00, 23:59
- Jobs receive the `Bot` instance for sending messages
- Per-user exception handling (one user's error doesn't skip others)

### 7.2 No Other Integrations

Same as original: no Redis, no external APIs, no payment providers.

---

## 8. Config and Startup Flow

### 8.1 Configuration (`config/settings.py`)

All configuration from environment variables with sensible defaults:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MAX_BOT_TOKEN` | (required) | Bot API token |
| `DATABASE_PATH` | `data/bot.db` | SQLite database file path |
| `TIMEZONE` | `Europe/Moscow` | Timezone for scheduled jobs |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CHECK_HOUR_EVENING` | `23` | Evening check hour |
| `CHECK_MINUTE_EVENING` | `0` | Evening check minute |
| `REMINDER_HOUR` | `16` | Reminder hour |
| `REMINDER_MINUTE` | `0` | Reminder minute |
| `RESET_HOUR` | `23` | Reset hour |
| `RESET_MINUTE` | `59` | Reset minute |
| `MAX_MESSAGE_LENGTH` | `4000` | Message split threshold |

### 8.2 Startup Sequence (`app/main.py`)

```
1. Load .env file
2. Parse configuration
3. Configure logging
4. Initialize database (create tables)
5. Create Bot instance with token
6. Create Dispatcher instance
7. Register all handlers (routers)
8. Create and start APScheduler with cron jobs
9. Start polling loop (dp.start_polling(bot))
```

---

## 9. Polling Loop Design

Managed by `maxapi.Dispatcher.start_polling()`:

```
┌───────────────────────┐
│  Start Polling Loop   │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  GET /updates         │
│  marker=last_marker   │
│  timeout=30           │
└───────────┬───────────┘
            │
      ┌─────┴─────┐
      │ Response?  │
      └─────┬─────┘
            │
   ┌────────┼─────────┐
   │        │         │
Timeout   Error    Updates[]
   │        │         │
   │   Wait 5s    Save marker
   │        │     For each update:
   │        │       dispatch(event)
   │        │         │
   └────────┴─────────┘
            │
            ▼
        Continue loop
```

---

## 10. Error Handling and Logging Strategy

### 10.1 Error Handling Layers

| Layer | Strategy |
|-------|----------|
| **Polling loop** | Catches all exceptions per-iteration; logs and continues |
| **Handler dispatch** | Each handler wrapped in try/except; sends user-friendly error message on failure |
| **Scheduled jobs** | Per-user try/except; one user's error doesn't block others |
| **Service layer** | Raises domain exceptions; handlers catch and translate to user messages |
| **Repository layer** | Raises `sqlite3` exceptions; service layer handles or propagates |

### 10.2 Logging

- Python `logging` module with configurable level
- Structured log format: `%(asctime)s | %(name)s | %(levelname)s | %(message)s`
- Key log points:
  - Bot startup (token validation, bot info)
  - Handler invocation (user_id, action)
  - Service operations (business events)
  - Scheduled job execution (user count, errors)
  - Database operations (at DEBUG level)
  - Error stack traces (at ERROR level)

---

## 11. State Machine Design

### 11.1 States

```python
class BotState(str, Enum):
    MENU = "menu"
    MAIN = "main"
    ANKETA = "anketa"
    TRAINING = "training"
    TECHNIQUE = "technique"
    
    # Form states
    FORM_HEIGHT = "form_height"
    FORM_WEIGHT = "form_weight"
    FORM_ACTIVITY = "form_activity"
    FORM_GENDER = "form_gender"
    FORM_AGE = "form_age"
    FORM_GOAL = "form_goal"
    FORM_SHORT_WEIGHT = "form_short_weight"
    FORM_SHORT_ACTIVITY = "form_short_activity"
    
    # Collection states
    COLLECTING_EXERCISE_WEIGHT = "collecting_exercise_weight"
    COLLECTING_BODY_WEIGHT = "collecting_body_weight"
    COLLECTING_CALORIES = "collecting_calories"
```

### 11.2 State Transitions

Navigation states are changed via `context.set_state()` when callback buttons are pressed.
Form states advance sequentially as user provides valid input.
Collection states remain active until all items are collected.

### 11.3 Session Data

Transient data stored in a per-user dict (global `user_sessions: dict[int, dict]`):
- `weight_collection`: `{queue: [(id, name), ...], collected: [(name, weight), ...], index: int}`
- `pain_type`: `str`
- `check_step`: `str`
- `session_id`: `int`
- `technique_exercises`: `list[int]`
- `form_data`: `dict` (partial form being filled)
