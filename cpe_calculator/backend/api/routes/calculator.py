import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models.calculation import Calculation
from backend.api.schemas.calculator import CalculatorRequest, CalculatorResponse
from backend.ai.planner import generate_cpe_plan
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

router = APIRouter(prefix="/calculate", tags=["calculator"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("/", response_model=CalculatorResponse)
def calculate(req: CalculatorRequest, db: Session = Depends(get_db)):
    try:
        plan = generate_cpe_plan(
            state=req.state,
            renewal_date=req.renewal_date,
            hours_completed=req.hours_completed,
            license_type=req.license_type,
            specialty=req.specialty or "General Pharmacy",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        raise HTTPException(status_code=500, detail="Plan generation failed. Please try again.")

    calc = Calculation(
        session_id=req.session_id,
        state=req.state,
        renewal_date=req.renewal_date,
        hours_completed=req.hours_completed,
        hours_required=plan["hours_required"],
        hours_gap=plan["hours_gap"],
        days_until_renewal=plan["days_until_renewal"],
        specialty=req.specialty,
        license_type=req.license_type,
        plan_json=json.dumps(plan),
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)

    preview_count = settings.free_preview_hours
    all_courses = plan.get("courses", [])

    return CalculatorResponse(
        calculation_id=str(calc.id),
        state=plan["state"],
        state_name=plan["state_name"],
        hours_required=plan["hours_required"],
        hours_completed=plan["hours_completed"],
        hours_gap=plan["hours_gap"],
        pct_complete=plan["pct_complete"],
        days_until_renewal=plan["days_until_renewal"],
        renewal_date=plan["renewal_date"],
        urgency_level=plan.get("urgency_level", "low"),
        urgency_message=plan.get("urgency_message"),
        summary=plan.get("summary", ""),
        total_plan_hours=plan.get("total_plan_hours", plan["hours_gap"]),
        mandatory_covered=plan.get("mandatory_covered", False),
        courses=all_courses[:preview_count],
        member_savings_usd=plan.get("member_savings_usd", 0),
        member_cta=plan.get("member_cta", ""),
        state_notes=plan.get("state_notes", ""),
        is_preview=True,
        preview_courses_count=preview_count,
    )


@router.get("/full/{calculation_id}", response_model=CalculatorResponse)
def get_full_plan(calculation_id: str, session_id: str, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    from backend.db.models.lead import Lead
    lead = db.query(Lead).filter(Lead.session_id == session_id).first()
    if not lead:
        raise HTTPException(status_code=403, detail="Email required to view full plan")

    calc.lead_captured = True
    db.commit()
    plan = json.loads(calc.plan_json)

    return CalculatorResponse(
        calculation_id=calculation_id,
        state=plan["state"],
        state_name=plan["state_name"],
        hours_required=plan["hours_required"],
        hours_completed=plan["hours_completed"],
        hours_gap=plan["hours_gap"],
        pct_complete=plan["pct_complete"],
        days_until_renewal=plan["days_until_renewal"],
        renewal_date=plan["renewal_date"],
        urgency_level=plan.get("urgency_level", "low"),
        urgency_message=plan.get("urgency_message"),
        summary=plan.get("summary", ""),
        total_plan_hours=plan.get("total_plan_hours", plan["hours_gap"]),
        mandatory_covered=plan.get("mandatory_covered", False),
        courses=plan.get("courses", []),
        member_savings_usd=plan.get("member_savings_usd", 0),
        member_cta=plan.get("member_cta", ""),
        state_notes=plan.get("state_notes", ""),
        is_preview=False,
        preview_courses_count=len(plan.get("courses", [])),
    )
