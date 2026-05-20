# BOT_REVERSE_ENGINEERING_REPORT.md

> **Generated:** 2026-04-01  
> **Source repository:** `c:\Users\dontworry\Desktop\telegrammbot`  
> **Method:** Full static analysis of all 15 application Python files, config files, and project structure  
> **Certainty disclaimer:** All statements below are derived exclusively from the codebase. Inferences are explicitly marked as `[INFERENCE]`.

---

# 1. Project Overview

## What This Bot Does

This is a **personal fitness coaching Telegram bot** that manages a multi-week training program using bodyweight exercises and resistance bands. It operates as a 1-on-1 personal trainer assistant for each user.

## Core Business Functions

1. **User profiling** — Collects anthropometric data (height, weight, age, gender, activity level, fitness goal) via a structured questionnaire ("anketa")
2. **BMR calculation** — Computes Basal Metabolic Rate using the Mifflin-St Jeor equation, adjusted by an activity multiplier
3. **Diet recommendations** — Provides static nutritional guidance based on the user's goal (caloric deficit for weight loss, surplus for muscle gain)
4. **Training program delivery** — Serves a 3-day/week push-pull-legs training plan using resistance bands, organized by weeks
5. **Training tracking** — Tracks completed training days per week, exercise weights per session, and body weight over time
6. **Pain-adaptive filtering** — Excludes exercises targeting a painful body part (arms, back, legs) before each workout
7. **Weekly check-ins** — After week completion, runs check01 (all trainings done?) and check02 (average caloric intake) questionnaires
8. **Scheduled reminders** — Sends automated "did you train today?" messages at 23:00 and follow-up reminders at 16:00 the next day
9. **Exercise technique reference** — Displays technique descriptions for each exercise in the current day's program

## Target Users

Individual fitness clients who follow a structured resistance-band training program. The bot is designed for a **single coach serving multiple clients** model. There is no explicit admin panel; all users have equal access.

`[INFERENCE]` The bot appears to be built for a specific fitness coach's clients — the training plan content, diet texts, and exercise catalog are hardcoded for a particular methodology. There is no multi-tenancy or coach-vs-client role separation in the code.

## User Roles

- **User (client):** The only role present in the code. Every person interacting with the bot is treated as a client.
- **Admin:** No admin role exists. No admin commands, no admin user ID checks, no access control.

## Main Scenarios

1. New user → `/start` → fills full questionnaire → receives diet plan → starts training process → selects training days → performs weekly training cycle
2. Returning user → updates questionnaire (short form: weight + activity only) → continues training
3. Daily cycle: view exercises → report health → log exercise weights → mark training complete → (weekly body weigh-in if 7+ days since last)
4. Week completion → check01 (week 2 only) → check02 (week 2+) → advance to next week

---

# 2. Repository Structure

## Directory Layout

```
telegrammbot/
├── .env                          # Environment variables (TELEGRAM_BOT_TOKEN)
├── .gitignore                    # Standard Python + IDE + DB gitignore
├── main.py                       # Application entry point
├── anketa_launcher.py            # ConversationHandler registration for forms
├── exercises_template.py         # Exercise catalog + weekly training plan
├── error_solutions.py            # Message-splitting utility
├── get_bot_info.py               # Standalone utility to print bot info (not part of runtime)
├── requirements.txt              # Dependencies: python-telegram-bot, python-dotenv, apscheduler
├── start_bot.bat                 # Windows launch script
├── database/
│   └── DataBase.py               # All SQLite operations (init, CRUD, queries)
├── handlers/
│   ├── form.py                   # Questionnaire filling logic (full + short forms)
│   ├── navigation.py             # Menu navigation, exercise display, weight input handling
│   ├── show.py                   # User data display commands
│   ├── training.py               # Training session creation, inline callback handlers
│   └── training_check.py         # Scheduled checks, week completion, check01/check02 flows
├── Keyboards/
│   └── keyboards.py              # All ReplyKeyboardMarkup layouts
├── utils/
│   ├── calculations.py           # BMR computation, input parsing/validation
│   ├── states.py                 # Integer state constants for ConversationHandler + navigation
│   └── texts.py                  # Static long-form text content (diet plans, training program, recovery)
├── .venv/                        # Python 3.13 virtual environment (not committed)
└── .idea/                        # PyCharm project files (not committed)
```

## Entry Point

**`main.py`** is the sole entry point. The application starts via:

```
start_bot.bat → activates .venv → runs `python main.py`
```

`main.py` performs:
1. Loads `.env` via `python-dotenv`
2. Calls `init_db()` to create/verify SQLite tables
3. Builds a `telegram.ext.Application` with the bot token
4. Registers handlers in order: `/start` command → anketa handlers → training callback handlers → universal text message handler
5. Configures 3 APScheduler cron jobs
6. Starts the scheduler via `job_queue.run_once`
7. Enters polling mode via `application.run_polling()`

## How Modules Connect

- `main.py` imports from all other modules and wires everything together
- `anketa_launcher.py` creates a `ConversationHandler` and registers show/clear commands
- `handlers/` modules import from `database/DataBase.py`, `utils/`, `Keyboards/`, and `exercises_template.py`
- There is no dependency injection; all imports are direct
- `context.user_data` is used as the primary in-memory state store between messages

---

# 3. Architecture

## Overall Architecture

**Monolithic single-process application** with no service separation. All logic runs in one Python process.

## Layering

The architecture has **weak separation of concerns**:

| Layer | Location | Notes |
|-------|----------|-------|
| **Transport (Telegram)** | `main.py`, `handlers/*.py`, `Keyboards/keyboards.py` | Tightly coupled to `python-telegram-bot` types (`Update`, `ContextTypes`, `ReplyKeyboardMarkup`, etc.) |
| **Business Logic** | Spread across `handlers/*.py`, `utils/calculations.py`, `exercises_template.py` | Mixed with transport layer — business decisions happen inside Telegram handlers |
| **Data Access** | `database/DataBase.py` | Standalone module with pure SQLite operations; no ORM. Returns raw tuples (not dicts or models). |
| **Configuration** | `.env` (single var), hardcoded constants in multiple files | No config module; values are scattered |
| **Content/Templates** | `utils/texts.py`, `exercises_template.py` | Static Russian-language text blocks |

## Key Architectural Characteristics

1. **No business logic layer** — Domain rules (week completion, check logic, exercise filtering) live directly in Telegram handler functions
2. **Raw tuple data access** — DB functions return `sqlite3` tuples; consumers access fields by numeric index (e.g., `session[4]` for `current_day`). This is fragile and error-prone.
3. **State management via `context.user_data`** — Telegram's in-memory per-user dict is used for all transient state (current menu, weight collection queue, check step, etc.). This state is lost on bot restart.
4. **No middleware** — No logging middleware, auth middleware, or error handling middleware
5. **No tests** — No test files exist in the repository
6. **No Docker** — Deployment is Windows-only via batch file
7. **Background jobs** — APScheduler runs 3 cron jobs in the same process for scheduled notifications

## Honest Assessment

The architecture is a **prototype-level implementation**. Business logic is not separable from the Telegram transport layer without significant refactoring. The data access layer is the cleanest separation point — `DataBase.py` has no Telegram imports and could be reused directly.

---

# 4. Functional Map of the Bot

## 4.1 Questionnaire System ("Anketa")

### 4.1.1 Full Questionnaire (First-Time Users)

- **Trigger:** `/form` command when user has no existing forms (`has_user_forms()` returns `False`)
- **Who:** Any user without prior forms
- **Flow:** Height → Weight → Activity Level → Gender → Age → Goal
- **Inputs & Validation:**
  - Height: float, 50–250 cm (`parse_height` in `utils/calculations.py`)
  - Weight: float, 20–300 kg (`parse_weight`)
  - Activity: one of "Очень высокая", "Высокая", "Средняя", "Низкая" (`validate_activity`)
  - Gender: "Мужской" or "Женский" (`normalize_gender`)
  - Age: integer, 1–120 (`parse_age`)
  - Goal: "Снизить вес (дефицит)" → stored as "дефицит", or "Набрать вес (профицит)" → stored as "профицит"
