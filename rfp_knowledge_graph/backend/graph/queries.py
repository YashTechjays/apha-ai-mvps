import uuid
from typing import Optional
from backend.graph.neo4j_client import get_session
from backend.utils.logger import get_logger

logger = get_logger("graph_queries")


def create_rfp_with_relations(rfp_data: dict) -> str:
    rfp_id = rfp_data.get("id") or str(uuid.uuid4())

    # Enhancement #2 — compute a semantic embedding for vector similarity search.
    embedding = None
    try:
        from backend.ai.embeddings import embed_rfp
        embedding = embed_rfp(rfp_data)
    except Exception as e:
        logger.warning(f"Skipping embedding for RFP {rfp_id}: {e}")

    query = """
    MERGE (r:RFP {id: $id})
    SET r.title = $title,
        r.description = $description,
        r.deadline = $deadline,
        r.posted_date = $posted_date,
        r.url = $url,
        r.source_url = $source_url,
        r.budget_range = $budget_range,
        r.contact_name = $contact_name,
        r.contact_email = $contact_email,
        r.status = $status,
        r.embedding = coalesce($embedding, r.embedding),
        r.created_at = coalesce(r.created_at, datetime())

    WITH r

    FOREACH (_ IN CASE WHEN $org_name IS NOT NULL THEN [1] ELSE [] END |
        MERGE (o:Organization {name: $org_name})
        SET o.type = $org_type, o.website = $org_website
        MERGE (r)-[:POSTED_BY]->(o)
        FOREACH (_ IN CASE WHEN $location_name IS NOT NULL THEN [1] ELSE [] END |
            MERGE (loc:Location {name: $location_name})
            SET loc.state = $location_state, loc.city = $location_city
            MERGE (o)-[:BASED_IN]->(loc)
        )
    )

    WITH r

    FOREACH (_ IN CASE WHEN $location_name IS NOT NULL THEN [1] ELSE [] END |
        MERGE (loc:Location {name: $location_name})
        SET loc.state = $location_state, loc.city = $location_city
        MERGE (r)-[:LOCATED_IN]->(loc)
    )

    WITH r
    UNWIND $categories AS cat_name
    MERGE (c:Category {name: cat_name})
    MERGE (r)-[:CATEGORIZED_AS]->(c)

    WITH r
    UNWIND $requirements AS req_desc
    MERGE (req:Requirement {description: req_desc})
    MERGE (r)-[:REQUIRES]->(req)

    RETURN r.id AS id
    """

    params = {
        "id": rfp_id,
        "title": rfp_data.get("title", ""),
        "description": rfp_data.get("description", ""),
        "deadline": rfp_data.get("deadline"),
        "posted_date": rfp_data.get("posted_date"),
        "url": rfp_data.get("url", ""),
        "source_url": rfp_data.get("source_url", ""),
        "budget_range": rfp_data.get("budget_range"),
        "contact_name": rfp_data.get("contact_name"),
        "contact_email": rfp_data.get("contact_email"),
        "status": rfp_data.get("status", "open"),
        "org_name": rfp_data.get("organization", {}).get("name") if rfp_data.get("organization") else None,
        "org_type": rfp_data.get("organization", {}).get("type") if rfp_data.get("organization") else None,
        "org_website": rfp_data.get("organization", {}).get("website") if rfp_data.get("organization") else None,
        "location_name": rfp_data.get("location", {}).get("name") if rfp_data.get("location") else None,
        "location_state": rfp_data.get("location", {}).get("state") if rfp_data.get("location") else None,
        "location_city": rfp_data.get("location", {}).get("city") if rfp_data.get("location") else None,
        "categories": rfp_data.get("categories", []),
        "requirements": rfp_data.get("requirements", []),
        "embedding": embedding,
    }

    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        return record["id"] if record else rfp_id


