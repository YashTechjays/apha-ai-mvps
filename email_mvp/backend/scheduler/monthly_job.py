import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.models.member import Member
from backend.db.models.email_send import EmailSend, EmailStatus
from backend.ai.benefit_valuation import compute_benefit_summary
from backend.ai.email_generator import generate_email_content
from backend.email_delivery.template_renderer import render_html, render_plain_text
from backend.email_delivery.quality_check import run_quality_check
from backend.email_delivery.sendgrid_client import send_email
from backend.pipeline.etl import run_full_sync
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def process_member_email(db: Session, member: Member, send_month: str) -> EmailSend:
    email_send = EmailSend(
        id=str(uuid.uuid4()),
        member_id=member.id,
        send_month=send_month,
        status=EmailStatus.PENDING,
    )
    db.add(email_send)

    try:
        summary = compute_benefit_summary(member, send_month)
        content = generate_email_content(summary)
        html_body = render_html(summary, content)
        plain_body = render_plain_text(summary, content)

        qc = run_quality_check(summary, content, html_body)
        email_send.qc_score = qc.score
        email_send.personalization_score = qc.personalization_score
        email_send.token_count = qc.token_count
        email_send.qc_notes = "; ".join(qc.notes) if qc.notes else None

        email_send.subject_line = content.get("subject", "")
        email_send.html_body = html_body
        email_send.plain_text_body = plain_body
        email_send.total_value_usd = summary.total_value_usd
        email_send.cpe_value_usd = summary.cpe_value_usd
        email_send.webinar_value_usd = summary.webinar_value_usd
        email_send.journal_value_usd = summary.journal_value_usd
        email_send.pharmacylibrary_value_usd = summary.pharmacylibrary_value_usd
        email_send.events_value_usd = summary.events_value_usd

        if not qc.passed:
            email_send.status = EmailStatus.QC_FAILED
            logger.warning(f"QC failed for {member.email}: score={qc.score} notes={qc.notes}")
            db.commit()
            return email_send

        email_send.status = EmailStatus.QC_PASSED
        result = send_email(
            to_email=member.email,
            to_name=f"{member.first_name} {member.last_name}",
            subject=email_send.subject_line,
            html_body=html_body,
            plain_text_body=plain_body,
        )

        if result["status"] in ("sent", "mock_sent"):
            email_send.status = EmailStatus.SENT
            email_send.sendgrid_message_id = result.get("message_id")
            email_send.sent_at = datetime.utcnow()
        else:
            email_send.status = EmailStatus.FAILED

    except Exception as exc:
        logger.error(f"Failed to process email for {member.id}: {exc}")
        email_send.status = EmailStatus.FAILED
        email_send.qc_notes = str(exc)

    db.commit()
    return email_send


def run_monthly_email_job(db: Session, send_month: str | None = None, dry_run: bool = False) -> dict:
    if not send_month:
        send_month = datetime.utcnow().strftime("%Y-%m")

    logger.info(f"Starting monthly email job for {send_month} | dry_run={dry_run}")

    sync_count = run_full_sync(db)
    logger.info(f"ETL sync complete: {sync_count} members updated")

    members = db.query(Member).filter(Member.is_active == True).all()

    results = {"total": len(members), "sent": 0, "qc_failed": 0, "failed": 0, "skipped": 0}

    batch = members if not settings.pilot_batch_size else members[:settings.pilot_batch_size]

    for member in batch:
        if dry_run:
            summary = compute_benefit_summary(member, send_month)
            logger.info(f"[DRY RUN] {member.email} | value=${summary.total_value_usd:.0f} | roi={summary.roi_multiplier}x")
            results["skipped"] += 1
            continue

        send = process_member_email(db, member, send_month)
        if send.status == EmailStatus.SENT:
            results["sent"] += 1
        elif send.status == EmailStatus.QC_FAILED:
            results["qc_failed"] += 1
        else:
            results["failed"] += 1

    logger.info(f"Monthly email job complete: {results}")
    return results
