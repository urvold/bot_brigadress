# Deploy to Railway (GitHub → Railway) in 10–15 minutes

This repo is a **monorepo** with two deployable apps:
- `backend/` — FastAPI API + serves the Telegram WebApp (`/webapp/`)
- `bot/` — aiogram Telegram bot (long polling)

Railway deploys **each folder as its own Service** by setting **Root Directory**. citeturn0search0turn0search4

## 0) Prereqs
- You have a Telegram bot token from @BotFather.
- You know your Telegram numeric ID (for admin notifications).
  - Easy: send a message to @userinfobot and copy your `Id`.

## 1) Push to GitHub
Upload this repo to GitHub (or push with git).

## 2) Create Railway Project and Postgres
1. Railway → New Project → Deploy from GitHub Repo (select your repo).
2. Add → Database → PostgreSQL. citeturn0search2

## 3) Deploy BACKEND service
1. Add → Service → GitHub Repo (select the same repo).
2. Service Settings → **Root Directory**: `backend` citeturn0search0turn0search4
3. Variables (set these):
   - `BOT_TOKEN` = your bot token
   - `ADMIN_TELEGRAM_IDS` = your id (or comma-separated ids)
   - `PUBLIC_BASE_URL` = (set later, after you generate a domain)
   - `POSTGRES_HOST` = value of Postgres `PGHOST`
   - `POSTGRES_PORT` = value of `PGPORT`
   - `POSTGRES_USER` = value of `PGUSER`
   - `POSTGRES_PASSWORD` = value of `PGPASSWORD`
   - `POSTGRES_DB` = value of `PGDATABASE`
4. Settings → Networking → Generate Domain (Railway gives you an https URL).

Now set:
- `PUBLIC_BASE_URL=https://<your-backend-domain>`

Healthcheck:
- `https://<your-backend-domain>/api/health`

## 4) Deploy BOT service
1. Add → Service → GitHub Repo (same repo).
2. Service Settings → **Root Directory**: `bot` citeturn0search0turn0search4
3. Variables:
   - `BOT_TOKEN` = your bot token
   - `ADMIN_TELEGRAM_IDS` = your id(s)
   - `PUBLIC_BASE_URL=https://<your-backend-domain>`
   - `API_INTERNAL_URL` = choose one option below

### Option A (simplest): call API via public domain
- `API_INTERNAL_URL=https://<your-backend-domain>`

### Option B (recommended): call API via Railway private network
Railway provides an internal DNS name: `<service-name>.railway.internal` + the service PORT. citeturn0search3turn0search6  
If your backend service is named `backend`, use:
- `API_INTERNAL_URL=http://backend.railway.internal:8000`

## 5) Test
1. In Telegram: open your bot → `/start` → press **Open WebApp**
2. Submit a lead. Then open WebApp → Admin → see the lead and change status.

## Notes
- Backend Dockerfile listens on `$PORT` (Railway sets it automatically). citeturn0search5
- You will still need **two Railway services** for a monorepo. Railway staff confirms this is done via service settings (Root Directory). citeturn0search1
