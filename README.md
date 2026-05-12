# Just Call

AI-powered sales calling workspace for professional cold callers.

The product is now shaped around a calm premium workflow:

- prepare prospects with clean context
- launch browser calls through Twilio Voice
- capture notes, transcripts, outcomes, and quick actions
- store AI review fields without calling any AI service yet
- replay previous calls through AI simulation sessions
- keep profile, analytics, and settings ready for the new frontend

## Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Alembic, Twilio
- Frontend: Vue 3, TypeScript, Vite, Tailwind CSS, Pinia

## Start

```bash
./scripts/dev.sh
```

The dev script  starts PostgreSQL, ru ns Alembic migrations, seeds the default
workspace, and starts both backend and frontend.
