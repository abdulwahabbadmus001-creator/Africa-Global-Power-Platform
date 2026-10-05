from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.otp import PASSWORD_RESET_PURPOSE
from app.core.security import create_purpose_token, decode_purpose_token, hash_password
from app.models.user import User
from app.schemas.account_recovery import (
    RecoveryComplete,
    RecoveryMessage,
    RecoveryRequest,
    RecoveryVerify,
    RecoveryVerifyResponse,
)
from app.services.authentication import issue_otp_challenge, record_auth_event, verify_otp_challenge
from app.services.email import EmailDeliveryError, send_password_reset_otp

router = APIRouter()
RESET_TOKEN_PURPOSE = "password_reset_complete"
GENERIC = "If the address belongs to an eligible AGP account, a recovery code has been sent."


@router.post("/request", response_model=RecoveryMessage)
def request_reset(payload: RecoveryRequest, request: Request, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active or not getattr(user, "is_email_verified", False):
        return RecoveryMessage(message=GENERIC)
    code, _challenge = issue_otp_challenge(db, user=user, purpose=PASSWORD_RESET_PURPOSE)
    record_auth_event(db, request=request, event_type="PASSWORD_RESET_REQUESTED", success=True, user=user)
    db.commit()
    try:
        send_password_reset_otp(recipient=user.email, first_name=user.first_name, code=code)
    except EmailDeliveryError:
        record_auth_event(db, request=request, event_type="PASSWORD_RESET_EMAIL_FAILED", success=False, user=user)
        db.commit()
    return RecoveryMessage(message=GENERIC)


@router.post("/verify", response_model=RecoveryVerifyResponse)
def verify_reset(payload: RecoveryVerify, request: Request, db: Session = Depends(get_db)):
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="Unable to verify recovery code")
    valid, message = verify_otp_challenge(db, user=user, purpose=PASSWORD_RESET_PURPOSE, code=payload.code)
    if not valid:
        record_auth_event(db, request=request, event_type="PASSWORD_RESET_VERIFY_FAILED", success=False, user=user, details={"reason": message})
        db.commit()
        raise HTTPException(status_code=400, detail=message)
    token = create_purpose_token(str(user.id), purpose=RESET_TOKEN_PURPOSE, minutes=10)
    record_auth_event(db, request=request, event_type="PASSWORD_RESET_VERIFIED", success=True, user=user)
    db.commit()
    return RecoveryVerifyResponse(reset_token=token, message="Recovery code verified. Choose a new password.")


@router.post("/complete", response_model=RecoveryMessage)
def complete_reset(payload: RecoveryComplete, request: Request, db: Session = Depends(get_db)):
    subject = decode_purpose_token(payload.reset_token, purpose=RESET_TOKEN_PURPOSE)
    if not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recovery session expired. Start again.")
    try:
        user_id = UUID(subject)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid recovery session")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Account unavailable")
    user.password_hash = hash_password(payload.new_password)
    record_auth_event(db, request=request, event_type="PASSWORD_RESET_COMPLETED", success=True, user=user)
    db.commit()
    return RecoveryMessage(message="Password changed successfully. You can now sign in.")
