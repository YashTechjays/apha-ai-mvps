from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import salary, interactions, career, leads, analytics
from backend.db.base import Base
from backend.db.session import engine
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA Acquisition Funnels API",
    description="AI-powered public acquisition tools for APhA",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(salary.router)
app.include_router(interactions.router)
app.include_router(career.router)
app.include_router(leads.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("APhA Acquisition Funnels API ready.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-acquisition-funnels"}
