import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import calculator, leads, analytics
from backend.db.base import Base
from backend.db.session import engine
from backend.db.models import Calculation, Lead  # noqa: F401
from backend.utils.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="APhA CPE Gap Calculator API",
    description="Free CPE gap calculator for pharmacists — powered by AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator.router)
app.include_router(leads.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    logger.info("Creating DB tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("CPE Calculator API ready.")


@app.get("/health")
def health():
    return {"status": "ok", "service": "apha-cpe-calculator"}


@app.get("/seo/state/{state_code}")
def state_seo(state_code: str):
    data_path = Path(__file__).parent / "data" / "state_requirements.json"
    data = json.loads(data_path.read_text())
    state = data.get(state_code.upper(), {})
    if not state:
        return {"error": "State not found"}
    return {
        "title": f"{state['name']} Pharmacist CPE Requirements 2026 | Free Gap Calculator",
        "description": (
            f"Free tool: calculate your {state['name']} pharmacist CPE gap. "
            f"{state['name']} requires {state['hours_required']} hours every "
            f"{state['cycle_years']} year(s). Get your personalized plan in 30 seconds."
        ),
        "hours_required": state["hours_required"],
        "state_name": state["name"],
    }
