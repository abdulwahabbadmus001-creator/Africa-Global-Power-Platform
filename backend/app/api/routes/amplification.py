import hashlib
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import (
    Session,
    joinedload,
)

from app.api.deps import (
    get_current_user,
    get_db,
)

from app.core.config import settings

from app.models.amplification import (
    InstitutionalAnnouncement,
    ResearchShareClick,
    ResearchShareEvent,
)

from app.models.publication import (
    Publication,
    PublicationStatus,
)

from app.models.user import (
    User,
    UserRole,
)

from app.schemas.amplification import (
    AmplificationMetricsOut,
    EditorialAmplificationQueueItem,
    InstitutionalAnnouncementOut,
    InstitutionalAnnouncementUpdate,
    InstitutionalDistributionRequest,
    ShareClickRequest,
    ShareClickResponse,
    ShareLinkRequest,
    ShareLinkResponse,
)


router = APIRouter()


EDITORIAL_ROLES = {
    UserRole.reviewer,
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
}


def utcnow() -> datetime:
    return datetime.now(
        timezone.utc
    )


def canonical_publication_url(
    publication: Publication,
) -> str:
    site = (
        settings.public_site_url
        .rstrip("/")
    )

    return (
        f"{site}/research/"
        f"{publication.slug}"
    )


def author_name(
    publication: Publication,
) -> str:
    if publication.author:
        return (
            f"{publication.author.first_name} "
            f"{publication.author.last_name}"
        )

    return "AGP Research"


def default_share_message(
    publication: Publication,
) -> str:
    author = author_name(
        publication
    )

    return (
        f'New research from Africa & Global Power: '
        f'“{publication.title}” by {author}.'
    )


def institutional_message(
    publication: Publication,
) -> str:
    author = author_name(
        publication
    )

    abstract = (
        publication.abstract
        .strip()
        .replace("\n", " ")
    )

    if len(abstract) > 220:
        abstract = (
            abstract[:217].rstrip()
            + "..."
        )

    return (
        f"Congratulations to {author} on the "
        f'publication of “{publication.title}” '
        f"with Africa & Global Power.\n\n"
        f"{abstract}\n\n"
        f"Read the full research:"
    )


def build_tracked_url(
    publication: Publication,
    event: ResearchShareEvent,
) -> str:
    canonical = (
        canonical_publication_url(
            publication
        )
    )

    params = urlencode(
        {
            "agp_share": str(
                event.id
            ),
            "utm_source": (
                event.channel
            ),
            "utm_medium": "social",
            "utm_campaign": (
                "agp_publication"
            ),
        }
    )

    return (
        f"{canonical}?{params}"
    )


def external_share_target(
    *,
    channel: str,
    message: str,
    tracked_url: str,
) -> tuple[str, str, str | None]:
    encoded_url = quote(
        tracked_url,
        safe="",
    )

    encoded_message = quote(
        message,
        safe="",
    )

    combined = quote(
        f"{message}\n\n{tracked_url}",
        safe="",
    )

    if channel == "linkedin":
        return (
            (
                "https://www.linkedin.com/"
                "sharing/share-offsite/"
                f"?url={encoded_url}"
            ),
            "composer",
            None,
        )

    if channel == "x":
        return (
            (
                "https://twitter.com/"
                "intent/tweet"
                f"?text={encoded_message}"
                f"&url={encoded_url}"
            ),
            "composer",
            None,
        )

    if channel == "facebook":
        return (
            (
                "https://www.facebook.com/"
                "sharer/sharer.php"
                f"?u={encoded_url}"
            ),
            "composer",
            None,
        )

    if channel == "whatsapp":
        return (
            (
                "https://wa.me/"
                f"?text={combined}"
            ),
            "composer",
            None,
        )

    if channel == "email":
        subject = quote(
            f"Research: {message}",
            safe="",
        )

        return (
            (
                f"mailto:?subject={subject}"
                f"&body={combined}"
            ),
            "composer",
            None,
        )

    if channel == "medium":
        return (
            "https://medium.com/",
            "copy_and_open",
            (
                "AGP will copy the publication "
                "URL. In Medium, use "
                "Stories → Import a story and "
                "paste the AGP URL."
            ),
        )

    if channel == "researchgate":
        return (
            (
                "https://www.researchgate.net/"
                "publications/create"
                "?publicationType=article"
            ),
            "copy_and_open",
            (
                "AGP will copy the publication "
                "URL and announcement. Add the "
                "published research to your "
                "ResearchGate profile."
            ),
        )

    if channel == "academia":
        return (
            "https://www.academia.edu/",
            "copy_and_open",
            (
                "AGP will copy the publication "
                "URL. Use Academia's Upload "
                "option to add the research "
                "and publication details."
            ),
        )

    if channel == "github":
        return (
            "https://github.com/new",
            "copy_and_open",
            (
                "Use GitHub for datasets, code, "
                "notebooks, appendices or "
                "replication materials connected "
                "to this publication."
            ),
        )

    return (
        tracked_url,
        "copy",
        None,
    )


