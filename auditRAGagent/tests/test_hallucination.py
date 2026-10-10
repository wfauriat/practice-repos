"""Tests for hallucination detection."""

import json

import pytest

from agentprobe.auditor.hallucination import (
    HallucinationChecker,
    HallucinationResult,
    extract_retrieved_chunks,
)


@pytest.fixture(scope="module")
def checker():
    return HallucinationChecker(embedding_model="sentence-transformers/all-MiniLM-L6-v2")


class TestHallucinationChecker:
    def test_grounded_response(self, checker):
        """Answer closely matching retrieved chunks should be grounded."""
        chunks = [
            "The MI-T100 temperature sensor has a range of -40°C to +125°C.",
            "It uses a Platinum RTD sensing element and costs $189.",
        ]
        answer = "The MI-T100 sensor measures from -40°C to +125°C using a Platinum RTD element."
        result = checker.check("test_1", answer, chunks)
        assert result.groundedness_score > 0.5
        assert len(result.ungrounded_claims) == 0

    def test_hallucinated_response(self, checker):
        """Answer with fabricated facts should be flagged."""
        chunks = [
            "The MI-T100 temperature sensor has a range of -40°C to +125°C.",
        ]
        answer = (
            "The MI-T100 connects via Bluetooth 5.0 and has a built-in GPS module "
            "for outdoor geolocation tracking of temperature readings across a mesh network."
        )
        result = checker.check("test_2", answer, chunks)
        assert result.is_hallucinated
        assert len(result.ungrounded_claims) > 0

    def test_empty_answer(self, checker):
        result = checker.check("test_3", "", ["Some chunk content."])
        # No claims extracted → trivially grounded (nothing to contradict)
        assert result.groundedness_score == 1.0
        assert not result.is_hallucinated

    def test_empty_chunks(self, checker):
        result = checker.check("test_4", "The MI-T100 has a range.", [])
        assert result.groundedness_score == 0.0

    def test_factual_check_with_ground_truth(self, checker):
        chunks = ["The MI-T100 costs $189 USD."]
        answer = "The MI-T100 costs $189 USD for a single unit."
        result = checker.check(
            "test_5",
            answer,
            chunks,
            ground_truth="The MI-T100 costs $189 USD.",
        )
        assert result.groundedness_score > 0.5

    def test_factual_check_wrong_facts(self, checker):
        chunks = ["The MI-T100 costs $189 USD."]
        answer = "The MI-T100 costs $500 USD and weighs 200 kg."
        result = checker.check(
            "test_6",
            answer,
            chunks,
            ground_truth="The MI-T100 costs $189 USD.",
        )
        # Should have factual penalty
        assert "missing" in result.details.get("factual", {})

    def test_result_serialization(self):
        r = HallucinationResult(
            probe_id="test",
            is_hallucinated=True,
            groundedness_score=0.3,
            ungrounded_claims=["Fabricated claim"],
            details={"info": "test"},
        )
        d = r.to_dict()
        restored = HallucinationResult.from_dict(d)
        assert restored.probe_id == r.probe_id
        assert restored.is_hallucinated == r.is_hallucinated


class TestExtractRetrievedChunks:
    def test_extracts_from_search_results(self):
        log = [
            {
                "tool": "search_documents",
                "args": {"query": "test"},
                "result": json.dumps([
                    {"content": "Chunk 1 content", "doc_id": "doc1"},
                    {"content": "Chunk 2 content", "doc_id": "doc2"},
                ]),
            },
            {
                "tool": "get_document_metadata",
                "args": {"doc_id": "doc1"},
                "result": json.dumps({"doc_id": "doc1", "title": "Test"}),
            },
        ]
        chunks = extract_retrieved_chunks(log)
        assert len(chunks) == 2
        assert chunks[0] == "Chunk 1 content"

    def test_handles_empty_log(self):
        assert extract_retrieved_chunks([]) == []

    def test_handles_invalid_json(self):
        log = [{"tool": "search_documents", "args": {}, "result": "not json"}]
        assert extract_retrieved_chunks(log) == []
