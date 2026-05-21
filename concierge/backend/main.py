from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import chat, leads, analytics
from backend.db.base import Base
from backend.db.session import engine
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA AI Membership Concierge API",
    description="AI-powered membership concierge for the American Pharmacists Association",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(leads.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    logger.info("Creating DB tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Initializing vector store...")
    from backend.rag.retriever import get_vector_store
    get_vector_store()
    logger.info("Concierge API ready.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-concierge-api"}
