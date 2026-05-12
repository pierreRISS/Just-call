# Render Free backend deployment

Use Render Free to expose the FastAPI backend at a public HTTPS URL.

## What this repo includes

- `backend/Dockerfile`: builds and starts the FastAPI API.
- `render.yaml`: Render Blueprint with:
  - `just-call-api` web service
  - `just-call-db` free PostgreSQL database
- `backend/app/config.py`: accepts Render's `postgres://` or `postgresql://` connection string and converts it to the installed `psycopg` SQLAlchemy driver.

## Deploy

1. Push this repo to GitHub.
2. In Render, create a new **Blueprint** from the repo.
3. Render will read `render.yaml`.
4. Create the services.

The API will run:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## After Render deploys

Copy the Render web service URL, for example:

```text
https://just-call-api.onrender.com
```

Then set Cloudflare Pages production environment variable:

```env
VITE_API_URL=https://just-call-api.onrender.com
```

Also update Render environment variables after you know your Cloudflare Pages/custom domain:

```env
FRONTEND_ORIGIN=https://your-frontend.pages.dev
FRONTEND_ORIGINS=https://your-frontend.pages.dev,https://your-custom-domain.com
```

## Free tier caveats

Render Free web services spin down after inactivity and may take about a minute to wake up. Render Free Postgres is for testing and preview use, not production permanence.
