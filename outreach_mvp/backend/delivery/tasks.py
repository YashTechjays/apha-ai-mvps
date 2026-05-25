"""Celery tasks for async email generation and sending."""
from celery import Celery
from utils.config import get_settings

settings = get_settings()
celery_app = Celery(
    "outreach",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.beat_schedule = {
    "process-send-queue-every-5-min": {
        "task": "process_send_queue",
        "schedule": 300,
    },
}


@celery_app.task(name="generate_sequence_for_prospect")
def generate_sequence_for_prospect(prospect_id: str, campaign_id: str):
    """Generate all 3 touch emails for a prospect asynchronously."""
    from db.session import SessionLocal
    from db.models.prospect import Prospect
    from db.models.email_send import EmailSend
    from ai.email_writer import generate_full_sequence
    from datetime import datetime, timedelta
    from utils.logger import get_logger

    logger = get_logger("tasks")
    db = SessionLocal()
    try:
        prospect = db.query(Prospect).filter(Prospect.id == prospect_id).first()
        if not prospect:
            return {"error": "Prospect not found"}

        sequence = generate_full_sequence(prospect)

        base_date = datetime.utcnow()
        delays = [0, 5, 10]

        for touch in sequence:
            touch_num = touch["touch_number"]
            scheduled = base_date + timedelta(days=delays[touch_num - 1])
            send = EmailSend(
                prospect_id=prospect.id,
                campaign_id=campaign_id,
                touch_number=touch_num,
                subject=touch["subject"],
                body_text=touch["body"],
                icp_score=prospect.icp_score,
                status="pending",
                scheduled_for=scheduled,
            )
            db.add(send)

        prospect.status = "queued"
        db.commit()
        logger.info(f"Sequence generated for prospect {prospect_id}")
        return {"generated": 3, "prospect_id": prospect_id}
    finally:
        db.close()


@celery_app.task(name="process_send_queue")
def process_send_queue():
    """Process scheduled emails that are due to send."""
    from db.session import SessionLocal
    from db.models.email_send import EmailSend
    from db.models.prospect import Prospect
    from delivery.suppression_manager import is_suppressed
    from delivery.deliverability import (
        is_send_window_open, check_hourly_rate, check_daily_rate, check_domain_throttle
    )
    from delivery.sendgrid_client import send_email
    from utils.logger import get_logger
    from datetime import datetime

    logger = get_logger("tasks.send_queue")
    db = SessionLocal()
    sent = skipped = failed = 0

    try:
        if not is_send_window_open():
            logger.info("Outside send window -- skipping")
            return

        due_sends = db.query(EmailSend).filter(
            EmailSend.status == "pending",
            EmailSend.scheduled_for <= datetime.utcnow(),
        ).limit(50).all()

        for email_send in due_sends:
            prospect = db.query(Prospect).filter(
                Prospect.id == email_send.prospect_id
            ).first()

            if not prospect or not prospect.email:
                email_send.status = "skipped"
                skipped += 1
                continue

            if prospect.do_not_contact or is_suppressed(prospect.email, db):
                email_send.status = "suppressed"
                skipped += 1
                continue

            hourly_ok, _ = check_hourly_rate(str(email_send.campaign_id))
            daily_ok, _ = check_daily_rate(str(email_send.campaign_id))
            if not hourly_ok or not daily_ok:
                logger.info("Rate limit reached -- stopping batch")
                break

            domain = prospect.email.split("@")[-1]
            if not check_domain_throttle(domain):
                skipped += 1
                continue

            try:
                msg_id = send_email(
                    to_email=prospect.email,
                    to_name=f"{prospect.first_name} {prospect.last_name}",
                    subject=email_send.subject,
                    body_text=email_send.body_text,
                    prospect_id=str(prospect.id),
                    campaign_id=str(email_send.campaign_id),
                )
                email_send.status = "sent"
                email_send.sent_at = datetime.utcnow()
                email_send.sendgrid_message_id = msg_id

                prospect.emails_sent = (prospect.emails_sent or 0) + 1
                prospect.last_email_sent_at = datetime.utcnow()
                if prospect.status == "queued":
                    prospect.status = "contacted"

                db.commit()
                sent += 1
            except Exception as e:
                logger.error(f"Send failed for {prospect.email}: {e}")
                email_send.status = "failed"
                db.commit()
                failed += 1

        logger.info(f"Send queue processed: sent={sent} skipped={skipped} failed={failed}")
        return {"sent": sent, "skipped": skipped, "failed": failed}
    finally:
        db.close()
