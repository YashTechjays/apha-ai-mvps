"""ChromaDB vector store wrapper with sentence-transformer embeddings."""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

from apps.drug_ref.utils.config import settings
from apps.drug_ref.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Thin wrapper around ChromaDB.

    Lazily initializes the persistent client and embedding function to keep
    test startup fast and avoid hard import-time dependencies.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.collection_name = collection_name or settings.chroma_collection_name
        self._client = None
        self._collection = None
        self._embedder = None

    # ------------------------------------------------------------------ #
    # Lazy initializers
    # ------------------------------------------------------------------ #
    def _get_client(self):
        if self._client is None:
            try:
                import chromadb

                os.makedirs(self.persist_dir, exist_ok=True)
                self._client = chromadb.PersistentClient(path=self.persist_dir)
            except Exception as e:
                logger.warning(f"ChromaDB unavailable, using in-memory fallback: {e}")
                self._client = _InMemoryClient()
        return self._client

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"SentenceTransformer unavailable, using hash embedder: {e}")
                self._embedder = _HashEmbedder()
        return self._embedder

    def _get_collection(self):
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    # ------------------------------------------------------------------ #
    # Embedding
    # ------------------------------------------------------------------ #
    def embed(self, texts: List[str]) -> List[List[float]]:
        embedder = self._get_embedder()
        vectors = embedder.encode(texts) if hasattr(embedder, "encode") else [embedder(t) for t in texts]
        if hasattr(vectors, "tolist"):
            vectors = vectors.tolist()
        return vectors

    # ------------------------------------------------------------------ #
    # Add and query
    # ------------------------------------------------------------------ #
    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        collection = self._get_collection()
        embeddings = self.embed(documents)
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def query(
        self,
        query_text: str,
        top_k: int = 6,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        query_embedding = self.embed([query_text])[0]
        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        # Normalize result into list of dicts
        out: List[Dict[str, Any]] = []
        ids = (result.get("ids") or [[]])[0]
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        dists = (result.get("distances") or [[]])[0]

        for i, doc in enumerate(docs):
            distance = dists[i] if i < len(dists) else 0.0
            # cosine distance -> similarity in [0,1]
            score = max(0.0, 1.0 - float(distance))
            out.append({
                "id": ids[i] if i < len(ids) else f"r{i}",
                "text": doc,
                "metadata": metas[i] if i < len(metas) else {},
                "score": score,
            })
        return out

    def count(self) -> int:
        try:
            return self._get_collection().count()
        except Exception:
            return 0

    def reset(self) -> None:
        try:
            client = self._get_client()
            client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._collection = None


# ---------------------------------------------------------------------- #
# In-memory fallbacks (used in tests / when libraries are unavailable)
# ---------------------------------------------------------------------- #
class _HashEmbedder:
    """Deterministic 64-dim hash-based embedder for tests / fallback."""

    DIM = 64

    def encode(self, texts):
        import hashlib

        vectors = []
        for t in texts:
            h = hashlib.sha256(t.encode("utf-8")).digest()
            # Convert bytes -> [0,1] floats, repeat to fill DIM
            vec = [b / 255.0 for b in h[: self.DIM]]
            while len(vec) < self.DIM:
                vec.append(0.0)
            vectors.append(vec)
        return vectors


class _InMemoryClient:
    """Minimal Chroma-like in-memory client used as fallback."""

    def __init__(self):
        self.collections: Dict[str, "_InMemoryCollection"] = {}

    def get_or_create_collection(self, name: str, metadata=None):
        if name not in self.collections:
            self.collections[name] = _InMemoryCollection(name)
        return self.collections[name]

    def delete_collection(self, name: str):
        self.collections.pop(name, None)


class _InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.records: List[Dict[str, Any]] = []

    def add(self, ids, documents, metadatas, embeddings):
        for i, _id in enumerate(ids):
            self.records.append({
                "id": _id,
                "document": documents[i],
                "metadata": metadatas[i],
                "embedding": embeddings[i],
            })

    def _cosine(self, a, b):
        import math
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def query(self, query_embeddings, n_results=6, where=None):
        qv = query_embeddings[0]
        scored = []
        for r in self.records:
            if where:
                ok = all(r["metadata"].get(k) == v for k, v in where.items())
                if not ok:
                    continue
            sim = self._cosine(qv, r["embedding"])
            scored.append((sim, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:n_results]
        return {
            "ids": [[r["id"] for _, r in top]],
            "documents": [[r["document"] for _, r in top]],
            "metadatas": [[r["metadata"] for _, r in top]],
            "distances": [[1.0 - s for s, _ in top]],
        }

    def count(self):
        return len(self.records)


# Singleton accessor
_global_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _global_store
    if _global_store is None:
        _global_store = VectorStore()
    return _global_store
