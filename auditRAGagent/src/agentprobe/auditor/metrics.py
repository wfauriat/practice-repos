"""Aggregate audit metrics computed from evaluation results."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class AuditMetrics:
    """Metrics aggregated across all probes in an audit run."""

    # Per-category scores (0.0–1.0)
    accuracy_p1: float = 0.0
    refusal_rate_p2: float = 0.0
    ambiguity_detection_p3: float = 0.0
    contradiction_detection_p4: float = 0.0
    completeness_p5: float = 0.0
    adversarial_robustness_p6: float = 0.0
    calibration_score_p7: float = 0.0

    # Transversal metrics
    hallucination_rate: float = 0.0
    groundedness_score: float = 0.0
    avg_response_latency: float = 0.0
    tool_use_efficiency: float = 0.0
    failure_categories: dict = field(default_factory=dict)

    # Counts for context
    total_probes: int = 0
    total_passed: int = 0

    @classmethod
    def compute(
        cls,
        evaluations: list[dict],
        hallucination_results: list[dict],
        agent_stats: list[dict],
    ) -> AuditMetrics:
        """Build metrics from raw evaluation/hallucination/agent dicts.

        Parameters
        ----------
        evaluations:
            List of EvaluationResult-like dicts (keys: probe_category,
            passed, score, …).
        hallucination_results:
            List of HallucinationResult-like dicts (keys: is_hallucinated,
            groundedness_score, …).
        agent_stats:
            List of dicts with ``latency_ms`` and ``tool_calls_made``.
        """
        m = cls()
        m.total_probes = len(evaluations)
        m.total_passed = sum(1 for e in evaluations if e.get("passed"))

        # --- Per-category averages ---
        m.accuracy_p1 = _avg_score(evaluations, "P1")
        m.refusal_rate_p2 = _avg_score(evaluations, "P2")
        m.ambiguity_detection_p3 = _avg_score(evaluations, "P3")
        m.contradiction_detection_p4 = _avg_score(evaluations, "P4")
        m.completeness_p5 = _avg_score(evaluations, "P5")
        m.adversarial_robustness_p6 = _avg_score(evaluations, "P6")
        m.calibration_score_p7 = _avg_score(evaluations, "P7")

        # --- Hallucination ---
        if hallucination_results:
            m.hallucination_rate = (
                sum(1 for h in hallucination_results if h.get("is_hallucinated"))
                / len(hallucination_results)
            )
            gs = [h.get("groundedness_score", 0) for h in hallucination_results]
            m.groundedness_score = sum(gs) / len(gs) if gs else 0.0

        # --- Agent-level stats ---
        if agent_stats:
            lats = [s.get("latency_ms", 0) for s in agent_stats]
            m.avg_response_latency = sum(lats) / len(lats)
            tcs = [s.get("tool_calls_made", 0) for s in agent_stats]
            m.tool_use_efficiency = sum(tcs) / len(tcs)

        # --- Failure breakdown ---
        failures = Counter()
        for e in evaluations:
            if not e.get("passed"):
                failures[e.get("probe_category", "unknown")] += 1
        m.failure_categories = dict(failures)

        return m

    def to_dict(self) -> dict:
        return {
            "accuracy_p1": self.accuracy_p1,
            "refusal_rate_p2": self.refusal_rate_p2,
            "ambiguity_detection_p3": self.ambiguity_detection_p3,
            "contradiction_detection_p4": self.contradiction_detection_p4,
            "completeness_p5": self.completeness_p5,
            "adversarial_robustness_p6": self.adversarial_robustness_p6,
            "calibration_score_p7": self.calibration_score_p7,
            "hallucination_rate": self.hallucination_rate,
            "groundedness_score": self.groundedness_score,
            "avg_response_latency": self.avg_response_latency,
            "tool_use_efficiency": self.tool_use_efficiency,
            "failure_categories": self.failure_categories,
            "total_probes": self.total_probes,
            "total_passed": self.total_passed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> AuditMetrics:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def summary_lines(self) -> list[str]:
        """Human-readable one-line-per-metric summary."""
        lines = [
            f"P1  Factual accuracy:      {self.accuracy_p1:.1%}",
            f"P2  Refusal rate:           {self.refusal_rate_p2:.1%}",
            f"P3  Ambiguity detection:    {self.ambiguity_detection_p3:.1%}",
            f"P4  Contradiction detection:{self.contradiction_detection_p4:.1%}",
            f"P5  Completeness:           {self.completeness_p5:.1%}",
            f"P6  Adversarial robustness: {self.adversarial_robustness_p6:.1%}",
            f"P7  Calibration:            {self.calibration_score_p7:.1%}",
            f"",
            f"Hallucination rate:         {self.hallucination_rate:.1%}",
            f"Groundedness:               {self.groundedness_score:.1%}",
            f"Avg latency:                {self.avg_response_latency:.0f} ms",
            f"Avg tool calls:             {self.tool_use_efficiency:.1f}",
            f"Total probes:               {self.total_probes}",
            f"Passed:                     {self.total_passed}/{self.total_probes}",
        ]
        return lines


def _avg_score(evaluations: list[dict], category: str) -> float:
    scores = [e["score"] for e in evaluations if e.get("probe_category") == category]
    return sum(scores) / len(scores) if scores else 0.0
