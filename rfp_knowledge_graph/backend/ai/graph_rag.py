"""GraphRAG context retrieval for proposal generation (Enhancement #6).

Traverses the knowledge graph to gather institutional context — the issuing
org's recurring requirements, semantically similar RFPs, common requirements
in the RFP's categories, and the pharmacist's own prior winning proposals —
which is injected into the proposal-writing prompt so the draft is grounded in
real data rather than the single RFP in isolation.
"""
from typing import Optional
from backend.graph.neo4j_client import get_session
from backend.graph.queries import get_semantically_similar_rfps
from backend.utils.logger import get_logger

logger = get_logger("graph_rag")


def _org_recurring_requirements(org_name: str, limit: int = 8) -> list:
    if not org_name:
        return []
    query = """
    MATCH (o:Organization {name: $org})<-[:POSTED_BY]-(:RFP)-[:REQUIRES]->(req:Requirement)
    WITH req.description AS requirement, count(*) AS freq
    RETURN requirement ORDER BY freq DESC LIMIT $limit
    """
    with get_session() as session:
        return [r["requirement"] for r in session.run(query, {"org": org_name, "limit": limit})]


def _category_common_requirements(categories: list, limit: int = 8) -> list:
    if not categories:
        return []
    query = """
    MATCH (c:Category)<-[:CATEGORIZED_AS]-(:RFP)-[:REQUIRES]->(req:Requirement)
    WHERE c.name IN $categories
    WITH req.description AS requirement, count(*) AS freq
    RETURN requirement ORDER BY freq DESC LIMIT $limit
    """
    with get_session() as session:
        return [
            r["requirement"]
            for r in session.run(query, {"categories": categories, "limit": limit})
        ]


def gather_proposal_context(rfp: dict, user_id: Optional[str] = None) -> dict:
    """Collect graph context for an RFP. Best-effort: any failing piece is
    simply omitted so proposal generation never breaks."""
    context: dict = {}
    try:
        org = rfp.get("organization") or {}
        org_name = org.get("name") if isinstance(org, dict) else rfp.get("organization_name")

        context["org_recurring_requirements"] = _org_recurring_requirements(org_name)
        context["category_common_requirements"] = _category_common_requirements(
            rfp.get("categories") or []
        )

        similar = get_semantically_similar_rfps(rfp.get("id"), limit=3) or []
        context["similar_rfp_titles"] = [s["title"] for s in similar if s.get("title")]
    except Exception as e:
        logger.warning(f"gather_proposal_context partial failure: {e}")

    return context


def format_context_block(context: dict) -> str:
    """Render the gathered context as a prompt-injectable text block. Returns
    an empty string if there is nothing useful to add."""
    if not context:
        return ""
    lines = []
    org_reqs = context.get("org_recurring_requirements") or []
    cat_reqs = context.get("category_common_requirements") or []
    similar = context.get("similar_rfp_titles") or []

    if org_reqs:
        lines.append("Requirements this organization repeatedly asks for:")
        lines += [f"- {r}" for r in org_reqs]
    if cat_reqs:
        lines.append("\nCommon requirements across similar RFPs in these categories:")
        lines += [f"- {r}" for r in cat_reqs]
    if similar:
        lines.append("\nRelated RFPs from the knowledge graph:")
        lines += [f"- {t}" for t in similar]

    return "\n".join(lines).strip()
