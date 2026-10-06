import json
import smtplib
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def _send_via_smtp(*, recipient: str, subject: str, text_body: str) -> None:
    if not settings.smtp_host or not settings.smtp_username or not settings.smtp_password:
        raise EmailDeliveryError("SMTP is not fully configured")

    sender = settings.email_from or settings.smtp_username
    message = EmailMessage()
    message["From"] = f"{settings.email_from_name} <{sender}>"
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            smtp.ehlo()
            if settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    except Exception as exc:
        raise EmailDeliveryError(str(exc)) from exc


def _send_via_brevo_api(*, recipient: str, subject: str, text_body: str) -> None:
    if not settings.brevo_api_key:
        raise EmailDeliveryError("BREVO_API_KEY is not configured")

    if not settings.email_from:
        raise EmailDeliveryError("EMAIL_FROM is required for Brevo API delivery")

    payload = {
        "sender": {
            "name": settings.email_from_name,
            "email": settings.email_from,
        },
        "to": [{"email": recipient}],
        "subject": subject,
        "textContent": text_body,
    }

    request = Request(
        settings.brevo_api_url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "accept": "application/json",
            "api-key": settings.brevo_api_key,
            "content-type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=20) as response:
            if response.status < 200 or response.status >= 300:
                raise EmailDeliveryError(
                    f"Brevo API returned HTTP {response.status}"
                )
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = ""
        message = f"Brevo API returned HTTP {exc.code}"
        if detail:
            message = f"{message}: {detail[:500]}"
            print(f"BREVO EMAIL ERROR: {message}", flush=True)
        raise EmailDeliveryError(message) from exc
    except URLError as exc:
        raise EmailDeliveryError(f"Brevo API network error: {exc.reason}") from exc
    except TimeoutError as exc:
        raise EmailDeliveryError("Brevo API request timed out") from exc


def _send_email(*, recipient: str, subject: str, text_body: str) -> None:
    mode = settings.email_delivery_mode.lower().strip()

    if mode == "console":
        print("\nAGP DEVELOPMENT EMAIL")
        print(f"To: {recipient}")
        print(f"Subject: {subject}\n")
        print(text_body)
        print("")
        return

    if mode == "smtp":
        _send_via_smtp(
            recipient=recipient,
            subject=subject,
            text_body=text_body,
        )
        return

    if mode == "brevo_api":
        _send_via_brevo_api(
            recipient=recipient,
            subject=subject,
            text_body=text_body,
        )
        return

    raise EmailDeliveryError(f"Unsupported EMAIL_DELIVERY_MODE: {mode}")


def send_registration_otp(*, recipient: str, first_name: str, code: str) -> None:
    _send_email(
        recipient=recipient,
        subject="Verify your Africa & Global Power account",
        text_body=(
            f"Hello {first_name},\n\n"
            f"Your AGP account verification code is: {code}\n\n"
            "The code expires in 10 minutes and can only be used once. "
            "If you did not create this account, you can ignore this email.\n\n"
            "Africa & Global Power"
        ),
    )


def send_login_otp(*, recipient: str, first_name: str, code: str) -> None:
    _send_email(
        recipient=recipient,
        subject="Your Africa & Global Power sign-in code",
        text_body=(
            f"Hello {first_name},\n\n"
            f"Your AGP sign-in verification code is: {code}\n\n"
            "The code expires in 10 minutes and can only be used once. "
            "If you did not attempt to sign in, change your password and contact AGP.\n\n"
            "Africa & Global Power"
        ),
    )


def send_password_reset_otp(*, recipient: str, first_name: str, code: str) -> None:
    _send_email(
        recipient=recipient,
        subject="Reset your Africa & Global Power password",
        text_body=(
            f"Hello {first_name},\n\n"
            f"Your AGP password recovery code is: {code}\n\n"
            "The code expires in 10 minutes and can only be used once. "
            "If you did not request a password reset, do not share this code.\n\n"
            "Africa & Global Power"
        ),
    )


def send_contact_message(
    *,
    sender_name: str,
    sender_email: str,
    subject: str,
    body: str,
) -> None:
    recipient = (
        settings.contact_recipient_email
        or settings.email_from
        or settings.smtp_username
    )
    if not recipient:
        raise EmailDeliveryError("CONTACT_RECIPIENT_EMAIL is not configured")

    _send_email(
        recipient=recipient,
        subject=f"AGP Contact: {subject}",
        text_body=(
            f"From: {sender_name} <{sender_email}>\n\n"
            f"{body}\n"
        ),
    )
