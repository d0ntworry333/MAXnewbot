# Migration Plan: Telegram Bot → MAX Messenger Bot

> **Date:** 2026-04-01
> **Source:** Telegram fitness coaching bot (reverse-engineering report)
> **Target:** MAX messenger bot with equivalent business functionality

---

## 1. Features Preserved (1:1 mapping)

| # | Feature | Telegram Implementation | MAX Implementation | Notes |
|---|---------|------------------------|-------------------|-------|
| F1 | Full questionnaire (height/weight/activity/gender/age/goal) | ConversationHandler FSM | State machine via `maxapi` MemoryContext + states | Same validation rules, same fields |
| F2 | Short questionnaire (weight + activity only, returning users) | ConversationHandler FSM | Same FSM, separate entry point | Inherits fields from first form |
| F3 | BMR calculation (Mifflin-St Jeor) | Pure math in `utils/calculations.py` | Ported as-is to `core/calculations.py` | Zero platform dependency |
| F4 | Diet recommendations (deficit/surplus) | Static text blocks | Same static text blocks | Content unchanged |
| F5 | Training session creation (3 day-schedule options) | Inline keyboard → callback handler | Inline keyboard with `CallbackButton` | Callback mechanism maps cleanly |
| F6 | Training status display | Reply keyboard trigger → text | Callback or message button → text | Same data, different trigger |
| F7 | Daily exercises with pain filtering | Text menu → health keyboard → filter → display | Same flow via inline buttons | Core filtering logic unchanged |
| F8 | Sequential weight collection per exercise | `context.user_data` state machine | MemoryContext state machine | Same sequential flow |
| F9 | Mark training complete | Button press → DB update → counter advance | Same flow | Business logic unchanged |
| F10 | Week completion checks (check01/check02) | State-driven flow in handler | Same state-driven flow | Same branching by week number |
| F11 | Body weight tracking (≥7 day interval) | Post-training prompt | Same prompt timing | Same validation rules |
| F12 | Exercise technique browser | Dynamic keyboard → technique text | Inline buttons → technique text | Same content delivery |
| F13 | Week navigation (prev/next) | Button press → DB update | Same flow | Same counter reset logic |
| F14 | View user profile | `/show_me` command | `/show_me` command or button | Bug fix: correct date indices |
| F15 | View all forms (with deltas) | `/my_forms` command | Single command (deduped from `/show_all`) | Removes duplicate code |
| F16 | Delete forms (last/all) | `/clear_last`, `/clear_all` | Same commands | Same DB operations |
| F17 | Scheduled evening check (23:00) | APScheduler cron job | APScheduler cron job | Notification delivery adapted |
| F18 | Scheduled reminder (16:00) | APScheduler cron job | APScheduler cron job | Same logic |
| F19 | Session deactivation (23:59) | APScheduler cron job | APScheduler cron job | Same logic |
| F20 | Recovery recommendations | Static text display | Same | Content unchanged |
| F21 | Training plan description | Static text display | Same | Content unchanged |

---

## 2. Telegram Concepts Adapted for MAX

### 2.1 Reply Keyboards → Inline Keyboards with MessageButton

**Telegram:** `ReplyKeyboardMarkup` creates a persistent keyboard at the bottom of the chat. Buttons send their label text as a message.

**MAX:** No persistent reply keyboard concept exists. MAX only supports inline keyboards attached to specific messages.

**Adaptation:**
- All reply keyboard menus are converted to inline keyboards attached to the bot's last message.
- Navigation buttons use `CallbackButton` type (triggers `message_callback` event with payload).
- Each menu transition sends a new message with a new inline keyboard (instead of replacing a persistent keyboard).
- This means users see a message with buttons instead of a persistent bottom keyboard.

**Impact:** Slightly different UX — menus are contextual per-message instead of persistent. This is actually a cleaner pattern for state-driven menus.

### 2.2 Text-Based Navigation → Callback-Based Navigation

**Telegram:** The old bot matched button text (hardcoded strings like `"training process"`, `"📋 Упражнения дня"`) from `update.message.text`.

**MAX Adaptation:**
- All navigation uses `CallbackButton` with structured payload strings (e.g., `nav:main_menu`, `nav:training`, `action:complete_training`).
- This eliminates fragile string matching and makes routing explicit.
- For inputs that require free text (height, weight, age, caloric intake), the bot switches to text input mode and parses `message_created` events.

### 2.3 ConversationHandler → Custom State Machine

**Telegram:** `python-telegram-bot`'s `ConversationHandler` manages multi-step forms with states, entry points, and fallbacks.

