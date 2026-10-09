from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from slugify import slugify
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.publication import Publication, PublicationStatus, PublicationVersion
from app.models.trust import ManuscriptFile
from app.models.user import User, UserRole
from app.schemas.publication import PublicationCreate, PublicationOut, PublicationUpdate
from app.services.storage import get_private_object
from app.services.trust import seal_submission


router = APIRouter()
AUTHOR_ROLES = {
    UserRole.researcher,
    UserRole.contributor,
}


def unique_slug(db: Session, title: str, publication_id: UUID | None = None) -> str:
    base = slugify(title)[:400] or "research"
    candidate = base
    n = 2
    while True:
        stmt = select(Publication).where(Publication.slug == candidate)
        if publication_id:
            stmt = stmt.where(Publication.id != publication_id)
        if not db.scalar(stmt):
            return candidate
        candidate = f"{base}-{n}"
        n += 1


@router.get("", response_model=list[PublicationOut])
def public_list(
    q: str | None = Query(default=None),
    topic: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(Publication)
        .options(joinedload(Publication.author))
        .where(Publication.status == PublicationStatus.published)
        .order_by(Publication.published_at.desc())
    )
    if topic:
        stmt = stmt.where(Publication.topic == topic)
    if q:
        term = f"%{q}%"
        stmt = stmt.where(
            or_(
                Publication.title.ilike(term),
                Publication.abstract.ilike(term),
                Publication.body.ilike(term),
            )
        )
    return list(db.scalars(stmt.limit(100)).unique().all())


@router.get("/mine", response_model=list[PublicationOut])
def mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(Publication)
        .options(joinedload(Publication.author))
        .where(Publication.author_id == user.id)
        .order_by(Publication.updated_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


@router.get("/author/{author_id}", response_model=list[PublicationOut])
def by_author(author_id: UUID, db: Session = Depends(get_db)):
    stmt = (
        select(Publication)
        .options(joinedload(Publication.author))
        .where(
            Publication.author_id == author_id,
            Publication.status == PublicationStatus.published,
        )
        .order_by(Publication.published_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


@router.get("/public/{slug}/download")
def public_manuscript_download(slug: str, db: Session = Depends(get_db)):
    publication = db.scalar(
        select(Publication).where(
            Publication.slug == slug,
            Publication.status == PublicationStatus.published,
        )
    )
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    manuscript = db.scalar(
        select(ManuscriptFile)
        .where(
            ManuscriptFile.publication_id == publication.id,
            ManuscriptFile.public_on_publish.is_(True),
        )
        .order_by(ManuscriptFile.version_number.desc())
        .limit(1)
    )
    if not manuscript:
        raise HTTPException(status_code=404, detail="No public manuscript file is attached")

    try:
        data = get_private_object(manuscript.storage_key, manuscript.storage_backend)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Published manuscript object is unavailable")

    safe_name = manuscript.original_filename.replace('"', "")
    return Response(
        content=data,
        media_type=manuscript.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/{slug}", response_model=PublicationOut)
def detail(slug: str, db: Session = Depends(get_db)):
    pub = db.scalar(
        select(Publication)
        .options(joinedload(Publication.author))
        .where(Publication.slug == slug, Publication.status == PublicationStatus.published)
    )
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub


@router.post("", response_model=PublicationOut, status_code=201)
def create(
    payload: PublicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in AUTHOR_ROLES:
        raise HTTPException(status_code=403, detail="Research publishing access required")

    if payload.submission_method in {"form", "both"}:
        if len(payload.abstract.strip()) < 40:
            raise HTTPException(status_code=422, detail="Abstract must contain at least 40 characters.")
        if len(payload.body.strip()) < 100:
            raise HTTPException(status_code=422, detail="Research body must contain at least 100 characters.")

    pub = Publication(
        author_id=user.id,
        slug=unique_slug(db, payload.title),
        **payload.model_dump(),
    )
    db.add(pub)
    db.flush()
    db.add(
        PublicationVersion(
            publication_id=pub.id,
            version_number=1,
            title=pub.title,
            abstract=pub.abstract,
            body=pub.body,
            created_by_id=user.id,
            change_note="Initial draft",
        )
    )
    db.commit()
    db.refresh(pub)
    return pub


@router.patch("/{publication_id}", response_model=PublicationOut)
def update(
    publication_id: UUID,
    payload: PublicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pub = db.get(Publication, publication_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if user.role not in AUTHOR_ROLES or pub.author_id != user.id:
        raise HTTPException(status_code=403, detail="Author access required")
    if pub.author_id == user.id and pub.status not in {
        PublicationStatus.draft,
        PublicationStatus.revision_requested,
    }:
        raise HTTPException(
            status_code=409,
            detail="This research is locked while it is in the editorial workflow",
        )

    data = payload.model_dump(exclude_unset=True)
    change_note = data.pop("change_note", None)
    if "title" in data:
        pub.slug = unique_slug(db, data["title"], pub.id)
    for key, value in data.items():
        setattr(pub, key, value)

    pub.current_version += 1
    db.add(
        PublicationVersion(
            publication_id=pub.id,
            version_number=pub.current_version,
            title=pub.title,
            abstract=pub.abstract,
            body=pub.body,
            created_by_id=user.id,
            change_note=change_note or "Updated draft",
        )
    )
    if pub.status == PublicationStatus.revision_requested:
        pub.status = PublicationStatus.draft
    db.commit()
    db.refresh(pub)
    return pub


@router.post("/{publication_id}/submit", response_model=PublicationOut)
def submit(
    publication_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pub = db.get(Publication, publication_id)
    if (
        user.role not in AUTHOR_ROLES
        or not pub
        or pub.author_id != user.id
    ):
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.status not in {PublicationStatus.draft, PublicationStatus.revision_requested}:
        raise HTTPException(
            status_code=409,
            detail="This publication cannot be submitted from its current state",
        )

    seal_submission(db, publication=pub, author=user)
    pub.status = PublicationStatus.submitted
    pub.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pub)
    return pub
