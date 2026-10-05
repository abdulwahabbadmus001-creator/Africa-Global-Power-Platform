from html import escape
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import EDITOR_ROLES, get_current_user, get_db
from app.core.config import settings
from app.models.publication import Publication, PublicationStatus
from app.models.trust import (
    ManuscriptFile,
    TrustAccessEvent,
    TrustConfidentialityAcceptance,
    TrustConflictDeclaration,
    TrustSnapshot,
)
from app.models.user import User
from app.schemas.publication import PublicationOut
from app.schemas.trust import (
    ConflictDeclarationRequest,
    EditorTrustState,
    ManuscriptFileOut,
    PublicCertificateVerification,
    ReviewPackageOut,
    TrustAccessEventOut,
    TrustOverviewOut,
    TrustSnapshotOut,
)
from app.services.storage import get_private_object
from app.services.trust import (
    assert_editor_can_access,
    editor_access_state,
    record_trust_event,
    store_manuscript,
)


router = APIRouter()


def _publication(db: Session, publication_id: UUID) -> Publication:
    publication = db.scalar(
        select(Publication)
        .options(joinedload(Publication.author))
        .where(Publication.id == publication_id)
    )
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return publication


def _overview(db: Session, publication: Publication, user: User) -> TrustOverviewOut:
    files = list(
        db.scalars(
            select(ManuscriptFile)
            .where(ManuscriptFile.publication_id == publication.id)
            .order_by(ManuscriptFile.version_number.desc())
        ).all()
    )
    snapshots = list(
        db.scalars(
            select(TrustSnapshot)
            .where(TrustSnapshot.publication_id == publication.id)
            .order_by(TrustSnapshot.submission_sequence.desc())
        ).all()
    )
    state = None
    if user.role in EDITOR_ROLES:
        state = EditorTrustState(**editor_access_state(db, publication=publication, user=user))
    return TrustOverviewOut(
        publication_id=publication.id,
        files=files,
        snapshots=snapshots,
        latest_snapshot=snapshots[0] if snapshots else None,
        editor_state=state,
    )


