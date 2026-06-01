"""Foresight — predict RFPs before they are posted.

Mines each organization's historical ``posted_date`` cadence from the knowledge
graph and projects the next expected posting window with a confidence score.
Pure Python over Cypher results — no GDS required. Degrades gracefully (the LLM
rationale is optional and falls back to a deterministic sentence).
"""
from datetime import date, datetime, timedelta
from statistics import median, pstdev
from typing import Optional

from backend.graph.neo4j_client import get_session
from backend.utils.logger import get_logger

logger = get_logger("foresight")

_DATE_FMT = "%Y-%m-%d"


def _parse(d) -> Optional[date]:
    if not d:
        return None
    try:
        return datetime.strptime(str(d)[:10], _DATE_FMT).date()
    except ValueError:
        return None


def _org_posting_history() -> list[dict]:
    """Per organization: sorted posting dates, categories, and the latest RFP."""
    query = """
    MATCH (o:Organization)<-[:POSTED_BY]-(r:RFP)
    WHERE r.posted_date IS NOT NULL
    OPTIONAL MATCH (r)-[:CATEGORIZED_AS]->(c:Category)
    OPTIONAL MATCH (o)-[:BASED_IN]->(loc:Location)
    WITH o, r, loc, collect(DISTINCT c.name) AS cats
    WITH o.name AS organization, o.type AS org_type,
         head(collect(loc.state)) AS state,
         collect({date: r.posted_date, id: r.id, title: r.title, cats: cats}) AS postings
    RETURN organization, org_type, state, postings
    """
    with get_session() as session:
        return [
            {
                "organization": r["organization"],
                "org_type": r["org_type"],
                "state": r["state"],
                "postings": r["postings"],
            }
            for r in session.run(query)
        ]


def _cadence(dates: list[date]) -> Optional[dict]:
    """Median interval (days) + a regularity-based confidence from sorted dates."""
    if len(dates) < 2:
        return None
    ordered = sorted(dates)
    intervals = [(b - a).days for a, b in zip(ordered, ordered[1:]) if (b - a).days > 0]
    if not intervals:
        return None
    med = median(intervals)
    if med <= 0:
        return None
    # Regularity: low spread relative to the median => high confidence.
    spread = pstdev(intervals) if len(intervals) > 1 else 0.0
    regularity = max(0.0, 1.0 - (spread / med)) if med else 0.0
    sample_factor = min(1.0, len(intervals) / 4.0)  # 4+ intervals = full credit
    confidence = int(round(100 * (0.5 * regularity + 0.5 * sample_factor)))
    return {
        "median_days": med,
        "confidence": max(5, min(99, confidence)),
        "last_posted": ordered[-1],
        "intervals": intervals,
    }


def _months(days: float) -> float:
    return round(days / 30.44, 1)


