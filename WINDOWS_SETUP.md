# AGP Windows Development Setup

This guide assumes you are working in PowerShell using Antigravity IDE, VS Code, or another editor.

## What runs where

You will run two development servers:

1. **AGP Backend** — FastAPI at `http://localhost:8000`
2. **AGP Frontend** — React at `http://localhost:5173`

PostgreSQL stores AGP accounts, publications, editorial history, messages and analytics.

## Recommended route: Docker Desktop for the backend database/API

### Step 1 — Open the project

Extract the ZIP, then open the `agp-platform` folder in your IDE.

### Step 2 — Start PostgreSQL + FastAPI

Open PowerShell in the project root and run:

```powershell
docker compose up -d --build
```

Then create the database schema:

```powershell
docker compose exec api alembic upgrade head
```

Add the demonstration accounts/publication:

```powershell
docker compose exec api python -m app.scripts.seed
```

Check the API:

```text
http://localhost:8000/health
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

### Step 3 — Start the React frontend

Open a second PowerShell terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Local demonstration accounts

```text
Super Admin / Editorial
Email: editor@agp.local
Password: ChangeMe123!

Researcher
Email: researcher@agp.local
Password: ChangeMe123!
```

These are local development accounts only. Do not use these passwords in production.

## What to test first

1. Open the home page.
2. Open the seeded research publication.
3. Sign in as the researcher.
4. Create a new publication draft.
5. Edit and save a new version.
6. Submit it to Editorial.
7. Sign out.
8. Sign in using the Editorial account.
9. Open **Editorial Dashboard**.
10. Move the research through desk review, editorial review and source check.
11. Request a revision or approve it.
12. Sign back in as the researcher and inspect the publication workspace and analytics.
13. Open the researcher network and test internal messaging.

## Deploying later

The frontend can be deployed independently to Netlify. The FastAPI backend should be deployed to a Python-capable service with PostgreSQL.

Recommended domain structure:

```text
www.africaglobalpower.org     -> Netlify frontend
api.africaglobalpower.org     -> FastAPI backend
```

In Netlify set:

```text
VITE_API_URL=https://api.africaglobalpower.org/api/v1
```

In the production API configuration set the real frontend domain in `CORS_ORIGINS`, use a strong `SECRET_KEY`, enable secure cookies, and use a managed PostgreSQL database.
