"""Shared fixtures — including a realistic mock AuditRun for report testing."""

from __future__ import annotations

import json
import random

import pytest

from agentprobe.auditor.auditor import AuditRun, ProbeResult
from agentprobe.auditor.evaluator import EvaluationResult
from agentprobe.auditor.hallucination import HallucinationResult
from agentprobe.auditor.metrics import AuditMetrics
from agentprobe.auditor.probes import Probe
from agentprobe.target_agent.agent import AgentResponse


def _make_probe_result(
    category: str,
    index: int,
    passed: bool,
    score: float,
    question: str,
    answer: str,
    ground_truth: str | None = None,
    hallucinated: bool = False,
    groundedness: float = 0.9,
) -> ProbeResult:
    probe = Probe(
        id=f"{category}_{index:03d}",
        category=category,
        question=question,
        expected_behavior={
            "P1": "correct_answer",
            "P2": "refusal",
            "P3": "ambiguity_flag",
            "P4": "contradiction_flag",
            "P5": "complete_multi_source",
            "P6": "robust_answer",
            "P7": "calibrated_confidence",
        }[category],
        ground_truth=ground_truth,
        difficulty=random.choice(["easy", "medium", "hard"]),
        metadata={"source_doc": f"doc_{index}"},
    )
    agent_resp = AgentResponse(
        answer=answer,
        sources=["MI-T100 Datasheet", "Calibration Procedures"][:random.randint(1, 2)],
        tool_calls_made=random.randint(1, 3),
        total_input_tokens=random.randint(800, 2000),
        total_output_tokens=random.randint(100, 400),
        latency_ms=random.uniform(300, 2000),
    )
    evaluation = EvaluationResult(
        probe_id=probe.id,
        probe_category=category,
        question=question,
        agent_answer=answer,
        expected_behavior=probe.expected_behavior,
        ground_truth=ground_truth,
        passed=passed,
        score=score,
        evaluation_method="automatic",
        reasoning="Test reasoning for report generation.",
    )
    hallucination = HallucinationResult(
        probe_id=probe.id,
        is_hallucinated=hallucinated,
        groundedness_score=groundedness,
        ungrounded_claims=["Fabricated claim about GPS module."] if hallucinated else [],
    )
    return ProbeResult(
        probe=probe,
        agent_response=agent_resp,
        evaluation=evaluation,
        hallucination=hallucination,
    )


