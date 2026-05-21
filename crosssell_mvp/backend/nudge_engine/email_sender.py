from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.db.models.nudge import Nudge
from backend.db.models.crosssell_score import CrossSellScore
from backend.ai.message_generator import generate_email_nudge
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

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

    if settings.env == "development" or not settings.sendgrid_api_key:
        logger.info(
            f"[EMAIL MOCK] To: {member.email} | "
            f"Subject: {content['subject']} | Product: {score.product}"
        )
        nudge.status = "sent"
        nudge.sent_at = datetime.utcnow()
        nudge.sendgrid_message_id = f"mock-{str(nudge.id)[:8]}"
    else:
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
            msg = Mail(
                from_email=(settings.from_email, "APhA Membership Team"),
                to_emails=member.email,
                subject=content["subject"],
                plain_text_content=content["body"],
            )
            resp = sg.send(msg)
            nudge.status = "sent"
            nudge.sent_at = datetime.utcnow()
            nudge.sendgrid_message_id = resp.headers.get("X-Message-Id", "unknown")
        except Exception as e:
            logger.error(f"Email send failed for {member.email}: {e}")
            nudge.status = "failed"

    db.commit()
    return nudge
