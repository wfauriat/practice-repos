"""Tests for probe definitions and category parsing."""

import pytest

from agentprobe.auditor.probes import ALL_CATEGORIES, Probe, ProbeCategory, parse_categories


class TestProbeCategory:
    def test_all_categories_has_seven(self):
        assert len(ALL_CATEGORIES) == 7

    def test_category_values(self):
        vals = {c.value for c in ProbeCategory}
        assert vals == {"P1", "P2", "P3", "P4", "P5", "P6", "P7"}

    def test_label_exists(self):
        for cat in ALL_CATEGORIES:
            assert isinstance(cat.label, str)
            assert len(cat.label) > 0

    def test_expected_behavior(self):
        assert ProbeCategory.P1_FACTUAL.expected_behavior == "correct_answer"
        assert ProbeCategory.P2_OUT_OF_SCOPE.expected_behavior == "refusal"


class TestParseCategories:
    def test_all(self):
        cats = parse_categories("all")
        assert len(cats) == 7

    def test_single(self):
        cats = parse_categories("P1")
        assert cats == [ProbeCategory.P1_FACTUAL]

    def test_multiple(self):
        cats = parse_categories("P1,P3,P6")
        assert cats == [ProbeCategory.P1_FACTUAL, ProbeCategory.P3_AMBIGUOUS, ProbeCategory.P6_ADVERSARIAL]

    def test_case_insensitive(self):
        cats = parse_categories("p2,p5")
        assert cats == [ProbeCategory.P2_OUT_OF_SCOPE, ProbeCategory.P5_COMPOSITE]

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown probe category"):
            parse_categories("P8")

    def test_whitespace_tolerance(self):
        cats = parse_categories(" P1 , P2 ")
        assert len(cats) == 2


class TestProbe:
    def test_round_trip(self):
        probe = Probe(
            id="test_123",
            category="P1",
            question="What is the range?",
            expected_behavior="correct_answer",
            ground_truth="-40°C to +125°C",
            difficulty="easy",
            metadata={"source_doc": "mi_t100"},
        )
        d = probe.to_dict()
        restored = Probe.from_dict(d)
        assert restored.id == probe.id
        assert restored.question == probe.question
        assert restored.ground_truth == probe.ground_truth
        assert restored.metadata == probe.metadata

    def test_defaults(self):
        probe = Probe(id="x", category="P2", question="Q?", expected_behavior="refusal")
        assert probe.ground_truth is None
        assert probe.difficulty == "medium"
        assert probe.metadata == {}
