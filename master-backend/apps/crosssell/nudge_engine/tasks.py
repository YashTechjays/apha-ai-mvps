from celery import Celery
from apps.crosssell.utils.config import get_settings

settings = get_settings()
celery_app = Celery("crosssell", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="run_weekly_crosssell_scoring")
def run_weekly_crosssell_scoring():
    from apps.crosssell.db.session import SessionLocal
    from apps.crosssell.ml.score import run_batch_scoring
    db = SessionLocal()
    try:
        return run_batch_scoring(db)
    finally:
        db.close()


@celery_app.task(name="send_batch_email_nudges")
def send_batch_email_nudges(campaign_id: str = None):
    from apps.crosssell.db.session import SessionLocal
    from apps.crosssell.db.models.member import Member
    from apps.crosssell.nudge_engine.router import get_top_opportunity
    from apps.crosssell.nudge_engine.email_sender import send_email_nudge

    db = SessionLocal()
    try:
        members = db.query(Member).filter(Member.is_active == True).all()
        sent = 0
        for member in members:
            score, channel = get_top_opportunity(member, db)
            if score and channel == "email":
                send_email_nudge(member, score, db)
                sent += 1
        return {"sent": sent}
    finally:
        db.close()
