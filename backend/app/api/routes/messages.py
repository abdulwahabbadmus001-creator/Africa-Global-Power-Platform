from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_current_user, get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter()


@router.get("", response_model=list[MessageOut])
def list_messages(box: str = Query(default="inbox", pattern="^(inbox|sent)$"), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    condition = Message.recipient_id == user.id if box == "inbox" else Message.sender_id == user.id
    stmt = select(Message).options(joinedload(Message.sender), joinedload(Message.recipient)).where(condition).order_by(Message.created_at.desc())
    return list(db.scalars(stmt.limit(200)).unique().all())


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = len(db.scalars(select(Message).where(Message.recipient_id == user.id, Message.is_read.is_(False))).all())
    return {"unread": count}


@router.post("", response_model=MessageOut, status_code=201)
def send(payload: MessageCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.recipient_id == user.id:
        raise HTTPException(status_code=422, detail="You cannot message yourself")
    recipient = db.get(User, payload.recipient_id)
    if not recipient or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found")
    msg = Message(sender_id=user.id, **payload.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{message_id}/read", response_model=MessageOut)
def mark_read(message_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.get(Message, message_id)
    if not msg or msg.recipient_id != user.id:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = True
    db.commit()
    db.refresh(msg)
    return msg
