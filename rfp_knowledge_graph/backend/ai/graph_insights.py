"""Organization & category intelligence from the graph (Enhancement #5b).

Uses pure Cypher aggregations (degree-based activity ranking + category demand
over time) so it works on Neo4j Community without the GDS plugin. The shapes
mirror what gds.pageRank / centrality would produce, so swapping in GDS later
is a drop-in upgrade.
"""
from backend.graph.neo4j_client import get_session
from backend.utils.logger import get_logger

logger = get_logger("graph_insights")


def top_organizations(limit: int = 10) -> list:
    """Most active organizations by number of RFPs posted (degree centrality)."""
    query = """
    MATCH (o:Organization)<-[:POSTED_BY]-(r:RFP)
    WITH o, count(r) AS rfp_count,
         sum(CASE WHEN r.status = 'open' THEN 1 ELSE 0 END) AS open_count
    RETURN o.name AS organization, o.type AS type,
           rfp_count, open_count
    ORDER BY rfp_count DESC
    LIMIT $limit
    """
    with get_session() as session:
        return [
            {
                "organization": r["organization"],
                "type": r["type"],
                "rfp_count": r["rfp_count"],
                "open_count": r["open_count"],
            }
            for r in session.run(query, {"limit": limit})
        ]


def trending_categories(limit: int = 10) -> list:
    """Categories ranked by total RFP demand."""
    query = """
    MATCH (c:Category)<-[:CATEGORIZED_AS]-(r:RFP)
    WITH c, count(r) AS demand,
         sum(CASE WHEN r.status = 'open' THEN 1 ELSE 0 END) AS open_demand
    RETURN c.name AS category, demand, open_demand
    ORDER BY demand DESC
    LIMIT $limit
    """
    with get_session() as session:
        return [
            {
                "category": r["category"],
                "demand": r["demand"],
                "open_demand": r["open_demand"],
            }
            for r in session.run(query, {"limit": limit})
        ]


def get_insights(limit: int = 10) -> dict:
    return {
        "top_organizations": top_organizations(limit),
        "trending_categories": trending_categories(limit),
    }


def summarize_insights(insights: dict) -> str:
    """One-paragraph LLM digest of the graph trends (for the weekly email)."""
    try:
        from backend.utils.config import get_settings
        from openai import OpenAI
        settings = get_settings()
        client = OpenAI(api_key=settings.openai_api_key)

        orgs = ", ".join(
            f"{o['organization']} ({o['rfp_count']} RFPs)"
            for o in insights.get("top_organizations", [])[:5]
        )
        cats = ", ".join(
            f"{c['category']} ({c['demand']})"
            for c in insights.get("trending_categories", [])[:5]
        )
        prompt = (
            "Write a concise 2-3 sentence weekly summary for pharmacists about RFP "
            "market trends.\n"
            f"Most active organizations: {orgs}\n"
            f"Top categories by demand: {cats}\n"
        )
        resp = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"Insights summary failed: {e}")
        return "Weekly RFP trends are available on your dashboard."
