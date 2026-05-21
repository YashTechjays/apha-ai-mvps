"""Tests for the RAG ingestion pipeline and retriever."""
from __future__ import annotations

from pathlib import Path

from backend.rag.ingestion.pipeline import (
    IngestionPipeline,
    derive_category,
    extract_title,
    split_markdown,
)
from backend.rag.retriever import Retriever
from backend.rag.vector_store import VectorStore


def test_split_markdown_basic():
    text = "# Title\n\n## Section A\n" + ("paragraph. " * 80) + "\n\n## Section B\nshort body."
    chunks = split_markdown(text, chunk_size=400, chunk_overlap=50)
    assert len(chunks) >= 2
    assert all(c for c in chunks)


def test_extract_title_falls_back():
    assert extract_title("# Metformin", "x") == "Metformin"
    assert extract_title("no heading here", "fallback") == "fallback"


def test_derive_category():
    p = Path("/some/content/drug_monographs/x.md")
    assert derive_category(p) == "drug_monograph"
    p2 = Path("/some/content/clinical_guidelines/y.md")
    assert derive_category(p2) == "clinical_guideline"


def test_ingestion_and_retrieval_end_to_end(tmp_path, monkeypatch):
    # Build a tiny content tree
    root = tmp_path / "content"
    (root / "drug_monographs").mkdir(parents=True)
    (root / "drug_monographs" / "metformin.md").write_text(
        "# Metformin\n\nMetformin lowers hepatic glucose production. Renal dosing: avoid if eGFR <30.\n"
    )
    (root / "clinical_guidelines").mkdir(parents=True)
    (root / "clinical_guidelines" / "diabetes.md").write_text(
        "# Diabetes\n\nFirst-line treatment for T2D is lifestyle plus metformin.\n"
    )

    # Use isolated vector store
    vs = VectorStore(persist_dir=str(tmp_path / "chroma"), collection_name="test_col")
    monkeypatch.setattr("backend.rag.ingestion.pipeline.get_vector_store", lambda: vs)
    monkeypatch.setattr("backend.rag.retriever.get_vector_store", lambda: vs)

    pipeline = IngestionPipeline(content_root=str(root))
    results = pipeline.run()
    assert len(results) == 2
    assert all(r["chunk_count"] >= 1 for r in results)

    # Query
    retriever = Retriever(top_k=4, min_score=0.0)
    retriever.store = vs
    chunks = retriever.retrieve("metformin renal dosing")
    assert len(chunks) >= 1
    assert any("metformin" in c.text.lower() for c in chunks)
