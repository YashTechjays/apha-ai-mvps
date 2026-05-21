"""Top-level clinical assistant that orchestrates retrieval + LLM + safety."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from backend.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from backend.ai.query_classifier import classify_query, safety_check
from backend.ai.citation_builder import build_citations, format_citations_markdown
from backend.rag.retriever import get_retriever
from backend.utils.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# Lazy-init module for testability — tests can set OpenAI to None
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class AssistantResponse:
    answer: str
    query_type: str
    citations: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]
    latency_ms: int
    safety_flagged: bool
    safety_reason: Optional[str]
    answer_tokens: int
    used_fallback: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "query_type": self.query_type,
            "citations": self.citations,
            "chunks_used": len(self.chunks),
            "latency_ms": self.latency_ms,
            "safety_flagged": self.safety_flagged,
            "safety_reason": self.safety_reason,
            "answer_tokens": self.answer_tokens,
            "used_fallback": self.used_fallback,
        }


class ClinicalAssistant:
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.openai_model_name
        self.retriever = get_retriever()

    def _get_client(self):
        if OpenAI is None:
            return None
        if not settings.openai_api_key:
            return None
        try:
            return OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            logger.warning(f"OpenAI client init failed: {e}")
            return None

    def answer(self, query: str, category: Optional[str] = None) -> AssistantResponse:
        start = time.time()

        sc = safety_check(query)
        if sc["safe"] != "true":
            return AssistantResponse(
                answer=(
                    "This question appears to involve patient-specific clinical decision-making. "
                    "The APhA Clinical Assistant provides reference information only and cannot "
                    "make recommendations for individual patients. Please consult primary literature "
                    "and the patient's clinical team."
                ),
                query_type="blocked",
                citations=[],
                chunks=[],
                latency_ms=int((time.time() - start) * 1000),
                safety_flagged=True,
                safety_reason=sc["reason"],
                answer_tokens=0,
                used_fallback=True,
            )

        query_type = classify_query(query)

        chunks = self.retriever.retrieve_with_diversity(query)
        chunk_dicts = [
            (c.to_dict() if hasattr(c, "to_dict") else dict(c)) for c in chunks
        ]
        citations = build_citations(chunks)

        client = self._get_client()
        used_fallback = client is None
        if used_fallback:
            answer_text = self._fallback_answer(query, query_type, chunk_dicts, citations)
            answer_tokens = len(answer_text.split())
        else:
            try:
                answer_text, answer_tokens = self._call_llm(query, query_type, chunk_dicts, client)
            except Exception as e:
                logger.warning(f"LLM call failed, falling back: {e}")
                answer_text = self._fallback_answer(query, query_type, chunk_dicts, citations)
                answer_tokens = len(answer_text.split())
                used_fallback = True

        latency_ms = int((time.time() - start) * 1000)

        return AssistantResponse(
            answer=answer_text,
            query_type=query_type,
            citations=citations,
            chunks=chunk_dicts,
            latency_ms=latency_ms,
            safety_flagged=False,
            safety_reason=None,
            answer_tokens=answer_tokens,
            used_fallback=used_fallback,
        )

    def _call_llm(
        self,
        query: str,
        query_type: str,
        chunks: List[Dict[str, Any]],
        client,
    ) -> tuple[str, int]:
        user_prompt = build_user_prompt(query, chunks, query_type)
        resp = client.chat.completions.create(
            model=self.model,
            max_tokens=settings.max_answer_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        tokens = getattr(usage, "completion_tokens", 0) if usage else len(answer.split())
        return answer, tokens

    def _fallback_answer(
        self,
        query: str,
        query_type: str,
        chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> str:
        if not chunks:
            return (
                "_The APhA reference library did not return relevant content for this query._\n\n"
                "Please try rephrasing the question with more specific drug name, indication, "
                "or clinical context. For questions outside the current reference scope, consult "
                "primary literature or specialty clinical resources."
            )

        intro_by_type = {
            "dosing": "Based on APhA reference content, the relevant dosing information is summarized below.",
            "interaction": "The APhA references identify the following relevant drug interaction information.",
            "adverse_effect": "Key adverse effect information from the APhA reference library is summarized below.",
            "monitoring": "The following monitoring parameters are noted in the APhA references.",
            "counseling": "Patient counseling guidance from the APhA references:",
            "pregnancy_lactation": "Pregnancy and lactation considerations from the APhA references:",
            "pediatric": "Pediatric considerations from the APhA references:",
            "mechanism": "Mechanism and pharmacology information from the APhA references:",
            "indication": "Indication information from the APhA references:",
            "general": "Based on the APhA reference library:",
        }
        intro = intro_by_type.get(query_type, intro_by_type["general"])

        section_lines = [intro, ""]
        for ch in chunks[:4]:
            title = ch.get("source_title", "Unknown")
            text = (ch.get("text") or "").strip()
            snippet = text[:600]
            if len(text) > 600:
                snippet += "..."
            section_lines.append(f"**From {title}:**")
            section_lines.append(snippet)
            section_lines.append(f"_[Source: {title}]_")
            section_lines.append("")

        section_lines.append(
            "_This is a deterministic reference-library summary (LLM API not configured). "
            "Verify all clinical decisions against primary literature and patient-specific factors._"
        )
        section_lines.append("")
        section_lines.append(format_citations_markdown(citations))

        return "\n".join(section_lines)


_assistant: Optional[ClinicalAssistant] = None


def get_assistant() -> ClinicalAssistant:
    global _assistant
    if _assistant is None:
        _assistant = ClinicalAssistant()
    return _assistant
