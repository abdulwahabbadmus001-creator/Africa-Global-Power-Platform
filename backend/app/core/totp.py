import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

from app.core.config import settings


TOTP_DIGITS = 6
TOTP_PERIOD = 30

RECOVERY_ALPHABET = (
    "ABCDEFGHJKLMNPQRSTUVWXYZ"
    "23456789"
)


def generate_editor_totp_secret(
    user_id: str,
    generation: int,
) -> str:
    message = (
        f"editorial-mfa:{user_id}:{generation}"
    ).encode("utf-8")

    digest = hmac.new(
        settings.mfa_secret_key.encode("utf-8"),
        message,
        hashlib.sha256,
    ).digest()

    secret_bytes = digest[:20]

    return (
        base64.b32encode(secret_bytes)
        .decode("ascii")
        .rstrip("=")
    )


def _decode_base32(
    secret: str,
) -> bytes:
    normalized = secret.strip().upper()

    padding = (
        8 - len(normalized) % 8
    ) % 8

    normalized += "=" * padding

    return base64.b32decode(
        normalized,
        casefold=True,
    )


def _totp_for_counter(
    secret: str,
    counter: int,
) -> str:
    key = _decode_base32(secret)

    counter_bytes = struct.pack(
        ">Q",
        counter,
    )

    digest = hmac.new(
        key,
        counter_bytes,
        hashlib.sha1,
    ).digest()

    offset = digest[-1] & 0x0F

    binary = (
        ((digest[offset] & 0x7F) << 24)
        | (digest[offset + 1] << 16)
        | (digest[offset + 2] << 8)
        | digest[offset + 3]
    )

    value = binary % (
        10 ** TOTP_DIGITS
    )

    return f"{value:0{TOTP_DIGITS}d}"


def current_totp(
    secret: str,
) -> str:
    counter = int(
        time.time() // TOTP_PERIOD
    )

    return _totp_for_counter(
        secret,
        counter,
    )


def verify_totp(
    secret: str,
    code: str,
    *,
    window: int = 1,
) -> bool:
    normalized = (
        code.strip()
        .replace(" ", "")
    )

    if (
        len(normalized)
        != TOTP_DIGITS
        or not normalized.isdigit()
    ):
        return False

    current_counter = int(
        time.time() // TOTP_PERIOD
    )

    for offset in range(
        -window,
        window + 1,
    ):
        candidate = _totp_for_counter(
            secret,
            current_counter + offset,
        )

        if hmac.compare_digest(
            candidate,
            normalized,
        ):
            return True

    return False


def build_otpauth_uri(
    *,
    secret: str,
    email: str,
) -> str:
    issuer = settings.mfa_issuer

    label = quote(
        f"{issuer}:{email}",
        safe="",
    )

    encoded_issuer = quote(
        issuer,
        safe="",
    )

    return (
        f"otpauth://totp/{label}"
        f"?secret={secret}"
        f"&issuer={encoded_issuer}"
        f"&algorithm=SHA1"
        f"&digits={TOTP_DIGITS}"
        f"&period={TOTP_PERIOD}"
    )


def generate_recovery_code() -> str:
    raw = "".join(
        secrets.choice(
            RECOVERY_ALPHABET
        )
        for _ in range(12)
    )

    return (
        f"AGP-{raw[:4]}-"
        f"{raw[4:8]}-"
        f"{raw[8:12]}"
    )


def normalize_recovery_code(
    code: str,
) -> str:
    return (
        code.strip()
        .upper()
        .replace("-", "")
        .replace(" ", "")
    )


def hash_recovery_code(
    *,
    user_id: str,
    code: str,
) -> str:
    normalized = (
        normalize_recovery_code(
            code,
        )
    )

    message = (
        f"recovery:{user_id}:"
        f"{normalized}"
    ).encode("utf-8")

    return hmac.new(
        settings.mfa_secret_key.encode(
            "utf-8"
        ),
        message,
        hashlib.sha256,
    ).hexdigest()