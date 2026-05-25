"""
SendGrid event webhooks -- open, click, bounce, unsubscribe, spam report.
These MUST be handled immediately and correctly for CAN-SPAM compliance.
"""
import hmac
import hashlib
import json
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime
from db.session import SessionLocal
from db.models.email_send import EmailSend
from db.models.prospect import Prospect
from db.models.campaign import Campaign
from delivery.suppression_manager import add_suppression
from utils.config import get_settings
from utils.logger import get_logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("/sendgrid")
async def sendgrid_webhook(request: Request):
    """Handle SendGrid event webhook batch."""
    body = await request.body()

    if settings.sendgrid_webhook_secret and settings.env != "development":
        sig = request.headers.get("X-Twilio-Email-Event-Webhook-Signature", "")
        timestamp = request.headers.get("X-Twilio-Email-Event-Webhook-Timestamp", "")
        payload_to_verify = timestamp + body.decode()
        expected = hmac.new(
            settings.sendgrid_webhook_secret.encode(),
            payload_to_verify.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    events = json.loads(body)
    if not isinstance(events, list):
        events = [events]

    db = SessionLocal()
    try:
        for event in events:
            _handle_event(event, db)
        db.commit()
    finally:
        db.close()

    return {"received": len(events)}


def _handle_event(event: dict, db):
    """Handle a single SendGrid event."""
    event_type = event.get("event", "")
    sg_msg_id = event.get("sg_message_id", "").split(".")[0]
    email = event.get("email", "").lower()
    timestamp = datetime.fromtimestamp(event.get("timestamp", 0))

    logger.info(f"Webhook: {event_type} | {email} | {sg_msg_id}")

    send = db.query(EmailSend).filter(
        EmailSend.sendgrid_message_id.like(f"{sg_msg_id}%")
    ).first()

    if event_type == "open":
        if send and not send.opened_at:
            send.opened_at = timestamp
            _update_prospect(send.prospect_id, "opened", timestamp, db)
            _update_campaign_metric(send.campaign_id, "emails_opened", db)

    elif event_type == "click":
        if send and not send.clicked_at:
            send.clicked_at = timestamp
            _update_prospect(send.prospect_id, "clicked", timestamp, db)
            _update_campaign_metric(send.campaign_id, "emails_clicked", db)

    elif event_type == "unsubscribe":
        add_suppression(email, "unsubscribe", db, "sendgrid_webhook")
        if send:
            send.unsubscribed_at = timestamp
        _update_campaign_metric(send.campaign_id if send else None, "unsubscribes", db)
        logger.info(f"Unsubscribe processed: {email}")

    elif event_type == "bounce" and event.get("type") == "bounce":
        add_suppression(email, "hard_bounce", db, "sendgrid_webhook")
        if send:
            send.bounced_at = timestamp
            send.status = "bounced"
        _update_campaign_metric(send.campaign_id if send else None, "bounces", db)

    elif event_type == "spamreport":
        add_suppression(email, "spam_report", db, "sendgrid_webhook")
        if send:
            send.spam_reported_at = timestamp


def _update_prospect(prospect_id, event: str, ts: datetime, db):
    p = db.query(Prospect).filter(Prospect.id == prospect_id).first()
    if not p:
        return
    if event == "opened":
        p.last_opened_at = ts
    elif event == "clicked":
        p.last_clicked_at = ts
        p.status = "replied"


def _update_campaign_metric(campaign_id, metric: str, db):
    if not campaign_id:
        return
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if c:
        current = getattr(c, metric, 0) or 0
        setattr(c, metric, current + 1)
