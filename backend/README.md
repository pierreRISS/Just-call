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

The TwiML App voice request URL must point to the public backend route.
When testing locally, first expose the backend with ngrok:

```bash
ngrok http 8000
```

Copy the HTTPS URL from ngrok and use it as the TwiML App Voice Request URL:

```text
https://your-ngrok-url.ngrok-free.app/voice/twiml
```

Then copy the TwiML App SID, which starts with `AP`, into `TWILIO_TWIML_APP_SID`
and restart the backend.

## Routes

- `GET /health`
- `GET /voice/config`
- `GET /voice/token`
- `POST /voice/twiml`
- `GET /contacts`
- `POST /contacts`
- `PATCH /contacts/{contact_id}`
- `DELETE /contacts/{contact_id}`
- `GET /call-logs`
- `POST /call-logs`