- **Internal Processing:**
  - Computes BMR via Mifflin-St Jeor: `((10 * weight) + (6.25 * height) - (5 * age) + 5) * activity` for men, `-161` instead of `+5` for women
  - Activity multipliers: Очень высокая=1.725, Высокая=1.55, Средняя=1.375, Низкая=1.2
- **Data Written:** New row in `users` table (always INSERT, never UPDATE)
- **Output:**
  - Confirmation message with all entered data
  - Diet plan text (`text01` for deficit, `text02` for surplus)
  - Returns to main menu
- **Edge Cases:**
  - Invalid input at any step → re-prompts for same field
  - `/cancel` at any step → aborts, returns to main menu
- **Files:** `handlers/form.py:21-173`, `utils/calculations.py`, `anketa_launcher.py`

### 4.1.2 Short Questionnaire (Returning Users)

- **Trigger:** `/form` command when user has existing forms
- **Flow:** Weight → Activity Level (only 2 steps)
- **Internal Processing:**
  - Copies height, gender, age, goal from the user's **first** form (`get_user_first_form`)
  - Recalculates BMR with new weight + activity
- **Data Written:** New row in `users` table with updated weight/activity, inherited fields from first form
- **Files:** `handlers/form.py:176-252`

### 4.1.3 View Own Data

- **`/show_me`:** Shows latest form (height, weight, BMI, activity, gender, age). Uses `get_user_by_id` (most recent form). File: `handlers/show.py:47-73`
- **`/my_forms`:** Shows all forms with progress tracking. First form shown in full; subsequent forms show only weight + activity changes compared to previous form. File: `handlers/show.py:76-157`
- **`/show_all`:** Identical logic to `/my_forms` (code is duplicated). File: `handlers/show.py:160-241`

### 4.1.4 Delete Forms

- **`/clear_last`:** Deletes the most recent form. File: `handlers/show.py:260-266`
- **`/clear_all`:** Deletes all forms for the user. File: `handlers/show.py:269-275`

## 4.2 Training Process

### 4.2.1 Training Day Selection

- **Trigger:** "training process" button when no active session exists
- **Who:** Any user with no active training session
- **UI:** Inline keyboard with 3 options:
  - "Пн-Ср-Пт" (Mon-Wed-Fri) → callback `days_mon_wed_fri`
  - "Вт-Чт-Сб" (Tue-Thu-Sat) → callback `days_tue_thu_sat`
  - "Ср-Пт-Вс" (Wed-Fri-Sun) → callback `days_wed_fri_sun`
- **Data Written:** Creates `training_sessions` row with `week_number=1`, `current_day=0`, `completed_days=0`
- **Output:** Shows training plan text (`text04`) + "Начать тренировки" inline button
- **Files:** `handlers/navigation.py:328-343`, `handlers/training.py:9-39`

### 4.2.2 Training Status Display

- **Trigger:** "training process" button when active session exists, or "📊 Статус" button
- **Shows:** Week number, training days, completed days out of 3, current day number
- **Files:** `handlers/navigation.py:346-377`

### 4.2.3 View Today's Exercises

- **Trigger:** "📋 Упражнения дня" button
- **Flow:**
  1. Asks health status: "Здоров", "Болит рука", "Болит спина", "Болят ноги"
  2. Filters exercises based on pain (excludes exercises targeting painful muscle groups)
  3. Displays filtered exercise list with names and descriptions
  4. Starts weight collection: asks user to enter weight (kg) for each exercise sequentially
- **Pain Filtering Logic** (in `exercises_template.py:164-203`):
  - "Болит рука" → excludes exercises with muscle_group "руки"
  - "Болит спина" → excludes exercises with muscle_group "спина"
  - "Болят ноги" → excludes exercises with muscle_group "ноги"
  - "Здоров" → no filtering
- **Weight Collection:**
  - Iterates through each exercise in queue
  - Accepts float input (comma or dot as decimal separator)
  - Validates: must be numeric, must be ≥ 0
  - Stores collected weights in `context.user_data['weight_collection']`
  - After all weights collected, shows summary and training keyboard
- **Files:** `handlers/navigation.py:411-607`

### 4.2.4 Mark Training Complete

- **Trigger:** "✅ Я выполнил тренировку" button
- **Internal Processing:**
  1. Adds `training_log` entry (completed=True)
  2. Saves collected exercise weights to `exercise_weights` table (if any)
  3. Increments `completed_days`, advances `current_day = (current_day + 1) % 3`
  4. If `completed_days >= 3` → triggers week completion flow
  5. Checks if body weigh-in needed (≥7 days since last `weight_progress` entry)
- **Files:** `handlers/navigation.py:665-738`

### 4.2.5 Training Schedule View

- **Trigger:** "📅 Расписание" button
- **Shows:** Week number, training days, 3 training types with completion status (✅/⏳/⭕)
- **Hardcoded training types:**
  - День 1: Грудь, Плечи, Трицепс (PUSH)
  - День 2: Спина, Бицепс (PULL)
  - День 3: Ноги и Кор (LEGS)
- **Files:** `handlers/navigation.py:636-662`

### 4.2.6 Exercise Technique Menu

- **Trigger:** "🧠 Техника" button
- **Shows:** Keyboard with all exercises for current day (filtered by pain if previously set)
- **On exercise selection:** Shows technique text from `exercises_template.py`
- **Files:** `handlers/navigation.py:82-288`

### 4.2.7 Week Navigation

- **"⬅️ Предыдущая неделя":** Decreases week number, resets counters. Blocked at week 1. File: `handlers/navigation.py:802-835`
- **"➡️ Следующая неделя":** Advances to next week, resets counters. File: `handlers/navigation.py:838-859`
- **"Следующая неделя" (from anketa menu):** Advances week AND triggers short form for parameter update. File: `handlers/navigation.py:380-408`

## 4.3 Week Completion and Check System

### 4.3.1 Week Completion Logic

- **Trigger:** When `completed_days >= 3` after marking a training complete
- **Branching by week number** (in `handlers/training_check.py:315-360`):
  - **Week 1:** Simply shows "week complete" message
  - **Week 2:** Requires both check01 AND check02
  - **Week 3+:** Requires only check02

### 4.3.2 Check01 (Training Compliance)

- **Trigger:** After week 2 completion, if `check01_passed = False`
- **Question:** "Выполнили ли вы все тренировки?"
- **Responses:**
  - "✅ Да" → marks check01_passed, proceeds to check02
  - "❌ Нет" → resets `completed_days=0, current_day=0` (user must redo the week)
- **Files:** `handlers/training_check.py:363-455`

### 4.3.3 Check02 (Caloric Intake)

- **Trigger:** After check01 passes (week 2) or directly after week completion (week 3+)
- **Question:** "Введите вашу среднюю калорийность за неделю"
- **Response handling:** `[IMPORTANT]` Currently accepts ANY text input (marked as "ВРЕМЕННАЯ ЗАПЛАТКА" / temporary patch in the code). No validation.
- **Effect:** Marks `check02_passed`, shows "week complete" message
- **Files:** `handlers/training_check.py:458-499`

## 4.4 Scheduled Background Jobs

### 4.4.1 Evening Training Check (23:00)

- **Function:** `check_training_completion` in `handlers/training_check.py:57-100`
- **Logic:** For each active session where today is a training day and no pending log exists → creates a `training_log` entry with `completed=NULL` and sends "Did you train today?" message with Yes/No keyboard
- **Uses:** `DAYS_MAPPING` to determine if today is a scheduled training day for the user's chosen schedule

### 4.4.2 Next-Day Reminder (16:00)

- **Function:** `check_training_completion_next_day` in `handlers/training_check.py:103-135`
- **Logic:** For each active session where yesterday was a training day and a pending (unanswered) log exists → sends reminder message

### 4.4.3 Unanswered Session Reset (23:59)

- **Function:** `reset_unanswered_sessions` in `handlers/training_check.py:502-523`
- **Logic:** For each active session with a pending training log from 2 days ago → deactivates the session (`session_active=False`) and notifies the user

## 4.5 Body Weight Tracking

- **Trigger:** After marking training complete, if ≥7 days since last body weight entry (or no entry exists)
- **Input:** Float, 20–300 kg
- **Data Written:** New row in `weight_progress` table
- **Files:** `handlers/navigation.py:610-633`, `database/DataBase.py:440-466`

