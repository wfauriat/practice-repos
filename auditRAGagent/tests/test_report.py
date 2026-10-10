"""Tests for report generation using mock audit data."""

from pathlib import Path

import pytest

from agentprobe.auditor.auditor import AuditRun
from agentprobe.report.generator import ReportGenerator


@pytest.fixture
def generator():
    return ReportGenerator(thresholds={
        "accuracy_min": 0.85,
        "hallucination_max": 0.10,
        "refusal_rate_min": 0.80,
        "calibration_min": 0.60,
    })


class TestHTMLReport:
    def test_generates_valid_html(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_contains_run_id(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert mock_audit_run.run_id in html

    def test_contains_metrics(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Factual accuracy" in html
        assert "Refusal rate" in html
        assert "Hallucination rate" in html
        assert "Groundedness" in html

    def test_contains_category_sections(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Direct Factual Questions" in html
        assert "Out-of-Scope Questions" in html
        assert "Adversarial Reformulations" in html

    def test_contains_critical_cases(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Critical Cases" in html

    def test_contains_recommendations(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Recommendations" in html

    def test_contains_appendix(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Full Probe Log" in html

    def test_color_coded_badges(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "badge-green" in html or "badge-orange" in html or "badge-red" in html

    def test_has_examples(self, generator, mock_audit_run):
        html = generator.generate(mock_audit_run, fmt="html")
        assert "Good Example" in html
        assert "Bad Example" in html

    def test_write_to_file(self, generator, mock_audit_run, tmp_path):
        path = generator.write(mock_audit_run, tmp_path, fmt="html")
        assert path.exists()
        assert path.suffix == ".html"
        content = path.read_text()
        assert "<!DOCTYPE html>" in content


class TestMarkdownReport:
    def test_generates_markdown(self, generator, mock_audit_run):
        md = generator.generate(mock_audit_run, fmt="markdown")
        assert md.startswith("# Audit Report:")

    def test_contains_dashboard_table(self, generator, mock_audit_run):
        md = generator.generate(mock_audit_run, fmt="markdown")
        assert "| Category | Score | Status |" in md

    def test_contains_all_sections(self, generator, mock_audit_run):
        md = generator.generate(mock_audit_run, fmt="markdown")
        assert "## Executive Summary" in md
        assert "## Metrics Dashboard" in md
        assert "## Analysis by Category" in md
        assert "## Critical Cases" in md
        assert "## Recommendations" in md
        assert "## Appendix: Full Probe Log" in md

    def test_write_to_file(self, generator, mock_audit_run, tmp_path):
        path = generator.write(mock_audit_run, tmp_path, fmt="markdown")
        assert path.exists()
        assert path.suffix == ".md"

    def test_probe_log_table(self, generator, mock_audit_run):
        md = generator.generate(mock_audit_run, fmt="markdown")
        # Should have a row for each probe (match "| 1 | P", "| 2 | P", etc.)
        import re
        log_section = md.split("## Appendix")[1]
        row_count = len(re.findall(r"\| \d+ \| P\d", log_section))
        assert row_count == len(mock_audit_run.probe_results)


class TestOverallScore:
    def test_perfect_score(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m = AuditMetrics(
            accuracy_p1=1.0, refusal_rate_p2=1.0, ambiguity_detection_p3=1.0,
            contradiction_detection_p4=1.0, completeness_p5=1.0,
            adversarial_robustness_p6=1.0, calibration_score_p7=1.0,
            hallucination_rate=0.0, groundedness_score=1.0,
        )
        score = generator._overall_score(m)
        assert score == 1.0

    def test_zero_score(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m = AuditMetrics(hallucination_rate=1.0)
        score = generator._overall_score(m)
        assert score == 0.0

    def test_hallucination_penalizes(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m_clean = AuditMetrics(accuracy_p1=0.9, hallucination_rate=0.0, groundedness_score=0.9)
        m_dirty = AuditMetrics(accuracy_p1=0.9, hallucination_rate=0.5, groundedness_score=0.9)
        assert generator._overall_score(m_clean) > generator._overall_score(m_dirty)


class TestRecommendations:
    def test_low_accuracy_triggers_recommendation(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m = AuditMetrics(accuracy_p1=0.5)
        recs = generator._recommendations(m)
        assert any("accuracy" in r.lower() or "retrieval" in r.lower() for r in recs)

    def test_high_hallucination_triggers_recommendation(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m = AuditMetrics(hallucination_rate=0.3)
        recs = generator._recommendations(m)
        assert any("hallucination" in r.lower() for r in recs)

    def test_all_good_gives_positive_message(self, generator):
        from agentprobe.auditor.metrics import AuditMetrics
        m = AuditMetrics(
            accuracy_p1=0.95, refusal_rate_p2=0.95, ambiguity_detection_p3=0.8,
            contradiction_detection_p4=0.8, completeness_p5=0.8,
            adversarial_robustness_p6=0.8, calibration_score_p7=0.8,
            hallucination_rate=0.02, groundedness_score=0.95,
        )
        recs = generator._recommendations(m)
        assert any("within acceptable" in r.lower() or "continue" in r.lower() for r in recs)
