"""OpenAI embeddings for RFP semantic similarity (Enhancement #2)."""
from typing import Optional
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger("embeddings")


def embed_text(text: str) -> Optional[list[float]]:
    """Return an embedding vector for arbitrary text, or None on failure."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        from openai import OpenAI
        settings = get_settings()
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(
            model=settings.embedding_model_name,
            input=text[:8000],  # stay well under token limits
        )
        return resp.data[0].embedding
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return None


def embed_rfp(rfp: dict) -> Optional[list[float]]:
    """Build a single embedding from the RFP's most descriptive fields."""
    parts = [
        rfp.get("title") or "",
        rfp.get("description") or "",
        " ".join(rfp.get("categories") or []),
        " ".join(rfp.get("requirements") or []),
    ]
    combined = "\n".join(p for p in parts if p).strip()
    if not combined:
        return None
    return embed_text(combined)
