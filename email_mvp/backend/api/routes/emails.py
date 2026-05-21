from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.db.models.email_send import EmailSend
from backend.api.schemas.email_send import EmailSendResponse, EmailPreviewResponse
from backend.ai.benefit_valuation import compute_benefit_summary
from backend.ai.email_generator import generate_email_content
from backend.email_delivery.template_renderer import render_html
from backend.scheduler.monthly_job import run_monthly_email_job, process_member_email

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/", response_model=List[EmailSendResponse])
def list_email_sends(
    send_month: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(EmailSend)
    if send_month:
        q = q.filter(EmailSend.send_month == send_month)
    if status:
        q = q.filter(EmailSend.status == status)
    return q.order_by(EmailSend.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/member/{member_id}", response_model=List[EmailSendResponse])
def get_member_emails(member_id: str, db: Session = Depends(get_db)):
    return (
        db.query(EmailSend)
        .filter(EmailSend.member_id == member_id)
        .order_by(EmailSend.created_at.desc())
        .all()
    )


@router.get("/preview/{member_id}", response_model=EmailPreviewResponse)
def preview_email(member_id: str, send_month: str | None = None, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    month = send_month or datetime.utcnow().strftime("%Y-%m")
    summary = compute_benefit_summary(member, month)
    content = generate_email_content(summary)
    html_body = render_html(summary, content)
    return EmailPreviewResponse(
        member_id=member.id,
        member_email=member.email,
        send_month=month,
        subject=content.get("subject", ""),
        preview_text=content.get("preview_text", ""),
        total_value_usd=summary.total_value_usd,
        roi_multiplier=summary.roi_multiplier,
        engagement_level=summary.engagement_level,
        html_body=html_body,
    )


@router.post("/send/{member_id}", response_model=EmailSendResponse)
def send_single_email(member_id: str, send_month: str | None = None, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    month = send_month or datetime.utcnow().strftime("%Y-%m")
    send = process_member_email(db, member, month)
    return send


@router.post("/run-batch")
def run_batch(
    send_month: str | None = None,
    dry_run: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    month = send_month or datetime.utcnow().strftime("%Y-%m")
    results = run_monthly_email_job(db, send_month=month, dry_run=dry_run)
    return {"send_month": month, "dry_run": dry_run, **results}


@router.post("/webhook/sendgrid")
async def sendgrid_webhook(events: list[dict], db: Session = Depends(get_db)):
    import uuid
    from backend.db.models.email_event import EmailEvent

    processed = 0
    for event in events:
        sg_id = event.get("sg_message_id", "")
        send = db.query(EmailSend).filter(EmailSend.sendgrid_message_id == sg_id).first()
        if not send:
            continue

        event_type = event.get("event", "")
        ev = EmailEvent(
            id=str(uuid.uuid4()),
            email_send_id=send.id,
            member_id=send.member_id,
            event_type=event_type,
            sendgrid_event_id=sg_id,
            url_clicked=event.get("url"),
            user_agent=event.get("useragent"),
            ip_address=event.get("ip"),
            raw_payload=event,
        )
        db.add(ev)

        if event_type == "open" and not send.opened:
            send.opened = True
            send.first_open_at = datetime.utcnow()
        elif event_type == "click":
            send.clicked = True
            send.click_count += 1
            if not send.first_click_at:
                send.first_click_at = datetime.utcnow()

        processed += 1

    db.commit()
    return {"processed": processed}
