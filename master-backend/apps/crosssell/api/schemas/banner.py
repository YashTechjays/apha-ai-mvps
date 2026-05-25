from pydantic import BaseModel


class BannerResponse(BaseModel):
    nudge_id: str
    product: str
    icon: str
    headline: str
    body: str
    cta_label: str
    cta_url: str
    expansion_score: float
    has_banner: bool = True