@router.get("/publications/{publication_id}/overview", response_model=TrustOverviewOut)
def trust_overview(
    publication_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    if publication.author_id != user.id and user.role not in EDITOR_ROLES:
        raise HTTPException(status_code=403, detail="Not allowed")
    return _overview(db, publication, user)


@router.post("/publications/{publication_id}/manuscript", response_model=ManuscriptFileOut, status_code=201)
async def upload_manuscript(
    publication_id: UUID,
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    if publication.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can upload manuscript versions.")
    if publication.status not in {PublicationStatus.draft, PublicationStatus.revision_requested}:
        raise HTTPException(status_code=409, detail="Manuscript uploads are locked during editorial review.")

    data = await file.read()
    manuscript = store_manuscript(
        db,
        publication=publication,
        author=user,
        filename=file.filename or "manuscript",
        content_type=file.content_type,
        data=data,
    )
    db.commit()
    db.refresh(manuscript)
    return manuscript


@router.get("/manuscripts/{file_id}/download")
def download_private_manuscript(
    file_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    manuscript = db.get(ManuscriptFile, file_id)
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    publication = _publication(db, manuscript.publication_id)

    if publication.author_id != user.id:
        assert_editor_can_access(db, publication=publication, user=user)

    try:
        data = get_private_object(manuscript.storage_key, manuscript.storage_backend)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Stored manuscript object is unavailable")

    record_trust_event(
        db,
        publication_id=publication.id,
        actor=user,
        action="manuscript_downloaded",
        object_type="manuscript_file",
        object_id=manuscript.id,
        details={"version_number": manuscript.version_number},
    )
    db.commit()

    safe_name = manuscript.original_filename.replace('"', "")
    return Response(
        content=data,
        media_type=manuscript.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/publications/{publication_id}/confidentiality", response_model=EditorTrustState)
def accept_confidentiality(
    publication_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    if user.role not in EDITOR_ROLES or publication.assigned_editor_id != user.id:
        raise HTTPException(status_code=403, detail="This submission must be assigned to you first.")

    existing = db.scalar(
        select(TrustConfidentialityAcceptance).where(
            TrustConfidentialityAcceptance.publication_id == publication.id,
            TrustConfidentialityAcceptance.user_id == user.id,
        )
    )
    if not existing:
        db.add(
            TrustConfidentialityAcceptance(
                publication_id=publication.id,
                user_id=user.id,
                statement_version=settings.trust_statement_version,
            )
        )
        record_trust_event(
            db,
            publication_id=publication.id,
            actor=user,
            action="confidentiality_accepted",
            details={"statement_version": settings.trust_statement_version},
        )
        db.commit()

    return EditorTrustState(**editor_access_state(db, publication=publication, user=user))


@router.post("/publications/{publication_id}/conflict", response_model=EditorTrustState)
def declare_conflict(
    publication_id: UUID,
    payload: ConflictDeclarationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    if user.role not in EDITOR_ROLES or publication.assigned_editor_id != user.id:
        raise HTTPException(status_code=403, detail="This submission must be assigned to you first.")

    declaration = db.scalar(
        select(TrustConflictDeclaration).where(
            TrustConflictDeclaration.publication_id == publication.id,
            TrustConflictDeclaration.user_id == user.id,
        )
    )
    if declaration:
        declaration.decision = payload.decision
        declaration.note = payload.note
    else:
        declaration = TrustConflictDeclaration(
            publication_id=publication.id,
            user_id=user.id,
            decision=payload.decision,
            note=payload.note,
        )
        db.add(declaration)

    if payload.decision == "recuse":
        publication.assigned_editor_id = None

    record_trust_event(
        db,
        publication_id=publication.id,
        actor=user,
        action="conflict_declared",
        details={"decision": payload.decision, "note": payload.note},
    )
    db.commit()
    return EditorTrustState(**editor_access_state(db, publication=publication, user=user))


@router.get("/editorial/publications/{publication_id}/review-package", response_model=ReviewPackageOut)
def review_package(
    publication_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    assert_editor_can_access(db, publication=publication, user=user)
    files = list(
        db.scalars(
            select(ManuscriptFile)
            .where(ManuscriptFile.publication_id == publication.id)
            .order_by(ManuscriptFile.version_number.desc())
        ).all()
    )
    record_trust_event(
        db,
        publication_id=publication.id,
        actor=user,
        action="confidential_review_opened",
        details={"file_count": len(files)},
    )
    db.commit()
    return ReviewPackageOut(publication=PublicationOut.model_validate(publication), files=files)


@router.get("/publications/{publication_id}/access-history", response_model=list[TrustAccessEventOut])
def access_history(
    publication_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    publication = _publication(db, publication_id)
    if publication.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can view this access history.")

    events = list(
        db.scalars(
            select(TrustAccessEvent)
            .where(TrustAccessEvent.publication_id == publication.id)
            .order_by(TrustAccessEvent.created_at.desc())
        ).all()
    )
    user_ids = {event.actor_user_id for event in events if event.actor_user_id}
    users = {}
    if user_ids:
        from app.models.user import User as UserModel
        users = {u.id: u for u in db.scalars(select(UserModel).where(UserModel.id.in_(user_ids))).all()}

    return [
        TrustAccessEventOut(
            id=event.id,
            actor_name=(
                f"{users[event.actor_user_id].first_name} {users[event.actor_user_id].last_name}"
                if event.actor_user_id in users
                else "AGP System"
            ),
            actor_role=event.actor_role,
            action=event.action,
            object_type=event.object_type,
            details=event.details,
            event_hash=event.event_hash,
            created_at=event.created_at,
        )
        for event in events
    ]


@router.get("/certificates/{snapshot_id}", response_model=TrustSnapshotOut)
def certificate(
    snapshot_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    snapshot = db.get(TrustSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Certificate not found")
    publication = _publication(db, snapshot.publication_id)
    if publication.author_id != user.id and user.role not in EDITOR_ROLES:
        raise HTTPException(status_code=403, detail="Not allowed")
    return snapshot


@router.get("/certificates/{snapshot_id}/print", response_class=HTMLResponse)
def printable_certificate(
    snapshot_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    snapshot = db.get(TrustSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Certificate not found")
    publication = _publication(db, snapshot.publication_id)
    if publication.author_id != user.id and user.role not in EDITOR_ROLES:
        raise HTTPException(status_code=403, detail="Not allowed")

    title = escape(publication.title)
    submission_id = escape(snapshot.submission_id)
    fingerprint = escape(snapshot.fingerprint_sha256)
    timestamp = escape(snapshot.submitted_at.isoformat())
    author = escape(f"{publication.author.first_name} {publication.author.last_name}" if publication.author else "AGP Researcher")

    return HTMLResponse(
        f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>AGP Submission Certificate</title>
<style>
body{{font-family:Georgia,serif;background:#f5f1e7;color:#171a17;padding:48px}}
.certificate{{max-width:900px;margin:auto;background:white;border:2px solid #18251d;padding:54px}}
h1{{font-size:36px;margin:8px 0 28px}} .label{{font:700 12px Arial;letter-spacing:.12em;color:#687269}}
.value{{font-size:18px;margin:5px 0 22px}} code{{font-size:13px;word-break:break-all}}
.note{{margin-top:36px;border-top:1px solid #ddd;padding-top:22px;color:#596159}}
@media print{{body{{background:white;padding:0}}.certificate{{border:1px solid #111}}}}
</style>
</head>
<body>
<div class="certificate">
<div class="label">AFRICA &amp; GLOBAL POWER — RESEARCH TRUST VAULT</div>
<h1>Submission Certificate</h1>
<div class="label">SUBMISSION ID</div><div class="value">{submission_id}</div>
<div class="label">RESEARCH</div><div class="value">{title}</div>
<div class="label">AUTHOR</div><div class="value">{author}</div>
<div class="label">SEALED AT</div><div class="value">{timestamp}</div>
<div class="label">SHA-256 FINGERPRINT</div><div class="value"><code>{fingerprint}</code></div>
<div class="label">SUBMISSION SEQUENCE</div><div class="value">{snapshot.submission_sequence}</div>
<div class="note">This certificate records the immutable metadata fingerprint captured by the AGP Research Trust Vault at submission. Use your browser's Print command to save this certificate as PDF.</div>
</div>
</body>
</html>
"""
    )


@router.get("/verify/{submission_id}", response_model=PublicCertificateVerification)
def verify_certificate(submission_id: str, db: Session = Depends(get_db)):
    snapshot = db.scalar(select(TrustSnapshot).where(TrustSnapshot.submission_id == submission_id))
    if not snapshot:
        raise HTTPException(status_code=404, detail="Submission certificate not found")
    publication = db.get(Publication, snapshot.publication_id)
    return PublicCertificateVerification(
        submission_id=snapshot.submission_id,
        valid=True,
        submitted_at=snapshot.submitted_at,
        fingerprint_sha256=snapshot.fingerprint_sha256,
        publication_status=publication.status.value if publication else "unknown",
        published_title=(publication.title if publication and publication.status == PublicationStatus.published else None),
    )
