# Just Call

Full-stack call cadence app for cold calling sessions:

- `backend/`: FastAPI + PostgreSQL
- `frontend/`: Vue 3 + Vite + Tailwind CSS

## Start Everything

```bash
./scripts/dev.sh
```

For Twilio Voice, use the deployed backend as the TwiML App Voice Request URL:

```text
https://just-call-api.onrender.com/voice/twiml
```

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
cp .env.example .env  # skip if backend/.env already exists
uv run alembic upgrade head
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
cp .env.example .env  # skip if frontend/.env already exists
npm run dev
```

Frontend: `http://localhost:5173`

## API

- `GET /health`
- `GET /me`
- `GET /prospects`
- `POST /prospects`
- `PATCH /prospects/{prospect_id}`
- `DELETE /prospects/{prospect_id}`
- `GET /calls`
- `POST /calls`
- `PATCH /calls/{call_id}`
- `DELETE /calls/{call_id}`
- `POST /ai-reviews`
- `GET /replay-sessions`
- `POST /replay-sessions`
- `GET /settings`
- `PATCH /settings`
- `POST /twilio/outbound-calls`
