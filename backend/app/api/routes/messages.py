from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_current_user, get_db
from app.models.engagement import Notification
from app.models.message import Message
from app.models.user import User, UserRole
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter()
RESEARCH_ROLES = (
    UserRole.researcher, UserRole.contributor, UserRole.reviewer,
    UserRole.editor, UserRole.senior_editor, UserRole.managing_editor,
)
READER_MESSAGE_TYPES = {"general", "opportunity", "collaboration"}
MESSAGE_LIMIT_PER_HOUR = 12

@router.get("", response_model=list[MessageOut])
def list_messages(box: str = Query(default="inbox", pattern="^(inbox|sent)$"), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    condition = Message.recipient_id == user.id if box == "inbox" else Message.sender_id == user.id
    stmt = select(Message).options(joinedload(Message.sender), joinedload(Message.recipient)).where(condition).order_by(Message.created_at.desc())
    items = list(db.scalars(stmt.limit(200)).unique().all())
    if box == "inbox":
        changed = False
        for item in items:
            if not item.is_read:
                item.is_read = True
                changed = True
        if changed:
            db.commit()
    return items

@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.scalar(select(func.count(Message.id)).where(Message.recipient_id == user.id, Message.is_read.is_(False)))
    return {"unread": int(count or 0)}

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send(payload: MessageCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.recipient_id == user.id:
        raise HTTPException(status_code=422, detail="You cannot message yourself")
    recipient = db.get(User, payload.recipient_id)
    if recipient is None or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found")
    message_type = (payload.context_type or "general").strip().lower()
    if user.role == UserRole.reader:
        if recipient.role not in RESEARCH_ROLES:
            raise HTTPException(status_code=403, detail="Reader accounts can contact researchers only.")
        if not recipient.collaboration_open:
            raise HTTPException(status_code=403, detail="This researcher is not currently accepting direct inquiries.")
        if message_type not in READER_MESSAGE_TYPES:
            raise HTTPException(status_code=422, detail="Choose a valid message type.")
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_count = db.scalar(select(func.count(Message.id)).where(Message.sender_id == user.id, Message.created_at >= since))
    if int(recent_count or 0) >= MESSAGE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Message limit reached. Please try again later.")
    msg = Message(
        sender_id=user.id, recipient_id=payload.recipient_id, subject=payload.subject.strip(),
        body=payload.body.strip(), context_type=message_type, context_id=payload.context_id,
    )
    db.add(msg); db.flush()
    label = {"opportunity":"Opportunity inquiry", "collaboration":"Collaboration inquiry", "general":"New message"}.get(message_type, "New message")
    db.add(Notification(user_id=recipient.id, actor_id=user.id, kind="message", title=label, body=f"{user.first_name} {user.last_name}: {msg.subject}", link="/messages"))
    db.commit()
    return db.scalar(select(Message).options(joinedload(Message.sender), joinedload(Message.recipient)).where(Message.id == msg.id))

@router.post("/{message_id}/read", response_model=MessageOut)
def mark_read(message_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.get(Message, message_id)
    if msg is None or msg.recipient_id != user.id:
        raise HTTPException(status_code=404, detail="Message not found")
    msg.is_read = True; db.commit()
    return db.scalar(select(Message).options(joinedload(Message.sender), joinedload(Message.recipient)).where(Message.id == msg.id))
