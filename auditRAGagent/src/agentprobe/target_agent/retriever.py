"""Retriever — combines chunker + vector store for end-to-end RAG retrieval."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from agentprobe.target_agent.chunker import Chunk, DocumentChunker
from agentprobe.target_agent.vectorstore import VectorStore


@dataclass(frozen=True)
class RetrievalResult:
    """A single search hit returned to the caller."""

    chunk: Chunk
    score: float  # lower = more similar (ChromaDB L2 distance)


class Retriever:
    """Orchestrates chunking, indexing, and search over a document corpus."""

    def __init__(
        self,
        vectorstore: VectorStore,
        chunker: DocumentChunker,
        top_k: int = 5,
    ):
        self.vectorstore = vectorstore
        self.chunker = chunker
        self.top_k = top_k

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index_corpus(self, corpus_dir: str | Path) -> int:
        """Chunk and index every supported file in *corpus_dir*.

        Returns the number of chunks indexed.
        """
        corpus_dir = Path(corpus_dir)
        if not corpus_dir.is_dir():
            raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

        chunks = self.chunker.chunk_directory(corpus_dir)
        if not chunks:
            return 0

        self.vectorstore.add_chunks(chunks)
        return len(chunks)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int | None = None) -> list[RetrievalResult]:
        """Return the most relevant chunks for *query*."""
        k = top_k if top_k is not None else self.top_k
        hits = self.vectorstore.search(query, top_k=k)
        return [RetrievalResult(chunk=chunk, score=dist) for chunk, dist in hits]

    # ------------------------------------------------------------------
    # Metadata pass-through
    # ------------------------------------------------------------------

    def get_document_metadata(self, doc_id: str) -> dict:
        return self.vectorstore.get_document_metadata(doc_id)

    def list_documents(self) -> list[dict]:
        return self.vectorstore.list_documents()

    @property
    def chunk_count(self) -> int:
        return self.vectorstore.count
