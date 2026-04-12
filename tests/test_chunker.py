"""Tests for the document chunker."""

from pathlib import Path

import pytest

from agentprobe.target_agent.chunker import Chunk, DocumentChunker


class TestDocumentChunker:
    def test_basic_chunking(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph that is a bit longer."
        chunks = chunker.chunk_text(text, doc_id="test")
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.doc_id == "test" for c in chunks)

    def test_chunk_ids_are_unique(self):
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        text = "\n\n".join(f"Paragraph number {i} with some content." for i in range(20))
        chunks = chunker.chunk_text(text, doc_id="test")
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids)), "Chunk IDs must be unique"

    def test_chunk_ids_are_deterministic(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
        text = "Hello world.\n\nThis is a test."
        c1 = chunker.chunk_text(text, doc_id="doc1")
        c2 = chunker.chunk_text(text, doc_id="doc1")
        assert [c.id for c in c1] == [c.id for c in c2]

    def test_overlap_invalid(self):
        with pytest.raises(ValueError, match="chunk_overlap must be less than chunk_size"):
            DocumentChunker(chunk_size=100, chunk_overlap=100)

    def test_small_chunk_size_splits_properly(self):
        chunker = DocumentChunker(chunk_size=30, chunk_overlap=5)
        text = "A short paragraph.\n\nAnother short paragraph."
        chunks = chunker.chunk_text(text, doc_id="test")
        assert len(chunks) >= 2

    def test_long_paragraph_is_split(self):
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        text = "This is a very long paragraph. " * 20
        chunks = chunker.chunk_text(text, doc_id="test")
        assert len(chunks) > 1
        for c in chunks:
            # Allow some slack for overlap mechanics
            assert len(c.content) <= 60, f"Chunk too long: {len(c.content)} chars"

    def test_metadata_propagation(self):
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)
        text = "# My Title\n\nSome content here."
        chunks = chunker.chunk_text(text, doc_id="mydoc", metadata={"source_file": "mydoc.md", "title": "My Title"})
        assert all(c.metadata.get("source_file") == "mydoc.md" for c in chunks)
        assert all(c.metadata.get("title") == "My Title" for c in chunks)
        assert all("chunk_index" in c.metadata for c in chunks)
        assert all("total_chunks" in c.metadata for c in chunks)

    def test_chunk_index_sequential(self):
        chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
        text = "\n\n".join(f"Paragraph {i}." for i in range(10))
        chunks = chunker.chunk_text(text, doc_id="test")
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_empty_text(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk_text("", doc_id="empty")
        assert chunks == []

    def test_chunk_directory(self, tmp_path: Path):
        # Create some test files
        (tmp_path / "doc1.md").write_text("# Doc 1\n\nContent of document one.")
        (tmp_path / "doc2.txt").write_text("Content of document two. No heading.")
        (tmp_path / "ignore.pdf").write_text("Should be ignored")

        chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)
        chunks = chunker.chunk_directory(tmp_path)
        doc_ids = {c.doc_id for c in chunks}
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids
        assert "ignore" not in doc_ids

    def test_extract_title_from_markdown(self):
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
        text = "# My Great Document\n\nSome content."
        chunks = chunker.chunk_text(text, doc_id="test", metadata={"source_file": "test.md", "title": "default"})
        # Title comes from metadata passed in, not auto-extracted here
        assert chunks[0].metadata["title"] == "default"

    def test_chunk_file(self, tmp_path: Path):
        f = tmp_path / "sample.md"
        f.write_text("# Sample\n\nParagraph one.\n\nParagraph two.")
        chunker = DocumentChunker(chunk_size=500, chunk_overlap=50)
        chunks = chunker.chunk_file(f)
        assert len(chunks) >= 1
        assert chunks[0].doc_id == "sample"
        assert chunks[0].metadata["title"] == "Sample"
