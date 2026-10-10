"""Tests for metrics aggregation."""

from agentprobe.auditor.metrics import AuditMetrics


def _make_eval(category: str, passed: bool, score: float) -> dict:
    return {"probe_category": category, "passed": passed, "score": score}


def _make_hall(hallucinated: bool, groundedness: float) -> dict:
    return {"is_hallucinated": hallucinated, "groundedness_score": groundedness}


def _make_stats(latency: float, tool_calls: int) -> dict:
    return {"latency_ms": latency, "tool_calls_made": tool_calls}


class TestAuditMetrics:
    def test_compute_basic(self):
        evals = [
            _make_eval("P1", True, 1.0),
            _make_eval("P1", True, 0.8),
            _make_eval("P1", False, 0.3),
            _make_eval("P2", True, 1.0),
            _make_eval("P2", False, 0.0),
        ]
        halls = [
            _make_hall(False, 0.9),
            _make_hall(False, 0.8),
            _make_hall(True, 0.3),
            _make_hall(False, 0.95),
            _make_hall(False, 0.85),
        ]
        stats = [
            _make_stats(500, 2),
            _make_stats(600, 1),
            _make_stats(400, 3),
            _make_stats(300, 1),
            _make_stats(700, 2),
        ]
        m = AuditMetrics.compute(evals, halls, stats)

        assert m.total_probes == 5
        assert m.total_passed == 3
        assert abs(m.accuracy_p1 - 0.7) < 0.01  # (1.0 + 0.8 + 0.3) / 3
        assert abs(m.refusal_rate_p2 - 0.5) < 0.01  # (1.0 + 0.0) / 2
        assert abs(m.hallucination_rate - 0.2) < 0.01  # 1/5
        assert abs(m.avg_response_latency - 500.0) < 0.01
        assert abs(m.tool_use_efficiency - 1.8) < 0.01

    def test_compute_empty(self):
        m = AuditMetrics.compute([], [], [])
        assert m.total_probes == 0
        assert m.accuracy_p1 == 0.0

    def test_failure_categories(self):
        evals = [
            _make_eval("P1", False, 0.2),
            _make_eval("P1", False, 0.1),
            _make_eval("P2", False, 0.0),
            _make_eval("P3", True, 0.8),
        ]
        m = AuditMetrics.compute(evals, [], [])
        assert m.failure_categories == {"P1": 2, "P2": 1}

    def test_round_trip(self):
        m = AuditMetrics(
            accuracy_p1=0.85,
            refusal_rate_p2=0.9,
            total_probes=100,
            total_passed=80,
        )
        d = m.to_dict()
        restored = AuditMetrics.from_dict(d)
        assert restored.accuracy_p1 == m.accuracy_p1
        assert restored.total_probes == m.total_probes

    def test_summary_lines(self):
        m = AuditMetrics(accuracy_p1=0.85, total_probes=10, total_passed=8)
        lines = m.summary_lines()
        assert len(lines) > 0
        assert any("85.0%" in line for line in lines)

    def test_groundedness_computation(self):
        halls = [
            _make_hall(False, 0.9),
            _make_hall(False, 0.7),
        ]
        m = AuditMetrics.compute([], halls, [])
        assert abs(m.groundedness_score - 0.8) < 0.01
