from backend.rag.retriever import retrieve_context


def test_retrieve_returns_results():
    chunks = retrieve_context("How much does student membership cost?")
    assert isinstance(chunks, list)


def test_retrieve_filters_low_relevance():
    chunks = retrieve_context("completely unrelated random query xyz123")
    for chunk in chunks:
        assert chunk["score"] > 0.2


def test_retrieve_returns_source():
    chunks = retrieve_context("What CPE hours are included in membership?")
    for chunk in chunks:
        assert "source" in chunk
        assert "content" in chunk
