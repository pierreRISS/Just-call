# Cloudflare deployment

## Frontend: Cloudflare Pages

This frontend is a Vue/Vite static app, so deploy it with Cloudflare Pages.

Cloudflare Pages settings:

- Root directory: `frontend`
- Framework preset: `Vue` or `Vite`
- Build command: `npm run build`
- Build output directory: `dist`
- Production environment variable:
  - `VITE_API_URL=https://api.your-domain.com`

Cloudflare documents Vue/Vite Pages builds with `npm run build` and `dist` as the output directory:

- https://developers.cloudflare.com/pages/configuration/build-configuration/
- https://developers.cloudflare.com/pages/framework-guides/deploy-a-vite3-project/

## Manual deploy with Wrangler

From `frontend/`:

```bash
npm run deploy:cloudflare
```

Or explicitly:

```bash
npm run build
npx wrangler pages deploy dist --project-name just-call
```

If this is your first deploy, Wrangler will ask you to log in to Cloudflare and create/select the Pages project.

## Backend requirement

The frontend cannot call `localhost` once deployed. The backend must be available on a public HTTPS URL, for example:

```text
https://just-call-api.onrender.com
```

Then set this value in Cloudflare Pages as `VITE_API_URL`.

For the backend CORS allowlist, add the frontend production domain to:

```env
FRONTEND_ORIGINS=https://your-domain.com,https://just-call.pages.dev
```

For the free Render backend path, s ee [RENDER_DEPLOY.md](./RENDER_DEPLOY.md).

## Recommended public setup

- `app.your-domain.com` or `your-domain.com`: Cloudflare Pages frontend
- `api.your-domain.com` or `just-call-api.onrender.com`: FastAPI backend on Render Free
- PostgreSQL: managed database or your server
