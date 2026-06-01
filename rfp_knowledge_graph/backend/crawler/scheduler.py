from datetime import datetime
from celery import Celery
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("crawler_scheduler")
settings = get_settings()

celery_app = Celery(
    "rfp_crawler",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.beat_schedule = {
    "scheduled-crawl": {
        "task": "backend.crawler.scheduler.scheduled_crawl",
        "schedule": settings.crawl_interval_hours * 3600,
    },
    "weekly-trends-digest": {
        "task": "backend.crawler.scheduler.send_weekly_trends_digest",
        "schedule": 7 * 24 * 3600,  # weekly
    },
}
celery_app.conf.timezone = "UTC"


@celery_app.task(name="backend.crawler.scheduler.notify_new_rfp_matches")
def notify_new_rfp_matches(new_rfp_ids: list):
    """For each new RFP, score against all active pharmacist profiles and email those above threshold."""
    if not new_rfp_ids:
        return

    from backend.db.session import SessionLocal
    from backend.db.models.user import User, UserRole
    from backend.graph.queries import get_rfp_detail
    from backend.ai.matcher import score_rfp_for_profile
    from backend.utils.email import send_rfp_match_email

    db = SessionLocal()
    try:
        pharmacists = db.query(User).filter(
            User.role == UserRole.pharmacist,
            User.is_active == True,
        ).all()

        if not pharmacists:
            logger.info("No active pharmacists to notify")
            return

        sent = 0
        for rfp_id in new_rfp_ids:
            rfp = get_rfp_detail(rfp_id)
            if not rfp:
                continue

            org = rfp.get("organization") or {}
            rfp_for_scoring = {
                **rfp,
                "org_type": org.get("type") if isinstance(org, dict) else None,
                "location_state": (rfp.get("location") or {}).get("state"),
            }

            for user in pharmacists:
                profile = user.profile
                if not profile or not profile.notify_on_match:
                    continue

                profile_dict = {
                    "specialties": profile.specialties or [],
                    "certifications": profile.certifications or [],
                    "location_state": profile.location_state,
                    "org_types_preferred": profile.org_types_preferred or [],
                }

                score = score_rfp_for_profile(rfp_for_scoring, profile_dict)
                if score < profile.notify_threshold:
                    continue

                send_rfp_match_email(
                    to_email=user.email,
                    to_name=profile.full_name or user.username,
                    rfp_title=rfp["title"],
                    rfp_org=org.get("name") if isinstance(org, dict) else "",
                    rfp_deadline=rfp.get("deadline") or "",
                    match_score=score,
                    rfp_id=rfp_id,
                    frontend_url=settings.frontend_url,
                    smtp_host=settings.smtp_host,
                    smtp_port=settings.smtp_port,
                    smtp_username=settings.smtp_username,
                    smtp_password=settings.smtp_password,
                    smtp_from_email=settings.smtp_from_email,
                )
                sent += 1

        logger.info(f"Notification task complete: {sent} emails sent for {len(new_rfp_ids)} new RFPs")
    finally:
        db.close()


@celery_app.task(name="backend.crawler.scheduler.send_weekly_trends_digest")
def send_weekly_trends_digest():
    """Enhancement #5b — email active pharmacists a weekly graph-trends digest."""
    from backend.db.session import SessionLocal
    from backend.db.models.user import User, UserRole
    from backend.ai.graph_insights import get_insights, summarize_insights
    from backend.utils.email import send_trends_digest_email

    insights = get_insights(limit=10)
    summary = summarize_insights(insights)

    db = SessionLocal()
    try:
        pharmacists = db.query(User).filter(
            User.role == UserRole.pharmacist,
            User.is_active == True,
        ).all()
        sent = 0
        for user in pharmacists:
            profile = user.profile
            if not profile or not profile.notify_on_match:
                continue
            ok = send_trends_digest_email(
                to_email=user.email,
                to_name=profile.full_name or user.username,
                summary=summary,
                top_organizations=insights["top_organizations"],
                trending_categories=insights["trending_categories"],
                frontend_url=settings.frontend_url,
                smtp_host=settings.smtp_host,
                smtp_port=settings.smtp_port,
                smtp_username=settings.smtp_username,
                smtp_password=settings.smtp_password,
                smtp_from_email=settings.smtp_from_email,
            )
            sent += 1 if ok else 0
        logger.info(f"Weekly trends digest sent to {sent} pharmacists")
    finally:
        db.close()


@celery_app.task(name="backend.crawler.scheduler.run_crawl_job")
def run_crawl_job(job_id: str):
    from backend.db.session import SessionLocal
    from backend.db.models.crawl_job import CrawlJob, CrawlStatus
    from backend.crawler.firecrawl_client import crawl_url
    from backend.ai.entity_extractor import extract_rfp_entities
    from backend.graph.queries import create_rfp_with_relations

    db = SessionLocal()
    try:
        job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = CrawlStatus.running
        job.started_at = datetime.utcnow()
        db.commit()

        new_rfp_ids = []
        try:
            pages = crawl_url(job.url, max_pages=settings.max_pages_per_crawl, include_patterns=job.include_patterns)
            job.pages_crawled = len(pages)

            total_rfps = 0
            for page in pages:
                if not page.get("markdown"):
                    continue
                rfps = extract_rfp_entities(page["markdown"], page["url"])
                for rfp_data in rfps:
                    if not rfp_data.get("url"):
                        rfp_data["url"] = page["url"]
                    rfp_id = create_rfp_with_relations(rfp_data)
                    new_rfp_ids.append(rfp_id)
                    total_rfps += 1

            job.rfps_extracted = total_rfps
            job.status = CrawlStatus.completed
            job.completed_at = datetime.utcnow()
            logger.info(f"Job {job_id} completed: {len(pages)} pages, {total_rfps} RFPs")

        except Exception as e:
            job.status = CrawlStatus.failed
            job.error_message = str(e)[:500]
            job.completed_at = datetime.utcnow()
            logger.error(f"Job {job_id} failed: {e}")

        db.commit()

        # Fire-and-forget notification task after successful crawl
        if new_rfp_ids:
            notify_new_rfp_matches.delay(new_rfp_ids)
            logger.info(f"Queued notifications for {len(new_rfp_ids)} RFPs")

    finally:
        db.close()


@celery_app.task(name="backend.crawler.scheduler.scheduled_crawl")
def scheduled_crawl():
    from backend.crawler.targets import CRAWL_TARGETS
    from backend.db.session import SessionLocal
    from backend.db.models.crawl_job import CrawlJob

    logger.info("Running scheduled crawl for all targets")
    db = SessionLocal()
    try:
        for target in CRAWL_TARGETS:
            job = CrawlJob(
                url=target["url"],
                include_patterns=target.get("include_patterns"),
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            run_crawl_job.delay(str(job.id))
            logger.info(f"Queued crawl job for {target['url']}")
    finally:
        db.close()
