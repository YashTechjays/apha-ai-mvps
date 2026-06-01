from backend.graph.neo4j_client import get_session
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("graph_schema")

CONSTRAINTS = [
    "CREATE CONSTRAINT rfp_id IF NOT EXISTS FOR (r:RFP) REQUIRE r.id IS UNIQUE",
    "CREATE CONSTRAINT org_name IF NOT EXISTS FOR (o:Organization) REQUIRE o.name IS UNIQUE",
    "CREATE CONSTRAINT loc_name IF NOT EXISTS FOR (l:Location) REQUIRE l.name IS UNIQUE",
    "CREATE CONSTRAINT cat_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
    # Enhancement #1 — pharmacist/certification nodes mirrored from PostgreSQL
    "CREATE CONSTRAINT pharmacist_id IF NOT EXISTS FOR (p:Pharmacist) REQUIRE p.user_id IS UNIQUE",
    "CREATE CONSTRAINT cert_name IF NOT EXISTS FOR (c:Certification) REQUIRE c.name IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX rfp_deadline IF NOT EXISTS FOR (r:RFP) ON (r.deadline)",
    "CREATE INDEX rfp_status IF NOT EXISTS FOR (r:RFP) ON (r.status)",
    "CREATE INDEX rfp_title IF NOT EXISTS FOR (r:RFP) ON (r.title)",
]


def _vector_index_stmt() -> str:
    settings = get_settings()
    # Enhancement #2 — native Neo4j 5 vector index over RFP embeddings
    return (
        "CREATE VECTOR INDEX rfp_embedding IF NOT EXISTS "
        "FOR (r:RFP) ON r.embedding "
        "OPTIONS { indexConfig: { "
        f"`vector.dimensions`: {settings.embedding_dimensions}, "
        "`vector.similarity_function`: 'cosine' } }"
    )


def init_schema():
    with get_session() as session:
        for stmt in CONSTRAINTS + INDEXES:
            session.run(stmt)
        try:
            session.run(_vector_index_stmt())
            logger.info("Neo4j vector index initialized")
        except Exception as e:
            logger.warning(f"Vector index init skipped (requires Neo4j 5.13+): {e}")
        logger.info("Neo4j schema constraints and indexes initialized")