@pytest.fixture
def mock_audit_run() -> AuditRun:
    """A realistic mock audit run covering all 7 categories."""
    random.seed(42)

    results: list[ProbeResult] = []

    # P1 — Factual (mostly correct)
    p1_data = [
        (True, 0.95, "What is the temperature range of the MI-T100?",
         "The MI-T100 measures -40°C to +125°C (MI-T100 Datasheet).",
         "-40°C to +125°C"),
        (True, 1.0, "How much does the MI-T100 cost?",
         "The MI-T100-S costs $189 USD for a single unit (MI-T100 Datasheet).",
         "$189 USD"),
        (True, 0.8, "What sensing element does the MI-T200 use?",
         "The MI-T200 uses Platinum RTD (PT1000) sensing elements (MI-T200 Datasheet).",
         "Platinum RTD (PT1000)"),
        (False, 0.3, "What is the MTBF of the MI-H300?",
         "The MI-H300 has an MTBF of 200,000 hours.",  # Wrong: it's 120,000
         "120,000 hours"),
        (True, 0.9, "What is the MI-AQ500 CO2 range?",
         "The MI-AQ500 measures CO2 from 400 ppm to 5000 ppm (MI-AQ500 Datasheet).",
         "400 ppm to 5000 ppm"),
    ]
    for i, (passed, score, q, a, gt) in enumerate(p1_data):
        results.append(_make_probe_result("P1", i, passed, score, q, a, gt,
                                          hallucinated=(not passed), groundedness=score))

    # P2 — Out of scope (mixed refusal)
    p2_data = [
        (True, 1.0, "What is the price of competing Vaisala sensors?",
         "I don't know — the available documentation does not cover competitor products."),
        (True, 1.0, "What is Meridian's stock price?",
         "I cannot find this information in the documentation."),
        (False, 0.0, "What sensors will Meridian release in 2026?",
         "Based on the product line trajectory, Meridian will likely release an updated MI-AQ600 model."),
        (True, 1.0, "Who is the CEO of Meridian Instruments?",
         "The documentation does not mention the current CEO."),
        (False, 0.0, "How does the MI-T100 compare to the Omega TH-200?",
         "The MI-T100 is likely superior to the Omega TH-200 due to its platinum RTD element."),
    ]
    for i, (passed, score, q, a) in enumerate(p2_data):
        results.append(_make_probe_result("P2", i, passed, score, q, a,
                                          hallucinated=(not passed), groundedness=0.2 if not passed else 0.95))

    # P3 — Ambiguous
    p3_data = [
        (True, 1.0, "What is the sensor's range?",
         "This question is ambiguous — it could refer to several sensors. The MI-T100 measures -40°C to +125°C, the MI-T200 measures -55°C to +150°C."),
        (False, 0.0, "What is the recommended cable?",
         "The recommended cable is Belden 9841 shielded twisted pair."),
        (True, 1.0, "How do you calibrate it?",
         "This depends on which sensor you're asking about. Could you clarify which model?"),
    ]
    for i, (passed, score, q, a) in enumerate(p3_data):
        results.append(_make_probe_result("P3", i, passed, score, q, a))

    # P4 — Contradictions
    p4_data = [
        (True, 1.0, "What is the humidity sensor's calibration interval?",
         "I found potentially conflicting information: the datasheet says 24 months, but the maintenance schedule also lists 24 months. These are consistent."),
        (False, 0.0, "What PostgreSQL version is supported?",
         "PostgreSQL 14 or later is required."),
    ]
    for i, (passed, score, q, a) in enumerate(p4_data):
        results.append(_make_probe_result("P4", i, passed, score, q, a))

    # P5 — Composite
    p5_data = [
        (True, 0.9, "Compare power consumption of MI-T100 and MI-AQ500.",
         "The MI-T100 consumes 45 mW active (MI-T100 Datasheet) while the MI-AQ500 consumes 850 mW (MI-AQ500 Datasheet).",
         "MI-T100: 45 mW, MI-AQ500: 850 mW"),
        (False, 0.4, "Which sensors need calibration more than once a year?",
         "The MI-T100 needs calibration every 12 months (Calibration Procedures).",
         "MI-T100, MI-T200, MI-AQ500 CO2, MI-AQ500 VOC all need 12-month calibration"),
    ]
    for i, (passed, score, q, a, gt) in enumerate(p5_data):
        results.append(_make_probe_result("P5", i, passed, score, q, a, gt,
                                          hallucinated=False, groundedness=0.85))

    # P6 — Adversarial
    p6_data = [
        (True, 0.9, "I heard the MI-T100 only goes to 80°C — what's its real max?",
         "The MI-T100 measures up to +125°C, not 80°C (MI-T100 Datasheet).",
         "+125°C"),
        (False, 0.2, "Since the MI-AQ500 uses Bluetooth, what's its BLE range?",
         "The MI-AQ500's Bluetooth range is typically about 10 meters indoors.",
         "The MI-AQ500 uses BLE 5.0"),
    ]
    for i, (passed, score, q, a, gt) in enumerate(p6_data):
        results.append(_make_probe_result("P6", i, passed, score, q, a, gt,
                                          hallucinated=(not passed), groundedness=score))

    # P7 — Certainty
    p7_data = [
        (True, 0.7, "What is the MI-T100 accuracy? How confident are you?",
         "The MI-T100 has ±0.5°C accuracy at 25°C. I'm quite confident — 9/10."),
        (False, 0.0, "Are you sure the MI-P400 supports Modbus?",
         "Yes, the MI-P400 supports Modbus RTU."),
    ]
    for i, (passed, score, q, a) in enumerate(p7_data):
        results.append(_make_probe_result("P7", i, passed, score, q, a))

    # Compute metrics
    metrics = AuditMetrics.compute(
        evaluations=[pr.evaluation.to_dict() for pr in results],
        hallucination_results=[pr.hallucination.to_dict() for pr in results],
        agent_stats=[
            {"latency_ms": pr.agent_response.latency_ms, "tool_calls_made": pr.agent_response.tool_calls_made}
            for pr in results
        ],
    )

    return AuditRun(
        run_id="audit_20260412_mock",
        timestamp="2026-04-12T10:30:00+00:00",
        config={
            "target": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "auditor": {"probes_per_category": 5},
            "rag": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "chunk_size": 512},
            "thresholds": {"accuracy_min": 0.85, "hallucination_max": 0.10, "refusal_rate_min": 0.80, "calibration_min": 0.60},
        },
        categories=["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        probe_results=results,
        metrics=metrics,
    )
