from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserPublic

router = APIRouter()
RESEARCH_ROLES = [UserRole.researcher, UserRole.contributor, UserRole.reviewer, UserRole.editor, UserRole.senior_editor, UserRole.managing_editor]


@router.get("", response_model=list[UserPublic])
def list_researchers(q: str | None = Query(default=None), db: Session = Depends(get_db)):
    stmt = select(User).where(User.is_active.is_(True), User.role.in_(RESEARCH_ROLES)).order_by(User.created_at.desc())
    if q:
        term = f"%{q}%"
        stmt = stmt.where(or_(User.first_name.ilike(term), User.last_name.ilike(term), User.expertise.ilike(term), User.institution.ilike(term)))
    return list(db.scalars(stmt.limit(100)).all())


@router.get("/{user_id}", response_model=UserPublic)
def researcher(user_id: UUID, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="Researcher not found")
    return user
