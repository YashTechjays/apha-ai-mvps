"""Pharmacist projection into the knowledge graph (Enhancement #1).

PostgreSQL remains the source of truth for users, profiles and applications.
These functions mirror that data into Neo4j as a *projection* so graph
traversals and algorithms (win-prediction #3, collaborative recs #4,
explainability #5) can reason over it. All writes are idempotent (MERGE),
so re-syncing is always safe.
"""
from typing import Optional
from backend.graph.neo4j_client import get_session
from backend.utils.logger import get_logger

logger = get_logger("pharmacist_graph")


def sync_pharmacist_profile_to_graph(
    user_id: str,
    full_name: Optional[str],
    location_state: Optional[str],
    specialties: Optional[list],
    certifications: Optional[list],
) -> None:
    """Mirror a pharmacist profile: (Pharmacist)-[:HAS_SPECIALTY]->(Category)
    and (Pharmacist)-[:HOLDS]->(Certification)."""
    query = """
    MERGE (p:Pharmacist {user_id: $user_id})
    SET p.full_name = $full_name, p.location_state = $location_state

    WITH p
    OPTIONAL MATCH (p)-[s:HAS_SPECIALTY]->()
    DELETE s
    WITH p
    OPTIONAL MATCH (p)-[h:HOLDS]->()
    DELETE h

    WITH p
    FOREACH (spec IN $specialties |
        MERGE (c:Category {name: spec})
        MERGE (p)-[:HAS_SPECIALTY]->(c)
    )
    FOREACH (cert IN $certifications |
        MERGE (ct:Certification {name: cert})
        MERGE (p)-[:HOLDS]->(ct)
    )
    """
    try:
        with get_session() as session:
            session.run(query, {
                "user_id": str(user_id),
                "full_name": full_name,
                "location_state": location_state,
                "specialties": specialties or [],
                "certifications": certifications or [],
            })
    except Exception as e:
        logger.warning(f"Profile graph sync failed for {user_id}: {e}")


def sync_application_to_graph(
    user_id: str,
    rfp_id: str,
    status: str,
    applied_at: Optional[str] = None,
) -> None:
    """Mirror an application: (Pharmacist)-[:APPLIED_TO {status}]->(RFP)."""
    query = """
    MERGE (p:Pharmacist {user_id: $user_id})
    WITH p
    MATCH (r:RFP {id: $rfp_id})
    MERGE (p)-[a:APPLIED_TO]->(r)
    SET a.status = $status,
        a.applied_at = coalesce(a.applied_at, $applied_at)
    """
    try:
        with get_session() as session:
            session.run(query, {
                "user_id": str(user_id),
                "rfp_id": rfp_id,
                "status": status,
                "applied_at": applied_at,
            })
    except Exception as e:
        logger.warning(f"Application graph sync failed ({user_id}->{rfp_id}): {e}")


# ---------------------------------------------------------------------------
# Read queries used by win-prediction (#3), recommendations (#4), explain (#5)
# ---------------------------------------------------------------------------

def get_org_win_rate(org_name: str) -> Optional[float]:
    """Fraction of applications to this org that were won (None if no history)."""
    if not org_name:
        return None
    query = """
    MATCH (:Pharmacist)-[a:APPLIED_TO]->(:RFP)-[:POSTED_BY]->(o:Organization {name: $org})
    WITH count(a) AS total,
         sum(CASE WHEN a.status = 'won' THEN 1 ELSE 0 END) AS won
    RETURN total, won
    """
    with get_session() as session:
        rec = session.run(query, {"org": org_name}).single()
        if not rec or not rec["total"]:
            return None
        return rec["won"] / rec["total"]


def get_category_affinity(user_id: str, categories: list) -> Optional[float]:
    """This pharmacist's historical win rate in the given RFP's categories."""
    if not categories:
        return None
    query = """
    MATCH (p:Pharmacist {user_id: $user_id})-[a:APPLIED_TO]->(r:RFP)-[:CATEGORIZED_AS]->(c:Category)
    WHERE c.name IN $categories
    WITH count(DISTINCT a) AS total,
         count(DISTINCT CASE WHEN a.status = 'won' THEN r END) AS won
    RETURN total, won
    """
    with get_session() as session:
        rec = session.run(query, {"user_id": str(user_id), "categories": categories}).single()
        if not rec or not rec["total"]:
            return None
        return rec["won"] / rec["total"]


def get_peer_recommendations(user_id: str, limit: int = 10) -> list:
    """Collaborative filtering (#4) in pure Cypher: open RFPs pursued by
    pharmacists who overlap with me, that I haven't applied to yet."""
    query = """
    MATCH (me:Pharmacist {user_id: $user_id})-[:APPLIED_TO]->(shared:RFP)
          <-[:APPLIED_TO]-(peer:Pharmacist)
    WHERE peer <> me
    MATCH (peer)-[:APPLIED_TO]->(rec:RFP)
    WHERE rec.status = 'open' AND NOT (me)-[:APPLIED_TO]->(rec)
    OPTIONAL MATCH (rec)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (rec)-[:LOCATED_IN]->(loc:Location)
    WITH rec, o.name AS org_name, loc.name AS location,
         count(DISTINCT peer) AS peer_count
    RETURN rec.id AS id, rec.title AS title, rec.deadline AS deadline,
           rec.status AS status, org_name, location, peer_count
    ORDER BY peer_count DESC, rec.deadline ASC
    LIMIT $limit
    """
    with get_session() as session:
        results = session.run(query, {"user_id": str(user_id), "limit": limit})
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "deadline": r["deadline"],
                "status": r["status"],
                "organization_name": r["org_name"],
                "location": r["location"],
                "peer_count": r["peer_count"],
            }
            for r in results
        ]


def get_match_explanation_path(user_id: str, rfp_id: str) -> Optional[dict]:
    """Pathfinding (#5): shortest connection between a pharmacist and an RFP,
    returned as a human-readable chain of node descriptions."""
    query = """
    MATCH (p:Pharmacist {user_id: $user_id}), (r:RFP {id: $rfp_id})
    MATCH path = shortestPath((p)-[*..6]-(r))
    RETURN [n IN nodes(path) |
        coalesce(n.full_name, n.title, n.name, n.description, 'node')] AS chain,
        length(path) AS hops
    """
    try:
        with get_session() as session:
            rec = session.run(query, {"user_id": str(user_id), "rfp_id": rfp_id}).single()
            if not rec:
                return None
            return {"chain": rec["chain"], "hops": rec["hops"]}
    except Exception as e:
        logger.warning(f"Explain path failed ({user_id}->{rfp_id}): {e}")
        return None
