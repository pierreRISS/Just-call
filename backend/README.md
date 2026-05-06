# Backend

FastAPI boilerplate for a tiny todo API backed by PostgreSQL.

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
- `GET /todos`
- `POST /todos`
- `DELETE /todos/{todo_id}`