## 4.6 Diet and Recovery Info

- **"goal & diet" button:** Shows user's goal + corresponding diet text (`text01` for deficit, `text02` for surplus). File: `handlers/navigation.py:50-79`
- **"recovery recommendations" button:** Shows static recovery text (`text03`). File: `handlers/navigation.py:235-242`

## 4.7 Utility Features

- **`/achievements` command:** Stub — returns "in development" message. File: `handlers/navigation.py:290-296`
- **`get_bot_info.py`:** Standalone script to print bot metadata. Not part of runtime.
- **`error_solutions.py`:** `send_long_message()` splits messages >4096 chars. Used in `handlers/show.py`.

---

# 5. Full User Journey Map

## 5.1 First Contact Flow

```
User sends /start
  → show_menu() displays main menu keyboard: ["main", "/achievements"]
  → User taps "main"
    → show_main() displays: ["questionnaire", "goal & diet"], ["recovery recommendations", "training process"], ["main menu"]
    → User taps "questionnaire"
      → show_anketa_menu() displays: ["/form", "return"], ["/clear_last", "/show_all"], ["/cancel", "/clear_all"]
      → User taps /form (first time, no forms exist)
        → Full questionnaire: height → weight → activity → gender → age → goal
        → BMR calculated and saved
        → Diet plan displayed
        → Returns to main menu (MAIN_STATE)
```

## 5.2 Training Onboarding Flow

```
User taps "training process" (no active session)
  → start_training_process() shows inline keyboard: Пн-Ср-Пт / Вт-Чт-Сб / Ср-Пт-Вс
  → User taps a day option (e.g., "Пн-Ср-Пт")
    → handle_training_days_selection() creates training_sessions row (week 1)
    → Shows training plan text + "Начать тренировки" inline button
    → User taps "Начать тренировки"
      → show_training_status() shows status + training keyboard
```

## 5.3 Daily Training Flow

```
User taps "📋 Упражнения дня"
  → Health check: Здоров / Болит рука / Болит спина / Болят ноги
  → User selects health status
    → Exercises filtered by pain type
    → Exercise list displayed
    → Weight collection starts:
      → "Упражнение 1/N: [name]. Введите вес (кг):"
      → User enters weight → next exercise → ... → last exercise
      → "✅ Все веса записаны! [summary]"
      → Training keyboard shown

User taps "✅ Я выполнил тренировку"
  → Training logged, weights saved to DB
  → completed_days incremented
  → If completed_days < 3: "Отлично! Тренировка засчитана."
  → If completed_days >= 3: week completion flow (see 5.4)
  → If ≥7 days since last weigh-in: prompts for body weight
```

## 5.4 Week Completion Flow

```
completed_days reaches 3
  → handle_week_completion():
    Week 1:
      → "Неделя выполнена! Для перехода используйте 'Следующая неделя'"
    
    Week 2:
      → check01: "Выполнили ли вы все тренировки?"
        → Да → check01_passed = True → check02
        → Нет → completed_days=0, current_day=0 (redo week)
      → check02: "Введите среднюю калорийность"
        → Any input accepted → check02_passed = True → "Неделя завершена"
    
    Week 3+:
      → check02 only (same as above)
      → "Неделя завершена"
```

## 5.5 Week Transition Flow

```
User taps "➡️ Следующая неделя" (from training keyboard)
  → advance_to_next_week(): week_number++, completed_days=0, current_day=0, check02_passed=0

OR

User taps "Следующая неделя" (from anketa menu)
  → advance_to_next_week() + triggers short form (weight + activity update)
```

## 5.6 Scheduled Check Flow (Evening)

```
23:00 cron job fires
  → For each active session where today is a training day:
    → If no pending log for today:
      → Creates training_log with completed=NULL
      → Sends "Выполнили ли вы тренировку сегодня?" + Yes/No keyboard
      
User responds:
  → "✅ Да, выполнил" → completed=True, counters updated
  → "❌ Нет, не выполнил" → training postponed message

16:00 next day:
  → If yesterday's training still has completed=NULL → sends reminder

23:59:
  → If 2-day-old training has completed=NULL → session deactivated
```

## 5.7 Error / Fallback Branches

- **Unrecognized text:** Falls through to `handle_navigation` which returns current state (no error message, bot remains silent)
- **No active session:** Returns "❌ У вас нет активной тренировочной сессии" for training-related actions
- **No forms:** Returns "❌ У вас еще нет заполненных анкет" for profile-related actions
- **Invalid numeric input:** Re-prompts with validation message
- **Missing exercises for week:** Returns "❌ Упражнения для недели N, день M не заполнены"

---

# 6. Commands, Buttons, Callbacks, States

## 6.1 Bot Commands

| Command | Handler | Description | File |
|---------|---------|-------------|------|
| `/start` | `start()` | Shows main menu | `main.py:40-42` |
| `/form` | `start_form()` | Starts full or short questionnaire | `handlers/form.py:21-37` |
| `/show_me` | `show_me()` | Shows latest user profile | `handlers/show.py:47-73` |
| `/my_forms` | `show_my_forms()` | Shows all user forms | `handlers/show.py:76-157` |
| `/show_all` | `show_all()` | Same as `/my_forms` (duplicate) | `handlers/show.py:160-241` |
| `/clear_last` | `clear_last()` | Deletes latest form | `handlers/show.py:260-266` |
| `/clear_all` | `clear_all()` | Deletes all forms | `handlers/show.py:269-275` |
| `/cancel` | `cancel()` | Cancels questionnaire | `handlers/form.py:255-263` |
| `/achievements` | inline in navigation | Stub: "in development" | `handlers/navigation.py:290-296` |

## 6.2 Reply Keyboard Layouts

### Menu Keyboard (`MENU_STATE`)
```
[ "main"          ] [ "/achievements" ]
```

### Main Keyboard (`MAIN_STATE`)
```
[ "questionnaire"            ] [ "goal & diet"                ]
[ "recovery recommendations" ] [ "training process"           ]
[ "main menu"                ]
```

### Anketa Keyboard (`ANKETA_STATE`)
```
[ "/form"       ] [ "return"     ]
[ "/clear_last" ] [ "/show_all"  ]
[ "/cancel"     ] [ "/clear_all" ]
```

### Training Keyboard (active training)
```
[ "📋 Упражнения дня"          ] [ "📅 Расписание"      ]
[ "✅ Я выполнил тренировку"    ] [ "📊 Статус"          ]
[ "🧠 Техника"                 ] [ "📋 Основное меню"    ]
[ "⬅️ Предыдущая неделя"       ] [ "➡️ Следующая неделя" ]
```

### Health Check Keyboard (before exercises)
```
[ "Здоров"       ] [ "Болит рука"  ]
[ "Болит спина"  ] [ "Болят ноги"  ]
```

### Activity Level Keyboard (questionnaire)
```
[ "Очень высокая" ] [ "Высокая" ]
[ "Средняя"       ] [ "Низкая"  ]
[ "/cancel"        ]
```

### Gender Keyboard (questionnaire)
```
[ "Мужской" ] [ "Женский" ]
[ "/cancel" ]
```

### Goal Keyboard (questionnaire)
```
[ "Снизить вес (дефицит)" ] [ "Набрать вес (профицит)" ]
[ "/cancel"                ]
```

### Training Completion Keyboard (scheduled check)
```
[ "✅ Да, выполнил" ] [ "❌ Нет, не выполнил" ]
```

### Check01 Keyboard
```
[ "✅ Да" ] [ "❌ Нет" ]
```

### Technique Keyboard (dynamic — per current day's exercises)
```
[ "📋 [Exercise 1 name]" ]
[ "📋 [Exercise 2 name]" ]
[ ...                     ]
[ "return"                ]
```

## 6.3 Inline Keyboards (Callbacks)

| Callback Data | Handler | Description | File |
|---------------|---------|-------------|------|
| `days_mon_wed_fri` | `handle_training_days_selection` | Select Mon-Wed-Fri | `handlers/training.py:9-39` |
| `days_tue_thu_sat` | `handle_training_days_selection` | Select Tue-Thu-Sat | `handlers/training.py:9-39` |
| `days_wed_fri_sun` | `handle_training_days_selection` | Select Wed-Fri-Sun | `handlers/training.py:9-39` |
| `start_training` | `start_training` | Begin training | `handlers/training.py:42-56` |
| `skip_day` | `skip_day` | Skip training day (test) | `handlers/training.py:59-97` |
| `show_status` | `show_status` | Show status | `handlers/training.py:100-113` |

