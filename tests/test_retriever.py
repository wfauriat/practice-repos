"""Integration tests for retriever (chunker + vectorstore + search)."""

from pathlib import Path

import pytest

from agentprobe.target_agent.chunker import DocumentChunker
from agentprobe.target_agent.retriever import Retriever, RetrievalResult
from agentprobe.target_agent.vectorstore import VectorStore


@pytest.fixture()
def corpus_dir(tmp_path: Path) -> Path:
    d = tmp_path / "corpus"
    d.mkdir()
    (d / "sensors.md").write_text(
        "# Sensor Overview\n\n"
        "The MI-T100 is a temperature sensor with a range of -40C to +125C.\n\n"
        "It uses a Platinum RTD sensing element and has IP67 protection.\n\n"
        "The MI-T100 costs $189 for a single unit."
    )
    (d / "software.md").write_text(
        "# MeridianLink Platform\n\n"
        "MeridianLink is a software platform for sensor management.\n\n"
        "It supports up to 16 sensors in the free Desktop edition.\n\n"
        "The Server edition requires PostgreSQL 14 or later."
    )
    return d


@pytest.fixture()
def retriever(tmp_path: Path, corpus_dir: Path) -> Retriever:
    vs = VectorStore(
        persist_dir=str(tmp_path / "chroma"),
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    )
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)
    r = Retriever(vectorstore=vs, chunker=chunker, top_k=3)
    r.index_corpus(corpus_dir)
    return r


class TestRetriever:
    def test_index_creates_chunks(self, retriever: Retriever):
        assert retriever.chunk_count > 0

    def test_search_returns_results(self, retriever: Retriever):
        results = retriever.search("temperature sensor range")
        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)

    def test_search_relevance(self, retriever: Retriever):
        results = retriever.search("temperature sensor")
        # The most relevant chunk should come from the sensors document
        assert results[0].chunk.doc_id == "sensors"

    def test_search_different_topic(self, retriever: Retriever):
        results = retriever.search("PostgreSQL database requirements")
        assert results[0].chunk.doc_id == "software"

    def test_top_k_respected(self, retriever: Retriever):
        results = retriever.search("sensor", top_k=2)
        assert len(results) <= 2

    def test_document_metadata(self, retriever: Retriever):
        meta = retriever.get_document_metadata("sensors")
        assert meta["doc_id"] == "sensors"
        assert meta["title"] == "Sensor Overview"
        assert meta["total_chunks"] > 0

    def test_document_metadata_not_found(self, retriever: Retriever):
        meta = retriever.get_document_metadata("nonexistent")
        assert "error" in meta

    def test_list_documents(self, retriever: Retriever):
        docs = retriever.list_documents()
        doc_ids = {d["doc_id"] for d in docs}
        assert "sensors" in doc_ids
        assert "software" in doc_ids

    def test_index_nonexistent_dir_raises(self, retriever: Retriever):
        with pytest.raises(FileNotFoundError):
            retriever.index_corpus("/nonexistent/path")


class TestVectorStore:
    def test_clear(self, tmp_path: Path, corpus_dir: Path):
        vs = VectorStore(persist_dir=str(tmp_path / "chroma_clear"))
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)
        chunks = chunker.chunk_directory(corpus_dir)
        vs.add_chunks(chunks)
        assert vs.count > 0
        vs.clear()
        assert vs.count == 0

    def test_search_empty_store(self, tmp_path: Path):
        vs = VectorStore(persist_dir=str(tmp_path / "chroma_empty"))
        results = vs.search("anything", top_k=5)
        assert results == []
