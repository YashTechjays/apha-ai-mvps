"""One-time script to build/rebuild the RAG knowledge base vector store."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.rag.knowledge_base import build_vector_store

if __name__ == "__main__":
    print("Building APhA knowledge base vector store...")
    vs = build_vector_store()
    print("Done. Vector store ready.")
