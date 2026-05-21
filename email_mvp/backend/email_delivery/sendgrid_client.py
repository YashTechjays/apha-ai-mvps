from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, MimeType
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    plain_text_body: str,
) -> dict:
    if settings.env == "development" or not settings.sendgrid_api_key:
        logger.info(f"[MOCK SEND] To: {to_email} | Subject: {subject}")
        return {"message_id": f"mock-{to_email}-{subject[:20]}", "status": "mock_sent"}

    message = Mail(
        from_email=(settings.from_email, settings.from_name),
        to_emails=[(to_email, to_name)],
        subject=subject,
    )
    message.content = [
        Content(MimeType.text, plain_text_body),
        Content(MimeType.html, html_body),
    ]

    try:
        client = SendGridAPIClient(settings.sendgrid_api_key)
        response = client.send(message)
        message_id = response.headers.get("X-Message-Id", "")
        logger.info(f"Email sent to {to_email} | message_id={message_id} | status={response.status_code}")
        return {"message_id": message_id, "status": "sent"}
    except Exception as exc:
        logger.error(f"SendGrid error for {to_email}: {exc}")
        return {"message_id": None, "status": "failed", "error": str(exc)}