def search_rfps(
    query: Optional[str] = None,
    category: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    conditions = []
    params = {"limit": limit, "offset": offset}

    if query:
        conditions.append("(toLower(r.title) CONTAINS toLower($query) OR toLower(r.description) CONTAINS toLower($query))")
        params["query"] = query
    if status:
        conditions.append("r.status = $status")
        params["status"] = status

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Category and state filtering via relationships
    match_clause = "MATCH (r:RFP)"
    if category:
        match_clause += "\nMATCH (r)-[:CATEGORIZED_AS]->(c:Category {name: $category})"
        params["category"] = category
    if state:
        match_clause += "\nMATCH (r)-[:LOCATED_IN]->(loc:Location {state: $state})"
        params["state"] = state

    count_query = f"""
    {match_clause}
    {where_clause}
    RETURN count(DISTINCT r) AS total
    """

    data_query = f"""
    {match_clause}
    {where_clause}
    WITH DISTINCT r
    OPTIONAL MATCH (r)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(loc:Location)
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(cat:Category)
    RETURN r, o.name AS org_name, loc.name AS location,
           collect(DISTINCT cat.name) AS categories
    ORDER BY r.deadline ASC
    SKIP $offset LIMIT $limit
    """

    with get_session() as session:
        total = session.run(count_query, params).single()["total"]
        results = session.run(data_query, params)

        items = []
        for record in results:
            node = record["r"]
            items.append({
                "id": node["id"],
                "title": node["title"],
                "description": node.get("description", ""),
                "deadline": node.get("deadline"),
                "posted_date": node.get("posted_date"),
                "status": node.get("status", "open"),
                "url": node.get("url", ""),
                "budget_range": node.get("budget_range"),
                "organization_name": record["org_name"],
                "location": record["location"],
                "categories": record["categories"],
            })

    return {"items": items, "total": total}


def get_rfp_detail(rfp_id: str) -> Optional[dict]:
    query = """
    MATCH (r:RFP {id: $id})
    OPTIONAL MATCH (r)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(loc:Location)
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(cat:Category)
    OPTIONAL MATCH (r)-[:REQUIRES]->(req:Requirement)
    RETURN r, o, loc,
           collect(DISTINCT cat.name) AS categories,
           collect(DISTINCT req.description) AS requirements
    """

    with get_session() as session:
        result = session.run(query, {"id": rfp_id})
        record = result.single()
        if not record:
            return None

        node = record["r"]
        org = record["o"]
        loc = record["loc"]

        return {
            "id": node["id"],
            "title": node["title"],
            "description": node.get("description", ""),
            "deadline": node.get("deadline"),
            "posted_date": node.get("posted_date"),
            "status": node.get("status", "open"),
            "url": node.get("url", ""),
            "source_url": node.get("source_url", ""),
            "budget_range": node.get("budget_range"),
            "contact_name": node.get("contact_name"),
            "contact_email": node.get("contact_email"),
            "organization": {
                "name": org["name"],
                "type": org.get("type"),
                "website": org.get("website"),
            } if org else None,
            "location": {
                "name": loc["name"],
                "state": loc.get("state"),
                "city": loc.get("city"),
            } if loc else None,
            "categories": record["categories"],
            "requirements": record["requirements"],
            "similar_rfps": get_semantically_similar_rfps(rfp_id) or get_similar_rfps(rfp_id),
        }


def get_similar_rfps(rfp_id: str, limit: int = 5) -> list:
    query = """
    MATCH (r:RFP {id: $id})-[:CATEGORIZED_AS]->(c:Category)<-[:CATEGORIZED_AS]-(other:RFP)
    WHERE other.id <> $id
    OPTIONAL MATCH (other)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (other)-[:LOCATED_IN]->(loc:Location)
    WITH other, o.name AS org_name, loc.name AS location, count(c) AS shared_categories
    ORDER BY shared_categories DESC, other.deadline ASC
    LIMIT $limit
    RETURN other.id AS id, other.title AS title, other.deadline AS deadline,
           other.status AS status, org_name, location, shared_categories
    """
    with get_session() as session:
        results = session.run(query, {"id": rfp_id, "limit": limit})
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "deadline": r["deadline"],
                "status": r["status"],
                "organization_name": r["org_name"],
                "location": r["location"],
            }
            for r in results
        ]


def get_semantically_similar_rfps(rfp_id: str, limit: int = 5) -> Optional[list]:
    """Enhancement #2 — vector-index similarity. Returns None if no embedding exists
    (caller falls back to category-overlap similarity)."""
    query = """
    MATCH (r:RFP {id: $id})
    WHERE r.embedding IS NOT NULL
    CALL db.index.vector.queryNodes('rfp_embedding', $k, r.embedding)
    YIELD node AS other, score
    WHERE other.id <> $id
    OPTIONAL MATCH (other)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (other)-[:LOCATED_IN]->(loc:Location)
    RETURN other.id AS id, other.title AS title, other.deadline AS deadline,
           other.status AS status, o.name AS org_name, loc.name AS location, score
    ORDER BY score DESC
    LIMIT $limit
    """
    try:
        with get_session() as session:
            results = session.run(query, {"id": rfp_id, "k": limit + 1, "limit": limit})
            rows = [
                {
                    "id": r["id"],
                    "title": r["title"],
                    "deadline": r["deadline"],
                    "status": r["status"],
                    "organization_name": r["org_name"],
                    "location": r["location"],
                    "similarity": round(r["score"], 4),
                }
                for r in results
            ]
            return rows if rows else None
    except Exception as e:
        logger.warning(f"Vector similarity unavailable for {rfp_id}: {e}")
        return None


