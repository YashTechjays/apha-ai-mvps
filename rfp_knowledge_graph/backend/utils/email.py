import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.utils.logger import get_logger

logger = get_logger("email")


def send_rfp_match_email(
    to_email: str,
    to_name: str,
    rfp_title: str,
    rfp_org: str,
    rfp_deadline: str,
    match_score: int,
    rfp_id: str,
    frontend_url: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    smtp_from_email: str,
) -> bool:
    rfp_url = f"{frontend_url}/rfps/{rfp_id}"
    score_label = "Excellent" if match_score >= 80 else "Good" if match_score >= 60 else "Possible"

    subject = f"[{match_score}% Match] New RFP: {rfp_title}"

    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
      <div style="background: #1B4F8A; padding: 20px; border-radius: 8px 8px 0 0;">
        <h2 style="color: white; margin: 0;">New RFP Match Found</h2>
        <p style="color: #90b8e8; margin: 4px 0 0 0;">APhA RFP Knowledge Graph</p>
      </div>
      <div style="padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
        <p>Hi {to_name or to_email},</p>
        <p>A new RFP has been found that matches your profile with a <strong>{score_label} match score of {match_score}%</strong>.</p>
        <div style="background: #f9fafb; border-left: 4px solid #1B4F8A; padding: 16px; margin: 16px 0; border-radius: 0 8px 8px 0;">
          <h3 style="margin: 0 0 8px 0; color: #1B4F8A;">{rfp_title}</h3>
          <p style="margin: 4px 0; color: #6b7280;"><strong>Organization:</strong> {rfp_org or 'Not specified'}</p>
          <p style="margin: 4px 0; color: #6b7280;"><strong>Deadline:</strong> {rfp_deadline or 'Not specified'}</p>
          <p style="margin: 4px 0;"><strong>Match Score:</strong>
            <span style="background: {'#dcfce7' if match_score >= 80 else '#fef9c3'}; color: {'#166534' if match_score >= 80 else '#854d0e'}; padding: 2px 8px; border-radius: 12px; font-weight: bold;">
              {match_score}%
            </span>
          </p>
        </div>
        <a href="{rfp_url}" style="display: inline-block; background: #1B4F8A; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
          View RFP &amp; Generate Proposal
        </a>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
        <p style="color: #9ca3af; font-size: 12px;">
          You received this because you enabled RFP match notifications in your profile.
          <a href="{frontend_url}/profile" style="color: #6b7280;">Manage notification settings</a>
        </p>
      </div>
    </body></html>
    """

    text_body = (
        f"New RFP Match: {match_score}% match\n\n"
        f"{rfp_title}\n"
        f"Organization: {rfp_org or 'Not specified'}\n"
        f"Deadline: {rfp_deadline or 'Not specified'}\n\n"
        f"View RFP: {rfp_url}\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_from_email
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_from_email, to_email, msg.as_string())
        logger.info(f"Sent match email to {to_email} for RFP {rfp_id} ({match_score}% match)")
        return True
    except Exception as e:
        logger.error(f"Failed to send match email to {to_email}: {e}")
        return False


def send_trends_digest_email(
    to_email: str,
    to_name: str,
    summary: str,
    top_organizations: list,
    trending_categories: list,
    frontend_url: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    smtp_from_email: str,
) -> bool:
    """Weekly graph-insights digest (Enhancement #5b)."""
    org_rows = "".join(
        f"<li>{o['organization']} — {o['rfp_count']} RFPs ({o['open_count']} open)</li>"
        for o in top_organizations[:5]
    )
    cat_rows = "".join(
        f"<li>{c['category']} — {c['demand']} RFPs</li>"
        for c in trending_categories[:5]
    )
    html_body = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
      <div style="background: #1B4F8A; padding: 20px; border-radius: 8px 8px 0 0;">
        <h2 style="color: white; margin: 0;">Weekly RFP Market Trends</h2>
        <p style="color: #90b8e8; margin: 4px 0 0 0;">APhA RFP Knowledge Graph</p>
      </div>
      <div style="padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
        <p>Hi {to_name or to_email},</p>
        <p>{summary}</p>
        <h3 style="color: #1B4F8A;">Most Active Organizations</h3>
        <ul>{org_rows or '<li>No data yet</li>'}</ul>
        <h3 style="color: #1B4F8A;">Trending Categories</h3>
        <ul>{cat_rows or '<li>No data yet</li>'}</ul>
        <a href="{frontend_url}" style="display: inline-block; background: #1B4F8A; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
          View Dashboard
        </a>
      </div>
    </body></html>
    """
    text_body = f"Weekly RFP Market Trends\n\n{summary}\n\nView dashboard: {frontend_url}\n"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Weekly RFP Market Trends — APhA Knowledge Graph"
    msg["From"] = smtp_from_email
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_from_email, to_email, msg.as_string())
        logger.info(f"Sent trends digest to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send trends digest to {to_email}: {e}")
        return False
