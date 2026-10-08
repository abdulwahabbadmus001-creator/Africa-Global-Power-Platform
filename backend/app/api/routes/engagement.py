from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_current_user, get_db
from app.models.engagement import Notification, ResearcherFollow, SavedPublication
from app.models.publication import Publication, PublicationStatus
from app.models.user import User, UserRole
from app.schemas.engagement import ActionResponse, IdList, NotificationOut
from app.schemas.publication import PublicationOut
from app.schemas.user import UserPublic

router = APIRouter()
RESEARCH_ROLES = (
    UserRole.researcher, UserRole.contributor, UserRole.reviewer,
    UserRole.editor, UserRole.senior_editor, UserRole.managing_editor,
)

@router.get("/saved/ids", response_model=IdList)
def saved_ids(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ids = list(db.scalars(select(SavedPublication.publication_id).where(SavedPublication.user_id == user.id)).all())
    return IdList(ids=ids)

@router.get("/saved", response_model=list[PublicationOut])
def saved_publications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(Publication)
        .join(SavedPublication, SavedPublication.publication_id == Publication.id)
        .options(joinedload(Publication.author))
        .where(SavedPublication.user_id == user.id, Publication.status == PublicationStatus.published)
        .order_by(SavedPublication.created_at.desc())
    )
    return list(db.scalars(stmt).unique().all())

@router.post("/saved/{publication_id}", response_model=ActionResponse)
def save_publication(publication_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    publication = db.get(Publication, publication_id)
    if publication is None or publication.status != PublicationStatus.published:
        raise HTTPException(status_code=404, detail="Publication not found")
    existing = db.scalar(select(SavedPublication).where(SavedPublication.user_id == user.id, SavedPublication.publication_id == publication_id))
    if existing is None:
        db.add(SavedPublication(user_id=user.id, publication_id=publication_id)); db.commit()
    return ActionResponse(message="Research saved.")

@router.delete("/saved/{publication_id}", response_model=ActionResponse)
def unsave_publication(publication_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(delete(SavedPublication).where(SavedPublication.user_id == user.id, SavedPublication.publication_id == publication_id)); db.commit()
    return ActionResponse(message="Research removed from saved items.")

@router.get("/following/ids", response_model=IdList)
def following_ids(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ids = list(db.scalars(select(ResearcherFollow.researcher_id).where(ResearcherFollow.follower_id == user.id)).all())
    return IdList(ids=ids)

@router.get("/following", response_model=list[UserPublic])
def following(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(User)
        .join(ResearcherFollow, ResearcherFollow.researcher_id == User.id)
        .where(ResearcherFollow.follower_id == user.id, User.is_active.is_(True), User.role.in_(RESEARCH_ROLES))
        .order_by(ResearcherFollow.created_at.desc())
    )
    return list(db.scalars(stmt).all())

@router.post("/following/{researcher_id}", response_model=ActionResponse)
def follow_researcher(researcher_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if researcher_id == user.id:
        raise HTTPException(status_code=422, detail="You cannot follow yourself")
    researcher = db.get(User, researcher_id)
    if researcher is None or not researcher.is_active or researcher.role not in RESEARCH_ROLES:
        raise HTTPException(status_code=404, detail="Researcher not found")
    existing = db.scalar(select(ResearcherFollow).where(ResearcherFollow.follower_id == user.id, ResearcherFollow.researcher_id == researcher_id))
    if existing is None:
        db.add(ResearcherFollow(follower_id=user.id, researcher_id=researcher_id))
        actor_link = f"/researchers/{user.id}" if user.role in RESEARCH_ROLES else None
        db.add(Notification(user_id=researcher.id, actor_id=user.id, kind="new_follower", title="New AGP follower", body=f"{user.first_name} {user.last_name} started following your research profile.", link=actor_link))
        db.commit()
    return ActionResponse(message="Researcher followed.")

@router.delete("/following/{researcher_id}", response_model=ActionResponse)
def unfollow_researcher(researcher_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(delete(ResearcherFollow).where(ResearcherFollow.follower_id == user.id, ResearcherFollow.researcher_id == researcher_id)); db.commit()
    return ActionResponse(message="Researcher unfollowed.")

@router.get("/notifications", response_model=list[NotificationOut])
def notifications(unread_only: bool = Query(default=False), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Notification).options(joinedload(Notification.actor)).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    return list(db.scalars(stmt.limit(100)).unique().all())

@router.post("/notifications-read-all", response_model=ActionResponse)
def mark_all_notifications_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = list(db.scalars(select(Notification).where(Notification.user_id == user.id, Notification.is_read.is_(False))).all())
    for item in items:
        item.is_read = True
    db.commit()
    return ActionResponse(message="Notifications marked as read.")

@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True; db.commit()
    return db.scalar(select(Notification).options(joinedload(Notification.actor)).where(Notification.id == notification.id))