## 6.4 FSM / Conversation States

### ConversationHandler States (questionnaire)

Defined in `utils/states.py`:

| Constant | Value | Meaning | Expected Input |
|----------|-------|---------|----------------|
| `HEIGHT` | 0 | Waiting for height | Float 50–250 |
| `WEIGHT` | 1 | Waiting for weight | Float 20–300 |
| `ACTIVITY_LEVEL` | 2 | Waiting for activity | Button press |
| `GENDER` | 3 | Waiting for gender | Button press |
| `YEARS_EXPERIENCE` | 4 | Waiting for age | Integer 1–120 |
| `GOAL` | 5 | Waiting for goal | Button press |
| `SHORT_WEIGHT` | 6 | Short form: weight | Float 20–300 |
| `SHORT_ACTIVITY_LEVEL` | 7 | Short form: activity | Button press |

### Navigation States (manual, via `context.user_data['current_state']`)

| Constant | Value | Meaning |
|----------|-------|---------|
| `MENU_STATE` | 8 | Main menu level |
| `MAIN_STATE` | 9 | Core features menu |
| `ANKETA_STATE` | 10 | Questionnaire sub-menu |
| `TRAINING_TECHNIQUE_STATE` | 11 | Exercise technique browser |

### Implicit States (via `context.user_data` flags)

| Flag | Type | Meaning |
|------|------|---------|
| `check_step` | `'check01'` or `'check02'` | Active check process |
| `waiting_for_health_check` | bool | Awaiting health status response |
| `waiting_for_exercise_weight` | bool | Awaiting exercise weight input |
| `waiting_for_body_weight` | bool | Awaiting body weight input |
| `weight_collection` | dict | Active weight collection queue |
| `pain_type_for_exercises` | str | Last selected pain type |
| `technique_exercise_ids` | list | Exercise IDs for technique menu |
| `session_id` | int | Session ID for check context |

## 6.5 State Transitions

```
/start → MENU_STATE
  "main" → MAIN_STATE
    "questionnaire" → ANKETA_STATE
      "/form" → ConversationHandler (HEIGHT or SHORT_WEIGHT)
        ... → ConversationHandler.END → MAIN_STATE
      "return" → MAIN_STATE
    "goal & diet" → stays MAIN_STATE (shows text)
    "recovery recommendations" → stays MAIN_STATE (shows text)
    "training process" → stays MAIN_STATE (shows status or starts selection)
    "🧠 Техника" → TRAINING_TECHNIQUE_STATE
      exercise button → stays TRAINING_TECHNIQUE_STATE (shows technique)
      "return" → MAIN_STATE
    "main menu" → MENU_STATE
```

---

# 7. Data Model and Persistence

## Database Engine

**SQLite** — file-based, stored as `users.db` in the project root directory. No ORM; all queries are raw SQL via `sqlite3` module. Each function opens and closes its own connection (no connection pooling).

## Tables

### 7.1 `users`

Stores user profile questionnaires. **One user can have multiple rows** (append-only design for tracking progress).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| `id` | INTEGER PK AUTOINCREMENT | Internal record ID |
| `user_id` | INTEGER | Telegram user ID (not unique — multiple rows per user) |
| `username` | TEXT | Telegram username |
| `height` | REAL | Height in cm |
| `weight` | REAL | Weight in kg |
| `activity_level` | TEXT | "Очень высокая", "Высокая", "Средняя", "Низкая" |
| `gender` | TEXT | "Мужской" or "Женский" |
| `years_experience` | INTEGER | Age in years (misleading column name — actually stores age, not experience) |
| `brm` | REAL | Calculated BMR value |
| `goal` | TEXT | "дефицит" or "профицит" |
| `created_at` | TIMESTAMP | Row creation time (DEFAULT CURRENT_TIMESTAMP) |
| `updated_at` | TIMESTAMP | Never actually updated by application code (DEFAULT CURRENT_TIMESTAMP) |

**Index:** `idx_user_id` on `user_id`

**Critical note:** `[INFERENCE]` The `years_experience` column name suggests training experience, but the code always uses it to store the user's age. This is a naming inconsistency.

### 7.2 `training_sessions`

Stores active and historical training sessions. One user has at most one active session.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| `id` | INTEGER PK AUTOINCREMENT | Session ID |
| `user_id` | INTEGER | Telegram user ID (FK to users.user_id) |
| `week_number` | INTEGER | Current week number (starts at 1, incremented) |
| `training_days` | TEXT | "Пн-Ср-Пт", "Вт-Чт-Сб", or "Ср-Пт-Вс" |
| `current_day` | INTEGER | Current training day index (0, 1, or 2) |
| `completed_days` | INTEGER | Number of completed trainings this week (0–3) |
| `session_active` | BOOLEAN | 1=active, 0=deactivated |
| `check01_passed` | BOOLEAN | Check01 completion flag |
| `check02_passed` | BOOLEAN | Check02 completion flag |
| `created_at` | TIMESTAMP | Session creation time |
| `updated_at` | TIMESTAMP | Last update time |

**Index:** `idx_training_user_id` on `user_id`

**Key behavior:** `advance_to_next_week()` resets `completed_days=0, current_day=0, check02_passed=0` but does NOT reset `check01_passed`. `[INFERENCE]` This means check01 is a one-time gate at week 2.

### 7.3 `training_log`

Per-day training completion records.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| `id` | INTEGER PK AUTOINCREMENT | Log entry ID |
| `user_id` | INTEGER | Telegram user ID |
| `session_id` | INTEGER | FK to training_sessions.id |
| `training_date` | DATE | Date of training (YYYY-MM-DD) |
| `training_type` | TEXT | e.g., "День 1: Грудь, Плечи, Трицепс" |
| `completed` | BOOLEAN | True/False/NULL (NULL = pending check) |
| `pain_feedback` | TEXT | Health status feedback (nullable) |
| `created_at` | TIMESTAMP | Entry creation time |

**Index:** `idx_training_log_user_id` on `user_id`

**Key behavior:** `completed=NULL` is used as a sentinel for "pending check" by `get_pending_training_check()`.

### 7.4 `exercise_weights`

Per-exercise weight records for each training day.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| `id` | INTEGER PK AUTOINCREMENT | Record ID |
| `user_id` | INTEGER | Telegram user ID |
| `session_id` | INTEGER | FK to training_sessions.id |
| `training_date` | DATE | Date of training |
| `exercise_id` | INTEGER | Exercise ID from exercises_template |
| `exercise_name` | TEXT | Exercise name (denormalized) |
| `weight` | REAL | Weight used in first set (kg) |
| `week_number` | INTEGER | Week number (denormalized) |
| `day_number` | INTEGER | Day number 1–3 (denormalized) |
| `created_at` | TIMESTAMP | Entry creation time |

**Index:** `idx_exercise_weights_user` on `user_id`

### 7.5 `weight_progress`

Body weight tracking over time.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| `id` | INTEGER PK AUTOINCREMENT | Record ID |
| `user_id` | INTEGER | Telegram user ID |
| `weight` | REAL | Body weight in kg |
| `recorded_at` | DATE | Date of weigh-in |
| `created_at` | TIMESTAMP | Entry creation time |

**Index:** `idx_weight_progress_user` on `user_id`

## Data Access Patterns

- All DB functions return **raw tuples** accessed by positional index
- No ORM, no named tuples, no dataclasses
- Each function manages its own `sqlite3.connect()` / `conn.close()` lifecycle
- No transaction management beyond auto-commit
- `training_check.py:200-209` contains **inline raw SQL** bypassing the `DataBase.py` module (direct `sqlite3.connect('users.db')` inside a handler)

## Schema Notes

- No migrations system; schema is created via `CREATE TABLE IF NOT EXISTS` on every startup
- No foreign key enforcement (`PRAGMA foreign_keys` is not enabled)
- `users` table uses append-only pattern (each form submission = new row)
- `training_sessions` uses single-active-session pattern (only one `session_active=1` per user expected)

