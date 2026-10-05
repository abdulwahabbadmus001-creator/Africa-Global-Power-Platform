import hashlib
import hmac
import secrets

from app.core.config import settings


REGISTRATION_VERIFY_PURPOSE = "registration_verify"
LOGIN_VERIFY_PURPOSE = "login_verify"
PASSWORD_RESET_PURPOSE = "password_reset"


def generate_otp(length: int | None = None) -> str:
    code_length = length or settings.otp_length

    if code_length < 6:
        code_length = 6

    maximum = 10 ** code_length

    return f"{secrets.randbelow(maximum):0{code_length}d}"


def hash_otp(
    code: str,
    *,
    context: str,
) -> str:
    message = f"{context}:{code}".encode("utf-8")
    key = settings.secret_key.encode("utf-8")

    return hmac.new(
        key,
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_otp_hash(
    code: str,
    stored_hash: str,
    *,
    context: str,
) -> bool:
    candidate_hash = hash_otp(
        code,
        context=context,
    )

    return hmac.compare_digest(
        candidate_hash,
        stored_hash,
    )