from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from slugify import slugify
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.platform import (
    Dataset,
    Opportunity,
    PolicyRecord,
    ResearchRoom,
    ResearchRoomMember,
    ResearchRoomPost,
)
from app.models.user import User, UserRole
from app.schemas.platform import (
    DatasetCreate,
    DatasetOut,
    OpportunityCreate,
    OpportunityOut,
    PolicyCreate,
    PolicyOut,
    RoomCreate,
    RoomInvite,
    RoomOut,
    RoomPostCreate,
    RoomPostOut,
)

router = APIRouter()

EDITOR_ROLES = (
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
)


def _unique_slug(db: Session, model, title: str) -> str:
    base = slugify(title) or "item"
    candidate = base
    index = 2
    while db.scalar(select(model.id).where(model.slug == candidate)):
        candidate = f"{base}-{index}"
        index += 1
    return candidate


@router.get("/data-lab", response_model=list[DatasetOut])
def datasets(
    q: str | None = None,
    category: str | None = None,
    country: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Dataset).where(Dataset.is_published.is_(True))
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Dataset.title.ilike(term), Dataset.summary.ilike(term), Dataset.description.ilike(term)))
    if category:
        stmt = stmt.where(Dataset.category == category)
    if country:
        stmt = stmt.where(Dataset.country == country)
    return list(db.scalars(stmt.order_by(Dataset.updated_at.desc())).all())


@router.get("/data-lab/{slug}", response_model=DatasetOut)
def dataset_detail(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Dataset).where(Dataset.slug == slug, Dataset.is_published.is_(True)))
    if not item:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return item


@router.post("/data-lab", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
def create_dataset(
    payload: DatasetCreate,
    user: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    item = Dataset(
        **payload.model_dump(),
        slug=_unique_slug(db, Dataset, payload.title),
        created_by_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/policy-tracker", response_model=list[PolicyOut])
def policies(
    q: str | None = None,
    country: str | None = None,
    policy_area: str | None = None,
    policy_status: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    stmt = select(PolicyRecord).where(PolicyRecord.is_published.is_(True))
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(PolicyRecord.title.ilike(term), PolicyRecord.summary.ilike(term), PolicyRecord.agp_analysis.ilike(term)))
    if country:
        stmt = stmt.where(PolicyRecord.country == country)
    if policy_area:
        stmt = stmt.where(PolicyRecord.policy_area == policy_area)
    if policy_status:
        stmt = stmt.where(PolicyRecord.status == policy_status)
    return list(db.scalars(stmt.order_by(PolicyRecord.updated_at.desc())).all())


@router.get("/policy-tracker/{slug}", response_model=PolicyOut)
def policy_detail(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(select(PolicyRecord).where(PolicyRecord.slug == slug, PolicyRecord.is_published.is_(True)))
    if not item:
        raise HTTPException(status_code=404, detail="Policy record not found")
    return item


@router.post("/policy-tracker", response_model=PolicyOut, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: PolicyCreate,
    user: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    item = PolicyRecord(
        **payload.model_dump(),
        slug=_unique_slug(db, PolicyRecord, payload.title),
        created_by_id=user.id,
        last_checked_at=datetime.now(timezone.utc),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/opportunities", response_model=list[OpportunityOut])
def opportunities(
    q: str | None = None,
    category: str | None = None,
    country: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Opportunity).where(Opportunity.is_published.is_(True))
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Opportunity.title.ilike(term), Opportunity.organization.ilike(term), Opportunity.summary.ilike(term)))
    if category:
        stmt = stmt.where(Opportunity.category == category)
    if country:
        stmt = stmt.where(Opportunity.country == country)
    return list(db.scalars(stmt.order_by(Opportunity.deadline.asc().nullslast(), Opportunity.created_at.desc())).all())


@router.post("/opportunities", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    payload: OpportunityCreate,
    user: User = Depends(require_roles(*EDITOR_ROLES)),
    db: Session = Depends(get_db),
):
    item = Opportunity(**payload.model_dump(), created_by_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _room_out(db: Session, room: ResearchRoom, user: User) -> RoomOut:
    member_count = int(db.scalar(select(func.count(ResearchRoomMember.id)).where(ResearchRoomMember.room_id == room.id)) or 0)
    membership = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    return RoomOut.model_validate({
        **room.__dict__,
        "member_count": member_count,
        "is_member": membership is not None,
    })


@router.get("/research-rooms", response_model=list[RoomOut])
def rooms(
    user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)),
    db: Session = Depends(get_db),
):
    member_room_ids = select(ResearchRoomMember.room_id).where(ResearchRoomMember.user_id == user.id)
    rows = list(db.scalars(select(ResearchRoom).where(or_(ResearchRoom.visibility == "public", ResearchRoom.id.in_(member_room_ids))).order_by(ResearchRoom.updated_at.desc())).all())
    return [_room_out(db, room, user) for room in rows]


@router.post("/research-rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)),
    db: Session = Depends(get_db),
):
    if user.role == UserRole.reader:
        raise HTTPException(status_code=403, detail="Researcher access required to create a room")
    room = ResearchRoom(
        **payload.model_dump(),
        owner_id=user.id,
        slug=_unique_slug(db, ResearchRoom, payload.title),
    )
    db.add(room)
    db.flush()
    db.add(ResearchRoomMember(room_id=room.id, user_id=user.id, role="owner"))
    db.commit()
    db.refresh(room)
    return _room_out(db, room, user)


@router.get("/research-rooms/{slug}", response_model=RoomOut)
def room_detail(slug: str, user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)), db: Session = Depends(get_db)):
    room = db.scalar(select(ResearchRoom).where(ResearchRoom.slug == slug))
    if not room:
        raise HTTPException(status_code=404, detail="Research room not found")
    membership = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    if room.visibility == "private" and not membership:
        raise HTTPException(status_code=403, detail="This research room is private")
    return _room_out(db, room, user)


@router.post("/research-rooms/{slug}/join", response_model=RoomOut)
def join_room(slug: str, user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)), db: Session = Depends(get_db)):
    room = db.scalar(select(ResearchRoom).where(ResearchRoom.slug == slug))
    if not room:
        raise HTTPException(status_code=404, detail="Research room not found")
    if room.join_policy != "open" or room.visibility != "public":
        raise HTTPException(status_code=403, detail="This room requires an invitation")
    existing = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    if not existing:
        db.add(ResearchRoomMember(room_id=room.id, user_id=user.id, role="member"))
        db.commit()
    return _room_out(db, room, user)


