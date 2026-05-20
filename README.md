# MAX Fitness Bot

Personal fitness coaching bot for MAX messenger. Manages user profiles, delivers weekly training programs with resistance bands, tracks exercise/body weight progress, and performs automated training compliance checks.

Migrated from a Telegram bot — see `MIGRATION_PLAN.md` for adaptation details.

## Quick Start

### 1. Get a bot token

Go to [business.max.ru/self](https://business.max.ru/self) → Чат-боты → Интеграция → Получить токен.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set MAX_BOT_TOKEN
```

### 3. Install dependencies

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Run

```bash
# From project root
python app/main.py
```

Or set `PYTHONPATH` explicitly:
```bash
PYTHONPATH=. python app/main.py
```

### 5. Docker (optional)

```bash
# Copy and configure .env first
docker compose up -d
```

## Project Structure

```
├── app/main.py              # Entry point (polling mode)
├── config/settings.py       # Environment-based configuration
├── core/                    # Domain models, calculations, validators
├── content/                 # Static texts, exercise catalog
├── repositories/            # SQLite database access layer
├── services/                # Business logic orchestration
├── transport/max/           # MAX-specific keyboards and helpers
├── handlers/                # Event handlers (commands, callbacks, text input)
├── scheduler/jobs.py        # APScheduler cron jobs (23:00, 16:00, 23:59)
├── MIGRATION_PLAN.md        # Telegram → MAX adaptation notes
├── ARCHITECTURE.md          # Architecture documentation
└── BOT_REVERSE_ENGINEERING_REPORT.md  # Original Telegram bot analysis
```

## Architecture

- **Strict layer separation:** handlers → services → repositories. Business logic has zero MAX dependencies.
- **Transport isolation:** All MAX-specific code (keyboards, message sending) lives in `transport/max/`.
- **State management:** `maxapi` MemoryContext for FSM states + in-memory session store for transient data.
- **Database:** SQLite with named column access (no tuple indexing).

See `ARCHITECTURE.md` for full details.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/form` | Fill questionnaire (full or short) |
| `/show_me` | View latest profile |
| `/my_forms` | View all profiles |
| `/clear_last` | Delete latest profile |
| `/clear_all` | Delete all profiles |
| `/cancel` | Cancel current form |
| `/achievements` | Stub (in development) |

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_BOT_TOKEN` | *required* | Bot API token |
| `DATABASE_PATH` | `data/bot.db` | SQLite database path |
| `TIMEZONE` | `Europe/Moscow` | Timezone for scheduled jobs |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CHECK_HOUR_EVENING` | `23` | Evening check hour |
| `REMINDER_HOUR` | `16` | Reminder hour |
| `RESET_HOUR` | `23` | Session reset hour |

## Key Adaptations from Telegram

1. **No reply keyboards** — MAX only supports inline keyboards. All menus use callback buttons attached to messages.
2. **Callback-based navigation** — Instead of text matching, all navigation uses structured callback payloads (`nav:main`, `training:complete`, etc.).
3. **Message limit** — MAX allows 4000 characters per message (Telegram: 4096). Long messages are split accordingly.
4. **User ID** — MAX uses integer user IDs (same as Telegram). No schema changes needed.
5. **State machine** — Telegram's `ConversationHandler` replaced with `maxapi` MemoryContext states.

See `MIGRATION_PLAN.md` for the full mapping.

## Scheduled Jobs

| Time | Job | Description |
|------|-----|-------------|
| 23:00 | Evening check | Ask "did you train today?" on training days |
| 16:00 | Reminder | Remind about unanswered yesterday's check |
| 23:59 | Session reset | Deactivate sessions with 2-day-old unanswered checks |

## Known Limitations

- Only week 1 exercises are populated (weeks 2–6 show "not available").
- Check02 (caloric intake) accepts any text without validation (same as original).
- In-memory session state is lost on restart.
- SQLite may have issues under high concurrent load.

## License

Private project. Not for redistribution.
