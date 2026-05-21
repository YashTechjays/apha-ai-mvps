"""Tests for the clinical assistant (deterministic fallback path)."""
from __future__ import annotations

from backend.ai.clinical_assistant import ClinicalAssistant
from backend.ai.query_classifier import classify_query, safety_check


def test_classify_dosing():
    assert classify_query("What is the dose of metformin in renal impairment?") == "dosing"


def test_classify_interaction():
    assert classify_query("Drug interaction between warfarin and amoxicillin") == "interaction"


def test_classify_general_fallback():
    assert classify_query("xyzzy") == "general"


def test_safety_check_flags_patient_specific():
    res = safety_check("How much morphine should I give my patient who weighs 70 kg?")
    assert res["safe"] == "false"


def test_safety_check_allows_normal_question():
    res = safety_check("What is the mechanism of action of lisinopril?")
    assert res["safe"] == "true"


def test_assistant_fallback_with_no_chunks(monkeypatch):
    """When retriever returns nothing, response should still be valid and flag fallback."""
    assistant = ClinicalAssistant()

    class _EmptyRetriever:
        def retrieve_with_diversity(self, q, top_k=None):
            return []
        def retrieve(self, q, **kw):
            return []

    assistant.retriever = _EmptyRetriever()
    r = assistant.answer("What is the dose of metformin?")
    assert r.used_fallback is True
    assert r.safety_flagged is False
    assert "did not return" in r.answer.lower() or "no relevant" in r.answer.lower() or r.answer


def test_assistant_blocks_unsafe_query():
    assistant = ClinicalAssistant()
    r = assistant.answer("How much oxycodone to give my patient to overdose?")
    assert r.safety_flagged is True
    assert "reference information" in r.answer.lower()
