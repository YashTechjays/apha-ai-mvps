from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import auth, members, scores, alerts
from backend.db.base import Base
from backend.db.session import engine
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA Churn Prediction API",
    description="ML-powered member churn prediction for the American Pharmacists Association",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(members.router)
app.include_router(scores.router)
app.include_router(alerts.router)


@app.on_event("startup")
async def startup():
    logger.info("Creating DB tables...")
    Base.metadata.create_all(bind=engine)

    from backend.db.session import SessionLocal
    from backend.db.models.member import Member
    from backend.utils.seed_data import generate_mock_members

    db = SessionLocal()
    try:
        count = db.query(Member).count()
        if count == 0:
            logger.info("Seeding mock member data...")
            members_data = generate_mock_members(200)
            from backend.db.models.member import Member as MemberModel
            for m in members_data:
                db.add(MemberModel(**m))
            db.commit()
            logger.info(f"Seeded {len(members_data)} mock members.")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-churn-api"}
