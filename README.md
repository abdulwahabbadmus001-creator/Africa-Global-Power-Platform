<div align="center">

<img src="docs/assets/agp-logo.svg" alt="Africa & Global Power logo" width="720" />

# Africa & Global Power

### Research Africa. Understand Power.

A full-stack African research, policy-intelligence, publishing, collaboration, and knowledge-discovery platform.

[![Live Site](https://img.shields.io/badge/Live-africaglobalpower.netlify.app-071c16?style=for-the-badge&logo=netlify&logoColor=white)](https://africaglobalpower.netlify.app/)

</div>

---

## Launch Candidate Status

AGP is currently in **launch-freeze**. New discretionary features are paused while the production deployment and final smoke tests are completed.

**Current launch-candidate source commit:** `da676c0` — `Finalize professional Super Admin tab workflows`

The source code has passed the latest local release checks relevant to this launch candidate, including:

- frontend TypeScript/Vite production build;
- backend Python compile validation from the preceding launch-freeze release;
- dependency consistency checks;
- production dependency audit on the unchanged frontend dependency tree with 0 known vulnerabilities at the time of the audit;
- Git diff/secret-safety validation;
- clean working tree after push to `main`.

Before public launch, the remaining gates are operational rather than feature-development tasks:

1. confirm Netlify and Render are deploying the intended `main` revision;
2. run the production smoke-test checklist in `docs/LAUNCH-VALIDATION.md`;
3. verify authentication, role isolation, research submission/editorial publication flow, Super Admin controls, and public content behavior;
4. fix only genuine launch-blocking defects found during those tests;
5. keep the feature set frozen through launch.

A successful local build or Git push is **not** treated as proof that a hosting provider has deployed the same commit. Deployment parity must be checked in the Netlify and Render dashboards.

---

## Why I Built Africa & Global Power

Africa & Global Power began as a research and publication project hosted on **Blogger**. Blogger made it possible to publish quickly, but as my research interests expanded and I progressed further into software development, I began asking a simple question:

> If I am learning to build digital products, why should my research platform remain limited by a publishing tool I do not control?

AGP was therefore rebuilt as an **independent research platform** rather than a conventional blog.

The goal is not simply to display articles. The platform brings together:

- independent African research;
- policy and geopolitical analysis;
- researcher identities and professional profiles;
- editorial review and research-integrity controls;
- researcher-to-reader and researcher-to-researcher interaction;
- data and policy intelligence;
- opportunities, fellowships, collaborations, and research calls;
- publication analytics and research amplification;
- secure manuscript handling and traceable editorial activity.

For me, AGP also represents the intersection of **research, policy analysis, product thinking, and software engineering**. Building the platform allows the research itself to grow while also documenting my development journey through a production-oriented full-stack application.

---

## Product Philosophy

AGP is built around one idea: **African research should be discoverable, credible, professionally presented, and connected to the people producing it.**

The platform separates responsibilities rather than treating every account as the same type of user.

### Public / Guest Experience

Visitors can explore public research, researchers, policy intelligence, opportunities, Data Lab resources, legal pages, and the Trust Centre without an account.

### Reader Experience

Readers receive a private workspace designed for consuming and engaging with research rather than publishing it.

Reader features include:

- saved research;
- followed researchers;
- notifications;
- messaging;
- opportunity and collaboration inquiries;
- access to research rooms where permitted;
- private account settings.

### Researcher Experience

Researchers receive a professional workspace and public research identity.

Researcher features include:

- public researcher profile;
- professional headline and biography;
- expertise and research interests;
- tools and technical stack;
- languages;
- ORCID, website, GitHub, LinkedIn, Google Scholar, and ResearchGate links;
- selectable Featured Works;
- research submission;
- publication workflow;
- readership analytics;
- research amplification;
- internal messaging;
- collaboration preferences.

### Editorial Experience

Editorial operations are deliberately **not public-facing**.

The editorial interface is restricted because manuscript evaluation, source checking, conflict-of-interest declarations, revision decisions, and approval actions should not become a public popularity contest or an avenue for pressure, prejudice, manipulation, or fraudulent interference.

Public users can see AGP's editorial standards and research-integrity policies, while the operational editorial workspace remains role-restricted.

Editorial personnel are expected to use **individual provisioned accounts** rather than shared credentials. Each authorised editorial account has its own identity, password, TOTP authenticator setup, recovery codes, and auditable activity.

This separation is intended to protect:

- editorial independence;
- researcher confidentiality;
- manuscript integrity;
- conflict-of-interest controls;
- accountability;
- auditability of review decisions.

### Super Admin Experience

`super_admin` is the highest application-level role. It has a dedicated protected control centre at `/system` for platform administration.

The current Super Admin workflows include:

- platform overview metrics;
- Users & Roles management;
- role changes for existing accounts;
- account deactivate/reactivate controls;
- Opportunities management;
- Policy Tracker management;
- Data Lab management;
- contextual creation flows for Opportunity, Policy, and Dataset records;
- edit, publish/unpublish, close/reopen where applicable, and delete controls for managed content;
- access to protected editorial/content-management functions.

User accounts are **deactivated/reactivated rather than hard-deleted** from the Super Admin workflow so that authorship, Trust Vault records, publication attribution, messaging relationships, and editorial audit history are not casually destroyed.

Additional safeguards prevent a logged-in Super Admin from accidentally removing their own Super Admin role or deactivating the only remaining active Super Admin account.

Even high-privilege roles are intended to operate through explicit, traceable workflows rather than silently bypassing research-integrity controls.

---

## Role Model

```text
reader
researcher
contributor
reviewer
editor
senior_editor
managing_editor
super_admin
```

Current workspace model:

| Role | Primary workspace |
|---|---|
| Reader | Reader Workspace |
| Researcher | Researcher Portal |
| Contributor | Researcher/author workflow where authorised |
| Reviewer | Editorial Review Desk |
| Editor | Editorial Review Desk + Content Studio |
| Senior Editor | Editorial Review Desk + Content Studio |
| Managing Editor | Editorial Review Desk + Content Studio |
| Super Admin | Super Admin Control Centre + authorised editorial/content tools |

Editorial roles share parts of the Editorial Desk while remaining distinct account identities. Role-specific workflow authority should remain explicit and auditable as AGP governance matures.

---

## Design System

AGP is intentionally designed to feel closer to a **research institute, policy publication, or editorial intelligence platform** than to a conventional social network or personal blog.

### Typography

- **Manrope** — headings, navigation, metrics, labels, and interface hierarchy;
- **DM Sans** — body copy, research abstracts, long-form text, and reading-heavy sections.

### Colour System

- **Deep Forest** `#071c16` — authority, stability, institutional depth;
- **AGP Gold** `#c9a227` — identity and emphasis;
- **Lime Accent** `#d5ff62` — interaction and active states;
- **Paper** `#f5f3ec` — research-document background;
- **Ink** `#091711` — high-contrast reading text.

The interface separates:

- public discovery;
- reader activity;
- researcher publishing;
- editorial review;
- system administration.

Responsive layouts target phones, tablets, laptops, and desktop displays.

---

## Core Platform Areas

### Research

Public research discovery and publication pages with metadata, sources, author information, downloadable manuscripts where permitted, version context, and research-integrity information.

### Researchers

A public researcher directory with professional profiles, expertise, featured work, collaboration preferences, and direct AGP messaging for registered users.

### Africa Knowledge Layer

Africa-focused navigation and country-oriented research discovery.

### Opportunities Radar

Curated opportunities including fellowships, research calls, collaborations, grants, internships, scholarships, conferences, and related professional opportunities.

### Data Lab

A curated space for datasets and data resources relevant to African research and policy analysis.

### Policy Tracker

Structured policy records with official sources and AGP analysis.

### Research Rooms

Collaborative spaces for research discussions, invited participation, and shared resources.

### Trust Centre / Research Trust Vault

AGP's research-integrity layer for manuscript fingerprints, submission records, controlled manuscript access, confidentiality acceptance, conflict declarations, and verifiable research-trust records.

### Research Amplification

Tools for tracking and distributing published work through canonical links, referrals, institutional announcements, and publication-sharing workflows.

### Editorial Content Studio

A protected content-management interface for authorised editorial/system roles to create curated:

- datasets;
- policy records;
- opportunities.

When opened contextually from the Super Admin Control Centre, the Content Studio can open directly on the requested Dataset, Policy, or Opportunity form.

---

## Research Publication Workflow

```text
Researcher creates draft
        ↓
Researcher uploads manuscript / completes submission data
        ↓
Researcher submits
        ↓
Submission is sealed / recorded in the trust workflow
        ↓
Desk review
        ↓
Editorial review
        ↓
Revision request (when required)
        ↓
Source / integrity checks
        ↓
Approval
        ↓
Scheduling
        ↓
Publication
        ↓
Public discovery + analytics + amplification
```

Drafts can be deleted by their owner while they remain eligible drafts. Once a submission is sealed into the trust workflow, its research-integrity record is intentionally protected from casual destructive deletion.

Editorial actions are designed to remain traceable rather than invisible.

---

## Authentication & Access Model

### Reader / Researcher

- separate Reader and Researcher registration flows;
- email verification with OTP;
- password-based sign-in followed by email OTP;
- password recovery flow;
- secure cookie-based sessions.

### Editorial / Super Admin

Editorial accounts are **not publicly registered**.

Authorised accounts are provisioned separately and use:

- individual credentials;
- password authentication;
- TOTP-based MFA;
- recovery codes;
- protected editorial login flow;
- audited role identity.

On first editorial login, the account completes authenticator setup. Each editorial professional should use their own authenticator rather than sharing another person's MFA device or account.

A dedicated AGP mobile application is not required for editorial access. The dashboard is web-based; the authenticator application on the editor's phone supplies the TOTP code.

---

## Security & Research Integrity

AGP is designed around stronger controls than a conventional publishing blog.

Important protections include:

- email verification;
- login OTP challenges;
- editorial TOTP MFA;
- recovery codes;
- role-based access control;
- protected Super Admin routes;
- private manuscript storage;
- immutable research submission snapshots;
- SHA-256 manuscript fingerprints;
- confidentiality acknowledgement;
- conflict-of-interest declarations;
- controlled editorial assignment;
- research-access history;
- public certificate verification without exposing private manuscripts;
- secure cookies;
- production HTTPS configuration;
- production security headers and origin protections;
- restricted editorial and system interfaces;
- safeguards against removing the last active Super Admin.

AGP does not claim to be immune to attack. The security model is designed to reduce risk, preserve accountability, and make sensitive operations explicit and auditable.

The governing principle is simple: **trust should be demonstrated through system design, not merely claimed in a policy page.**

See `SECURITY.md` for repository security guidance.

---

## Technology Stack

<div align="center">

![React](https://img.shields.io/badge/React-18-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E?style=flat-square)
![Netlify](https://img.shields.io/badge/Netlify-Frontend-00C7B7?style=flat-square&logo=netlify&logoColor=white)
![Render](https://img.shields.io/badge/Render-API-000000?style=flat-square&logo=render&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Private%20Storage-3FCF8E?style=flat-square&logo=supabase&logoColor=white)
![Brevo](https://img.shields.io/badge/Brevo-Transactional%20Email-0B996E?style=flat-square)
![GitHub](https://img.shields.io/badge/GitHub-Version%20Control-181717?style=flat-square&logo=github&logoColor=white)

</div>

### Frontend

- React 18
- TypeScript
- Vite
- React Router
- Lucide React
- responsive CSS design system

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy 2
- Pydantic 2
- Alembic
- Psycopg 3
- session/authentication utilities
- Argon2 password hashing
- multipart upload support
- Boto3-compatible storage adapter

### Data & Infrastructure

- **Neon PostgreSQL** — primary relational database
- **Supabase Storage** — private S3-compatible manuscript/object storage
- **Render** — FastAPI production backend
- **Netlify** — React/Vite production frontend
- **Brevo HTTPS API** — transactional OTP and system email delivery
- **GitHub** — source control and deployment source

---

## Production Architecture

```text
                    ┌─────────────────────────┐
                    │      Netlify CDN        │
                    │ React + TypeScript +    │
                    │          Vite           │
                    └────────────┬────────────┘
                                 │
                          same-origin /api
                                 │
                    ┌────────────▼────────────┐
                    │      Render API         │
                    │ FastAPI + SQLAlchemy    │
                    └───────┬─────────┬───────┘
                            │         │
                 ┌──────────▼───┐   ┌─▼─────────────────┐
                 │ Neon         │   │ Supabase Storage  │
                 │ PostgreSQL   │   │ Private objects   │
                 └──────────────┘   └───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Brevo HTTPS API│
                    │ OTP / Email    │
                    └────────────────┘
```

The frontend and backend remain intentionally decoupled so the product is not permanently tied to one infrastructure provider.

---

## Repository Structure

```text
Africa-Global-Power-Platform/
├── backend/
│   ├── alembic/
│   └── app/
│       ├── api/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── scripts/
├── frontend/
│   └── src/
│       ├── components/
│       ├── lib/
│       └── pages/
├── docs/
│   ├── assets/
│   └── LAUNCH-VALIDATION.md
├── SECURITY.md
├── netlify.toml
└── README.md
```

---

## Running Locally

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the environment, install dependencies, configure `.env`, then run:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend health endpoint:

```text
http://localhost:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend development URL:

```text
http://localhost:5173
```

---

## Environment & Secret Handling

Secrets must never be committed to the repository.

Production configuration includes areas such as:

```text
DATABASE_URL
SECRET_KEY
MFA_SECRET_KEY
TRUST_LOG_SECRET
CORS_ORIGINS
PUBLIC_SITE_URL
BREVO_API_KEY
EMAIL_FROM
STORAGE_S3_ENDPOINT_URL
STORAGE_S3_BUCKET
STORAGE_S3_ACCESS_KEY_ID
STORAGE_S3_SECRET_ACCESS_KEY
```

Use `.env.example` only for safe configuration examples. Never place real production credentials in README files, issues, screenshots, logs, or commits.

---

## Editorial Account Provisioning

Editorial and Super Admin accounts are created separately from public registration.

From the backend environment:

```bash
python -m app.scripts.create_editor
```

Supported provisioned roles include:

```text
reviewer
editor
senior_editor
managing_editor
super_admin
```

Each professional should receive their **own account**. Shared editorial or Super Admin credentials are not an acceptable operating model.

The first editorial login completes MFA setup. The editor can scan the QR code with a compatible TOTP authenticator or use the manual setup key when configuring MFA on the same phone being used for the browser session.

Recovery codes should be stored privately and offline where practical.

---

## Super Admin Control Centre

Protected route:

```text
/system
```

The route is restricted to `super_admin`.

Current administrative areas:

```text
Overview
Users & Roles
Opportunities
Policies
Data Lab
```

The content tabs are contextual: creation controls appear inside the relevant section rather than as a permanently displayed global action panel.

### Users & Roles

The Super Admin can:

- review registered accounts;
- change application roles;
- deactivate an account;
- reactivate an account.

AGP intentionally avoids routine hard deletion from this interface because account deletion can damage authorship relationships, Trust Vault records, publication history, messages, and auditability.

### Opportunities

The Super Admin can:

- create an opportunity through the contextual Content Studio flow;
- edit an existing opportunity;
- publish/unpublish;
- mark closed/reopen;
- delete an opportunity.

### Policies

The Super Admin can:

- create a Policy Tracker record;
- edit;
- publish/unpublish;
- delete.

### Data Lab

The Super Admin can:

- create a dataset record;
- edit;
- publish/unpublish;
- delete.

Administrative data-load errors are surfaced in the interface rather than silently rendering an empty section.

---

## User Navigation Guide

A downloadable **AGP User Guide** is available from the application's **Help & Guide** area.

It covers:

- choosing the correct Reader or Researcher account;
- email verification and sign-in;
- Reader workspace navigation;
- saving research and following researchers;
- messaging researchers;
- Researcher profile setup;
- submitting research;
- Trust Vault and publication workflow;
- notifications;
- research rooms;
- opportunities;
- privacy, editorial policy, and research-integrity expectations.

The repository also includes `docs/LAUNCH-VALIDATION.md`, which is the operational checklist for final pre-launch verification.

---

## Current Implementation Status

The source code currently contains implementations for:

- public research discovery;
- distinct Reader and Researcher registration;
- OTP email verification;
- OTP sign-in security;
- researcher public profiles;
- Reader workspace;
- saved research;
- researcher following;
- notifications;
- internal messaging;
- research drafts and submissions;
- researcher-owned draft deletion where permitted;
- abstract readiness validation before submission;
- private manuscript upload/storage;
- editorial workflow;
- revision workflow;
- Trust Vault;
- research amplification;
- Data Lab;
- Policy Tracker;
- Opportunities;
- Research Rooms;
- Editorial Content Studio;
- Super Admin Control Centre;
- system user/role administration;
- responsive mobile, tablet, and desktop layouts.

### Launch Freeze

The product is now intentionally **feature-frozen for launch**.

No new module or discretionary redesign should be added before release. Work before launch should be limited to:

- deployment verification;
- production smoke testing;
- documentation;
- correcting confirmed launch-blocking defects.

Post-launch improvements should be prioritised from real user/editor feedback and operational evidence rather than extending the pre-launch scope indefinitely.

---

## Final Pre-Launch Verification

Use `docs/LAUNCH-VALIDATION.md` as the source of truth. The minimum production checks include:

- homepage and primary navigation;
- Reader/Researcher registration and OTP verification;
- login and session persistence;
- researcher draft creation and deletion;
- abstract submission gate;
- PDF/DOCX manuscript upload;
- editorial login and TOTP MFA;
- editorial queue and workflow transitions;
- revision request and replacement manuscript workflow;
- approval/publication path;
- public article visibility;
- reader/researcher/editorial/Super Admin role isolation;
- Super Admin Users & Roles controls;
- Super Admin Opportunity/Policy/Data Lab create and management flows;
- Trust Vault access/history behavior;
- logout/session behavior;
- responsive/mobile checks;
- error handling;
- contact form;
- production security headers where practical.

If these checks pass on the deployed release, the launch candidate can proceed without further feature development.

---

## Live Platform

**Africa & Global Power:** https://africaglobalpower.netlify.app/

**Production API:** https://africa-global-power-api.onrender.com/

The backend root route may intentionally return `404`; the production health endpoint is `/health`. API documentation routes are disabled in production.

---

<div align="center">

**Africa & Global Power — Research Africa. Understand Power.**

Built as an independent African research platform and as a practical full-stack software engineering project.

</div>
