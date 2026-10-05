from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.user import AdminRoleUpdate, UserMe

router = APIRouter()


@router.get("/users", response_model=list[UserMe])
def users(admin: User = Depends(require_roles(UserRole.super_admin)), db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.created_at.desc()).limit(500)).all())


@router.patch("/users/{user_id}", response_model=UserMe)
def update_user(user_id: UUID, payload: AdminRoleUpdate, admin: User = Depends(require_roles(UserRole.super_admin)), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id and payload.is_active is False:
        raise HTTPException(status_code=409, detail="You cannot disable your own active session")
    target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return target