def get_published_publication(
    publication_id: UUID,
    db: Session,
) -> Publication:
    publication = db.scalar(
        select(Publication)
        .options(
            joinedload(
                Publication.author
            )
        )
        .where(
            Publication.id
            == publication_id,
            Publication.status
            == PublicationStatus.published,
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Published research "
                "not found."
            ),
        )

    return publication


def require_editorial(
    user: User,
) -> None:
    if user.role not in EDITORIAL_ROLES:
        raise HTTPException(
            status_code=403,
            detail=(
                "Editorial access required."
            ),
        )


@router.post(
    "/publications/{publication_id}/share-link",
    response_model=ShareLinkResponse,
)
def create_share_link(
    publication_id: UUID,
    payload: ShareLinkRequest,
    db: Session = Depends(get_db),
):
    publication = (
        get_published_publication(
            publication_id,
            db,
        )
    )

    message = (
        payload.message_override.strip()
        if payload.message_override
        else default_share_message(
            publication
        )
    )

    event = ResearchShareEvent(
        publication_id=(
            publication.id
        ),
        channel=payload.channel,
        context=payload.context,
        message=message,
    )

    db.add(event)

    db.flush()

    tracked_url = build_tracked_url(
        publication,
        event,
    )

    (
        share_url,
        mode,
        instruction,
    ) = external_share_target(
        channel=payload.channel,
        message=message,
        tracked_url=tracked_url,
    )

    db.commit()

    return ShareLinkResponse(
        event_id=event.id,
        channel=payload.channel,
        canonical_url=(
            canonical_publication_url(
                publication
            )
        ),
        tracked_url=tracked_url,
        share_url=share_url,
        suggested_text=message,
        mode=mode,
        manual_instruction=instruction,
    )