@router.post("/research-rooms/{slug}/members", response_model=RoomOut)
def invite_room_member(
    slug: str,
    payload: RoomInvite,
    user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)),
    db: Session = Depends(get_db),
):
    room = db.scalar(select(ResearchRoom).where(ResearchRoom.slug == slug))
    if not room:
        raise HTTPException(status_code=404, detail="Research room not found")
    membership = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    if room.owner_id != user.id and (not membership or membership.role != "admin"):
        raise HTTPException(status_code=403, detail="Only the room owner or an administrator can invite members")
    invited = db.scalar(select(User).where(User.email == payload.email.lower().strip()))
    if not invited or not invited.is_active:
        raise HTTPException(status_code=404, detail="No active AGP account was found for that email")
    existing = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == invited.id))
    if not existing:
        db.add(ResearchRoomMember(room_id=room.id, user_id=invited.id, role="member"))
        db.commit()
    return _room_out(db, room, user)


@router.get("/research-rooms/{slug}/posts", response_model=list[RoomPostOut])
def room_posts(slug: str, user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)), db: Session = Depends(get_db)):
    room = db.scalar(select(ResearchRoom).where(ResearchRoom.slug == slug))
    if not room:
        raise HTTPException(status_code=404, detail="Research room not found")
    membership = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    if not membership:
        raise HTTPException(status_code=403, detail="Join the room to read discussions")
    posts = list(db.scalars(select(ResearchRoomPost).where(ResearchRoomPost.room_id == room.id).order_by(ResearchRoomPost.created_at.asc())).all())
    author_ids = {post.author_id for post in posts}
    authors = {u.id: u for u in db.scalars(select(User).where(User.id.in_(author_ids))).all()} if author_ids else {}
    return [
        RoomPostOut(
            id=post.id,
            room_id=post.room_id,
            author_id=post.author_id,
            author_name=(f"{authors[post.author_id].first_name} {authors[post.author_id].last_name}" if post.author_id in authors else "AGP Researcher"),
            body=post.body,
            resource_url=post.resource_url,
            created_at=post.created_at,
        )
        for post in posts
    ]


@router.post("/research-rooms/{slug}/posts", response_model=RoomPostOut, status_code=status.HTTP_201_CREATED)
def create_room_post(
    slug: str,
    payload: RoomPostCreate,
    user: User = Depends(require_roles(UserRole.reader, UserRole.researcher, UserRole.contributor)),
    db: Session = Depends(get_db),
):
    room = db.scalar(select(ResearchRoom).where(ResearchRoom.slug == slug))
    if not room:
        raise HTTPException(status_code=404, detail="Research room not found")
    membership = db.scalar(select(ResearchRoomMember).where(ResearchRoomMember.room_id == room.id, ResearchRoomMember.user_id == user.id))
    if not membership:
        raise HTTPException(status_code=403, detail="Join the room before posting")
    post = ResearchRoomPost(room_id=room.id, author_id=user.id, **payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return RoomPostOut(
        id=post.id,
        room_id=post.room_id,
        author_id=post.author_id,
        author_name=f"{user.first_name} {user.last_name}",
        body=post.body,
        resource_url=post.resource_url,
        created_at=post.created_at,
    )
