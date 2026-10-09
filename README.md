<div align="center">

<img src="docs/assets/agp-logo.svg" alt="Africa & Global Power logo" width="720" />

# Africa & Global Power

### Research Africa. Understand Power.

A full-stack African research, policy-intelligence, publishing, collaboration, and knowledge-discovery platform.

[![Live Site](https://img.shields.io/badge/Live-africaglobalpower.netlify.app-071c16?style=for-the-badge&logo=netlify&logoColor=white)](https://africaglobalpower.netlify.app/)

</div>

---

## Why I Built Africa & Global Power

Africa & Global Power began as a research and publication project hosted on **Blogger**. Blogger made it possible to publish quickly, but as my research interests expanded and I progressed further into software development, I began asking a simple question:

> If I am learning to build digital products, why should my research platform remain limited by a publishing tool I do not control?

AGP was therefore rebuilt as an **independent research platform** rather than a conventional blog.

The goal is not simply to display articles. The platform is designed to bring together:

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

The platform therefore separates the experience into distinct layers rather than treating everyone as the same type of user.

### Public / Guest Experience

Visitors can explore public research, researchers, policy intelligence, opportunities, Data Lab resources, legal pages, and the Trust Centre without needing an account.

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

Public users can see AGP's editorial standards and research-integrity policies, but the operational editorial workspace remains role-restricted.

This separation is intended to protect:

- editorial independence;
- researcher confidentiality;
- manuscript integrity;
- conflict-of-interest controls;
- accountability;
- auditability of review decisions.

### Super Admin Experience

`super_admin` is the highest application-level role. It controls system-level user and role administration and can access protected editorial/content-management functions.

However, AGP is intentionally designed so that even high-privilege roles operate through explicit workflows rather than silently bypassing research-integrity controls. Administrative power should remain traceable.

---

## Design System: Why the Interface Looks This Way

AGP is intentionally designed to feel closer to a **research institute, policy publication, or editorial intelligence platform** than to a typical social network or personal blog.

### Typography

The interface uses:

- **Manrope** for headings, navigation, metrics, labels, and strong interface hierarchy;
- **DM Sans** for body copy, research abstracts, long-form text, and reading-heavy sections.

Manrope gives the platform a structured, contemporary institutional identity, while DM Sans remains highly readable for longer research content.

### Colour System

The core interface uses a restrained palette:

- **Deep Forest** `#071c16` — authority, stability, seriousness, institutional depth;
- **AGP Gold** `#c9a227` — identity, African visual heritage, distinction, and emphasis;
- **Lime Accent** `#d5ff62` — interaction, active states, calls to action, and modern digital contrast;
- **Paper** `#f5f3ec` — a softer research-document background instead of stark white;
- **Ink** `#091711` — high-contrast reading text.

The result is intentionally editorial rather than decorative: research is the central visual object.

### Interface Structure

The application uses clear separation between:

- public discovery;
- reader activity;
- researcher publishing;
- editorial review;
- system administration.

This reduces role confusion and keeps sensitive workflows away from public interfaces.

Responsive layouts are designed for phones, tablets, laptops, and desktop displays.

---

## Core Platform Areas

### Research

Public research discovery and publication pages with metadata, sources, author information, downloadable manuscripts where permitted, version context, and research-integrity information.

### Researchers

A public researcher directory with professional profiles, expertise, featured work, collaboration preferences, and direct AGP messaging for registered users.

### Africa Knowledge Layer

Africa-focused navigation and country-oriented research discovery.

### Opportunities Radar

Curated opportunities including fellowships, research calls, collaborations, grants, and related professional opportunities.

### Data Lab

A curated space for useful datasets and data resources relevant to African research and policy analysis.

### Policy Tracker

Structured policy records with official sources and AGP analysis.

### Research Rooms

Collaborative spaces for research discussions, invited participation, and shared resources.

### Trust Centre / Research Trust Vault

AGP's research-integrity layer for manuscript fingerprints, submission records, controlled manuscript access, confidentiality acceptance, conflict declarations, and verifiable research-trust records.

### Research Amplification

Tools for tracking and distributing published work through canonical links, referrals, institutional announcements, and publication-sharing workflows.

### Editorial Content Studio

A protected content-management interface for publishing curated:

- datasets;
- policy records;
- opportunities.

It is accessible only to authorised editorial/system roles.

---

## How Research Moves Through AGP

```text
Researcher creates draft
        ↓
Researcher submits manuscript
        ↓
Submission is sealed / recorded
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

Editorial actions are designed to remain traceable rather than invisible.

---

## Authentication & Access Model

AGP uses separate account and security experiences for different responsibilities.

### Reader / Researcher

- separate Reader and Researcher registration flows;
- email verification with OTP;
- password-based sign-in followed by email OTP;
- password recovery flow;
- secure cookie-based sessions.

### Editorial

Editorial accounts are not publicly registered.

Editorial access is provisioned separately and protected with stronger authentication controls, including TOTP-based MFA and recovery mechanisms.

### Roles

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
- JWT/session utilities
- Argon2 password hashing
- multipart upload support
- Boto3-compatible storage adapter

### Data & Infrastructure

- **Neon PostgreSQL** — primary relational database
- **Supabase Storage** — private S3-compatible manuscript/object storage
- **Render** — FastAPI production backend
- **Netlify** — React/Vite production frontend
- **Brevo API** — transactional OTP and system email delivery
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
│   └── assets/
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

Use `.env.example` only for safe configuration examples.

---

## Security & Research Integrity

AGP is designed around stronger controls than a conventional publishing blog.

Important protections include:

- email verification;
- login OTP challenges;
- editorial MFA;
- role-based access control;
- private manuscript storage;
- immutable research submission snapshots;
- SHA-256 manuscript fingerprints;
- confidentiality acknowledgement;
- conflict-of-interest declarations;
- controlled editorial assignment;
- research-access history;
- public certificate verification without exposing private manuscripts;
- secure cookies;
- production-only HTTPS deployment;
- restricted editorial and system interfaces.

The long-term principle is simple: **trust should be demonstrated through system design, not merely claimed in a policy page.**

---

## Publishing Opportunities as an Authorised Editor / Super Admin

AGP already includes an internal Content Studio for authorised roles.

```text
Editorial / Super Admin
        ↓
Content Studio
        ↓
Opportunity
        ↓
Enter organisation, category, deadline,
summary, application URL and tags
        ↓
Publish
        ↓
Opportunity becomes visible on the
public Opportunities page
```

This keeps public opportunity listings curated rather than allowing arbitrary public submissions to appear automatically.

---

## User Navigation Guide

A downloadable **AGP User Guide** is available from the live application's **Help & Guide** page and footer.

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

The repository also includes `docs/LAUNCH-VALIDATION.md`, a production checklist for the final pre-launch review.

---

## Current Production Status

The platform currently includes production implementations for:

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
- research submissions;
- editorial workflow;
- Trust Vault;
- research amplification;
- Data Lab;
- Policy Tracker;
- Opportunities;
- Research Rooms;
- Editorial Content Studio;
- system role administration;
- responsive mobile, tablet, and desktop layouts.

AGP remains an actively developed research and software project. New modules are added when they serve the core purpose of improving African research discovery, integrity, collaboration, and policy intelligence.

---

## Live Platform

**Africa & Global Power:** https://africaglobalpower.netlify.app/

---

<div align="center">

**Africa & Global Power — Research Africa. Understand Power.**

Built as an independent African research platform and as a practical full-stack software engineering project.

</div>
