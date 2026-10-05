import hashlib
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.analytics import AnalyticsEvent
from app.models.publication import Publication, PublicationStatus
from app.models.user import User
from app.schemas.analytics import AnalyticsEventCreate, PublicationAnalytics

router = APIRouter()
ALLOWED_EVENTS = {"view", "save", "share", "download", "source_click"}


@router.post("/event", status_code=201)
def record(payload: AnalyticsEventCreate, db: Session = Depends(get_db)):
    pub = db.get(Publication, payload.publication_id)
    if not pub or pub.status != PublicationStatus.published:
        raise HTTPException(status_code=404, detail="Publication not found")
    if payload.event_type not in ALLOWED_EVENTS:
        raise HTTPException(status_code=422, detail="Unsupported analytics event")
    session_hash = hashlib.sha256(payload.session_id.encode()).hexdigest() if payload.session_id else None
    db.add(AnalyticsEvent(publication_id=payload.publication_id, event_type=payload.event_type, session_hash=session_hash, referrer_host=payload.referrer_host))
    db.commit()
    return {"ok": True}


def stats_for(db: Session, pub_id: UUID) -> PublicationAnalytics:
    def count(event):
        return db.scalar(select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.publication_id == pub_id, AnalyticsEvent.event_type == event)) or 0
    unique = db.scalar(select(func.count(distinct(AnalyticsEvent.session_hash))).where(AnalyticsEvent.publication_id == pub_id, AnalyticsEvent.event_type == "view", AnalyticsEvent.session_hash.is_not(None))) or 0
    return PublicationAnalytics(publication_id=pub_id, views=count("view"), unique_readers=unique, saves=count("save"), shares=count("share"), downloads=count("download"), source_clicks=count("source_click"))


@router.get("/mine", response_model=list[PublicationAnalytics])
def my_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pubs = db.scalars(select(Publication).where(Publication.author_id == user.id)).all()
    return [stats_for(db, p.id) for p in pubs]


@router.get("/publication/{publication_id}", response_model=PublicationAnalytics)
def publication_stats(publication_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pub = db.get(Publication, publication_id)
    if not pub or pub.author_id != user.id:
        raise HTTPException(status_code=404, detail="Publication not found")
    return stats_for(db, publication_id)
