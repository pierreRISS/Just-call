# Just Call

Boilerplate full-stack todo list with:

- `backend/`: FastAPI + PostgreSQL
- `frontend/`: Vue 3 + Vite + Tailwind CSS

## Start PostgreSQL

```bash
docker compose up -d postgres
```

The compose file maps PostgreSQL to local port `5433` by default to avoid
conflicts with an existing local PostgreSQL on `5432`.

## Start the API

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload
```

API: `http://localhost:8000`

For local development, CORS accepts Vite origins on `localhost`, `127.0.0.1`,
and private network IPs on ports `5173` to `5179`. Add more origins in
`backend/.env` with `FRONTEND_ORIGINS` if needed.

## Start the frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: `http://localhost:5173`

## Todo API

- `GET /todos`
- `POST /todos` with `{ "title": "My todo" }`
- `DELETE /todos/{todo_id}`
