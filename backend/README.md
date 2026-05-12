# Backend

FastAPI API for the Just Call AI-powered sales calling workspace, backed by PostgreSQL.

## Setup

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

By default the API expects PostgreSQL at:

```text
postgresql+psycopg://postgres:postgres@localhost:5433/just_call
```

You can override it with `DATABASE_URL`.

`SEED_ON_STARTUP=true` inserts a default mono-user workspace with sample prospects,
calls, AI review data, replay sessions, and settings.

## Migrations

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

## Twilio Voice

For browser calls, create a Twilio API key and a TwiML App, then set:

```env
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+...
TWILIO_API_KEY_SID=SK...
TWILIO_API_KEY_SECRET=...
TWILIO_TWIML_APP_SID=AP...
```

When testing locally, expose the backend with ngrok and set the TwiML App Voice Request URL:

```text
https://your-ngrok-url.ngrok-free.app/voice/twiml
```

## Routes

- `GET /health`
- `GET /me`
- `GET /prospects`
- `POST /prospects`
- `GET /prospects/{prospect_id}`
- `PATCH /prospects/{prospect_id}`
- `DELETE /prospects/{prospect_id}`
- `GET /calls`
- `POST /calls`
- `GET /calls/{call_id}`
- `PATCH /calls/{call_id}`
- `DELETE /calls/{call_id}`
- `POST /ai-reviews`
- `PATCH /ai-reviews/{review_id}`
- `GET /replay-sessions`
- `POST /replay-sessions`
- `PATCH /replay-sessions/{replay_session_id}`
- `POST /replay-sessions/{replay_session_id}/messages`
- `GET /settings`
- `PATCH /settings`
- `POST /twilio/outbound-calls`
- `GET /voice/config`
- `GET /voice/token`
- `GET /voice/twiml`
- `POST /voice/twiml`
- `POST /voice/dial-status`
- `POST /voice/recording-status`
