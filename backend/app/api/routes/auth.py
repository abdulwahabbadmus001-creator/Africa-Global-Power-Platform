from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
)
from app.core.config import settings
from app.core.otp import (
    LOGIN_VERIFY_PURPOSE,
    REGISTRATION_VERIFY_PURPOSE,
)
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import (
    User,
    UserRole,
)
from app.schemas.auth import (
    ChangeRegistrationEmailRequest,
    LoginStartResponse,
    MessageResponse,
    RegistrationEmailChangeResponse,
    RegistrationStartResponse,
    ResendRegistrationCodeRequest,
    VerifyLoginRequest,
    VerifyRegistrationRequest,
)
from app.schemas.user import (
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    UserMe,
)
from app.services.authentication import (
    issue_otp_challenge,
    record_auth_event,
    verify_otp_challenge,
)
from app.services.email import (
    EmailDeliveryError,
    send_login_otp,
    send_registration_otp,
)


router = APIRouter()


EDITORIAL_ROLES = {
    UserRole.reviewer,
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
}


def set_auth_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=(
            settings.access_token_minutes
            * 60
        ),
        domain=(
            settings.cookie_domain
            or None
        ),
        path="/",
    )


@router.post(
    "/register",
    response_model=RegistrationStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    existing = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing:
        record_auth_event(
            db,
            request=request,
            event_type="REGISTER_REJECTED_EXISTING_EMAIL",
            success=False,
            user=existing,
            email=email,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email "
                "already exists."
            ),
        )

    role = UserRole(
        payload.requested_role
    )

    user = User(
        email=email,
        password_hash=hash_password(
            payload.password,
        ),
        first_name=(
            payload.first_name.strip()
        ),
        last_name=(
            payload.last_name.strip()
        ),
        country=payload.country,
        institution=payload.institution,
        role=role,
        is_active=False,
        is_email_verified=False,
    )

    db.add(user)
    db.flush()

    code, _challenge = issue_otp_challenge(
        db,
        user=user,
        purpose=REGISTRATION_VERIFY_PURPOSE,
    )

    record_auth_event(
        db,
        request=request,
        event_type="REGISTRATION_STARTED",
        success=True,
        user=user,
    )

    db.commit()

    try:
        send_registration_otp(
            recipient=user.email,
            first_name=user.first_name,
            code=code,
        )

    except EmailDeliveryError:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_EMAIL_DELIVERY_FAILED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Your account was created, "
                "but AGP could not deliver the "
                "verification email. "
                "Use the resend verification "
                "option and try again."
            ),
        )

    return RegistrationStartResponse(
        message=(
            "Account created. "
            "Enter the verification code "
            "sent to your email."
        ),
        email=user.email,
        requires_verification=True,
    )


@router.post(
    "/verify-registration",
    response_model=UserMe,
)
def verify_registration(
    payload: VerifyRegistrationRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if user is None:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_VERIFY_FAILED"
            ),
            success=False,
            email=email,
            details={
                "reason": "unknown_email",
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unable to verify this account."
            ),
        )

    if user.is_email_verified:
        if user.is_active:
            token = create_access_token(
                str(user.id),
            )

            set_auth_cookie(
                response,
                token,
            )

        return user

    valid, message = verify_otp_challenge(
        db,
        user=user,
        purpose=REGISTRATION_VERIFY_PURPOSE,
        code=payload.code,
    )

    if not valid:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_VERIFY_FAILED"
            ),
            success=False,
            user=user,
            details={
                "reason": message,
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    user.is_email_verified = True
    user.email_verified_at = (
        datetime.now(timezone.utc)
    )
    user.is_active = True

    record_auth_event(
        db,
        request=request,
        event_type=(
            "REGISTRATION_VERIFIED"
        ),
        success=True,
        user=user,
    )

    db.commit()
    db.refresh(user)

    token = create_access_token(
        str(user.id),
    )

    set_auth_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/change-registration-email",
    response_model=RegistrationEmailChangeResponse,
)
def change_registration_email(
    payload: ChangeRegistrationEmailRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    current_email = (
        payload.current_email
        .lower()
        .strip()
    )

    new_email = (
        payload.new_email
        .lower()
        .strip()
    )

    user = db.scalar(
        select(User).where(
            User.email == current_email
        )
    )

    if (
        user is None
        or user.is_email_verified
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_EMAIL_CHANGE_FAILED"
            ),
            success=False,
            user=user,
            email=current_email,
            details={
                "reason": (
                    "account_or_password_invalid"
                ),
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unable to change the email address. "
                "Check your password and try again."
            ),
        )

    if new_email == current_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Enter a different email address."
            ),
        )

    existing = db.scalar(
        select(User).where(
            User.email == new_email
        )
    )

    if existing:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_EMAIL_CHANGE_FAILED"
            ),
            success=False,
            user=user,
            email=current_email,
            details={
                "reason": (
                    "new_email_already_registered"
                ),
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "That email address is already "
                "registered with AGP."
            ),
        )

    previous_email = user.email

    user.email = new_email

    code, _challenge = issue_otp_challenge(
        db,
        user=user,
        purpose=REGISTRATION_VERIFY_PURPOSE,
    )

    record_auth_event(
        db,
        request=request,
        event_type=(
            "REGISTRATION_EMAIL_CHANGED"
        ),
        success=True,
        user=user,
        details={
            "previous_email": previous_email,
            "new_email": new_email,
        },
    )

    db.commit()
    db.refresh(user)

    try:
        send_registration_otp(
            recipient=user.email,
            first_name=user.first_name,
            code=code,
        )

    except EmailDeliveryError:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_EMAIL_CHANGE_DELIVERY_FAILED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Your email address was changed, "
                "but AGP could not deliver the new "
                "verification code. Use the resend "
                "option and try again."
            ),
        )

    return RegistrationEmailChangeResponse(
        message=(
            "Email address updated successfully. "
            "A new verification code has been "
            "sent to the new address."
        ),
        email=user.email,
    )


