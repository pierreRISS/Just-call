# Backend

FastAPI API for the Just Call cold calling cadence app, backed by PostgreSQL.

## Setup

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
```

By default the API expects PostgreSQL at:

```text
postgresql+psycopg://postgres:postgres@localhost:5433/just_call
```

You can override it with `DATABASE_URL`.

## Routes

- `GET /health`
- `GET /contacts`
- `POST /contacts`
- `PATCH /contacts/{contact_id}`
- `DELETE /contacts/{contact_id}`
- `GET /call-logs`
- `POST /call-logs`
