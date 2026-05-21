"""Ingest clinical content markdown into Chroma + database.

Usage:
    python -m scripts.ingest_content [--reset]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.db.base import Base  # noqa: E402
from backend.db.models import ContentSource  # noqa: E402
from backend.db.session import SessionLocal, engine  # noqa: E402
from backend.rag.ingestion.pipeline import IngestionPipeline  # noqa: E402
from backend.rag.vector_store import get_vector_store  # noqa: E402
from backend.utils.logger import get_logger  # noqa: E402

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset vector store before ingesting")
    parser.add_argument("--content-root", default=str(ROOT / "content"))
    args = parser.parse_args()

    # Ensure DB tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"create_all warning: {e}")

    if args.reset:
        logger.info("Resetting vector store...")
        get_vector_store().reset()

    pipeline = IngestionPipeline(content_root=args.content_root)
    results = pipeline.run()

    # Mirror to DB
    db = SessionLocal()
    try:
        for r in results:
            existing = (
                db.query(ContentSource)
                .filter(ContentSource.title == r["title"])
                .first()
            )
            if existing:
                existing.chunk_count = r["chunk_count"]
                existing.word_count = r["word_count"]
                existing.file_path = r["file_path"]
                existing.source_type = r["source_type"]
                existing.category = r["category"]
                existing.is_active = True
            else:
                db.add(ContentSource(
                    title=r["title"],
                    source_type=r["source_type"],
                    category=r["category"],
                    file_path=r["file_path"],
                    chunk_count=r["chunk_count"],
                    word_count=r["word_count"],
                    is_active=True,
                    version="2024.1",
                ))
        db.commit()
    finally:
        db.close()

    total_chunks = sum(r["chunk_count"] for r in results)
    logger.info(f"Ingestion complete: {len(results)} files, {total_chunks} chunks total.")


if __name__ == "__main__":
    main()
