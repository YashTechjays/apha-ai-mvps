from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from backend.db.session import get_db
from backend.db.models.member import Member
from backend.api.schemas.banner import BannerResponse
from backend.nudge_engine.router import get_top_opportunity
from backend.nudge_engine.banner_builder import build_banner

router = APIRouter(prefix="/banners", tags=["banners"])


def _empty_banner() -> BannerResponse:
    return BannerResponse(
        nudge_id="none", product="", icon="", headline="",
        body="", cta_label="", cta_url="", expansion_score=0, has_banner=False,
    )


@router.get("/{member_id}", response_model=BannerResponse)
def get_banner_for_member(member_id: UUID, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        return _empty_banner()

    score, channel = get_top_opportunity(member, db)
    if not score or channel != "banner":
        return _empty_banner()

    payload = build_banner(member, score, db)
    return BannerResponse(**payload, has_banner=True)
