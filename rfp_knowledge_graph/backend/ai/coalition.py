"""Coalition Finder — assemble a complementary team of pharmacists that
collectively covers an RFP's required specialties.

Pure-Cypher reads + a greedy set-cover in Python (no GDS). The RFP's
``CATEGORIZED_AS`` categories form the requirement set; each candidate
pharmacist covers the subset matching their ``HAS_SPECIALTY`` edges. We greedily
add the pharmacist who closes the most still-open requirements until the set is
covered or the team hits ``max_team_size``.
"""
from backend.graph.neo4j_client import get_session
from backend.utils.logger import get_logger

logger = get_logger("coalition")


def _rfp_requirements(rfp_id: str) -> dict:
    """Target coverage set for an RFP: its categories + title/org for context."""
    query = """
    MATCH (r:RFP {id: $rfp_id})
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(c:Category)
    OPTIONAL MATCH (r)-[:POSTED_BY]->(o:Organization)
    RETURN r.title AS title, o.name AS org_name,
           collect(DISTINCT c.name) AS categories
    """
    with get_session() as session:
        rec = session.run(query, {"rfp_id": rfp_id}).single()
        if not rec:
            return {}
        return {
            "title": rec["title"],
            "org_name": rec["org_name"],
            "categories": [c for c in rec["categories"] if c],
        }


def _candidate_pharmacists() -> list[dict]:
    """All pharmacists with their specialties, certifications and location."""
    query = """
    MATCH (p:Pharmacist)
    OPTIONAL MATCH (p)-[:HAS_SPECIALTY]->(c:Category)
    OPTIONAL MATCH (p)-[:HOLDS]->(ct:Certification)
    WITH p, collect(DISTINCT c.name) AS specialties,
         collect(DISTINCT ct.name) AS certifications
    RETURN p.user_id AS user_id, p.full_name AS full_name,
           p.location_state AS location_state, specialties, certifications
    """
    with get_session() as session:
        return [
            {
                "user_id": r["user_id"],
                "full_name": r["full_name"] or r["user_id"],
                "location_state": r["location_state"],
                "specialties": [s for s in r["specialties"] if s],
                "certifications": [c for c in r["certifications"] if c],
            }
            for r in session.run(query)
        ]


def find_coalition(rfp_id: str, max_team_size: int = 4) -> dict:
    """Greedy set-cover team assembly for an RFP.

    Returns {rfp_id, rfp_title, organization, required_categories,
             team: [{user_id, full_name, location_state, certifications,
                     covers: [...]}],
             covered_categories, uncovered_categories, coverage_pct}.
    """
    rfp = _rfp_requirements(rfp_id)
    required = set(rfp.get("categories") or [])
    base = {
        "rfp_id": rfp_id,
        "rfp_title": rfp.get("title"),
        "organization": rfp.get("org_name"),
        "required_categories": sorted(required),
    }
    if not required:
        return {**base, "team": [], "covered_categories": [],
                "uncovered_categories": [], "coverage_pct": 0}

    candidates = _candidate_pharmacists()
    remaining = set(required)
    team: list[dict] = []
    used: set[str] = set()

    while remaining and len(team) < max_team_size:
        best, best_cover = None, set()
        for c in candidates:
            if c["user_id"] in used:
                continue
            cover = set(c["specialties"]) & remaining
            if len(cover) > len(best_cover):
                best, best_cover = c, cover
        if not best or not best_cover:
            break
        team.append({
            "user_id": best["user_id"],
            "full_name": best["full_name"],
            "location_state": best["location_state"],
            "certifications": best["certifications"],
            "covers": sorted(best_cover),
        })
        used.add(best["user_id"])
        remaining -= best_cover

    covered = required - remaining
    coverage_pct = int(round(100 * len(covered) / len(required)))
    return {
        **base,
        "team": team,
        "covered_categories": sorted(covered),
        "uncovered_categories": sorted(remaining),
        "coverage_pct": coverage_pct,
    }
