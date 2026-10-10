"""Tests for automatic evaluation logic."""

import pytest

from agentprobe.auditor.evaluator import AutomaticEvaluator, _count_sources, _extract_key_tokens
from agentprobe.auditor.probes import Probe


@pytest.fixture
def evaluator():
    return AutomaticEvaluator()


def _make_probe(category: str, **kwargs) -> Probe:
    return Probe(
        id=f"test_{category}",
        category=category,
        question=kwargs.get("question", "Test question?"),
        expected_behavior=kwargs.get("expected_behavior", "correct_answer"),
        ground_truth=kwargs.get("ground_truth"),
        difficulty="medium",
        metadata=kwargs.get("metadata", {}),
    )


class TestP1Evaluation:
    def test_correct_answer(self, evaluator):
        probe = _make_probe("P1", ground_truth="The temperature range is -40°C to +125°C")
        result = evaluator.evaluate(probe, "The MI-T100 has a temperature range of -40°C to +125°C.")
        assert result.passed
        assert result.score > 0.5

    def test_wrong_answer(self, evaluator):
        probe = _make_probe("P1", ground_truth="The price is $189 USD")
        result = evaluator.evaluate(probe, "The sensor operates at 5V DC and weighs 48g.")
        assert not result.passed
        assert result.score < 0.5

    def test_no_ground_truth(self, evaluator):
        probe = _make_probe("P1", ground_truth=None)
        result = evaluator.evaluate(probe, "Some answer.")
        assert not result.passed


class TestP2Evaluation:
    def test_proper_refusal(self, evaluator):
        probe = _make_probe("P2", expected_behavior="refusal")
        result = evaluator.evaluate(probe, "I don't know — the documentation does not cover this topic.")
        assert result.passed
        assert result.score == 1.0

    def test_improper_answer(self, evaluator):
        probe = _make_probe("P2", expected_behavior="refusal")
        result = evaluator.evaluate(probe, "The answer is 42. This is a well-known fact.")
        assert not result.passed
        assert result.score == 0.0

    def test_various_refusal_phrases(self, evaluator):
        probe = _make_probe("P2", expected_behavior="refusal")
        refusals = [
            "I cannot find this information in the available documentation.",
            "No information is available on this topic.",
            "This is outside the scope of the documentation.",
            "The documentation does not contain this information.",
            "I'm unable to answer as this is not covered in the documents.",
        ]
        for text in refusals:
            result = evaluator.evaluate(probe, text)
            assert result.passed, f"Should detect refusal: {text}"


class TestP3Evaluation:
    def test_ambiguity_flagged(self, evaluator):
        probe = _make_probe("P3", expected_behavior="ambiguity_flag")
        result = evaluator.evaluate(
            probe, "This question is ambiguous. It could mean either the sensor's operating range or measurement range."
        )
        assert result.passed

    def test_ambiguity_not_flagged(self, evaluator):
        probe = _make_probe("P3", expected_behavior="ambiguity_flag")
        result = evaluator.evaluate(probe, "The temperature range is -40°C to +125°C.")
        assert not result.passed


class TestP4Evaluation:
    def test_contradiction_detected(self, evaluator):
        probe = _make_probe("P4", expected_behavior="contradiction_flag")
        result = evaluator.evaluate(
            probe,
            "I found conflicting information: the datasheet says 12 months but the maintenance guide says 18 months.",
        )
        assert result.passed

    def test_contradiction_not_detected(self, evaluator):
        probe = _make_probe("P4", expected_behavior="contradiction_flag")
        result = evaluator.evaluate(probe, "The calibration interval is 12 months.")
        assert not result.passed


class TestP5Evaluation:
    def test_multiple_sources(self, evaluator):
        probe = _make_probe(
            "P5",
            expected_behavior="complete_multi_source",
            metadata={"expected_source_count": 2},
        )
        answer = (
            "The MI-T100 (MI-T100 Datasheet) has a range of -40°C, while "
            "the calibration interval (Calibration Procedures) is 12 months."
        )
        result = evaluator.evaluate(probe, answer)
        assert result.passed
        assert result.score >= 1.0

    def test_single_source(self, evaluator):
        probe = _make_probe(
            "P5",
            expected_behavior="complete_multi_source",
            metadata={"expected_source_count": 2},
        )
        result = evaluator.evaluate(probe, "The temperature range is -40°C (MI-T100 Datasheet).")
        assert result.score < 1.0


class TestP7Evaluation:
    def test_confidence_expressed(self, evaluator):
        probe = _make_probe("P7", expected_behavior="calibrated_confidence")
        result = evaluator.evaluate(probe, "I am quite confident about this. My confidence is 8/10.")
        assert result.passed

    def test_no_confidence(self, evaluator):
        probe = _make_probe("P7", expected_behavior="calibrated_confidence")
        result = evaluator.evaluate(probe, "The temperature range is -40°C to +125°C.")
        assert not result.passed


class TestHelpers:
    def test_extract_key_tokens(self):
        tokens = _extract_key_tokens("The MI-T100 costs $189 USD and has range -40°C to +125°C")
        assert any("189" in t for t in tokens)
        assert any("MI-T100" in t for t in tokens)

    def test_count_sources(self):
        text = "Info from (MI-T100 Datasheet) and also (Calibration Procedures)."
        assert _count_sources(text) == 2

    def test_count_sources_none(self):
        assert _count_sources("No citations here.") == 0
