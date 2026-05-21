"""Content ingestion pipeline: markdown files -> chunks -> vector store + DB."""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.rag.vector_store import get_vector_store
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


# ---------------------------------------------------------------------- #
# Simple chunker (replaces LangChain MarkdownTextSplitter to keep deps minimal)
# ---------------------------------------------------------------------- #
def split_markdown(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[str]:
    """Split markdown by headings then by character length with overlap."""
    if not text:
        return []

    # Split on markdown headings (## or ###) keeping them with their section
    sections = re.split(r"(?=^#{1,3} )", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    chunks: List[str] = []
    for section in sections:
        if len(section) <= chunk_size:
            chunks.append(section)
            continue
        # Sliding window split
        start = 0
        while start < len(section):
            end = min(start + chunk_size, len(section))
            # try to break on paragraph
            if end < len(section):
                last_para = section.rfind("\n\n", start, end)
                if last_para > start + chunk_size // 2:
                    end = last_para
            chunks.append(section[start:end].strip())
            if end >= len(section):
                break
            start = max(0, end - chunk_overlap)
    return [c for c in chunks if c]


def derive_category(file_path: Path) -> str:
    parts = file_path.parts
    if "drug_monographs" in parts:
        return "drug_monograph"
    if "clinical_guidelines" in parts:
        return "clinical_guideline"
    if "pharmacy_practice" in parts:
        return "pharmacy_practice"
    return "general"


def extract_title(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback


def chunk_id_for(source_id: str, idx: int, text: str) -> str:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return f"{source_id}-{idx:03d}-{h}"


# ---------------------------------------------------------------------- #
# Ingestion driver
# ---------------------------------------------------------------------- #
class IngestionPipeline:
    def __init__(
        self,
        content_root: Optional[str] = None,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ):
        if content_root is None:
            content_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "..",
                "content",
            )
        self.content_root = Path(content_root).resolve()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.store = get_vector_store()

    def discover_files(self) -> List[Path]:
        if not self.content_root.exists():
            logger.warning(f"Content root does not exist: {self.content_root}")
            return []
        return sorted(self.content_root.rglob("*.md"))

    def process_file(self, path: Path) -> Dict[str, Any]:
        text = path.read_text(encoding="utf-8")
        title = extract_title(text, path.stem.replace("_", " ").title())
        category = derive_category(path)
        source_id = path.stem
        source_type = category  # use category as source_type label

        chunks = split_markdown(text, self.chunk_size, self.chunk_overlap)
        word_count = len(text.split())

        records: List[ChunkRecord] = []
        for i, ch in enumerate(chunks):
            records.append(ChunkRecord(
                chunk_id=chunk_id_for(source_id, i, ch),
                text=ch,
                metadata={
                    "source_id": source_id,
                    "source_title": title,
                    "source_type": source_type,
                    "category": category,
                    "chunk_index": i,
                    "file_path": str(path.relative_to(self.content_root)),
                },
            ))

        # Push to vector store in one batch
        if records:
            self.store.add(
                ids=[r.chunk_id for r in records],
                documents=[r.text for r in records],
                metadatas=[r.metadata for r in records],
            )

        return {
            "source_id": source_id,
            "title": title,
            "category": category,
            "source_type": source_type,
            "file_path": str(path.relative_to(self.content_root)),
            "chunk_count": len(records),
            "word_count": word_count,
        }

    def run(self) -> List[Dict[str, Any]]:
        files = self.discover_files()
        logger.info(f"Discovered {len(files)} markdown files under {self.content_root}")
        results: List[Dict[str, Any]] = []
        for f in files:
            try:
                summary = self.process_file(f)
                logger.info(
                    f"Ingested {summary['source_id']}: "
                    f"{summary['chunk_count']} chunks, {summary['word_count']} words"
                )
                results.append(summary)
            except Exception as e:
                logger.error(f"Failed to ingest {f}: {e}")
        return results
