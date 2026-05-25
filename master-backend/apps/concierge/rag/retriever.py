"""Query the APhA knowledge base and return relevant context chunks."""
from typing import List
from langchain_community.vectorstores import Chroma
from apps.concierge.rag.knowledge_base import get_or_build_vector_store
from apps.concierge.utils.logger import get_logger

logger = get_logger(__name__)

_vector_store: Chroma = None


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = get_or_build_vector_store()
    return _vector_store


def retrieve_context(query: str, k: int = 4) -> List[dict]:
    """
    Retrieve top-k relevant knowledge base chunks for a given query.
    Returns list of {content, source, score}
    """
    vs = get_vector_store()
    results = vs.similarity_search_with_relevance_scores(query, k=k)
    chunks = []
    for doc, score in results:
        if score > 0.2:
            chunks.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": round(score, 3),
            })
    logger.info(f"Retrieved {len(chunks)} chunks for query: '{query[:60]}...'")
    return chunks


def format_context_for_prompt(chunks: List[dict]) -> str:
    """Format retrieved chunks into a string block for the system prompt."""
    if not chunks:
        return "No specific knowledge base content found for this query."
    parts = []
    for chunk in chunks:
        parts.append(f"[Source: {chunk['source']}]\n{chunk['content']}")
    return "\n\n---\n\n".join(parts)
