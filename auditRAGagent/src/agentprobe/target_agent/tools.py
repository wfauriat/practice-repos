"""Tool definitions and executor for the target RAG agent."""

from __future__ import annotations

import json

from agentprobe.target_agent.retriever import Retriever


# -- Tool JSON schemas (provider-agnostic; wrappers adapt the format) ------

SEARCH_DOCUMENTS_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "Natural-language search query to find relevant document chunks.",
        },
    },
    "required": ["query"],
}

GET_DOCUMENT_METADATA_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "doc_id": {
            "type": "string",
            "description": (
                "The document identifier (stem of the source filename, "
                "e.g. '02_mi_t100_datasheet') to retrieve metadata for."
            ),
        },
    },
    "required": ["doc_id"],
}


class AgentTools:
    """Provides tool definitions and executes tool calls for the agent."""

    def __init__(self, retriever: Retriever):
        self._retriever = retriever

    # ------------------------------------------------------------------
    # Definitions (provider-agnostic dicts — the LLM wrapper converts)
    # ------------------------------------------------------------------

    def definitions(self) -> list[tuple[str, str, dict]]:
        """Return a list of ``(name, description, json_schema)`` tuples."""
        return [
            (
                "search_documents",
                (
                    "Search the document corpus for chunks relevant to the query. "
                    "Returns the top-k most similar text passages with their source document."
                ),
                SEARCH_DOCUMENTS_SCHEMA,
            ),
            (
                "get_document_metadata",
                (
                    "Retrieve metadata for a specific document, including title, "
                    "source filename, and number of chunks."
                ),
                GET_DOCUMENT_METADATA_SCHEMA,
            ),
        ]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool call synchronously and return a JSON string."""
        if tool_name == "search_documents":
            return self._search_documents(arguments["query"])
        if tool_name == "get_document_metadata":
            return self._get_document_metadata(arguments["doc_id"])
        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    # ------------------------------------------------------------------
    # Tool implementations
    # ------------------------------------------------------------------

    def _search_documents(self, query: str) -> str:
        results = self._retriever.search(query)
        hits = []
        for r in results:
            hits.append(
                {
                    "doc_id": r.chunk.doc_id,
                    "title": r.chunk.metadata.get("title", ""),
                    "source_file": r.chunk.metadata.get("source_file", ""),
                    "chunk_index": r.chunk.index,
                    "content": r.chunk.content,
                    "relevance_score": round(r.score, 4),
                }
            )
        return json.dumps(hits, indent=2)

    def _get_document_metadata(self, doc_id: str) -> str:
        meta = self._retriever.get_document_metadata(doc_id)
        return json.dumps(meta, indent=2)
