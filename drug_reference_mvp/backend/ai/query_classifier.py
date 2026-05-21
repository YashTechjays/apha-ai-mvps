"""Classify clinical queries to route to appropriate retrieval / response template."""
from __future__ import annotations

import re
from typing import Dict


QUERY_TYPE_KEYWORDS = {
    "dosing": [
        "dose", "dosing", "dosage", "mg", "mcg", "how much", "frequency",
        "maximum", "starting dose", "titrat", "renal adjustment", "hepatic adjustment",
    ],
    "interaction": [
        "interact", "interaction", "combine", "combination", "with", "concurrent",
        "together", "compatible", "cyp", "p-gp",
    ],
    "adverse_effect": [
        "side effect", "adverse", "toxicity", "reaction", "allerg", "rash",
        "black box", "warning", "rhabdomyolysis", "angioedema",
    ],
    "monitoring": [
        "monitor", "monitoring", "lab", "labs", "level", "inr", "trough",
        "check", "follow-up",
    ],
    "counseling": [
        "counsel", "counseling", "patient education", "teach", "instruct",
        "explain to patient",
    ],
    "pregnancy_lactation": [
        "pregnan", "lactat", "breastfeed", "breast feed", "nursing",
        "category", "trimester", "fetal",
    ],
    "pediatric": [
        "pediatric", "child", "infant", "neonat", "kids", "kg dosing",
    ],
    "mechanism": [
        "mechanism", "moa", "how does", "how it works", "pharmacolog",
        "pharmacodynamic", "pharmacokinetic",
    ],
    "indication": [
        "indication", "indicated", "use for", "treat", "fda-approved",
        "approved for",
    ],
}


def classify_query(query: str) -> str:
    """Return the dominant query type label or 'general'."""
    if not query:
        return "general"
    q = query.lower()
    scores: Dict[str, int] = {}
    for qtype, kws in QUERY_TYPE_KEYWORDS.items():
        score = 0
        for kw in kws:
            if kw in q:
                score += 1
        if score:
            scores[qtype] = score
    if not scores:
        return "general"
    return max(scores.items(), key=lambda kv: kv[1])[0]


SAFETY_REDFLAGS = [
    # Patient-specific dosing requests
    r"\bmy patient\b",
    r"\b(give|prescribe|administer) (?:to|for) (?:my|this) patient\b",
    # Self-harm / illicit
    r"how (much|many) .* to (overdose|kill|harm)",
    r"lethal dose",
    # Diversion
    r"how to obtain.*without prescription",
]


def safety_check(query: str) -> Dict[str, str]:
    """Pre-flight regex safety check on the inbound query."""
    if not query:
        return {"safe": "true", "reason": ""}
    q = query.lower()
    for pattern in SAFETY_REDFLAGS:
        if re.search(pattern, q):
            return {
                "safe": "false",
                "reason": "Query flagged for clinical safety review.",
            }
    return {"safe": "true", "reason": ""}