---

# 8. External Integrations

## 8.1 Telegram Bot API

- **Library:** `python-telegram-bot` v20+ (async)
- **Mode:** Long polling (`application.run_polling()`)
- **API Features Used:**
  - `ReplyKeyboardMarkup` (reply keyboards)
  - `InlineKeyboardMarkup` / `InlineKeyboardButton` (inline keyboards)
  - `CommandHandler`, `MessageHandler`, `CallbackQueryHandler`
  - `ConversationHandler` (multi-step forms)
  - `context.user_data` (per-user in-memory state)
  - `application.bot.send_message()` (proactive messages from scheduled jobs)
  - `callback_query.edit_message_text()` (editing inline keyboard messages)
  - `callback_query.answer()` (answering callback queries)

## 8.2 APScheduler

- **Library:** `apscheduler` v3.10+
- **Scheduler type:** `AsyncIOScheduler`
- **Jobs:**
  - `check_training_23` — CronTrigger(hour=23, minute=0)
  - `check_training_16` — CronTrigger(hour=16, minute=0)
  - `reset_unanswered` — CronTrigger(hour=23, minute=59)
- **Integration:** Scheduler is started via `application.job_queue.run_once()` 1 second after bot starts

## 8.3 No Other External Integrations

- No payment providers
- No email
- No Redis
- No message queues
- No analytics
- No external APIs
- No webhooks (outgoing)
- No cloud storage
- No admin panel

---

# 9. Configuration and Infrastructure

## 9.1 Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot API token from BotFather | Yes |

This is the **only** environment variable. There are no other configuration mechanisms.

## 9.2 Secrets

- `TELEGRAM_BOT_TOKEN` — the only secret. Stored in `.env` file (git-ignored).

## 9.3 Dependencies

