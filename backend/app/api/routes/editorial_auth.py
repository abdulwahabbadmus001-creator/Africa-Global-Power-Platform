from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import UUID

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy import (
    delete,
    func,
    select,
)
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_purpose_token,
    decode_purpose_token,
    verify_password,
)
from app.core.totp import (
    build_otpauth_uri,
    generate_editor_totp_secret,
    generate_recovery_code,
    hash_recovery_code,
    verify_totp,
)
from app.models.authentication import (
    AuthAuditEvent,
    MfaRecoveryCode,
)
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.editorial_auth import (
    EditorialAuthSuccess,
    EditorialLoginRequest,
    EditorialLoginResponse,
    EditorialMfaConfirmRequest,
    EditorialMfaSetupResponse,
    EditorialMfaSetupSuccess,
    EditorialMfaVerifyRequest,
)
from app.services.authentication import (
    record_auth_event,
)


router = APIRouter()


EDITORIAL_ROLES = {
    UserRole.reviewer,
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
}


EDITORIAL_CHALLENGE_PURPOSE = (
    "editorial_mfa"
)


def utcnow() -> datetime:
    return datetime.now(
        timezone.utc
    )


def set_editorial_challenge_cookie(
    response: Response,
    user: User,
) -> None:
    token = create_purpose_token(
        str(user.id),
        purpose=(
            EDITORIAL_CHALLENGE_PURPOSE
        ),
        minutes=(
            settings.editorial_challenge_minutes
        ),
    )

    response.set_cookie(
        key="editorial_challenge",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=(
            settings.editorial_challenge_minutes
            * 60
        ),
        path=(
            f"{settings.api_v1_prefix}"
            "/auth/editorial"
        ),
    )


def delete_editorial_challenge_cookie(
    response: Response,
) -> None:
    response.delete_cookie(
        "editorial_challenge",
        path=(
            f"{settings.api_v1_prefix}"
            "/auth/editorial"
        ),
    )


def set_editorial_access_cookie(
    response: Response,
    user: User,
) -> None:
    token = create_access_token(
        str(user.id),
        minutes=(
            settings.editor_session_minutes
        ),
        auth_level=(
            "editorial_mfa"
        ),
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=(
            settings.editor_session_minutes
            * 60
        ),
        domain=(
            settings.cookie_domain
            or None
        ),
        path="/",
    )


def get_challenge_user(
    db: Session,
    token: str | None,
) -> User:
    if not token:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Editorial authentication "
                "challenge expired. "
                "Sign in again."
            ),
        )

    subject = decode_purpose_token(
        token,
        purpose=(
            EDITORIAL_CHALLENGE_PURPOSE
        ),
    )

    if not subject:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Editorial authentication "
                "challenge expired. "
                "Sign in again."
            ),
        )

    try:
        user_id = UUID(subject)

    except ValueError:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Editorial authentication "
                "challenge is invalid."
            ),
        )

    user = db.get(
        User,
        user_id,
    )

    if (
        user is None
        or user.role
        not in EDITORIAL_ROLES
        or not user.is_active
        or not user.is_email_verified
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Editorial authentication "
                "is unavailable."
            ),
        )

    return user


def too_many_recent_failures(
    db: Session,
    *,
    user: User,
    event_type: str,
    minutes: int = 10,
    limit: int = 5,
) -> bool:
    cutoff = (
        utcnow()
        - timedelta(
            minutes=minutes,
        )
    )

    count = db.scalar(
        select(
            func.count(
                AuthAuditEvent.id
            )
        ).where(
            AuthAuditEvent.user_id
            == user.id,
            AuthAuditEvent.event_type
            == event_type,
            AuthAuditEvent.success
            == False,
            AuthAuditEvent.created_at
            >= cutoff,
        )
    )

    return (
        int(count or 0)
        >= limit
    )


@router.post(
    "/login",
    response_model=EditorialLoginResponse,
    status_code=(
        status.HTTP_202_ACCEPTED
    ),
)
def editorial_login(
    payload: EditorialLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = (
        payload.email
        .lower()
        .strip()
    )

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        user is not None
        and too_many_recent_failures(
            db,
            user=user,
            event_type=(
                "EDITORIAL_PASSWORD_FAILED"
            ),
            minutes=15,
            limit=5,
        )
    ):
        record_auth_event(
            db,
            request=request,
            event_type=(
                "EDITORIAL_LOGIN_THROTTLED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many unsuccessful "
                "authentication attempts. "
                "Try again later."
            ),
        )

    valid = (
        user is not None
        and user.role
        in EDITORIAL_ROLES
        and user.is_active
        and user.is_email_verified
        and verify_password(
            payload.password,
            user.password_hash,
        )
    )

    if not valid:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "EDITORIAL_PASSWORD_FAILED"
            ),
            success=False,
            user=user,
            email=email,
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Unable to authenticate "
                "with those credentials."
            ),
        )

    record_auth_event(
        db,
        request=request,
        event_type=(
            "EDITORIAL_PASSWORD_SUCCESS"
        ),
        success=True,
        user=user,
    )

    db.commit()

    set_editorial_challenge_cookie(
        response,
        user,
    )

    return EditorialLoginResponse(
        message=(
            "Password accepted. "
            "Complete editorial "
            "multi-factor authentication."
        ),
        requires_setup=(
            not user.editor_mfa_enabled
        ),
        requires_mfa=True,
    )


