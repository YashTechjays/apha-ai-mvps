"""Build structured citation lists from retrieved chunks."""
from __future__ import annotations

from typing import List, Dict, Any


def build_citations(chunks: List[Any]) -> List[Dict[str, Any]]:
    """De-duplicate chunks by source_title and produce a citation list."""
    seen: Dict[str, Dict[str, Any]] = {}
    for ch in chunks:
        title = _get(ch, "source_title", "Unknown Source")
        category = _get(ch, "category", "general")
        source_type = _get(ch, "source_type", category)
        meta = _get(ch, "metadata", {}) or {}
        file_path = meta.get("file_path", "")
        score = _get(ch, "score", 0.0)

        key = title
        if key not in seen:
            seen[key] = {
                "title": title,
                "category": category,
                "source_type": source_type,
                "file_path": file_path,
                "max_score": float(score),
                "snippet_count": 1,
            }
        else:
            seen[key]["snippet_count"] += 1
            if float(score) > seen[key]["max_score"]:
                seen[key]["max_score"] = float(score)

    citations = list(seen.values())
    citations.sort(key=lambda c: c["max_score"], reverse=True)
    return citations


def format_citations_markdown(citations: List[Dict[str, Any]]) -> str:
    if not citations:
        return "_No reference sources were retrieved for this query._"
    lines = ["**Sources**:"]
    for i, c in enumerate(citations, start=1):
        lines.append(
            f"{i}. {c['title']} ({c['category']}) — relevance {c['max_score']:.2f}"
        )
    return "\n".join(lines)


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)
