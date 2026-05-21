"""
Build and persist the APhA knowledge base vector store using ChromaDB.
Run once with: python scripts/ingest_knowledge_base.py
"""
from pathlib import Path
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from backend.utils.config import get_settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

CONTENT_DIR = Path(__file__).parent / "content"
COLLECTION_NAME = "apha_knowledge_base"


def get_embeddings():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


def build_vector_store() -> Chroma:
    """Ingest all markdown files in content/ and build the ChromaDB vector store."""
    splitter = MarkdownTextSplitter(chunk_size=600, chunk_overlap=80)
    docs = []
    for md_file in sorted(CONTENT_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = splitter.create_documents(
            [text],
            metadatas=[{"source": md_file.stem, "filename": md_file.name}],
        )
        docs.extend(chunks)
        logger.info(f"Ingested {md_file.name}: {len(chunks)} chunks")

    logger.info(f"Total chunks: {len(docs)}")
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=settings.chroma_persist_dir,
    )
    logger.info(f"Vector store built and persisted to {settings.chroma_persist_dir}")
    return vector_store


def load_vector_store() -> Chroma:
    """Load existing vector store from disk."""
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )


def get_or_build_vector_store() -> Chroma:
    """Load if exists, build if not."""
    persist_path = Path(settings.chroma_persist_dir)
    if persist_path.exists() and any(persist_path.iterdir()):
        logger.info("Loading existing vector store...")
        return load_vector_store()
    logger.info("Building vector store from scratch...")
    return build_vector_store()