**MAX Adaptation:**
- The `maxapi` library provides `MemoryContext` with state management (`get_state()`, `set_state()`).
- Handler decorators accept `states` parameter for state-based routing.
- The same state definitions (HEIGHT, WEIGHT, ACTIVITY_LEVEL, etc.) are preserved.
- Fallback to cancel is implemented via a cancel callback button available at every step.

### 2.4 `context.user_data` → MemoryContext + Custom Session Store

**Telegram:** `context.user_data` is a per-user in-memory dict provided by `python-telegram-bot`.

**MAX Adaptation:**
- `maxapi`'s `MemoryContext` provides per-user/per-chat context.
- An additional in-memory session store (`dict[int, dict]`) holds transient data like weight collection queues, check steps, and pain type.
- Like the original, this state is lost on restart. Future improvement: persist to DB or Redis.

### 2.5 Callback Query Answer → `POST /answers`

**Telegram:** `callback_query.answer()` dismisses the loading indicator; `callback_query.edit_message_text()` updates the message.

**MAX Adaptation:**
- `POST /answers` with `callback_id` updates the message and/or sends a notification.
- The `maxapi` library wraps this via `event.answer(new_text=...)`.
- Same behavioral pattern: acknowledge callback → update message or send new one.

### 2.6 Message Editing

**Telegram:** `callback_query.edit_message_text()` edits inline keyboard messages after selection.

**MAX:** `PUT /messages?message_id=...` edits messages (within 24h). Also available via `POST /answers` for callback responses.

**Adaptation:** Direct equivalent exists. No behavioral change needed.

### 2.7 Bot Commands

**Telegram:** `/start`, `/form`, `/cancel`, etc. are registered via `CommandHandler`.

**MAX:** The `maxapi` library provides `Command('start')` and `CommandStart()` filters. Commands work the same way — messages starting with `/`.

**Adaptation:** Commands are preserved as-is. The `bot_started` event in MAX fires when a user first opens the bot chat — used as an additional entry point alongside `/start`.

### 2.8 User Identification

**Telegram:** `user_id` is a stable integer. `chat_id == user_id` in private chats.

**MAX:** `user_id` is also an integer (confirmed from API docs: `"user_id": integer`). Private chat identification uses `user_id` directly.

**Adaptation:** No schema change needed. `user_id` column remains `INTEGER`.

### 2.9 Message Length Limit

**Telegram:** 4096 characters per message.

**MAX:** 4000 characters per message (from API docs: `text: string, до 4000 символов`).

**Adaptation:** Message splitting threshold changed from 4096 to 4000.

### 2.10 Proactive Messaging (Scheduled Notifications)

**Telegram:** `application.bot.send_message(chat_id=user_id, ...)` sends messages proactively.

**MAX:** `POST /messages?user_id={user_id}` sends messages proactively. The `maxapi` library provides `bot.send_message(user_id=..., text=...)`.

**Adaptation:** Direct equivalent exists. Scheduled jobs use the Bot instance to send messages.

---

## 3. Polling Implementation

### How it works in this project:
1. `maxapi.Dispatcher.start_polling(bot)` runs an infinite async loop.
2. Each iteration calls `GET /updates` with current `marker` and `timeout=30`.
3. The server holds the connection up to 30 seconds (long polling).
4. When updates arrive, the response includes an `updates[]` array and a `marker` for the next request.
5. The `marker` is saved on the bot instance (`bot.marker_updates`).
6. Each update is parsed into a typed event object and dispatched to matching handlers.
7. On connection errors, the loop retries after a delay (30s for connection errors, 5s for API errors).
8. Duplicate processing is avoided by the `marker` mechanism — the server only returns updates after the acknowledged marker.

### Continuation state:
- `marker` (integer or null) is managed automatically by the `maxapi` library.
- On first request (no marker), the server returns all pending updates.
- Subsequent requests pass the marker from the previous response.

### Failure handling:
- `AsyncioTimeoutError` → silently continues to next iteration.
- `ClientConnectorError` → waits 30 seconds, then retries.
- API error response → waits 5 seconds, then retries.
- Handler exceptions → logged, does not crash the polling loop.

---

## 4. Flow Mapping: Telegram → MAX

### 4.1 Main Menu Navigation

**Telegram flow:** `/start` → reply keyboard `["main", "/achievements"]` → text match routing.

**MAX flow:** `/start` or `bot_started` event → inline keyboard message with callback buttons → `message_callback` event routing via payload.

```
/start (or bot_started)
  → Send message "Добро пожаловать!" with inline keyboard:
    [CallbackButton("📋 Основное меню", payload="nav:main")]
    [CallbackButton("🏆 Достижения", payload="nav:achievements")]
  
  → User clicks "📋 Основное меню" → message_callback with payload "nav:main"
    → Send/edit message with main menu inline keyboard:
      [CallbackButton("📝 Анкета", payload="nav:anketa")]
      [CallbackButton("🎯 Цель и рацион", payload="nav:diet")]
      [CallbackButton("💪 Восстановление", payload="nav:recovery")]
      [CallbackButton("🏋️ Тренировочный процесс", payload="nav:training")]
      [CallbackButton("🏠 Главное меню", payload="nav:menu")]
```

