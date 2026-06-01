"""One-time backfill: compute and store embeddings for all existing RFPs.

Run inside the backend container:
    docker compose exec backend python -m backend.scripts.backfill_embeddings
"""
from backend.graph.neo4j_client import get_session
from backend.ai.embeddings import embed_rfp
from backend.utils.logger import get_logger

logger = get_logger("backfill_embeddings")


def run():
    fetch = """
    MATCH (r:RFP)
    WHERE r.embedding IS NULL
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(c:Category)
    OPTIONAL MATCH (r)-[:REQUIRES]->(req:Requirement)
    RETURN r.id AS id, r.title AS title, r.description AS description,
           collect(DISTINCT c.name) AS categories,
           collect(DISTINCT req.description) AS requirements
    """
    with get_session() as session:
        rows = list(session.run(fetch))
        logger.info(f"Embedding {len(rows)} RFPs without vectors")
        done = 0
        for r in rows:
            vec = embed_rfp({
                "title": r["title"],
                "description": r["description"],
                "categories": r["categories"],
                "requirements": r["requirements"],
            })
            if not vec:
                continue
            session.run(
                "MATCH (r:RFP {id: $id}) SET r.embedding = $vec",
                {"id": r["id"], "vec": vec},
            )
            done += 1
        logger.info(f"Backfill complete: {done}/{len(rows)} RFPs embedded")
        return done


if __name__ == "__main__":
    run()
