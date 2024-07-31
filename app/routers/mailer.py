from fastapi import APIRouter, HTTPException, status

from app.services.mail_sender import send_mail


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar correo electrónico")
async def send_email(email: dict):
    """Send an email."""
    try:
        send_mail(
            send_to=email.get("send_to"),
            subject=email.get("subject"),
            message=email.get("message"),
            files=email.get("files")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    return {"message": "Email sent successfully."}