### 4.2 Questionnaire Flow

Same step-by-step flow. At steps requiring button selection (activity, gender, goal), inline keyboards with `CallbackButton` are used. At steps requiring text input (height, weight, age), the bot sends a prompt and waits for `message_created` event.

### 4.3 Training Process

Inline keyboard with `CallbackButton` for day selection (same callback data pattern as Telegram). Training keyboard buttons become inline callbacks.

### 4.4 Scheduled Checks

Evening/reminder messages are sent proactively via `bot.send_message(user_id=...)`. Response buttons use inline keyboard with `CallbackButton`.

---

## 5. Assumptions (Where Report is Incomplete)

| # | Assumption | Reasoning |
|---|-----------|-----------|
| A1 | Only week 1 exercises are implemented; weeks 2–6 return "not available" message | Report confirms weeks 2–6 have empty exercise lists. Preserving as-is. |
| A2 | Check02 accepts any text input without validation | Report explicitly marks this as "ВРЕМЕННАЯ ЗАПЛАТКА" (temporary patch). Preserving as-is. |
| A3 | Timezone is Moscow (Europe/Moscow) for scheduled jobs | Report says no timezone configured. Assuming Moscow as most likely for Russian-language bot. Made configurable via env var. |
| A4 | SQLite is sufficient for expected load | No concurrent user count specified. SQLite works for <100 concurrent users. Made DB path configurable. |
| A5 | `years_experience` column renamed to `age` | Report confirms this is a naming bug. Fixed in new schema. |
| A6 | `show_me` date display bug is fixed | Report confirms indices 8/9 were wrong (showed BMR/goal instead of dates). Fixed in new code. |
| A7 | `/show_all` and `/my_forms` merged into single function | Report confirms these are 100% duplicate code. Merged. |
| A8 | Dead code (`skip_day`, `handle_skip_day_missed`, `handle_pain_feedback`) is excluded | Report confirms these are never called. Not ported. |
| A9 | `bot_started` event used alongside `/start` for initial greeting | MAX sends `bot_started` when user opens bot chat. Used as welcome trigger. |
| A10 | Button labels translated to Russian | Original had mixed English/Russian labels. All buttons now in Russian for consistency. |

---

## 6. Risks and Mismatches

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | No persistent reply keyboards in MAX | **High** | All menus converted to inline keyboards. UX changes: menus are per-message, not persistent. Users must interact with the latest message. |
| R2 | MAX inline keyboard limit (210 buttons, 30 rows, 7 per row) | **Low** | Largest keyboard is training keyboard (8 buttons). Well within limits. |
| R3 | In-memory state lost on restart | **Medium** | Same risk as Telegram version. Documented. Future: persist to DB. |
| R4 | `maxapi` library is young (v0.9.4) and may have bugs | **Medium** | Transport layer is isolated. Can be replaced with raw HTTP if needed. |
| R5 | Message editing limited to 24h in MAX | **Low** | Bot typically edits messages immediately after callback. Not a practical concern. |
| R6 | APScheduler scheduled jobs timezone dependency | **Medium** | Explicit timezone configuration via `TIMEZONE` env var (default: Europe/Moscow). |
| R7 | Concurrent SQLite access from scheduled jobs + handlers | **Medium** | Using WAL journal mode and connection-per-operation pattern. Same risk as original. |
| R8 | MAX `bot.send_message` for proactive messaging may fail if user blocked bot | **Medium** | Per-user exception handling in scheduled jobs (improvement over original). |
| R9 | `maxapi` MemoryContext is per chat_id+user_id, original was per user_id only | **Low** | In private chats, effectively the same. |

---

## 7. What Cannot Be Copied 1:1

1. **Reply keyboard menus** → Must be redesigned as inline keyboards (see §2.1).
2. **ConversationHandler** → Replaced with `maxapi` state machine (functionally equivalent).
3. **`context.user_data`** → Replaced with custom session store + MemoryContext.
4. **Text-based button matching** → Replaced with callback payload routing (cleaner).
5. **Message length splitting at 4096** → Changed to 4000 for MAX.
6. **Telegram-specific handler types** (`CommandHandler`, `MessageHandler`, `CallbackQueryHandler`) → Replaced with `maxapi` decorators (`@dp.message_created()`, `@dp.message_callback()`, etc.).
7. **`callback_query.answer()` pattern** → Replaced with `event.answer()` or `POST /answers`.
