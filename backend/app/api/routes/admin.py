from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.platform import Dataset, Opportunity, PolicyRecord, ResearchRoom
from app.models.publication import Publication
from app.models.user import User, UserRole
from app.schemas.platform import (
    DatasetOut,
    DatasetUpdate,
    OpportunityOut,
    OpportunityUpdate,
    PolicyOut,
    PolicyUpdate,
)
from app.schemas.user import AdminRoleUpdate, UserMe


router = APIRouter()

CLOSED_TAG = "AGP-CLOSED"


def _super_admin(
    admin: User = Depends(require_roles(UserRole.super_admin)),
) -> User:
    return admin


@router.get("/summary")
def summary(
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    return {
        "users": int(db.scalar(select(func.count(User.id))) or 0),
        "researchers": int(
            db.scalar(
                select(func.count(User.id)).where(
                    User.role.in_(
                        (
                            UserRole.researcher,
                            UserRole.contributor,
                        )
                    )
                )
            )
            or 0
        ),
        "publications": int(db.scalar(select(func.count(Publication.id))) or 0),
        "opportunities": int(db.scalar(select(func.count(Opportunity.id))) or 0),
        "policies": int(db.scalar(select(func.count(PolicyRecord.id))) or 0),
        "datasets": int(db.scalar(select(func.count(Dataset.id))) or 0),
        "research_rooms": int(db.scalar(select(func.count(ResearchRoom.id))) or 0),
    }


@router.get("/users", response_model=list[UserMe])
def users(
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(User)
            .order_by(User.created_at.desc())
            .limit(500)
        ).all()
    )


@router.patch("/users/{user_id}", response_model=UserMe)
def update_user(
    user_id: UUID,
    payload: AdminRoleUpdate,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    target = db.get(User, user_id)

    if not target:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if (
        target.id == admin.id
        and payload.is_active is False
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "You cannot disable your own "
                "active session"
            ),
        )

    target.role = payload.role

    if payload.is_active is not None:
        target.is_active = payload.is_active

    db.commit()
    db.refresh(target)

    return target


@router.get(
    "/content/opportunities",
    response_model=list[OpportunityOut],
)
def admin_opportunities(
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Opportunity).order_by(
                Opportunity.created_at.desc()
            )
        ).all()
    )


@router.patch(
    "/content/opportunities/{item_id}",
    response_model=OpportunityOut,
)
def update_opportunity(
    item_id: UUID,
    payload: OpportunityUpdate,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Opportunity, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/content/opportunities/{item_id}/close",
    response_model=OpportunityOut,
)
def close_opportunity(
    item_id: UUID,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Opportunity, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    tags = [
        tag
        for tag in (item.tags or [])
        if tag != CLOSED_TAG
    ]
    tags.append(CLOSED_TAG)
    item.tags = tags

    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/content/opportunities/{item_id}/reopen",
    response_model=OpportunityOut,
)
def reopen_opportunity(
    item_id: UUID,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Opportunity, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    item.tags = [
        tag
        for tag in (item.tags or [])
        if tag != CLOSED_TAG
    ]

    db.commit()
    db.refresh(item)

    return item


@router.delete("/content/opportunities/{item_id}")
def delete_opportunity(
    item_id: UUID,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Opportunity, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    db.delete(item)
    db.commit()

    return {"message": "Opportunity deleted."}


@router.get(
    "/content/policies",
    response_model=list[PolicyOut],
)
def admin_policies(
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(PolicyRecord).order_by(
                PolicyRecord.created_at.desc()
            )
        ).all()
    )


@router.patch(
    "/content/policies/{item_id}",
    response_model=PolicyOut,
)
def update_policy(
    item_id: UUID,
    payload: PolicyUpdate,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(PolicyRecord, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Policy record not found",
        )

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@router.delete("/content/policies/{item_id}")
def delete_policy(
    item_id: UUID,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(PolicyRecord, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Policy record not found",
        )

    db.delete(item)
    db.commit()

    return {"message": "Policy record deleted."}


@router.get(
    "/content/datasets",
    response_model=list[DatasetOut],
)
def admin_datasets(
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Dataset).order_by(
                Dataset.created_at.desc()
            )
        ).all()
    )


@router.patch(
    "/content/datasets/{item_id}",
    response_model=DatasetOut,
)
def update_dataset(
    item_id: UUID,
    payload: DatasetUpdate,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Dataset, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    return item


@router.delete("/content/datasets/{item_id}")
def delete_dataset(
    item_id: UUID,
    admin: User = Depends(_super_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Dataset, item_id)

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    db.delete(item)
    db.commit()

    return {"message": "Dataset deleted."}