From `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `python-telegram-bot` | ≥20.0 | Telegram Bot API wrapper |
| `python-dotenv` | ≥1.0.0 | .env file loading |
| `apscheduler` | ≥3.10.0 | Background job scheduling |

**Runtime:** Python 3.13 (per `.venv/pyvenv.cfg`)

## 9.4 Deployment

- **Platform:** Windows (batch file launcher)
- **No Docker** — no Dockerfile or docker-compose
- **No CI/CD** — no pipeline configuration
- **Launch:** `start_bot.bat` activates venv and runs `python main.py`
- **Process management:** None (bot runs in foreground console window)
- **Database location:** `users.db` in the working directory (typically project root)

## 9.5 Infrastructure Requirements

- Python 3.13+ installation
- Network access to `api.telegram.org`
- Write access to working directory (for `users.db`)
- No ports to expose (polling mode, not webhook)

## 9.6 Scheduled Jobs

| Job ID | Schedule | Function | Purpose |
|--------|----------|----------|---------|
| `check_training_23` | Daily 23:00 | `check_training_completion` | Ask users if they trained today |
| `check_training_16` | Daily 16:00 | `check_training_completion_next_day` | Remind users about yesterday's unanswered check |
| `reset_unanswered` | Daily 23:59 | `reset_unanswered_sessions` | Deactivate sessions with 2-day-old unanswered checks |

**Timezone:** `[INFERENCE]` No timezone is configured for APScheduler. It uses the system's local timezone by default. This could cause issues if deployed on a server in a different timezone than the users.

---

# 10. Telegram-Specific Dependencies

## 10.1 Update/Message Model

**What:** All handlers receive `telegram.Update` objects and `telegram.ext.ContextTypes.DEFAULT_TYPE` context. Message text is accessed via `update.message.text`, user ID via `update.message.from_user.id`.

**Why Telegram-specific:** MAX messenger will have a completely different event model, message structure, and user identification scheme.

**Redesign needed:** Abstract the incoming event into a messenger-agnostic `IncomingMessage` type with fields like `user_id`, `text`, `is_callback`, etc.

## 10.2 Reply Keyboard Markup

**What:** `ReplyKeyboardMarkup` with `KeyboardButton` is used extensively for persistent bottom-of-chat keyboards. Every state transition sends a new keyboard layout.

**Why Telegram-specific:** This is a Telegram-native UI element. MAX may use different keyboard/button mechanisms.

**Redesign needed:** Abstract keyboard creation into a platform-agnostic interface that each messenger adapter implements.

## 10.3 Inline Keyboard / Callback Queries

**What:** `InlineKeyboardMarkup` with `InlineKeyboardButton` used for training day selection. Callbacks processed via `CallbackQueryHandler` with pattern matching.

**Why Telegram-specific:** Inline keyboards attached to specific messages, callback query flow, `query.answer()`, `query.edit_message_text()` are all Telegram-specific.

**Redesign needed:** Design a generic interactive message/button system for MAX.

## 10.4 ConversationHandler (FSM)

**What:** `telegram.ext.ConversationHandler` manages the multi-step questionnaire flow with defined states, entry points, and fallbacks.

**Why Telegram-specific:** This is a `python-telegram-bot`-specific class that manages state transitions based on Telegram handler dispatch.

**Redesign needed:** Implement a generic FSM (finite state machine) that works with any messenger's event loop.

## 10.5 `context.user_data`

**What:** `python-telegram-bot`'s per-user in-memory dictionary. Used for ALL transient state: current menu state, weight collection queues, check step, pain type, etc.

**Why Telegram-specific:** This is part of `python-telegram-bot`'s context system. It's in-memory and lost on restart.

**Redesign needed:** Implement a proper user session store (could be in-memory dict, Redis, or DB-backed) that persists across restarts if needed.

## 10.6 Bot Proactive Messaging

**What:** `application.bot.send_message(chat_id=user_id, ...)` used by scheduled jobs to send messages to users without them initiating.

**Why Telegram-specific:** Uses Telegram's `chat_id` (which equals `user_id` in private chats) and Telegram's Bot API send method.

**Redesign needed:** MAX will have its own proactive messaging API. The concept (send message to user by ID) is universal, but the implementation is platform-specific.

## 10.7 Message Editing

**What:** `callback_query.edit_message_text()` used to update inline keyboard messages after selection.

**Why Telegram-specific:** Message editing via callback query response is Telegram-specific behavior.

**Redesign needed:** Determine if MAX supports message editing; if not, use delete+resend or alternative UX.

## 10.8 User Identification

**What:** `update.message.from_user.id` (Telegram numeric user ID) used as the primary user identifier throughout the database.

**Why Telegram-specific:** MAX will have its own user ID format/type.

**Redesign needed:** Abstract user identification. The `user_id` field in all DB tables stores Telegram IDs. For MAX, the same field can store MAX user IDs, but the type may differ (string vs integer).

## 10.9 Message Length Limit

**What:** `error_solutions.py` splits messages at 4096 characters — Telegram's message length limit.

**Why Telegram-specific:** MAX may have a different limit.

**Redesign needed:** Make the chunk size configurable.

## 10.10 Polling Mode

**What:** `application.run_polling()` — long-polling connection to Telegram's servers.

**Why Telegram-specific:** MAX may require webhooks or a different connection method.

**Redesign needed:** Implement MAX's required connection/event delivery mechanism.

---

# 11. Reusable Business Logic for MAX

## What Can Be Ported Conceptually

### 11.1 Domain Entities and Rules

- **User profile model:** Height, weight, activity level, gender, age, goal, BMR
- **Training session model:** Week number, training days schedule, current day, completed days, check flags
- **Training log model:** Per-day completion records with pain feedback
- **Exercise weight tracking model:** Per-exercise weight records
- **Body weight progression model:** Weekly weigh-in records

### 11.2 Business Calculations

- **BMR calculation** (`utils/calculations.py:1-23`): Mifflin-St Jeor equation — pure math, no messenger dependency
- **BMI calculation** (`utils/calculations.py:26-30`): Pure math
- **Input validation** (`utils/calculations.py:33-84`): `parse_height`, `parse_weight`, `validate_activity`, `normalize_gender`, `parse_age` — all pure functions

### 11.3 Exercise System

- **Exercise catalog** (`exercises_template.py:20-56`): List of exercise definitions with id, name, description, muscle_groups, technique
- **Weekly training plan** (`exercises_template.py:96-127`): Week→Day→Exercise ID mapping
- **Pain-based filtering** (`exercises_template.py:164-203`): Filter exercises by excluded muscle groups
- **Exercise text formatting** (`exercises_template.py:206-247`): Generate readable exercise list text

### 11.4 Data Access Layer

- **All functions in `database/DataBase.py`** are messenger-agnostic (no Telegram imports). They can be reused as-is for MAX, potentially with:
  - A migration to named tuples or dataclasses (instead of raw tuples)
  - Connection pooling
  - Potential switch to a different DB engine

### 11.5 Training Workflow Rules

- **3-day training cycle** with day rotation `(current_day + 1) % 3`
- **Week completion at 3 completed days**
- **Check01 gate at week 2** (redo week if failed)
- **Check02 every week from week 2+**
- **Week advancement** resets counters but preserves session
- **Training day schedule mapping**: `{"Пн-Ср-Пт": [0,2,4], "Вт-Чт-Сб": [1,3,5], "Ср-Пт-Вс": [2,4,6]}`
- **Training types**: 3 fixed types (Push, Pull, Legs)

### 11.6 Scheduled Job Logic

- **Evening check logic:** Iterate active sessions → check if training day → create pending log → notify user
- **Next-day reminder logic:** Check for unanswered yesterday logs → remind
- **Auto-deactivation logic:** Check for 2-day-old unanswered logs → deactivate session
- `[NOTE]` The scheduling infrastructure (APScheduler) is agnostic; only the notification delivery is messenger-specific.

### 11.7 Content

- Diet plan texts (`text01`, `text02`)
- Recovery recommendations (`text03`)
- Training program description (`text04`)
- Exercise technique descriptions

### 11.8 Short Form Update Pattern

- Returning users update only weight + activity level
- Other fields inherited from first form
- BMR recalculated with new values

### 11.9 Body Weight Tracking Rules

- Prompt for weigh-in if ≥7 days since last record or no record exists
- Weight validation: 20–300 kg

---

# 12. What Must Be Redesigned for MAX

## 12.1 Transport Layer (Complete Replacement)

- Replace `python-telegram-bot` with MAX messenger SDK/API client
- Implement MAX-specific event handling (message reception, callback handling)
- Implement MAX-specific message sending (text, keyboards, buttons)
- Implement MAX-specific proactive messaging for scheduled notifications

## 12.2 Event/Update Model

- Replace `telegram.Update` parsing with MAX event parsing
- Create adapter layer: `MAX event → internal command/message object → handler`

## 12.3 Authentication / User Identification

- Replace `update.message.from_user.id` (Telegram int) with MAX user identifier
- Determine MAX user ID format (may be string, UUID, or integer)
- Update `user_id` column type in DB if needed (currently `INTEGER`)

## 12.4 Keyboards and Buttons

- **Reply Keyboards:** Telegram's `ReplyKeyboardMarkup` must be replaced with MAX's equivalent persistent keyboard mechanism (if it exists)
- **Inline Keyboards:** Telegram's `InlineKeyboardMarkup` with callback data must be replaced with MAX's interactive message components
- `[CRITICAL]` If MAX does not support reply keyboards, the entire navigation model (state-based button menus) must be redesigned — potentially using commands, message-based menus, or inline buttons exclusively

## 12.5 Callback/Interaction Pattern

- Telegram's callback query model (click inline button → receive callback with data → answer + edit message) may not exist in MAX
- Need to understand MAX's equivalent for interactive elements

## 12.6 ConversationHandler / FSM

- Replace `telegram.ext.ConversationHandler` with a custom FSM implementation
- The state definitions and transitions (from `utils/states.py`) can be reused
- Need a new dispatch mechanism: incoming MAX message → determine current state → route to handler

## 12.7 Message Formatting

- Telegram supports basic markdown/HTML. MAX may have different formatting options.
- All emoji usage should work cross-platform, but verify MAX rendering
- Message length limits may differ (currently hardcoded 4096)

## 12.8 File Handling

- No file handling exists in the current bot
- `[NOTE]` If MAX has different media capabilities, this is not a current concern

## 12.9 Proactive Messaging Infrastructure

- Scheduled jobs use `application.bot.send_message(chat_id=user_id, ...)` — must be replaced with MAX's send API
- Determine if MAX allows bots to initiate conversations with users who haven't messaged recently

## 12.10 Session/Context Management

- `context.user_data` is a Telegram-library feature. Need to implement an equivalent:
  - In-memory dict keyed by MAX user ID (simplest, but lost on restart)
  - Redis-backed session store (recommended for production)
  - DB-backed session store (heaviest, most durable)

## 12.11 Connection Mode

- Telegram uses polling or webhooks. Determine MAX's bot connection model.
- If MAX requires webhooks, need to add an HTTP server (e.g., aiohttp, FastAPI)

## 12.12 Telegram Behavioral Assumptions

The following Telegram-specific behaviors are implicitly relied upon:

| Assumption | Telegram Reality | MAX Impact |
|------------|-----------------|------------|
| Reply keyboard persists until replaced | Yes, Telegram shows last keyboard | Verify MAX behavior |
| `from_user.id` is stable and unique | Yes, Telegram IDs are permanent | Verify MAX user ID stability |
| Private chat `chat_id == user_id` | Yes, in private chats | MAX may differ |
| Bot can message any user who started chat | Yes, after `/start` | Verify MAX bot→user messaging rules |
| Callback queries require `.answer()` | Yes, otherwise Telegram shows loading | MAX may not have this concept |
| Message editing after callback | Supported | Verify MAX support |

---

# 13. Risks, Ambiguities, and Hidden Logic

## 13.1 Column Name Mismatch

**Risk:** `years_experience` in the `users` table actually stores the user's **age**, not training experience. The form asks "Сколько вам полных лет?" (How old are you?) and the variable is called `years_experience` in states but `parse_age` in validation. This could cause confusion during migration.

## 13.2 Hardcoded Database Path

**Risk:** `'users.db'` is hardcoded as default in every `DataBase.py` function. The path is relative to the working directory. If the bot is launched from a different directory, the DB location changes silently.

## 13.3 Raw Tuple Indexing

**Risk:** All DB query results are accessed by positional index (e.g., `session[0]`, `session[2]`, `session[4]`). A schema change that adds or reorders columns will break all consumers silently.

**Tuple index mapping for `training_sessions`:**
- `[0]` = id
- `[1]` = user_id
- `[2]` = week_number
- `[3]` = training_days
- `[4]` = current_day
- `[5]` = completed_days
- `[6]` = session_active
- `[7]` = check01_passed
- `[8]` = check02_passed
- `[9]` = created_at
- `[10]` = updated_at

**Tuple index mapping for `users`:**
- `[0]` = id
- `[1]` = user_id
- `[2]` = username
- `[3]` = height
- `[4]` = weight
- `[5]` = activity_level
- `[6]` = gender
- `[7]` = years_experience (age)
- `[8]` = brm
- `[9]` = goal
- `[10]` = created_at
- `[11]` = updated_at

**NOTE:** In `handlers/show.py:54-55`, the code uses `user_data[8]` for `created_date` and `user_data[9]` for `updated_date`, but per the schema, index 8 is `brm` and index 9 is `goal`. This means `show_me()` displays the **BMR value as creation date** and the **goal as update date**. `[BUG CONFIRMED]` The indices are wrong — the actual date columns are at indices 10 and 11.

## 13.4 State Loss on Restart

**Risk:** All user state (`context.user_data`) is in-memory. If the bot restarts:
- Users mid-questionnaire lose their progress
- Users in weight collection lose entered weights
- Users in check flow lose their check step
- Current menu state resets to default (MENU_STATE)

## 13.5 Inline SQL in Handlers

**Risk:** `handlers/training_check.py:200-209` directly opens a SQLite connection and runs raw SQL instead of going through `DataBase.py`. Similarly, `handlers/training_check.py:251-260`. This creates a maintenance risk and bypasses any future DB abstraction.

## 13.6 Concurrent Access to SQLite

**Risk:** SQLite is not designed for concurrent writes. If two users trigger handlers simultaneously, or a scheduled job runs during a handler, they open separate connections. SQLite's file-level locking may cause `database is locked` errors under load.

## 13.7 Timezone Not Configured

**Risk:** APScheduler jobs run at 23:00, 16:00, 23:59 in the **system's local timezone**. No explicit timezone is set. If deployed on a cloud server in UTC, the times will be wrong for Moscow-timezone users.

## 13.8 Duplicate Code

**Risk:** `show_my_forms()` and `show_all()` in `handlers/show.py` contain **identical** logic (lines 76-157 and 160-241). Any bug fix must be applied twice.

## 13.9 Incomplete Training Plan

**Risk:** `exercises_template.py` only has exercises defined for week 1. Weeks 2–6 have empty exercise lists (`[]`). Users advancing past week 1 will see "Упражнения не заполнены" errors.

## 13.10 Check02 Accepts Any Input

**Explicitly marked in code:** `handle_check02_response` is described as "ВРЕМЕННАЯ ЗАПЛАТКА" (temporary patch). It accepts any text as caloric intake without validation.

## 13.11 Check01 Only Reset Partially

**Ambiguity:** When check01 fails (user says they didn't complete all trainings), `completed_days` and `current_day` are reset to 0, but the `training_log` entries for the completed days are NOT deleted. This means the user's training history shows completions that were "invalidated."

## 13.12 `skip_day` Callback Handler

**Hidden:** `handlers/training.py:59-97` registers a `skip_day` callback handler, but no inline button with `callback_data="skip_day"` is ever created in the current code. `[INFERENCE]` This appears to be a debug/test function that's registered but unreachable through normal UI.

## 13.13 `handle_skip_day_missed` Function

**Hidden:** `handlers/navigation.py:753-799` defines `handle_skip_day_missed()` but it is **never called** from anywhere. Dead code.

## 13.14 `handle_pain_feedback` Function

**Hidden:** `handlers/training_check.py:231-312` defines `handle_pain_feedback()` but it is **never called** from any handler or navigation flow. It references `context.user_data['training_log_id']` which is never set. Dead code.

## 13.15 Magic String Matching

**Risk:** Button text matching in `handle_all_messages` and `handle_navigation` uses hardcoded lowercase string comparisons. Any change to button text in `keyboards.py` must be mirrored in navigation handlers. No constant or enum ties them together.

## 13.16 Mixed Language Button Labels

**Ambiguity:** Some button labels are in English ("main", "questionnaire", "goal & diet", "recovery recommendations", "training process", "return", "main menu") while the bot messages are entirely in Russian. `[INFERENCE]` This may be intentional (developer-facing labels) or accidental (work in progress).

## 13.17 `updated_at` Never Updated

**Risk:** The `users` table has `updated_at` column but it's only set by `DEFAULT CURRENT_TIMESTAMP` on insert. No `UPDATE` query ever touches this column. It always equals `created_at`.

## 13.18 No Error Handling for Scheduled Jobs

**Risk:** If `check_training_completion`, `check_training_completion_next_day`, or `reset_unanswered_sessions` throws an exception (e.g., user blocked the bot), the error is not caught. APScheduler's default behavior may log it, but the other users in the same job batch may not be processed.

## 13.19 `show_me` Index Bug Detail

In `handlers/show.py:54-55`:
```python
created_date = format_date(user_data[8])  # Actually brm (REAL)
updated_date = format_date(user_data[9])  # Actually goal (TEXT)
```
Then displayed as:
```python
f"📅 Дата заполнения: {created_date}\n"
f"✏️ Дата обновления: {updated_date}\n"
```
The `format_date` function will attempt to parse the BMR number as a timestamp and the goal string as a date, producing nonsensical output.

---

# 14. Build Blueprint for a New MAX Bot

## Recommended Architecture

```
max-fitness-bot/
├── config/
│   ├── settings.py               # All configuration (env vars, constants)
│   └── .env                      # Secrets
├── core/
│   ├── models.py                 # Domain models (dataclasses: User, TrainingSession, etc.)
│   ├── services/
│   │   ├── user_service.py       # User profile CRUD, BMR calculation
│   │   ├── training_service.py   # Training session management, week transitions
│   │   ├── exercise_service.py   # Exercise catalog, filtering, formatting
│   │   ├── check_service.py      # Check01/check02 business logic
│   │   └── schedule_service.py   # Scheduled check logic (messenger-agnostic)
│   ├── validators.py             # Input validation (height, weight, age, etc.)
│   └── calculations.py           # BMR, BMI calculations
├── data/
│   ├── database.py               # DB connection management
│   ├── repositories/
│   │   ├── user_repo.py          # User table operations
│   │   ├── session_repo.py       # Training session operations
│   │   ├── log_repo.py           # Training log operations
│   │   ├── weight_repo.py        # Exercise weight operations
│   │   └── body_weight_repo.py   # Body weight operations
│   └── migrations/               # Schema versioning
├── content/
│   ├── texts.py                  # All static text content (Russian)
│   ├── exercises.py              # Exercise catalog and training plans
│   └── keyboards.py              # Abstract keyboard definitions (not messenger-specific)
├── transport/
│   ├── max_adapter.py            # MAX SDK wrapper (send message, send keyboard, etc.)
│   ├── handlers/
│   │   ├── start_handler.py      # /start and menu navigation
│   │   ├── form_handler.py       # Questionnaire flow
│   │   ├── training_handler.py   # Training process interaction
│   │   ├── check_handler.py      # Check01/check02 interaction
│   │   └── show_handler.py       # Data display
│   ├── fsm.py                    # Generic finite state machine
│   ├── session_store.py          # User session/state management
│   └── keyboards_max.py          # MAX-specific keyboard rendering
├── scheduler/
│   └── jobs.py                   # Cron job definitions and runner
├── main.py                       # Application entry point
├── requirements.txt
├── Dockerfile
└── README.md
```

## Key Design Principles

### 1. Strict Layer Separation

- **`core/`** has ZERO imports from `transport/`. Business logic is pure Python.
- **`transport/`** converts MAX events to service calls and service results to MAX messages.
- **`data/`** is the only module that touches the database.

### 2. Domain Models Replace Tuples

```python
@dataclass
class UserProfile:
    id: int
    user_id: str  # MAX user ID (may be string)
    username: str
    height: float
    weight: float
    activity_level: str
    gender: str
    age: int  # Renamed from years_experience
    bmr: float
    goal: str
    created_at: datetime
    updated_at: datetime

