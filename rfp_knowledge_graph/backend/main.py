from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import (
    auth, rfps, crawl, graph, recommendations, users, matches, applications,
    foresight, coalition, simulator, copilot,
)
from backend.db.base import Base
from backend.db.session import engine
from backend.db.models.crawl_job import CrawlJob  # noqa: F401
from backend.db.models.user import User  # noqa: F401
from backend.db.models.pharmacist_profile import PharmacistProfile  # noqa: F401
from backend.db.models.application import Application  # noqa: F401
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA RFP Knowledge Graph API",
    description="AI-powered pharmacy RFP discovery using Firecrawl + Neo4j knowledge graph",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3009", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)  # must be before rfps.router (avoids /api/rfps/{id} catching /matches)
app.include_router(applications.router)  # must be before rfps.router for same reason
app.include_router(coalition.router)  # /api/rfps/{id}/coalition — must precede rfps.router
app.include_router(rfps.router)
app.include_router(crawl.router)
app.include_router(graph.router)
app.include_router(recommendations.router)
app.include_router(users.router)
app.include_router(foresight.router)
app.include_router(simulator.router)
app.include_router(copilot.router)


@app.on_event("startup")
async def startup():
    # Create Postgres tables
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL tables created")

    # Initialize Neo4j schema
    try:
        from backend.graph.schema import init_schema
        init_schema()
    except Exception as e:
        logger.warning(f"Neo4j schema init failed (will retry on first query): {e}")

    # Seed graph with mock data if empty
    try:
        from backend.utils.seed_data import seed_graph
        seed_graph()
    except Exception as e:
        logger.warning(f"Seed data failed: {e}")


@app.on_event("shutdown")
async def shutdown():
    from backend.graph.neo4j_client import close_driver
    close_driver()


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-rfp-knowledge-graph"}
