from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.otp import (
    generate_otp,
    hash_otp,
    verify_otp_hash,
)
from app.models.authentication import (
    AuthAuditEvent,
    AuthChallenge,
)
from app.models.user import User


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def otp_context(
    user: User,
    purpose: str,
) -> str:
    return f"{user.id}:{purpose}"


def issue_otp_challenge(
    db: Session,
    *,
    user: User,
    purpose: str,
) -> tuple[str, AuthChallenge]:
    now = utcnow()

    latest = db.scalar(
        select(AuthChallenge)
        .where(
            AuthChallenge.user_id == user.id,
            AuthChallenge.purpose == purpose,
        )
        .order_by(
            AuthChallenge.created_at.desc(),
        )
        .limit(1)
    )

    if latest:
        elapsed = (
            now - latest.created_at
        ).total_seconds()

        if (
            latest.consumed_at is None
            and elapsed < settings.otp_resend_seconds
        ):
            remaining = max(
                1,
                int(
                    settings.otp_resend_seconds
                    - elapsed
                ),
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Please wait "
                    f"{remaining} seconds before requesting "
                    "another verification code."
                ),
            )

    active_challenges = list(
        db.scalars(
            select(AuthChallenge).where(
                AuthChallenge.user_id == user.id,
                AuthChallenge.purpose == purpose,
                AuthChallenge.consumed_at.is_(None),
            )
        ).all()
    )

    for challenge in active_challenges:
        challenge.consumed_at = now

    code = generate_otp(
        settings.otp_length,
    )

    context = otp_context(
        user,
        purpose,
    )

    challenge = AuthChallenge(
        user_id=user.id,
        purpose=purpose,
        code_hash=hash_otp(
            code,
            context=context,
        ),
        attempts=0,
        max_attempts=settings.otp_max_attempts,
        expires_at=(
            now
            + timedelta(
                minutes=settings.otp_expiry_minutes,
            )
        ),
    )

    db.add(challenge)

    return code, challenge


def verify_otp_challenge(
    db: Session,
    *,
    user: User,
    purpose: str,
    code: str,
) -> tuple[bool, str]:
    now = utcnow()

    challenge = db.scalar(
        select(AuthChallenge)
        .where(
            AuthChallenge.user_id == user.id,
            AuthChallenge.purpose == purpose,
            AuthChallenge.consumed_at.is_(None),
        )
        .order_by(
            AuthChallenge.created_at.desc(),
        )
        .limit(1)
    )

    if challenge is None:
        return (
            False,
            "No active verification code was found.",
        )

    if challenge.expires_at <= now:
        challenge.consumed_at = now

        return (
            False,
            "The verification code has expired.",
        )

    if challenge.attempts >= challenge.max_attempts:
        challenge.consumed_at = now

        return (
            False,
            "Too many incorrect attempts. "
            "Request a new verification code.",
        )

    challenge.attempts += 1

    context = otp_context(
        user,
        purpose,
    )

    valid = verify_otp_hash(
        code.strip(),
        challenge.code_hash,
        context=context,
    )

    if not valid:
        if challenge.attempts >= challenge.max_attempts:
            challenge.consumed_at = now

            return (
                False,
                "Too many incorrect attempts. "
                "Request a new verification code.",
            )

        remaining = (
            challenge.max_attempts
            - challenge.attempts
        )

        return (
            False,
            "Invalid verification code. "
            f"{remaining} attempt(s) remaining.",
        )

    challenge.consumed_at = now

    return (
        True,
        "Verification successful.",
    )


def record_auth_event(
    db: Session,
    *,
    request: Request | None,
    event_type: str,
    success: bool,
    user: User | None = None,
    email: str | None = None,
    details: dict | None = None,
) -> AuthAuditEvent:
    ip_address = None
    user_agent = None

    if request is not None:
        if request.client is not None:
            ip_address = request.client.host

        user_agent = request.headers.get(
            "user-agent",
        )

    event = AuthAuditEvent(
        user_id=user.id if user else None,
        email=(
            email.lower()
            if email
            else user.email
            if user
            else None
        ),
        event_type=event_type,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {},
    )

    db.add(event)

    return event