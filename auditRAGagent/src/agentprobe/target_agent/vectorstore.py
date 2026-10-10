"""ChromaDB-backed vector store with sentence-transformer embeddings."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from agentprobe.target_agent.chunker import Chunk


class VectorStore:
    """Thin wrapper around a ChromaDB collection.

    Handles persistence, embedding via a local sentence-transformer model,
    and provides search / metadata helpers consumed by the retriever and
    agent tools.
    """

    def __init__(
        self,
        persist_dir: str | Path = ".agentprobe/chromadb",
        collection_name: str = "corpus",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self._persist_dir = Path(persist_dir)
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        self._ef = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._ef,
        )

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def add_chunks(self, chunks: list[Chunk], batch_size: int = 256) -> None:
        """Upsert chunks into the collection in batches."""
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            self._collection.upsert(
                ids=[c.id for c in batch],
                documents=[c.content for c in batch],
                metadatas=[self._serialise_meta(c) for c in batch],
            )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Return the *top_k* most similar chunks to *query*."""
        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        out: list[tuple[Chunk, float]] = []
        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        for cid, doc, meta, dist in zip(ids, docs, metas, dists):
            chunk = Chunk(
                id=cid,
                doc_id=meta.get("doc_id", ""),
                content=doc,
                index=meta.get("chunk_index", 0),
                metadata=meta,
            )
            out.append((chunk, dist))

        return out

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------

    def get_document_metadata(self, doc_id: str) -> dict:
        """Return aggregate metadata for every chunk belonging to *doc_id*."""
        results = self._collection.get(
            where={"doc_id": doc_id},
            include=["metadatas"],
        )
        if not results["metadatas"]:
            return {"error": f"No document found with id '{doc_id}'"}

        metas = results["metadatas"]
        return {
            "doc_id": doc_id,
            "title": metas[0].get("title", doc_id),
            "source_file": metas[0].get("source_file", "unknown"),
            "total_chunks": len(metas),
        }

    def list_documents(self) -> list[dict]:
        """Return a deduplicated list of indexed documents with basic info."""
        all_meta = self._collection.get(include=["metadatas"])["metadatas"]
        seen: dict[str, dict] = {}
        for meta in all_meta:
            did = meta.get("doc_id", "")
            if did not in seen:
                seen[did] = {
                    "doc_id": did,
                    "title": meta.get("title", did),
                    "source_file": meta.get("source_file", ""),
                }
        return list(seen.values())

    @property
    def count(self) -> int:
        return self._collection.count()

    # ------------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Drop and re-create the collection."""
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            embedding_function=self._ef,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _serialise_meta(chunk: Chunk) -> dict:
        """Flatten metadata for ChromaDB (only str/int/float values allowed)."""
        flat: dict = {"doc_id": chunk.doc_id, "chunk_index": chunk.index}
        for k, v in chunk.metadata.items():
            if isinstance(v, (str, int, float, bool)):
                flat[k] = v
        return flat
