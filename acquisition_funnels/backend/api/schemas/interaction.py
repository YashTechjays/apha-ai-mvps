from pydantic import BaseModel
from typing import Optional


class InteractionRequest(BaseModel):
    session_id: str
    drug_a: str
    drug_b: str


class DrugSearchRequest(BaseModel):
    prefix: str
    limit: int = 8


class InteractionResponse(BaseModel):
    usage_id: str
    drug_a: str
    drug_b: str
    severity: str
    mechanism: Optional[str] = None
    clinical_effect: Optional[str] = None
    management: Optional[str] = None
    summary: str
    disclaimer: str
    remaining_free_checks: int
    is_limited: bool = False
