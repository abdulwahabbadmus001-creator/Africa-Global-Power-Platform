import hashlib
import hmac
import json
import uuid
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.publication import Publication
from app.models.trust import (
    ManuscriptFile,
    TrustAccessEvent,
    TrustConfidentialityAcceptance,
    TrustConflictDeclaration,
    TrustSnapshot,
)
from app.models.user import User, UserRole
from app.services.storage import put_private_object


EDITORIAL_ROLES = {
    UserRole.reviewer,
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
}

PDF_MIME = "application/pdf"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
ALLOWED_EXTENSIONS = {".pdf": PDF_MIME, ".docx": DOCX_MIME}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def validate_manuscript(filename: str, content_type: str | None, data: bytes) -> tuple[str, str]:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX manuscripts are accepted.",
        )

    max_bytes = settings.max_manuscript_mb * 1024 * 1024
    if not data:
        raise HTTPException(status_code=422, detail="The manuscript file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Manuscript exceeds the {settings.max_manuscript_mb} MB upload limit.",
        )

    expected_mime = ALLOWED_EXTENSIONS[suffix]

    if suffix == ".pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF.")

    if suffix == ".docx":
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                names = set(archive.namelist())
                if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                    raise ValueError("Missing DOCX structure")
        except (zipfile.BadZipFile, ValueError):
            raise HTTPException(status_code=415, detail="The uploaded file is not a valid DOCX.")

    if content_type and content_type not in {
        expected_mime,
        "application/octet-stream",
        "application/zip",
    }:
        raise HTTPException(status_code=415, detail="File type does not match the manuscript extension.")

    return suffix, expected_mime