@router.post(
    "/resend-registration-code",
    response_model=MessageResponse,
)
def resend_registration_code(
    payload: ResendRegistrationCodeRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    generic_message = (
        "If this email has an account "
        "awaiting verification, a new code "
        "has been sent."
    )

    if (
        user is None
        or user.is_email_verified
    ):
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_RESEND_IGNORED"
            ),
            success=False,
            user=user,
            email=email,
        )

        db.commit()

        return MessageResponse(
            message=generic_message,
        )

    code, _challenge = issue_otp_challenge(
        db,
        user=user,
        purpose=REGISTRATION_VERIFY_PURPOSE,
    )

    record_auth_event(
        db,
        request=request,
        event_type=(
            "REGISTRATION_CODE_RESENT"
        ),
        success=True,
        user=user,
    )

    db.commit()

    try:
        send_registration_otp(
            recipient=user.email,
            first_name=user.first_name,
            code=code,
        )

    except EmailDeliveryError:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "REGISTRATION_EMAIL_DELIVERY_FAILED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AGP could not deliver the "
                "verification email."
            ),
        )

    return MessageResponse(
        message=generic_message,
    )


@router.post(
    "/login",
    response_model=LoginStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user.password_hash,
        )
    ):
        record_auth_event(
            db,
            request=request,
            event_type="LOGIN_PASSWORD_FAILED",
            success=False,
            user=user,
            email=email,
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid email or password.",
        )

    if user.role in EDITORIAL_ROLES:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "EDITORIAL_LOGIN_ON_PUBLIC_PORTAL_BLOCKED"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This account requires the secure "
                "Editorial Access portal."
            ),
        )

    if not user.is_email_verified:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "LOGIN_BLOCKED_UNVERIFIED_EMAIL"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Email verification is required "
                "before you can sign in."
            ),
        )

    if not user.is_active:
        record_auth_event(
            db,
            request=request,
            event_type=(
                "LOGIN_BLOCKED_DISABLED_ACCOUNT"
            ),
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account unavailable.",
        )

    code, _challenge = issue_otp_challenge(
        db,
        user=user,
        purpose=LOGIN_VERIFY_PURPOSE,
    )

    record_auth_event(
        db,
        request=request,
        event_type="LOGIN_PASSWORD_SUCCESS",
        success=True,
        user=user,
    )

    record_auth_event(
        db,
        request=request,
        event_type="LOGIN_MFA_CHALLENGE_CREATED",
        success=True,
        user=user,
    )

    db.commit()

    try:
        send_login_otp(
            recipient=user.email,
            first_name=user.first_name,
            code=code,
        )

    except EmailDeliveryError:
        record_auth_event(
            db,
            request=request,
            event_type="LOGIN_MFA_EMAIL_FAILED",
            success=False,
            user=user,
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Your password was accepted, "
                "but AGP could not deliver the "
                "sign-in verification code."
            ),
        )

    return LoginStartResponse(
        message=(
            "Password accepted. "
            "Enter the verification code "
            "sent to your registered email."
        ),
        email=user.email,
        requires_mfa=True,
    )


@router.post(
    "/verify-login",
    response_model=UserMe,
)
def verify_login(
    payload: VerifyLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        user is None
        or user.role in EDITORIAL_ROLES
        or not user.is_active
        or not user.is_email_verified
    ):
        record_auth_event(
            db,
            request=request,
            event_type="LOGIN_MFA_FAILED",
            success=False,
            user=user,
            email=email,
            details={
                "reason": "account_unavailable",
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unable to complete authentication."
            ),
        )

    valid, message = verify_otp_challenge(
        db,
        user=user,
        purpose=LOGIN_VERIFY_PURPOSE,
        code=payload.code,
    )

    if not valid:
        record_auth_event(
            db,
            request=request,
            event_type="LOGIN_MFA_FAILED",
            success=False,
            user=user,
            details={
                "reason": message,
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    record_auth_event(
        db,
        request=request,
        event_type="LOGIN_MFA_SUCCESS",
        success=True,
        user=user,
    )

    db.commit()
    db.refresh(user)

    token = create_access_token(
        str(user.id),
    )

    set_auth_cookie(
        response,
        token,
    )

    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
):
    response.delete_cookie(
        "access_token",
        path="/",
        domain=(
            settings.cookie_domain
            or None
        ),
    )


@router.get(
    "/me",
    response_model=UserMe,
)
def me(
    user: User = Depends(
        get_current_user,
    ),
):
    return user


@router.patch(
    "/me",
    response_model=UserMe,
)
def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(
        get_current_user,
    ),
    db: Session = Depends(get_db),
):
    for key, value in payload.model_dump(
        exclude_unset=True
    ).items():
        setattr(
            user,
            key,
            value,
        )

    db.commit()
    db.refresh(user)

    return user