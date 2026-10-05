from fastapi import APIRouter, HTTPException, status

from app.schemas.contact import ContactRequest, ContactResponse
from app.services.email import EmailDeliveryError, send_contact_message

router = APIRouter()


@router.post("", response_model=ContactResponse)
def contact(payload: ContactRequest):
    try:
        send_contact_message(
            sender_name=payload.name.strip(),
            sender_email=payload.email.lower().strip(),
            subject=payload.subject.strip(),
            body=payload.message.strip(),
        )
    except EmailDeliveryError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AGP could not deliver your message at this time. Please try again later.",
        )
    return ContactResponse(message="Your message has been sent to Africa & Global Power.")