def record_trust_event(
    db: Session,
    *,
    publication_id,
    actor: User | None,
    action: str,
    object_type: str | None = None,
    object_id=None,
    details: dict | None = None,
) -> TrustAccessEvent:
    last_event = db.scalar(
        select(TrustAccessEvent)
        .where(TrustAccessEvent.publication_id == publication_id)
        .order_by(TrustAccessEvent.created_at.desc(), TrustAccessEvent.id.desc())
        .limit(1)
    )

    created_at = utcnow()
    previous_hash = last_event.event_hash if last_event else None
    payload = {
        "publication_id": str(publication_id),
        "actor_user_id": str(actor.id) if actor else None,
        "actor_role": actor.role.value if actor else None,
        "action": action,
        "object_type": object_type,
        "object_id": str(object_id) if object_id else None,
        "details": details or {},
        "previous_hash": previous_hash,
        "created_at": created_at.isoformat(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    event_hash = hmac.new(
        settings.trust_log_secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    event = TrustAccessEvent(
        publication_id=publication_id,
        actor_user_id=actor.id if actor else None,
        actor_role=actor.role.value if actor else None,
        action=action,
        object_type=object_type,
        object_id=object_id,
        details=details or {},
        previous_hash=previous_hash,
        event_hash=event_hash,
        created_at=created_at,
    )
    db.add(event)
    return event


def store_manuscript(
    db: Session,
    *,
    publication: Publication,
    author: User,
    filename: str,
    content_type: str | None,
    data: bytes,
) -> ManuscriptFile:
    suffix, mime_type = validate_manuscript(filename, content_type, data)

    latest_version = db.scalar(
        select(func.max(ManuscriptFile.version_number)).where(
            ManuscriptFile.publication_id == publication.id
        )
    )
    version_number = int(latest_version or 0) + 1
    digest = hashlib.sha256(data).hexdigest()
    key = f"manuscripts/{publication.id}/{uuid.uuid4().hex}{suffix}"
    backend = put_private_object(key, data, mime_type)

    manuscript = ManuscriptFile(
        publication_id=publication.id,
        author_id=author.id,
        version_number=version_number,
        original_filename=Path(filename).name[:500],
        mime_type=mime_type,
        size_bytes=len(data),
        sha256=digest,
        storage_backend=backend,
        storage_key=key,
    )
    db.add(manuscript)
    db.flush()

    record_trust_event(
        db,
        publication_id=publication.id,
        actor=author,
        action="manuscript_uploaded",
        object_type="manuscript_file",
        object_id=manuscript.id,
        details={
            "version_number": version_number,
            "filename": manuscript.original_filename,
            "sha256": digest,
            "size_bytes": len(data),
        },
    )
    return manuscript


def _latest_manuscript(db: Session, publication_id) -> ManuscriptFile | None:
    return db.scalar(
        select(ManuscriptFile)
        .where(ManuscriptFile.publication_id == publication_id)
        .order_by(ManuscriptFile.version_number.desc())
        .limit(1)
    )


def seal_submission(db: Session, *, publication: Publication, author: User) -> TrustSnapshot:
    manuscript = _latest_manuscript(db, publication.id)

    if publication.submission_method in {"upload", "both"} and manuscript is None:
        raise HTTPException(
            status_code=422,
            detail="Upload a PDF or DOCX manuscript before submitting this research.",
        )

    if publication.submission_method == "form" and len(publication.body.strip()) < 100:
        raise HTTPException(
            status_code=422,
            detail="The research body must contain at least 100 characters before submission.",
        )

    latest_sequence = db.scalar(
        select(func.max(TrustSnapshot.submission_sequence)).where(
            TrustSnapshot.publication_id == publication.id
        )
    )
    sequence = int(latest_sequence or 0) + 1
    submission_id = f"AGP-{utcnow().year}-{uuid.uuid4().hex[:10].upper()}"

    snapshot_payload = {
        "submission_id": submission_id,
        "publication_id": str(publication.id),
        "author_id": str(author.id),
        "publication_version": publication.current_version,
        "submission_sequence": sequence,
        "submission_method": publication.submission_method,
        "title": publication.title,
        "abstract": publication.abstract,
        "body": publication.body,
        "publication_type": publication.publication_type,
        "topic": publication.topic,
        "region": publication.region,
        "country": publication.country,
        "keywords": publication.keywords,
        "references": publication.references,
        "methodology": publication.methodology,
        "limitations": publication.limitations,
        "policy_implications": publication.policy_implications,
        "manuscript_sha256": manuscript.sha256 if manuscript else None,
        "manuscript_version": manuscript.version_number if manuscript else None,
    }
    canonical = json.dumps(snapshot_payload, sort_keys=True, separators=(",", ":"))
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    snapshot = TrustSnapshot(
        submission_id=submission_id,
        publication_id=publication.id,
        author_id=author.id,
        manuscript_file_id=manuscript.id if manuscript else None,
        submission_sequence=sequence,
        publication_version=publication.current_version,
        fingerprint_sha256=fingerprint,
        snapshot_payload=snapshot_payload,
        immutable=True,
    )
    db.add(snapshot)
    db.flush()

    if manuscript and sequence == 1:
        manuscript.is_original_submission = True

    record_trust_event(
        db,
        publication_id=publication.id,
        actor=author,
        action="submission_sealed",
        object_type="trust_snapshot",
        object_id=snapshot.id,
        details={
            "submission_id": submission_id,
            "submission_sequence": sequence,
            "fingerprint_sha256": fingerprint,
        },
    )
    return snapshot


def editor_access_state(db: Session, *, publication: Publication, user: User) -> dict:
    confidentiality = db.scalar(
        select(TrustConfidentialityAcceptance).where(
            TrustConfidentialityAcceptance.publication_id == publication.id,
            TrustConfidentialityAcceptance.user_id == user.id,
        )
    )
    conflict = db.scalar(
        select(TrustConflictDeclaration).where(
            TrustConflictDeclaration.publication_id == publication.id,
            TrustConflictDeclaration.user_id == user.id,
        )
    )
    return {
        "assigned_to_me": publication.assigned_editor_id == user.id,
        "confidentiality_accepted": confidentiality is not None,
        "conflict_decision": conflict.decision if conflict else None,
        "can_access_manuscript": (
            publication.assigned_editor_id == user.id
            and confidentiality is not None
            and conflict is not None
            and conflict.decision == "no_conflict"
        ),
    }


def assert_editor_can_access(db: Session, *, publication: Publication, user: User) -> None:
    if user.role not in EDITORIAL_ROLES:
        raise HTTPException(status_code=403, detail="Editorial access required.")
    state = editor_access_state(db, publication=publication, user=user)
    if not state["assigned_to_me"]:
        raise HTTPException(status_code=403, detail="This manuscript is not assigned to you.")
    if not state["confidentiality_accepted"]:
        raise HTTPException(status_code=403, detail="Accept the confidentiality and non-use declaration first.")
    if state["conflict_decision"] != "no_conflict":
        raise HTTPException(status_code=403, detail="A no-conflict declaration is required before manuscript access.")
