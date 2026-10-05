from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_claims
from app.db.session import SessionLocal
from app.models.user import User, UserRole


EDITOR_ROLES = (
    UserRole.reviewer,
    UserRole.editor,
    UserRole.senior_editor,
    UserRole.managing_editor,
    UserRole.super_admin,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _resolve_session(access_token: str | None, db: Session) -> tuple[User, dict]:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    claims = decode_access_claims(access_token)
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    try:
        user_id = UUID(str(claims["sub"]))
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account unavailable",
        )

    # Editorial roles are accepted only after the dedicated password + TOTP flow.
    if user.role in EDITOR_ROLES and claims.get("auth_level") != "editorial_mfa":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Secure Editorial authentication required",
        )

    return user, claims


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    user, _claims = _resolve_session(access_token, db)
    return user


def require_roles(*roles: UserRole):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permission",
            )
        return user

    return dependency
