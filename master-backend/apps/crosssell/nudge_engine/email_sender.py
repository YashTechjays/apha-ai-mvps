import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText

from sqlalchemy.orm import Session
from apps.crosssell.db.models.member import Member
from apps.crosssell.db.models.nudge import Nudge
from apps.crosssell.db.models.crosssell_score import CrossSellScore
from apps.crosssell.ai.message_generator import generate_email_nudge
from apps.crosssell.utils.config import get_settings
from apps.crosssell.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def send_email_nudge(member: Member, score: CrossSellScore, db: Session) -> Nudge:
    content = generate_email_nudge(member, score)

    nudge = Nudge(
        member_id=member.id,
        product=score.product,
        channel="email",
        expansion_score=score.score,
        subject_line=content["subject"],
        message_body=content["body"],
        cta_url=content["cta_url"],
        cta_label=content["cta_label"],
        status="pending",
    )
    db.add(nudge)
    db.commit()
    db.refresh(nudge)

    if settings.env == "development" or not settings.smtp_username:
        logger.info(
            f"[EMAIL MOCK] To: {member.email} | "
            f"Subject: {content['subject']} | Product: {score.product}"
        )
        nudge.status = "sent"
        nudge.sent_at = datetime.utcnow()
        nudge.sendgrid_message_id = f"mock-{str(nudge.id)[:8]}"
    else:
        try:
            msg = MIMEText(content["body"], "plain")
            msg["From"] = f"APhA Membership Team <{settings.from_email}>"
            msg["To"] = member.email
            msg["Subject"] = content["subject"]

            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)

            nudge.status = "sent"
            nudge.sent_at = datetime.utcnow()
            nudge.sendgrid_message_id = str(uuid.uuid4())
        except Exception as e:
            logger.error(f"Email send failed for {member.email}: {e}")
            nudge.status = "failed"

    db.commit()
    return nudge
