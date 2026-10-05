# Africa & Global Power (AGP)

Africa & Global Power is a full-stack research, policy-intelligence, publishing, and researcher-collaboration platform focused on Africa's place in a changing global order.

This repository contains the first production-oriented AGP foundation:

- Public research and intelligence website
- Researcher accounts and public profiles
- Researcher dashboard and publication analytics
- Publication drafting, submission, and version-aware editorial workflow
- Researcher-to-researcher messaging
- Editorial dashboard for vetting, source checks, revision requests, approvals, scheduling, and publication
- Restricted system administration for roles and platform controls
- FastAPI REST API
- PostgreSQL data layer with SQLAlchemy and Alembic
- Cookie-based authentication
- Netlify-ready frontend
- Docker-based local PostgreSQL/backend setup

## Architecture

```text
Netlify / static host
      |
React + TypeScript frontend
      |
HTTPS /api/v1
      |
FastAPI backend
      |
PostgreSQL
```

The frontend and backend are deliberately separated so AGP is not locked to one hosting provider. In production, a recommended setup is:

- `www.africaglobalpower.org` -> frontend on Netlify
- `api.africaglobalpower.org` -> FastAPI backend on Render, Railway, Fly.io, DigitalOcean, AWS, etc.
- Managed PostgreSQL -> provider of your choice
- S3-compatible object storage -> Cloudflare R2, Backblaze B2, AWS S3, etc. (adapter prepared for a later upload module)

## Project folders

```text
agp-platform/
├── backend/       FastAPI + PostgreSQL API
├── frontend/      React + TypeScript web app
├── docker-compose.yml
├── start-dev.ps1
└── start-dev.sh
```

## 1. Start the backend and PostgreSQL

The Docker Compose development configuration already contains local-only development values. `backend/.env.example` is provided for non-Docker or production-style configuration.

From the repository root:

```bash
docker compose up --build
```

The API will be available at:

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### Create database tables

In another terminal:

```bash
docker compose exec api alembic upgrade head
```

### Seed demo accounts and research

```bash
docker compose exec api python -m app.scripts.seed
```

Seeded accounts (change immediately outside local development):

- Managing editor: `editor@agp.local` / `ChangeMe123!`
- Researcher: `researcher@agp.local` / `ChangeMe123!`

## 2. Start the frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## Windows quick start

You can use `start-dev.ps1` from PowerShell. It starts Docker services, runs migrations, and then tells you how to start the frontend.

## Editorial workflow

AGP publications use the following workflow:

```text
DRAFT
  -> SUBMITTED
  -> DESK_REVIEW
  -> EDITORIAL_REVIEW
  -> REVISION_REQUESTED (if necessary)
  -> SOURCE_CHECK
  -> APPROVED
  -> SCHEDULED
  -> PUBLISHED
```

Every editorial action is stored in the editorial activity log.

## Account roles

- `reader`
- `researcher`
- `contributor`
- `reviewer`
- `editor`
- `senior_editor`
- `managing_editor`
- `super_admin`

A user's primary role controls access in this V1. The schema is intentionally designed so multi-role support can be introduced later without redesigning publications or editorial history.

## Production security checklist

Before deployment:

1. Change `SECRET_KEY` to a strong random value.
2. Set `COOKIE_SECURE=true`.
3. Restrict `CORS_ORIGINS` to your real frontend domains.
4. Use managed PostgreSQL with encrypted backups.
5. Put the API behind HTTPS.
6. Configure transactional email for verification, password resets, and message notifications.
7. Add rate limiting at the reverse proxy/API gateway and application level.
8. Configure object storage before enabling large PDF/dataset uploads.
9. Run dependency/security scans in CI.
10. Create a separate non-personal super-admin account and use MFA when the MFA module is enabled.

## Netlify deployment

The frontend contains `frontend/netlify.toml`.

Set this environment variable in Netlify:

```text
VITE_API_URL=https://api.africaglobalpower.org/api/v1
```

Then deploy the `frontend` directory.

## V1 scope versus later phases

This ZIP implements the core research publishing, researcher portal, messaging, editorial workflow, account roles, and analytics foundation.

The following larger modules are represented in the navigation/architecture but intentionally remain future modules rather than superficial mock implementations:

- Interactive Africa policy map
- Full Africa Policy Tracker
- Research Rooms collaborative workspaces
- Evidence Graph
- SourceCheck external DOI/URL verification service
- Data Lab connectors
- Opportunity ingestion engine
- Multilingual translation workflow
- Citation/export service

The database/API foundation is structured so these can be added as proper modules without replacing the core backend.