@dataclass
class TrainingSession:
    id: int
    user_id: str
    week_number: int
    training_days: str
    current_day: int
    completed_days: int
    session_active: bool
    check01_passed: bool
    check02_passed: bool
    created_at: datetime
    updated_at: datetime
```

### 3. Abstract Messenger Interface

```python
class MessengerAdapter(ABC):
    async def send_text(self, user_id: str, text: str) -> None: ...
    async def send_keyboard(self, user_id: str, text: str, buttons: list[list[str]]) -> None: ...
    async def send_inline_buttons(self, user_id: str, text: str, buttons: list[dict]) -> None: ...
    async def edit_message(self, message_id: str, text: str) -> None: ...
```

### 4. Generic FSM

```python
class StateMachine:
    def __init__(self, session_store: SessionStore):
        self.handlers: dict[State, Callable] = {}
        self.session_store = session_store
    
    def register(self, state: State, handler: Callable): ...
    async def dispatch(self, user_id: str, input_text: str): ...
```

### 5. Session Store Interface

```python
class SessionStore(ABC):
    async def get(self, user_id: str, key: str) -> Any: ...
    async def set(self, user_id: str, key: str, value: Any) -> None: ...
    async def clear(self, user_id: str) -> None: ...
```

### 6. Proper Error Handling

- All scheduled jobs should catch per-user exceptions and continue processing other users
- All handlers should have top-level try/except that returns a user-friendly error message
- Logging with structured format (user_id, action, result)

### 7. Configuration

- All hardcoded values extracted into `config/settings.py`
- Timezone explicitly configured
- DB path configurable
- Message length limits configurable
- Scheduled job times configurable

---

# 15. Final Condensed Implementation Specification

> If a developer had never seen the original Telegram bot, this is exactly what they must build.

## System Purpose

A personal fitness coaching bot that manages user profiles, delivers weekly training programs, tracks exercise and body weight progress, and performs automated training compliance checks.

## User Roles

Single role: **Client**. No admin panel. No authentication beyond messenger identity.

## Features to Implement

### F1: User Profile (Questionnaire)

**Full form (first time):**
- Collect: height (50–250 cm), weight (20–300 kg), activity level (4 options), gender (M/F), age (1–120), goal (deficit/surplus)
- Calculate BMR: Mifflin-St Jeor equation × activity multiplier
- Save all fields + BMR to database
- Show diet recommendation based on goal

**Short form (returning user):**
- Collect: weight, activity level only
- Copy height, gender, age, goal from first-ever profile
- Recalculate BMR
- Save as new profile row (append-only)

**Profile management:**
- View latest profile (with BMI calculation)
- View all profiles (first in full, subsequent as deltas vs previous)
- Delete latest profile
- Delete all profiles

### F2: Training Session Management

**Session creation:**
- User selects training days from 3 options: Mon-Wed-Fri, Tue-Thu-Sat, Wed-Fri-Sun
- Creates session: week 1, day 0, 0 completed

**Training cycle (per week):**
- 3 training days per week
- Day types rotate: Push → Pull → Legs → Push → ...
- Training day types:
  - Day 1: Грудь, Плечи, Трицепс (Chest, Shoulders, Triceps)
  - Day 2: Спина, Бицепс (Back, Biceps)
  - Day 3: Ноги и Кор (Legs and Core)

**Daily training flow:**
1. User views today's exercises
2. Bot asks health status (healthy / arm pain / back pain / leg pain)
3. Exercises filtered by pain (exclude exercises targeting painful area)
4. Display exercise list
5. Collect weight (kg) for each exercise sequentially
6. User marks training complete
7. Log training, save weights, advance counters
8. If week complete (3/3), trigger check flow
9. If ≥7 days since last weigh-in, ask for body weight

### F3: Exercise System

**Exercise catalog:** Each exercise has: id, name, description, muscle_groups[], technique text

**Current exercises:**
1. Отжимания с резиной (Push-ups with band) — chest, arms
2. Подтягивания с резиной (Pull-ups with band) — back, arms
3. Приседания с резиной (Squats with band) — legs
4. Тяга резины к поясу (Band row) — back, arms
5. Ягодичный мостик с резиной (Glute bridge with band) — legs, back

**Weekly training plan:** Maps week number × day number → list of exercise IDs. Currently only week 1 is populated.

**Pain filter mapping:**
- Arm pain → exclude exercises with "руки" muscle group
- Back pain → exclude exercises with "спина" muscle group
- Leg pain → exclude exercises with "ноги" muscle group

### F4: Week Completion Checks

**Week 1:** No checks. Show completion message.

**Week 2:** Two checks:
- Check01: "Did you complete all trainings?" (Yes/No)
  - Yes → proceed to check02
  - No → reset week (completed_days=0, current_day=0)
- Check02: "Enter average weekly caloric intake" (free text, currently no validation)
  - Any response → mark check02 passed, week complete

**Week 3+:** Only check02 (same as above).

**Week advancement:** Resets completed_days, current_day, check02_passed. Does NOT reset check01_passed.

### F5: Scheduled Notifications

**Daily at 23:00:** For each active session where today is a training day, if no pending check exists → send "Did you train today?" with Yes/No buttons.

**Daily at 16:00:** For each active session where yesterday was a training day and the check is still pending → send reminder.

**Daily at 23:59:** For each active session with a 2-day-old pending check → deactivate session, notify user.

**User responses to scheduled checks:**
- "Yes, completed" → log as completed, advance counters, check week completion
- "No, not completed" → log as not completed, show postponement message

### F6: Navigation Structure

```
Main Menu [MENU_STATE]
├── Main → Core Menu [MAIN_STATE]
│   ├── Questionnaire → Anketa Menu [ANKETA_STATE]
│   │   ├── /form → Full or Short questionnaire
│   │   ├── /show_all → View all profiles
│   │   ├── /clear_last → Delete latest profile
│   │   ├── /clear_all → Delete all profiles
│   │   ├── /cancel → Cancel form
│   │   ├── Следующая неделя → Advance week + short form
│   │   └── return → Back to Core Menu
│   ├── Goal & Diet → Show diet plan text
│   ├── Recovery Recommendations → Show recovery text
│   ├── Training Process → Training keyboard or session setup
│   │   ├── Упражнения дня → Health check → Exercises → Weight collection
│   │   ├── Расписание → Show weekly schedule
│   │   ├── Я выполнил тренировку → Mark complete
│   │   ├── Статус → Show training status
│   │   ├── Техника → Exercise technique browser [TRAINING_TECHNIQUE_STATE]
│   │   ├── Предыдущая неделя → Go back one week
│   │   ├── Следующая неделя → Advance one week
│   │   └── Основное меню → Back to Core Menu
│   └── Main Menu → Back to Main Menu
└── /achievements → Stub (in development)
```

### F7: Database Schema

5 tables: `users`, `training_sessions`, `training_log`, `exercise_weights`, `weight_progress`. See Section 7 for full schema.

**Key design decisions to preserve:**
- Users table is append-only (multiple rows per user for progress tracking)
- Training sessions: one active per user
- Training log: `completed=NULL` means pending check
- Exercise weights: denormalized (exercise_name stored alongside ID)

### F8: Static Content

4 text blocks in Russian:
1. Diet plan for deficit (text01)
2. Diet plan for surplus (text02)
3. Recovery recommendations (text03)
4. Training program description (text04)

### F9: BMR Formula

```
Men:   BMR = ((10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5) × activity_multiplier
Women: BMR = ((10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161) × activity_multiplier

Activity multipliers:
  "Очень высокая" = 1.725
  "Высокая"       = 1.55
  "Средняя"       = 1.375
  "Низкая"        = 1.2
```

---

# Open Questions Before MAX Implementation

1. **MAX Bot SDK:** What is the official MAX messenger bot SDK for Python? What event model does it use? Does it support webhooks, polling, or WebSocket?

2. **MAX Keyboard Support:** Does MAX support persistent reply keyboards (like Telegram's `ReplyKeyboardMarkup`)? If not, how should the menu-driven navigation be redesigned?

3. **MAX Inline Buttons:** Does MAX support inline buttons attached to messages with callback data? This is used for training day selection.

4. **MAX Message Editing:** Can MAX bots edit previously sent messages? This is used after inline button callbacks.

5. **MAX Proactive Messaging:** Can a MAX bot send messages to users proactively (without the user sending a message first)? This is required for scheduled training checks.

6. **MAX User ID Format:** What type is the MAX user ID (integer, string, UUID)? This affects the database schema.

7. **MAX Message Length Limit:** What is the maximum message length in MAX? (Currently hardcoded as 4096 for Telegram.)

8. **Timezone:** What timezone should scheduled jobs use? The current bot has no explicit timezone configuration.

9. **Deployment Target:** Will the MAX bot run on Windows (like the current Telegram bot) or on a Linux server? This affects Docker/deployment design.

10. **Training Plan Content:** Weeks 2–6 have empty exercise lists. Should the MAX bot launch with only week 1, or should the full plan be provided before development begins?

11. **Check02 Validation:** The caloric intake check currently accepts any text. Should it validate numeric input in the MAX version?

12. **Column Naming:** Should the `years_experience` column be renamed to `age` in the new schema to fix the naming inconsistency?

13. **Concurrent Users:** How many concurrent users are expected? This determines whether SQLite is sufficient or a switch to PostgreSQL is needed.

14. **State Persistence:** Should user session state (current menu, weight collection progress, etc.) survive bot restarts? Currently it does not.

15. **Admin Panel:** Is there a need for an admin role or admin commands in the MAX version that didn't exist in the Telegram version?

16. **Bug Fixes:** The `show_me` command displays BMR and goal where dates should appear (index bug). Should this be fixed in the MAX version? (Almost certainly yes.)

17. **`show_all` vs `my_forms`:** These two commands are identical. Should the MAX version keep both or merge them?

18. **Dead Code:** Several functions (`handle_skip_day_missed`, `handle_pain_feedback`, `skip_day` callback) are defined but never called. Should any of this intended-but-unfinished functionality be completed for MAX?
