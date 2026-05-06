# Just Call

Full-stack call cadence app for cold calling sessions:

- `backend/`: FastAPI + PostgreSQL
- `frontend/`: Vue 3 + Vite + Tailwind CSS

## Start Everything

```bash
./scripts/dev.sh
```

For Twilio Voice local testing, start the backend tunnel too:

```bash
./scripts/dev.sh --ngrok
```

This requires the `ngrok` CLI to be installed and authenticated first. If
`http://127.0.0.1:4040` refuses the connection, ngrok is not running.

Then open `http://127.0.0.1:4040`, copy the ngrok HTTPS URL, and use
`https://your-ngrok-url/voice/twiml` as the TwiML App Voice Request URL in
Twilio.

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
- `GET /contacts`
- `POST /contacts`
- `PATCH /contacts/{contact_id}`
- `DELETE /contacts/{contact_id}`
- `GET /call-logs`
- `POST /call-logs`
