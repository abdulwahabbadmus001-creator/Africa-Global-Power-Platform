# AGP Platform Architecture

## Product surfaces

### Public AGP

- Research discovery
- Publication pages
- Researcher discovery
- Public researcher profiles
- Africa knowledge architecture
- Opportunities architecture

### Researcher Portal

- Account/profile
- Private drafts
- Publication versioning
- Editorial submission
- Publication-level analytics
- Researcher messaging

### AGP Editorial

- Submission queue
- Desk review
- Editorial review
- Source-check stage
- Revision requests
- Approval/scheduling/publication
- Manuscript context: methodology, limitations, policy implications, references
- Audit history of editorial transitions

### Restricted System Administration

- User accounts
- Roles
- Account status

This technical area is deliberately separate from editorial operations.

## Core backend entities

```text
User
 |
 +---- Publication ---- PublicationVersion
 |          |
 |          +---------- EditorialAction
 |          |
 |          +---------- AnalyticsEvent
 |
 +---- Message (sender/recipient)
```

## Publication workflow

```text
DRAFT
  |
  v
SUBMITTED
  |
  v
DESK_REVIEW ------> REJECTED
  |                     ^
  v                     |
EDITORIAL_REVIEW -------+
  |        |
  |        +------> REVISION_REQUESTED -> author edits -> resubmission
  v
SOURCE_CHECK
  |        |
  |        +------> REVISION_REQUESTED
  v
APPROVED
  |      |
  |      +------> PUBLISHED
  v
SCHEDULED
  |
  v
PUBLISHED
```

## Hosting model

AGP is designed to avoid infrastructure lock-in.

```text
Browser
  |
  v
React/TypeScript frontend
(Netlify or another static/web host)
  |
  | HTTPS REST API
  v
FastAPI
(Python-capable host)
  |
  v
PostgreSQL
```

Later services can be added behind the same API for object storage, transactional email, research search, DOI verification, policy ingestion, background tasks and full-text indexing.