@router.get(
    "/mfa/setup",
    response_model=EditorialMfaSetupResponse,
)
def editorial_mfa_setup(
    editorial_challenge: str | None = Cookie(
        default=None
    ),
    db: Session = Depends(get_db),
):
    user = get_challenge_user(
        db,
        editorial_challenge,
    )

    if user.editor_mfa_enabled:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Authenticator MFA is "
                "already configured."
            ),
        )

    secret = (
        generate_editor_totp_secret(
            str(user.id),
            user.editor_mfa_generation,
        )
    )

    return EditorialMfaSetupResponse(
        issuer=settings.mfa_issuer,
        account=user.email,
        secret=secret,
        otpauth_uri=(
            build_otpauth_uri(
                secret=secret,
                email=user.email,
            )
        ),
    )


@router.post(
    "/mfa/setup/confirm",
    response_model=(
        EditorialMfaSetupSuccess
    ),
)
def confirm_editorial_mfa_setup(
    payload: EditorialMfaConfirmRequest,
    request: Request,
    response: Response,
    editorial_challenge: str | None = Cookie(
        default=None
    ),
    db: Session = Depends(get_db),
):
    user = get_challenge_user(
        db,
        editorial_challenge,
    )

    if user.editor_mfa_enabled:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Authenticator MFA is "
                "already configured."
            ),
        )

    if too_many_recent_failures(
        db,
        user=user,
        event_type=(
            "EDITORIAL_MFA_SETUP_FAILED"
        ),
        minutes=10,
        limit=5,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many failed setup "
                "attempts. Sign in again later."
            ),
        )

    secret = (
        generate_editor_totp_secret(
            str(user.id),
            user.editor_mfa_generation,
        )
    )

    if not verify_totp(
        secret,
        payload.code,
    ):
        record_auth_event(
            db,
            request=request,
            event_type=(
                "EDITORIAL_MFA_SETUP_FAILED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Invalid authenticator code."
            ),
        )

    db.execute(
        delete(
            MfaRecoveryCode
        ).where(
            MfaRecoveryCode.user_id
            == user.id
        )
    )

    recovery_codes: list[str] = []

    for _ in range(
        settings.recovery_code_count
    ):
        code = generate_recovery_code()

        recovery_codes.append(
            code
        )

        db.add(
            MfaRecoveryCode(
                user_id=user.id,
                code_hash=(
                    hash_recovery_code(
                        user_id=str(
                            user.id
                        ),
                        code=code,
                    )
                ),
            )
        )

    user.editor_mfa_enabled = True

    user.editor_mfa_enabled_at = (
        utcnow()
    )

    record_auth_event(
        db,
        request=request,
        event_type=(
            "EDITORIAL_MFA_ENABLED"
        ),
        success=True,
        user=user,
    )

    db.commit()
    db.refresh(user)

    set_editorial_access_cookie(
        response,
        user,
    )

    delete_editorial_challenge_cookie(
        response
    )

    return EditorialMfaSetupSuccess(
        message=(
            "Editorial multi-factor "
            "authentication is now enabled."
        ),
        recovery_codes=(
            recovery_codes
        ),
        user=user,
    )


@router.post(
    "/mfa/verify",
    response_model=EditorialAuthSuccess,
)
def verify_editorial_mfa(
    payload: EditorialMfaVerifyRequest,
    request: Request,
    response: Response,
    editorial_challenge: str | None = Cookie(
        default=None
    ),
    db: Session = Depends(get_db),
):
    user = get_challenge_user(
        db,
        editorial_challenge,
    )

    if not user.editor_mfa_enabled:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Authenticator setup is "
                "required first."
            ),
        )

    if too_many_recent_failures(
        db,
        user=user,
        event_type=(
            "EDITORIAL_MFA_FAILED"
        ),
        minutes=10,
        limit=5,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Too many unsuccessful MFA "
                "attempts. Try again later."
            ),
        )

    authenticated = False

    method = ""

    if payload.code:
        secret = (
            generate_editor_totp_secret(
                str(user.id),
                user.editor_mfa_generation,
            )
        )

        authenticated = verify_totp(
            secret,
            payload.code,
        )

        method = "totp"

    elif payload.recovery_code:
        recovery_hash = (
            hash_recovery_code(
                user_id=str(user.id),
                code=(
                    payload.recovery_code
                ),
            )
        )

        recovery = db.scalar(
            select(
                MfaRecoveryCode
            ).where(
                MfaRecoveryCode.user_id
                == user.id,
                MfaRecoveryCode.code_hash
                == recovery_hash,
                MfaRecoveryCode.used_at
                .is_(None),
            )
        )

        if recovery:
            recovery.used_at = (
                utcnow()
            )

            authenticated = True

        method = "recovery_code"

    if not authenticated:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "EDITORIAL_MFA_FAILED"
            ),
            success=False,
            user=user,
            details={
                "method": method
                or "missing",
            },
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Unable to verify the "
                "authentication code."
            ),
        )

    record_auth_event(
        db,
        request=request,
        event_type=(
            "EDITORIAL_MFA_SUCCESS"
        ),
        success=True,
        user=user,
        details={
            "method": method,
        },
    )

    db.commit()
    db.refresh(user)

    set_editorial_access_cookie(
        response,
        user,
    )

    delete_editorial_challenge_cookie(
        response
    )

    return EditorialAuthSuccess(
        message=(
            "Editorial authentication "
            "successful."
        ),
        user=user,
    )