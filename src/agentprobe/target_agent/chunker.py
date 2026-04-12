"""Document chunking with configurable size and overlap."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    """A piece of a document with tracking metadata."""

    id: str
    doc_id: str
    content: str
    index: int
    metadata: dict = field(default_factory=dict)


class DocumentChunker:
    """Split documents into overlapping text chunks.

    The chunker tries to break on paragraph boundaries.  When a single
    paragraph exceeds ``chunk_size`` it falls back to sentence boundaries,
    and finally to a hard character split.
    """

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst", ".html"}

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk_file(self, file_path: Path) -> list[Chunk]:
        """Read a single file and return its chunks."""
        text = file_path.read_text(encoding="utf-8")
        doc_id = file_path.stem
        title = self._extract_title(text, fallback=doc_id)
        metadata = {
            "source_file": file_path.name,
            "title": title,
        }
        return self.chunk_text(text, doc_id=doc_id, metadata=metadata)

    def chunk_text(self, text: str, *, doc_id: str, metadata: dict | None = None) -> list[Chunk]:
        """Split *text* into overlapping chunks."""
        metadata = metadata or {}
        paragraphs = self._split_paragraphs(text)
        raw_chunks = self._merge_paragraphs(paragraphs)
        chunks: list[Chunk] = []
        for idx, raw in enumerate(raw_chunks):
            chunk_id = self._make_id(doc_id, idx)
            chunks.append(
                Chunk(
                    id=chunk_id,
                    doc_id=doc_id,
                    content=raw,
                    index=idx,
                    metadata={**metadata, "chunk_index": idx, "total_chunks": len(raw_chunks)},
                )
            )
        return chunks

    def chunk_directory(self, dir_path: Path) -> list[Chunk]:
        """Chunk every supported file in *dir_path* (non-recursive)."""
        all_chunks: list[Chunk] = []
        for fpath in sorted(dir_path.iterdir()):
            if fpath.is_file() and fpath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                all_chunks.extend(self.chunk_file(fpath))
        return all_chunks

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        """Split text on blank lines, keeping non-empty paragraphs."""
        parts = re.split(r"\n{2,}", text.strip())
        return [p.strip() for p in parts if p.strip()]

    def _merge_paragraphs(self, paragraphs: list[str]) -> list[str]:
        """Greedily merge paragraphs into chunks respecting size limits."""
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)

            # Paragraph itself exceeds chunk_size → split it further
            if para_len > self.chunk_size:
                # Flush current accumulator first
                if current:
                    chunks.append("\n\n".join(current))
                    current, current_len = [], 0
                chunks.extend(self._split_long_paragraph(para))
                continue

            # Adding this paragraph would exceed the limit
            separator_len = 2 if current else 0  # "\n\n"
            if current_len + separator_len + para_len > self.chunk_size:
                chunks.append("\n\n".join(current))
                # Overlap: keep tail characters from the previous chunk
                overlap_text = self._overlap_tail(chunks[-1])
                if overlap_text:
                    current = [overlap_text]
                    current_len = len(overlap_text) + 2  # account for separator
                else:
                    current, current_len = [], 0

            current.append(para)
            current_len += (2 if len(current) > 1 else 0) + para_len

        if current:
            chunks.append("\n\n".join(current))

        return chunks

    def _split_long_paragraph(self, text: str) -> list[str]:
        """Split a paragraph that is longer than chunk_size."""
        # Try sentence boundaries first
        sentences = re.split(r"(?<=[.!?])\s+", text)
        if len(sentences) > 1:
            return self._merge_paragraphs(sentences)

        # Hard split as last resort
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    def _overlap_tail(self, text: str) -> str:
        """Return the last ``chunk_overlap`` characters for overlap."""
        if self.chunk_overlap <= 0:
            return ""
        return text[-self.chunk_overlap :]

    @staticmethod
    def _make_id(doc_id: str, index: int) -> str:
        raw = f"{doc_id}::{index}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def _extract_title(text: str, fallback: str) -> str:
        """Pull the first Markdown heading, if any."""
        match = re.match(r"^#\s+(.+)", text.strip())
        return match.group(1).strip() if match else fallback
