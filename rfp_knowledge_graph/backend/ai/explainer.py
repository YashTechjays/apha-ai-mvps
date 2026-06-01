"""Natural-language match explanations from graph paths (Enhancement #5)."""
from typing import Optional
from backend.graph.pharmacist_graph import get_match_explanation_path
from backend.utils.logger import get_logger

logger = get_logger("explainer")


def _format_chain(chain: list) -> str:
    return " -> ".join(str(c) for c in chain)


def explain_match(user_id: str, rfp_id: str, profile: dict, rfp: dict) -> dict:
    """Return a structured explanation: the raw graph path plus a one-sentence
    rationale generated from it. Falls back to a deterministic sentence if the
    LLM call is unavailable."""
    path = get_match_explanation_path(user_id, rfp_id)

    # Deterministic overlap facts (always available, no history required).
    shared = sorted(
        set(profile.get("specialties") or []) & set(rfp.get("categories") or [])
    )

    fallback = _deterministic_sentence(shared, rfp, path)

    try:
        from backend.utils.config import get_settings
        from openai import OpenAI
        settings = get_settings()
        client = OpenAI(api_key=settings.openai_api_key)

        context_lines = [
            f"RFP title: {rfp.get('title')}",
            f"RFP categories: {', '.join(rfp.get('categories') or []) or 'none'}",
            f"Pharmacist specialties: {', '.join(profile.get('specialties') or []) or 'none'}",
            f"Shared categories: {', '.join(shared) or 'none'}",
        ]
        if path:
            context_lines.append(f"Graph connection: {_format_chain(path['chain'])}")

        prompt = (
            "Explain in ONE concise sentence why this RFP was recommended to this "
            "pharmacist, referencing the shared specialties/categories and the graph "
            "connection. Be specific and factual.\n\n" + "\n".join(context_lines)
        )
        resp = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3,
        )
        sentence = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"LLM explanation failed, using fallback: {e}")
        sentence = fallback

    return {
        "rfp_id": rfp_id,
        "explanation": sentence,
        "shared_categories": shared,
        "path": path,
    }


def _deterministic_sentence(shared: list, rfp: dict, path: Optional[dict]) -> str:
    if shared:
        cats = ", ".join(shared)
        base = f"Matched because your {cats} specialty overlaps this RFP's categories"
    else:
        base = "Matched based on your profile and this RFP's requirements"
    if path and path.get("hops"):
        return f"{base} (connected in the graph within {path['hops']} steps)."
    return base + "."
