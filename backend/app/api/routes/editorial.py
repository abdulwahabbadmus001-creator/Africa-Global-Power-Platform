from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import EDITOR_ROLES, get_db, require_roles
from app.models.editorial import EditorialAction
from app.models.publication import Publication, PublicationStatus
from app.models.trust import ManuscriptFile, TrustSnapshot
from app.models.user import User
from app.schemas.publication import EditorialQueueItem, EditorialTransition, PublicationOut
from app.services.trust import record_trust_event


router = APIRouter()
EDITORIAL_ORDER = {
    PublicationStatus.submitted: {PublicationStatus.desk_review, PublicationStatus.rejected},
    PublicationStatus.desk_review: {
        PublicationStatus.editorial_review,
        PublicationStatus.revision_requested,
        PublicationStatus.rejected,
    },
    PublicationStatus.editorial_review: {
        PublicationStatus.source_check,
        PublicationStatus.revision_requested,
        PublicationStatus.rejected,
    },
    PublicationStatus.source_check: {
        PublicationStatus.approved,
        PublicationStatus.revision_requested,
        PublicationStatus.rejected,
    },
    PublicationStatus.approved: {PublicationStatus.scheduled, PublicationStatus.published},
    PublicationStatus.scheduled: {PublicationStatus.published, PublicationStatus.approved},
    PublicationStatus.revision_requested: {
        PublicationStatus.desk_review,
        PublicationStatus.editorial_review,
    },
}


@router.get("/queue", response_model=list[EditorialQueueItem])
def queue(
    editor: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Publication)
        .options(joinedload(Publication.author))
        .where(
            Publication.status.notin_(
                [PublicationStatus.draft, PublicationStatus.published, PublicationStatus.rejected]
            )
        )
        .order_by(Publication.updated_at.asc())
    )
    publications = list(db.scalars(stmt).unique().all())
    return [EditorialQueueItem.model_validate(p, from_attributes=True) for p in publications]


@router.get("/summary")
def summary(
    editor: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Publication.status, func.count(Publication.id)).group_by(Publication.status)
    ).all()
    counts = {status.value: count for status, count in rows}
    return {
        "counts": counts,
        "total_active": sum(
            value for key, value in counts.items() if key not in {"draft", "published", "rejected"}
        ),
    }


@router.post("/{publication_id}/claim", response_model=EditorialQueueItem)
def claim_submission(
    publication_id: UUID,
    editor: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    pub = db.scalar(
        select(Publication).options(joinedload(Publication.author)).where(Publication.id == publication_id)
    )
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.assigned_editor_id and pub.assigned_editor_id != editor.id:
        raise HTTPException(status_code=409, detail="This submission is already assigned to another editor.")
    if not pub.assigned_editor_id:
        pub.assigned_editor_id = editor.id
        db.add(
            EditorialAction(
                publication_id=pub.id,
                actor_id=editor.id,
                action="submission_claimed",
                from_status=pub.status.value,
                to_status=pub.status.value,
                note="Editor accepted assignment",
            )
        )
        record_trust_event(
            db,
            publication_id=pub.id,
            actor=editor,
            action="editor_assigned",
            details={"editor_id": str(editor.id)},
        )
        db.commit()
        db.refresh(pub)
    return EditorialQueueItem.model_validate(pub, from_attributes=True)


@router.post("/{publication_id}/transition", response_model=PublicationOut)
def transition(
    publication_id: UUID,
    payload: EditorialTransition,
    editor: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    pub = db.get(Publication, publication_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    if pub.assigned_editor_id != editor.id:
        raise HTTPException(status_code=403, detail="Claim this submission before changing editorial status.")

    allowed = EDITORIAL_ORDER.get(pub.status, set())
    if payload.to_status not in allowed:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot move {pub.status.value} to {payload.to_status.value}",
        )

    if payload.to_status in {PublicationStatus.approved, PublicationStatus.scheduled, PublicationStatus.published}:
        snapshot = db.scalar(
            select(TrustSnapshot)
            .where(TrustSnapshot.publication_id == pub.id)
            .order_by(TrustSnapshot.submission_sequence.desc())
            .limit(1)
        )
        if not snapshot:
            raise HTTPException(status_code=409, detail="Trust Vault submission seal is missing.")

    if payload.to_status in {PublicationStatus.scheduled, PublicationStatus.published}:
        if len(pub.abstract.strip()) < 40:
            raise HTTPException(status_code=422, detail="A public abstract is required before publication.")
        manuscript = db.scalar(
            select(ManuscriptFile)
            .where(ManuscriptFile.publication_id == pub.id)
            .order_by(ManuscriptFile.version_number.desc())
            .limit(1)
        )
        if len(pub.body.strip()) < 100 and manuscript is None:
            raise HTTPException(status_code=422, detail="Publication requires either a complete research body or an attached manuscript.")

    old = pub.status
    pub.status = payload.to_status

    if payload.assigned_editor_id and payload.assigned_editor_id != editor.id:
        raise HTTPException(status_code=403, detail="Reassignment is handled through the editorial administration workflow.")

    if payload.to_status == PublicationStatus.scheduled:
        if not payload.scheduled_for:
            raise HTTPException(status_code=422, detail="scheduled_for is required")
        pub.scheduled_for = payload.scheduled_for

    if payload.to_status == PublicationStatus.published:
        pub.published_at = datetime.now(timezone.utc)
        pub.scheduled_for = None

    db.add(
        EditorialAction(
            publication_id=pub.id,
            actor_id=editor.id,
            action="status_transition",
            from_status=old.value,
            to_status=pub.status.value,
            note=payload.note,
        )
    )
    record_trust_event(
        db,
        publication_id=pub.id,
        actor=editor,
        action="editorial_status_changed",
        details={"from": old.value, "to": pub.status.value, "note": payload.note},
    )
    db.commit()
    db.refresh(pub)
    return pub


@router.get("/{publication_id}/history")
def history(
    publication_id: UUID,
    editor: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    actions = db.scalars(
        select(EditorialAction)
        .options(joinedload(EditorialAction.actor))
        .where(EditorialAction.publication_id == publication_id)
        .order_by(EditorialAction.created_at.desc())
    ).all()
    return [
        {
            "id": str(action.id),
            "action": action.action,
            "from_status": action.from_status,
            "to_status": action.to_status,
            "note": action.note,
            "created_at": action.created_at,
            "actor": f"{action.actor.first_name} {action.actor.last_name}",
        }
        for action in actions
    ]
