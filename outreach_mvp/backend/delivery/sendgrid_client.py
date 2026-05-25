"""
SendGrid email delivery wrapper.
Handles transactional sends + tracking pixel + unsubscribe header.
"""
import sendgrid
from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking, OpenTracking
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def build_html_email(body_text: str, prospect_id: str, unsubscribe_url: str) -> str:
    """Wrap plain text body in minimal HTML with CAN-SPAM footer."""
    paragraphs = "".join(f"<p>{p}</p>" for p in body_text.strip().split("\n\n") if p.strip())
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;font-size:14px;line-height:1.7;color:#333;max-width:600px;margin:0 auto;padding:20px">
  {paragraphs}
  <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
  <p style="font-size:11px;color:#888;line-height:1.5">
    American Pharmacists Association<br>
    {settings.physical_address}<br><br>
    You are receiving this because you are a licensed pharmacist in the US.<br>
    <a href="{unsubscribe_url}?id={prospect_id}" style="color:#888">Unsubscribe</a> &nbsp;|&nbsp;
    <a href="https://www.pharmacist.com" style="color:#888">pharmacist.com</a>
  </p>
</body>
</html>"""


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    body_text: str,
    prospect_id: str,
    campaign_id: str,
) -> str:
    """
    Send a single email via SendGrid. Returns SendGrid message ID.
    MVP: mock mode if no API key. Production: set SENDGRID_API_KEY.
    """
    html_body = build_html_email(
        body_text, prospect_id, settings.unsubscribe_url
    )

    if settings.env == "development" or not settings.sendgrid_api_key:
        mock_id = f"mock-{prospect_id[:8]}-{campaign_id[:4]}"
        logger.info(f"[SENDGRID MOCK] To: {to_email} | Subject: {subject}")
        return mock_id

    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        message = Mail(
            from_email=(settings.from_email, settings.from_name),
            to_emails=to_email,
            subject=subject,
            plain_text_content=body_text,
            html_content=html_body,
        )
        message.header = {
            "X-Campaign-ID": campaign_id,
            "X-Prospect-ID": prospect_id,
            "List-Unsubscribe": f"<{settings.unsubscribe_url}?id={prospect_id}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
        tracking = TrackingSettings()
        tracking.click_tracking = ClickTracking(enable=True)
        tracking.open_tracking = OpenTracking(enable=True)
        message.tracking_settings = tracking

        response = sg.send(message)
        msg_id = response.headers.get("X-Message-Id", "unknown")
        logger.info(f"Sent: {to_email} | MsgID: {msg_id}")
        return msg_id
    except Exception as e:
        logger.error(f"SendGrid error for {to_email}: {e}")
        raise
