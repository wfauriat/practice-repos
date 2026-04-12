"""Tests for the agent tools."""

import json
from pathlib import Path

import pytest

from agentprobe.target_agent.chunker import DocumentChunker
from agentprobe.target_agent.retriever import Retriever
from agentprobe.target_agent.tools import AgentTools
from agentprobe.target_agent.vectorstore import VectorStore


@pytest.fixture()
def tools(tmp_path: Path) -> AgentTools:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "widgets.md").write_text(
        "# Widget Manual\n\n"
        "The Widget X200 weighs 350 grams and operates at 5V DC.\n\n"
        "It was released in March 2022 and costs $99.\n\n"
        "The Widget X200 has a maximum operating temperature of 85C."
    )
    vs = VectorStore(persist_dir=str(tmp_path / "chroma"))
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=30)
    retriever = Retriever(vectorstore=vs, chunker=chunker, top_k=3)
    retriever.index_corpus(corpus)
    return AgentTools(retriever)


class TestAgentTools:
    def test_definitions(self, tools: AgentTools):
        defs = tools.definitions()
        assert len(defs) == 2
        names = {d[0] for d in defs}
        assert names == {"search_documents", "get_document_metadata"}

    def test_search_documents(self, tools: AgentTools):
        result = tools.execute("search_documents", {"query": "widget weight"})
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0
        assert "content" in parsed[0]
        assert "doc_id" in parsed[0]

    def test_get_document_metadata(self, tools: AgentTools):
        result = tools.execute("get_document_metadata", {"doc_id": "widgets"})
        parsed = json.loads(result)
        assert parsed["doc_id"] == "widgets"
        assert parsed["title"] == "Widget Manual"

    def test_unknown_tool(self, tools: AgentTools):
        result = tools.execute("nonexistent_tool", {})
        parsed = json.loads(result)
        assert "error" in parsed
