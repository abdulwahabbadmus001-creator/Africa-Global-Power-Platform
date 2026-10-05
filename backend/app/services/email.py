import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def _send_email(*, recipient: str, subject: str, text_body: str) -> None:
    mode = settings.email_delivery_mode.lower().strip()

    if mode == "console":
        print("\nAGP DEVELOPMENT EMAIL")
        print(f"To: {recipient}")
        print(f"Subject: {subject}\n")
        print(text_body)
        print("")
        return

    if mode != "smtp":
        raise EmailDeliveryError(f"Unsupported EMAIL_DELIVERY_MODE: {mode}")

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


def send_contact_message(*, sender_name: str, sender_email: str, subject: str, body: str) -> None:
    recipient = settings.contact_recipient_email or settings.email_from or settings.smtp_username
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