def get_rfps_for_matching(status: str = "open", limit: int = 200) -> list[dict]:
    """Lightweight bulk fetch for the matching engine."""
    query = """
    MATCH (r:RFP)
    WHERE r.status = $status
    OPTIONAL MATCH (r)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(loc:Location)
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(cat:Category)
    OPTIONAL MATCH (r)-[:REQUIRES]->(req:Requirement)
    WITH r, o, loc,
         collect(DISTINCT cat.name) AS categories,
         collect(DISTINCT req.description) AS requirements
    RETURN r.id AS id, r.title AS title, r.description AS description,
           r.deadline AS deadline, r.status AS status,
           r.url AS url, r.budget_range AS budget_range,
           o.name AS organization_name, o.type AS org_type,
           loc.name AS location, loc.state AS location_state,
           categories, requirements
    ORDER BY r.deadline ASC
    LIMIT $limit
    """
    with get_session() as session:
        results = session.run(query, {"status": status, "limit": limit})
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "description": r["description"] or "",
                "deadline": r["deadline"],
                "status": r["status"],
                "url": r["url"] or "",
                "budget_range": r["budget_range"],
                "organization_name": r["organization_name"],
                "org_type": r["org_type"],
                "location": r["location"],
                "location_state": r["location_state"],
                "categories": r["categories"],
                "requirements": r["requirements"],
            }
            for r in results
        ]


def get_graph_stats() -> dict:
    query = """
    OPTIONAL MATCH (r:RFP) WITH count(r) AS rfps
    OPTIONAL MATCH (o:Organization) WITH rfps, count(o) AS orgs
    OPTIONAL MATCH (l:Location) WITH rfps, orgs, count(l) AS locations
    OPTIONAL MATCH (c:Category) WITH rfps, orgs, locations, count(c) AS categories
    OPTIONAL MATCH (req:Requirement) WITH rfps, orgs, locations, categories, count(req) AS requirements
    OPTIONAL MATCH ()-[rel]->() WITH rfps, orgs, locations, categories, requirements, count(rel) AS relationships
    OPTIONAL MATCH (r2:RFP) WHERE r2.status = 'open'
    RETURN rfps AS total_rfps, orgs AS total_organizations,
           locations AS total_locations, categories AS total_categories,
           requirements AS total_requirements, relationships AS total_relationships,
           count(r2) AS open_rfps
    """
    with get_session() as session:
        record = session.run(query).single()
        return {
            "total_rfps": record["total_rfps"],
            "open_rfps": record["open_rfps"],
            "total_organizations": record["total_organizations"],
            "total_locations": record["total_locations"],
            "total_categories": record["total_categories"],
            "total_requirements": record["total_requirements"],
            "total_relationships": record["total_relationships"],
        }


def get_recommendations(
    categories: Optional[list] = None,
    states: Optional[list] = None,
    limit: int = 10,
) -> list:
    conditions = ["r.status = 'open'"]
    params = {"limit": limit}

    match_extra = ""
    if categories:
        match_extra += "\nMATCH (r)-[:CATEGORIZED_AS]->(c:Category) WHERE c.name IN $categories"
        params["categories"] = categories
    if states:
        match_extra += "\nMATCH (r)-[:LOCATED_IN]->(loc:Location) WHERE loc.state IN $states"
        params["states"] = states

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
    MATCH (r:RFP)
    {match_extra}
    {where_clause}
    OPTIONAL MATCH (r)-[:POSTED_BY]->(o:Organization)
    OPTIONAL MATCH (r)-[:LOCATED_IN]->(l:Location)
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(cat:Category)
    WITH DISTINCT r, o.name AS org_name, l.name AS location,
         collect(DISTINCT cat.name) AS categories
    ORDER BY r.deadline ASC
    LIMIT $limit
    RETURN r.id AS id, r.title AS title, r.description AS description,
           r.deadline AS deadline, r.status AS status, r.budget_range AS budget_range,
           org_name, location, categories
    """

    with get_session() as session:
        results = session.run(query, params)
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "description": r["description"],
                "deadline": r["deadline"],
                "status": r["status"],
                "budget_range": r["budget_range"],
                "organization_name": r["org_name"],
                "location": r["location"],
                "categories": r["categories"],
            }
            for r in results
        ]
