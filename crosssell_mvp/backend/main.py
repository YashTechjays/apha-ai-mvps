from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import scores, nudges, banners, analytics, auth
from backend.db.base import Base
from backend.db.session import engine
from backend.db.models import Member, CrossSellScore, Nudge, Conversion  # noqa: F401
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA AI Cross-Sell Engine API",
    description="AI-powered product expansion engine for APhA members",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3004", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scores.router)
app.include_router(nudges.router)
app.include_router(banners.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    from backend.db.session import SessionLocal
    from backend.utils.seed_data import generate_mock_members

    db = SessionLocal()
    try:
        if db.query(Member).count() == 0:
            logger.info("Seeding 150 mock members with product usage data...")
            for m in generate_mock_members(150):
                db.add(Member(**m))
            db.commit()
            logger.info("Seeding complete.")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-crosssell-engine"}
