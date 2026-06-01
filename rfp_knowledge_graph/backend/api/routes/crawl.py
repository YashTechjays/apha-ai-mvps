from fastapi import APIRouter, Depends, HTTPException
from backend.api.deps import get_current_user
from backend.api.schemas.crawl import CrawlTriggerRequest, CrawlTriggerResponse, CrawlJobResponse
from backend.db.session import SessionLocal
from backend.db.models.crawl_job import CrawlJob, CrawlStatus
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/crawl", tags=["crawl"])
logger = get_logger("crawl_routes")


@router.post("/trigger", response_model=CrawlTriggerResponse)
def trigger_crawl(body: CrawlTriggerRequest = None, _=Depends(get_current_user)):
    from backend.crawler.scheduler import run_crawl_job

    db = SessionLocal()
    try:
        url = (body.url if body and body.url else "https://www.pharmacist.com")
        job = CrawlJob(url=url, status=CrawlStatus.pending)
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = str(job.id)
    finally:
        db.close()

    try:
        run_crawl_job.delay(job_id)
    except Exception as e:
        logger.warning(f"Celery not available, running sync: {e}")
        try:
            run_crawl_job(job_id)
        except Exception as sync_err:
            logger.error(f"Sync crawl failed: {sync_err}")

    return CrawlTriggerResponse(
        job_id=job_id,
        status="pending",
        message=f"Crawl job queued for {url}",
    )


@router.get("/status", response_model=list[CrawlJobResponse])
def crawl_status(_=Depends(get_current_user)):
    db = SessionLocal()
    try:
        jobs = db.query(CrawlJob).order_by(CrawlJob.created_at.desc()).limit(20).all()
        return [CrawlJobResponse.model_validate(j) for j in jobs]
    finally:
        db.close()


@router.get("/status/{job_id}", response_model=CrawlJobResponse)
def crawl_job_status(job_id: str, _=Depends(get_current_user)):
    db = SessionLocal()
    try:
        job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return CrawlJobResponse.model_validate(job)
    finally:
        db.close()
