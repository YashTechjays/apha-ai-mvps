import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apps.email_app.utils.config import get_settings
from apps.email_app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    plain_text_body: str,
) -> dict:
    if settings.env == "development" or not settings.smtp_username:
        logger.info(f"[MOCK SEND] To: {to_email} | Subject: {subject}")
        return {"message_id": f"mock-{to_email}-{subject[:20]}", "status": "mock_sent"}

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{settings.from_name} <{settings.from_email}>"
    msg["To"] = f"{to_name} <{to_email}>"
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)

        message_id = str(uuid.uuid4())
        logger.info(f"Email sent to {to_email} | message_id={message_id}")
        return {"message_id": message_id, "status": "sent"}
    except Exception as exc:
        logger.error(f"SMTP error for {to_email}: {exc}")
        return {"message_id": None, "status": "failed", "error": str(exc)}