def forecast_reposts(
    horizon_days: int = 180, min_history: int = 2, overdue_grace_days: int = 60,
    min_cadence_days: int = 75,
) -> list[dict]:
    """Project the next posting window for each org with a regular cadence.

    Keeps predictions whose projected date lands between ``today - overdue_grace_days``
    (recently due = "expected now") and ``today + horizon_days``.

    Cadences shorter than ``min_cadence_days`` are treated as noise rather than a
    genuine re-solicitation rhythm (e.g. the same agency listed twice a few days
    apart across seed sets) and are skipped.
    """
    today = date.today()
    horizon_end = today + timedelta(days=horizon_days)
    grace_start = today - timedelta(days=overdue_grace_days)

    predictions: list[dict] = []
    for org in _org_posting_history():
        postings = org["postings"]
        dates = [d for d in (_parse(p["date"]) for p in postings) if d]
        if len(dates) < min_history:
            continue
        cad = _cadence(dates)
        if not cad:
            continue
        if cad["median_days"] < min_cadence_days:
            continue

        predicted = cad["last_posted"] + timedelta(days=cad["median_days"])
        if predicted < grace_start or predicted > horizon_end:
            continue

        # Window = predicted +/- ~15% of the cadence (min 14 days each side).
        margin = max(14, int(cad["median_days"] * 0.15))
        window_start = predicted - timedelta(days=margin)
        window_end = predicted + timedelta(days=margin)

        latest = max(postings, key=lambda p: _parse(p["date"]) or date.min)
        cadence_months = _months(cad["median_days"])
        last_str = cad["last_posted"].strftime(_DATE_FMT)
        basis = (
            f"Posts ~every {cadence_months} months; last {last_str} "
            f"({len(dates)} prior RFPs)."
        )
        # Categories from the most recent posting (best signal for what's next).
        categories = latest.get("cats") or []

        predictions.append({
            "organization": org["organization"],
            "org_type": org["org_type"],
            "state": org["state"],
            "category": categories[0] if categories else None,
            "categories": categories,
            "predicted_date": predicted.strftime(_DATE_FMT),
            "predicted_window_start": window_start.strftime(_DATE_FMT),
            "predicted_window_end": window_end.strftime(_DATE_FMT),
            "confidence": cad["confidence"],
            "cadence_months": cadence_months,
            "history_count": len(dates),
            "basis": basis,
            "last_rfp_id": latest.get("id"),
            "last_rfp_title": latest.get("title"),
        })

    predictions.sort(key=lambda p: (p["predicted_date"], -p["confidence"]))
    return predictions


def _fit_score(prediction: dict, profile: dict) -> int:
    """Lightweight fit of a prediction to a pharmacist profile (0-100)."""
    pred_cats = set(prediction.get("categories") or [])
    my_cats = set(profile.get("specialties") or [])
    cat_overlap = len(pred_cats & my_cats) / len(pred_cats) if pred_cats else 0.0

    from backend.ai.matcher import normalize_state

    state = normalize_state(profile.get("location_state"))
    pred_state = normalize_state(prediction.get("state"))
    loc = 1.0 if state and pred_state and state == pred_state else 0.0

    score = 0.7 * cat_overlap + 0.3 * loc
    return int(round(score * 100))


def personalize_predictions(predictions: list[dict], profile: dict) -> list[dict]:
    """Attach a ``fit_score`` and re-rank by fit x confidence."""
    out = []
    for p in predictions:
        fit = _fit_score(p, profile)
        out.append({**p, "fit_score": fit})
    out.sort(key=lambda p: (p["fit_score"] * p["confidence"]), reverse=True)
    return out


def organization_timeline(org_name: str) -> dict:
    """Posting history + projected next window for a single organization."""
    for org in _org_posting_history():
        if org["organization"] != org_name:
            continue
        postings = sorted(
            ({"date": p["date"], "title": p["title"], "id": p["id"]} for p in org["postings"]),
            key=lambda p: p["date"] or "",
        )
        forecast = next(
            (f for f in forecast_reposts(horizon_days=730) if f["organization"] == org_name),
            None,
        )
        return {"organization": org_name, "postings": postings, "forecast": forecast}
    return {"organization": org_name, "postings": [], "forecast": None}


def explain_prediction(prediction: dict) -> str:
    """One-sentence rationale for a prediction (LLM with deterministic fallback)."""
    fallback = (
        f"{prediction['organization']} is expected to post a "
        f"{prediction.get('category') or 'pharmacy'} RFP around "
        f"{prediction['predicted_date']} based on its {prediction['cadence_months']}-month "
        f"posting cadence."
    )
    try:
        from backend.utils.config import get_settings
        from openai import OpenAI

        settings = get_settings()
        if not settings.openai_api_key:
            return fallback
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "In ONE concise sentence, tell a pharmacist why this upcoming RFP is "
            "predicted, referencing the agency, category and cadence. Be factual.\n"
            f"Agency: {prediction['organization']}\n"
            f"Category: {prediction.get('category')}\n"
            f"Cadence: every {prediction['cadence_months']} months\n"
            f"Predicted: {prediction['predicted_date']}\n"
        )
        resp = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=70,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip() or fallback
    except Exception as e:
        logger.warning(f"explain_prediction fell back: {e}")
        return fallback