@router.post(
    "/share-events/{event_id}/click",
    response_model=ShareClickResponse,
)
def register_share_click(
    event_id: UUID,
    payload: ShareClickRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    share_event = db.get(
        ResearchShareEvent,
        event_id,
    )

    if share_event is None:
        return ShareClickResponse(
            recorded=False
        )

    session_hash = hashlib.sha256(
        (
            f"{event_id}:"
            f"{payload.session_id}"
        ).encode("utf-8")
    ).hexdigest()

    existing = db.scalar(
        select(
            ResearchShareClick
        ).where(
            ResearchShareClick.share_event_id
            == event_id,
            ResearchShareClick.session_id_hash
            == session_hash,
        )
    )

    if existing:
        return ShareClickResponse(
            recorded=False
        )

    click = ResearchShareClick(
        share_event_id=event_id,
        session_id_hash=session_hash,
        referrer_host=(
            payload.referrer_host
        ),
        user_agent=(
            request.headers.get(
                "user-agent"
            )
        ),
    )

    db.add(click)

    db.commit()

    return ShareClickResponse(
        recorded=True
    )


@router.get(
    "/mine",
    response_model=list[
        AmplificationMetricsOut
    ],
)
def my_amplification(
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    publications = list(
        db.scalars(
            select(Publication)
            .where(
                Publication.author_id
                == user.id,
                Publication.status
                == PublicationStatus.published,
            )
            .order_by(
                Publication.published_at
                .desc()
            )
        ).all()
    )

    results: list[
        AmplificationMetricsOut
    ] = []

    for publication in publications:
        channel_rows = db.execute(
            select(
                ResearchShareEvent.channel,
                func.count(
                    ResearchShareEvent.id
                ),
            )
            .where(
                ResearchShareEvent.publication_id
                == publication.id
            )
            .group_by(
                ResearchShareEvent.channel
            )
        ).all()

        channels = {
            channel: int(count)
            for channel, count
            in channel_rows
        }

        share_actions = sum(
            channels.values()
        )

        referral_clicks = int(
            db.scalar(
                select(
                    func.count(
                        ResearchShareClick.id
                    )
                )
                .join(
                    ResearchShareEvent,
                    ResearchShareClick.share_event_id
                    == ResearchShareEvent.id,
                )
                .where(
                    ResearchShareEvent.publication_id
                    == publication.id
                )
            )
            or 0
        )

        results.append(
            AmplificationMetricsOut(
                publication_id=(
                    publication.id
                ),
                title=publication.title,
                slug=publication.slug,
                published_at=(
                    publication.published_at
                ),
                share_actions=(
                    share_actions
                ),
                referral_clicks=(
                    referral_clicks
                ),
                channels=channels,
            )
        )

    return results


@router.get(
    "/editorial/queue",
    response_model=list[
        EditorialAmplificationQueueItem
    ],
)
def editorial_amplification_queue(
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_editorial(user)

    publications = list(
        db.scalars(
            select(Publication)
            .options(
                joinedload(
                    Publication.author
                )
            )
            .where(
                Publication.status
                == PublicationStatus.published
            )
            .order_by(
                Publication.published_at
                .desc()
            )
        ).unique().all()
    )

    result: list[
        EditorialAmplificationQueueItem
    ] = []

    for publication in publications:
        announcement = db.scalar(
            select(
                InstitutionalAnnouncement
            ).where(
                InstitutionalAnnouncement.publication_id
                == publication.id
            )
        )

        result.append(
            EditorialAmplificationQueueItem(
                publication_id=(
                    publication.id
                ),
                title=publication.title,
                slug=publication.slug,
                author_name=(
                    author_name(
                        publication
                    )
                ),
                published_at=(
                    publication.published_at
                ),
                announcement=announcement,
            )
        )

    return result


@router.post(
    "/editorial/publications/"
    "{publication_id}/announcement",
    response_model=(
        InstitutionalAnnouncementOut
    ),
)
def create_institutional_announcement(
    publication_id: UUID,
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_editorial(user)

    publication = (
        get_published_publication(
            publication_id,
            db,
        )
    )

    existing = db.scalar(
        select(
            InstitutionalAnnouncement
        ).where(
            InstitutionalAnnouncement.publication_id
            == publication.id
        )
    )

    if existing:
        return existing

    announcement = (
        InstitutionalAnnouncement(
            publication_id=(
                publication.id
            ),
            created_by_id=user.id,
            message=(
                institutional_message(
                    publication
                )
            ),
            channels=[
                "linkedin",
                "x",
                "facebook",
            ],
            distributed_channels=[],
            status="draft",
        )
    )

    db.add(announcement)

    db.commit()

    db.refresh(announcement)

    return announcement


@router.patch(
    "/editorial/announcements/"
    "{announcement_id}",
    response_model=(
        InstitutionalAnnouncementOut
    ),
)
def update_institutional_announcement(
    announcement_id: UUID,
    payload: (
        InstitutionalAnnouncementUpdate
    ),
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_editorial(user)

    announcement = db.get(
        InstitutionalAnnouncement,
        announcement_id,
    )

    if announcement is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Announcement not found."
            ),
        )

    announcement.message = (
        payload.message.strip()
    )

    announcement.channels = (
        payload.channels
    )

    db.commit()

    db.refresh(announcement)

    return announcement


@router.post(
    "/editorial/announcements/"
    "{announcement_id}/distributed",
    response_model=(
        InstitutionalAnnouncementOut
    ),
)
def mark_announcement_distributed(
    announcement_id: UUID,
    payload: (
        InstitutionalDistributionRequest
    ),
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    require_editorial(user)

    announcement = db.get(
        InstitutionalAnnouncement,
        announcement_id,
    )

    if announcement is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Announcement not found."
            ),
        )

    current = set(
        announcement.distributed_channels
        or []
    )

    current.update(
        payload.channels
    )

    announcement.distributed_channels = (
        sorted(current)
    )

    announcement.status = "distributed"

    announcement.distributed_at = (
        utcnow()
    )

    db.commit()

    db.refresh(announcement)

    return announcement