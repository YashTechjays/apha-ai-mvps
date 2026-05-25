from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.db.session import get_db
from backend.db.models.usage import ToolUsage
from backend.db.models.lead import Lead

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total_uses = db.query(ToolUsage).count()
    total_leads = db.query(Lead).count()

    by_tool = db.query(ToolUsage.tool, func.count()).group_by(ToolUsage.tool).all()
    leads_by_tool = (
        db.query(Lead.source_tool, func.count()).group_by(Lead.source_tool).all()
    )

    tool_stats = {}
    for tool, count in by_tool:
        leads = next((lc for t, lc in leads_by_tool if t == tool), 0)
        tool_stats[tool] = {
            "uses": count,
            "leads": leads,
            "conversion_rate": round(leads / max(count, 1), 3),
        }

    return {
        "total_tool_uses": total_uses,
        "total_leads_captured": total_leads,
        "overall_conversion_rate": round(total_leads / max(total_uses, 1), 3),
        "by_tool": tool_stats,
    }
