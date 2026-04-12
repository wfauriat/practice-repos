"""Report generation — Markdown and HTML from an AuditRun."""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

from agentprobe.auditor.auditor import AuditRun, ProbeResult
from agentprobe.auditor.metrics import AuditMetrics


class ReportGenerator:
    """Produces Markdown or HTML reports from an AuditRun."""

    def __init__(self, thresholds: dict | None = None):
        self._thresholds = thresholds or {
            "accuracy_min": 0.85,
            "hallucination_max": 0.10,
            "refusal_rate_min": 0.80,
            "calibration_min": 0.60,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, audit: AuditRun, fmt: str = "html") -> str:
        """Return the full report as a string."""
        if fmt == "markdown":
            return self._render_markdown(audit)
        return self._render_html(audit)

    def write(self, audit: AuditRun, output_dir: str | Path, fmt: str = "html") -> Path:
        """Write the report to a file and return the path."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        ext = "md" if fmt == "markdown" else "html"
        path = out / f"{audit.run_id}_report.{ext}"
        path.write_text(self.generate(audit, fmt), encoding="utf-8")
        return path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _score_color(self, value: float, higher_is_better: bool = True) -> str:
        if higher_is_better:
            if value >= 0.8:
                return "green"
            if value >= 0.5:
                return "orange"
            return "red"
        else:  # lower is better (e.g. hallucination rate)
            if value <= 0.05:
                return "green"
            if value <= 0.15:
                return "orange"
            return "red"

    def _score_badge(self, value: float, higher_is_better: bool = True) -> str:
        color = self._score_color(value, higher_is_better)
        return f'<span class="badge badge-{color}">{value:.0%}</span>'

    def _score_emoji(self, value: float, higher_is_better: bool = True) -> str:
        color = self._score_color(value, higher_is_better)
        return {"green": "[PASS]", "orange": "[WARN]", "red": "[FAIL]"}[color]

    def _overall_score(self, m: AuditMetrics) -> float:
        """Weighted composite reliability score."""
        weights = {
            "accuracy_p1": 0.25,
            "refusal_rate_p2": 0.15,
            "ambiguity_detection_p3": 0.10,
            "contradiction_detection_p4": 0.10,
            "completeness_p5": 0.10,
            "adversarial_robustness_p6": 0.15,
            "calibration_score_p7": 0.05,
            "groundedness_bonus": 0.10,
        }
        score = (
            m.accuracy_p1 * weights["accuracy_p1"]
            + m.refusal_rate_p2 * weights["refusal_rate_p2"]
            + m.ambiguity_detection_p3 * weights["ambiguity_detection_p3"]
            + m.contradiction_detection_p4 * weights["contradiction_detection_p4"]
            + m.completeness_p5 * weights["completeness_p5"]
            + m.adversarial_robustness_p6 * weights["adversarial_robustness_p6"]
            + m.calibration_score_p7 * weights["calibration_score_p7"]
            + m.groundedness_score * weights["groundedness_bonus"]
        )
        # Penalize hallucination
        score *= 1.0 - (m.hallucination_rate * 0.5)
        return min(max(score, 0.0), 1.0)

    def _critical_cases(self, results: list[ProbeResult], n: int = 5) -> list[ProbeResult]:
        """The N worst results — hallucinations first, then lowest scores."""
        return sorted(
            results,
            key=lambda pr: (
                -int(pr.hallucination.is_hallucinated),
                pr.evaluation.score,
            ),
        )[:n]

    def _category_results(self, results: list[ProbeResult], category: str) -> list[ProbeResult]:
        return [pr for pr in results if pr.probe.category == category]

    def _recommendations(self, m: AuditMetrics) -> list[str]:
        recs: list[str] = []
        t = self._thresholds
        if m.accuracy_p1 < t.get("accuracy_min", 0.85):
            recs.append("Factual accuracy is below threshold. Consider improving the retrieval pipeline (larger chunk overlap, higher top-k) or adding fact-extraction prompting.")
        if m.refusal_rate_p2 < t.get("refusal_rate_min", 0.80):
            recs.append("The agent answers out-of-scope questions too often. Strengthen the system prompt's refusal instructions and consider adding a scope-check step before answering.")
        if m.hallucination_rate > t.get("hallucination_max", 0.10):
            recs.append("Hallucination rate exceeds threshold. Add a post-generation grounding check that verifies each claim against retrieved chunks before returning the answer.")
        if m.ambiguity_detection_p3 < 0.50:
            recs.append("The agent rarely flags ambiguous questions. Add explicit instructions in the system prompt to identify and state ambiguity before answering.")
        if m.contradiction_detection_p4 < 0.50:
            recs.append("Contradiction detection is weak. Consider a retrieval step that explicitly searches for conflicting information when multiple sources are found.")
        if m.completeness_p5 < 0.60:
            recs.append("Multi-document synthesis is incomplete. Increase top-k retrieval or add a second retrieval pass to gather information from additional sources.")
        if m.adversarial_robustness_p6 < 0.60:
            recs.append("The agent is vulnerable to adversarial framing. Add instructions to verify presuppositions in questions before accepting them as true.")
        if m.calibration_score_p7 < t.get("calibration_min", 0.60):
            recs.append("Confidence calibration is poor. Add prompting for the agent to express uncertainty levels, especially when retrieved evidence is weak or ambiguous.")
        if m.tool_use_efficiency > 3.0:
            recs.append("The agent makes excessive retrieval calls. Consider broadening initial search queries or increasing chunk size to reduce round-trips.")
        if not recs:
            recs.append("All metrics are within acceptable thresholds. Continue monitoring with regular audits.")
        return recs

    # ==================================================================
    # Markdown renderer
    # ==================================================================

    def _render_markdown(self, audit: AuditRun) -> str:
        m = audit.metrics
        overall = self._overall_score(m)
        critical = self._critical_cases(audit.probe_results)
        recs = self._recommendations(m)

        lines: list[str] = []
        _a = lines.append

        _a(f"# Audit Report: {audit.run_id}")
        _a(f"")
        _a(f"**Date:** {audit.timestamp}  ")
        _a(f"**Categories:** {', '.join(audit.categories)}  ")
        _a(f"**Total probes:** {m.total_probes}  ")
        _a(f"**Model:** {audit.config.get('target', {}).get('model', 'N/A')}  ")
        _a(f"")

        # Executive summary
        _a(f"## Executive Summary")
        _a(f"")
        _a(f"**Overall Reliability Score: {overall:.0%}** {self._score_emoji(overall)}")
        _a(f"")
        _a(f"- Probes passed: {m.total_passed}/{m.total_probes}")
        _a(f"- Hallucination rate: {m.hallucination_rate:.0%}")
        _a(f"- Groundedness: {m.groundedness_score:.0%}")
        _a(f"- Average latency: {m.avg_response_latency:.0f} ms")
        _a(f"")

        # Dashboard
        _a(f"## Metrics Dashboard")
        _a(f"")
        _a(f"| Category | Score | Status |")
        _a(f"|----------|------:|--------|")
        _a(f"| P1 Factual accuracy | {m.accuracy_p1:.0%} | {self._score_emoji(m.accuracy_p1)} |")
        _a(f"| P2 Refusal rate | {m.refusal_rate_p2:.0%} | {self._score_emoji(m.refusal_rate_p2)} |")
        _a(f"| P3 Ambiguity detection | {m.ambiguity_detection_p3:.0%} | {self._score_emoji(m.ambiguity_detection_p3)} |")
        _a(f"| P4 Contradiction detection | {m.contradiction_detection_p4:.0%} | {self._score_emoji(m.contradiction_detection_p4)} |")
        _a(f"| P5 Completeness | {m.completeness_p5:.0%} | {self._score_emoji(m.completeness_p5)} |")
        _a(f"| P6 Adversarial robustness | {m.adversarial_robustness_p6:.0%} | {self._score_emoji(m.adversarial_robustness_p6)} |")
        _a(f"| P7 Calibration | {m.calibration_score_p7:.0%} | {self._score_emoji(m.calibration_score_p7)} |")
        _a(f"| Hallucination rate | {m.hallucination_rate:.0%} | {self._score_emoji(m.hallucination_rate, higher_is_better=False)} |")
        _a(f"| Groundedness | {m.groundedness_score:.0%} | {self._score_emoji(m.groundedness_score)} |")
        _a(f"")

        # Per-category analysis
        _a(f"## Analysis by Category")
        _a(f"")
        cat_labels = {
            "P1": "P1 — Direct Factual Questions",
            "P2": "P2 — Out-of-Scope Questions",
            "P3": "P3 — Ambiguous Questions",
            "P4": "P4 — Intra-Corpus Contradictions",
            "P5": "P5 — Composite Multi-Document",
            "P6": "P6 — Adversarial Reformulations",
            "P7": "P7 — Certainty Calibration",
        }
        for cat in audit.categories:
            cat_results = self._category_results(audit.probe_results, cat)
            if not cat_results:
                continue
            passed_count = sum(1 for pr in cat_results if pr.evaluation.passed)
            _a(f"### {cat_labels.get(cat, cat)}")
            _a(f"")
            _a(f"**{passed_count}/{len(cat_results)} passed**")
            _a(f"")
            # Show one good and one bad example
            good = [pr for pr in cat_results if pr.evaluation.passed]
            bad = [pr for pr in cat_results if not pr.evaluation.passed]
            if good:
                pr = good[0]
                _a(f"**Good example:**")
                _a(f"> **Q:** {pr.probe.question}")
                _a(f"> **A:** {pr.agent_response.answer}")
                _a(f"> Score: {pr.evaluation.score:.0%} — {pr.evaluation.reasoning}")
                _a(f"")
            if bad:
                pr = bad[0]
                _a(f"**Bad example:**")
                _a(f"> **Q:** {pr.probe.question}")
                _a(f"> **A:** {pr.agent_response.answer}")
                _a(f"> Score: {pr.evaluation.score:.0%} — {pr.evaluation.reasoning}")
                _a(f"")

        # Critical cases
        _a(f"## Critical Cases")
        _a(f"")
        _a(f"The {len(critical)} worst results:")
        _a(f"")
        for i, pr in enumerate(critical, 1):
            _a(f"**{i}. [{pr.probe.category}] {pr.probe.question}**")
            _a(f"- Answer: {pr.agent_response.answer[:200]}{'...' if len(pr.agent_response.answer) > 200 else ''}")
            _a(f"- Score: {pr.evaluation.score:.0%}")
            _a(f"- Hallucinated: {'YES' if pr.hallucination.is_hallucinated else 'no'}")
            if pr.hallucination.ungrounded_claims:
                _a(f"- Ungrounded claims: {'; '.join(pr.hallucination.ungrounded_claims[:3])}")
            _a(f"")

        # Recommendations
        _a(f"## Recommendations")
        _a(f"")
        for i, rec in enumerate(recs, 1):
            _a(f"{i}. {rec}")
        _a(f"")

        # Appendix
        _a(f"## Appendix: Full Probe Log")
        _a(f"")
        _a(f"| # | Cat | Question | Passed | Score | Hallucinated |")
        _a(f"|---|-----|----------|--------|------:|:------------:|")
        for i, pr in enumerate(audit.probe_results, 1):
            q = pr.probe.question[:60] + ("..." if len(pr.probe.question) > 60 else "")
            p = "Y" if pr.evaluation.passed else "N"
            h = "Y" if pr.hallucination.is_hallucinated else ""
            _a(f"| {i} | {pr.probe.category} | {q} | {p} | {pr.evaluation.score:.0%} | {h} |")
        _a(f"")

        return "\n".join(lines)

    # ==================================================================
    # HTML renderer
    # ==================================================================

    def _render_html(self, audit: AuditRun) -> str:
        m = audit.metrics
        overall = self._overall_score(m)
        critical = self._critical_cases(audit.probe_results)
        recs = self._recommendations(m)

        cat_labels = {
            "P1": "P1 — Direct Factual Questions",
            "P2": "P2 — Out-of-Scope Questions",
            "P3": "P3 — Ambiguous Questions",
            "P4": "P4 — Intra-Corpus Contradictions",
            "P5": "P5 — Composite Multi-Document",
            "P6": "P6 — Adversarial Reformulations",
            "P7": "P7 — Certainty Calibration",
        }

        # Build category sections
        cat_sections = []
        for cat in audit.categories:
            cat_results = self._category_results(audit.probe_results, cat)
            if not cat_results:
                continue
            passed_count = sum(1 for pr in cat_results if pr.evaluation.passed)
            good = [pr for pr in cat_results if pr.evaluation.passed]
            bad = [pr for pr in cat_results if not pr.evaluation.passed]

            examples_html = ""
            if good:
                pr = good[0]
                examples_html += f"""
                <div class="example example-good">
                    <h4>Good Example</h4>
                    <p class="question"><strong>Q:</strong> {_esc(pr.probe.question)}</p>
                    <p class="answer"><strong>A:</strong> {_esc(pr.agent_response.answer)}</p>
                    <p class="meta">Score: {pr.evaluation.score:.0%} — {_esc(pr.evaluation.reasoning)}</p>
                </div>"""
            if bad:
                pr = bad[0]
                examples_html += f"""
                <div class="example example-bad">
                    <h4>Bad Example</h4>
                    <p class="question"><strong>Q:</strong> {_esc(pr.probe.question)}</p>
                    <p class="answer"><strong>A:</strong> {_esc(pr.agent_response.answer)}</p>
                    <p class="meta">Score: {pr.evaluation.score:.0%} — {_esc(pr.evaluation.reasoning)}</p>
                </div>"""

            cat_sections.append(f"""
            <div class="category-section">
                <h3>{cat_labels.get(cat, cat)}</h3>
                <p><strong>{passed_count}/{len(cat_results)}</strong> probes passed</p>
                {examples_html}
            </div>""")

        # Build critical cases
        critical_rows = []
        for i, pr in enumerate(critical, 1):
            hall_class = ' class="hallucinated"' if pr.hallucination.is_hallucinated else ""
            answer_trunc = _esc(pr.agent_response.answer[:200]) + ("..." if len(pr.agent_response.answer) > 200 else "")
            ungrounded = "; ".join(pr.hallucination.ungrounded_claims[:2]) if pr.hallucination.ungrounded_claims else ""
            critical_rows.append(f"""
                <tr{hall_class}>
                    <td>{i}</td>
                    <td>{pr.probe.category}</td>
                    <td>{_esc(pr.probe.question)}</td>
                    <td>{answer_trunc}</td>
                    <td>{pr.evaluation.score:.0%}</td>
                    <td>{"YES" if pr.hallucination.is_hallucinated else "no"}</td>
                    <td>{_esc(ungrounded)}</td>
                </tr>""")

        # Build probe log
        log_rows = []
        for i, pr in enumerate(audit.probe_results, 1):
            q = _esc(pr.probe.question[:80]) + ("..." if len(pr.probe.question) > 80 else "")
            row_class = "" if pr.evaluation.passed else ' class="failed"'
            log_rows.append(f"""
                <tr{row_class}>
                    <td>{i}</td>
                    <td>{pr.probe.category}</td>
                    <td>{q}</td>
                    <td>{"Pass" if pr.evaluation.passed else "Fail"}</td>
                    <td>{pr.evaluation.score:.0%}</td>
                    <td>{"Y" if pr.hallucination.is_hallucinated else ""}</td>
                    <td>{pr.agent_response.latency_ms:.0f}</td>
                </tr>""")

        # Recommendations
        recs_html = "".join(f"<li>{_esc(r)}</li>" for r in recs)

        return _HTML_TEMPLATE.format(
            run_id=audit.run_id,
            timestamp=audit.timestamp,
            categories=", ".join(audit.categories),
            total_probes=m.total_probes,
            model=audit.config.get("target", {}).get("model", "N/A"),
            overall_score=f"{overall:.0%}",
            overall_color=self._score_color(overall),
            passed_count=m.total_passed,
            hallucination_rate=f"{m.hallucination_rate:.0%}",
            groundedness=f"{m.groundedness_score:.0%}",
            avg_latency=f"{m.avg_response_latency:.0f} ms",
            accuracy_p1=self._score_badge(m.accuracy_p1),
            refusal_p2=self._score_badge(m.refusal_rate_p2),
            ambiguity_p3=self._score_badge(m.ambiguity_detection_p3),
            contradiction_p4=self._score_badge(m.contradiction_detection_p4),
            completeness_p5=self._score_badge(m.completeness_p5),
            adversarial_p6=self._score_badge(m.adversarial_robustness_p6),
            calibration_p7=self._score_badge(m.calibration_score_p7),
            hallucination_badge=self._score_badge(m.hallucination_rate, higher_is_better=False),
            groundedness_badge=self._score_badge(m.groundedness_score),
            category_sections="\n".join(cat_sections),
            critical_rows="\n".join(critical_rows),
            recommendations=recs_html,
            log_rows="\n".join(log_rows),
        )


def _esc(text: str) -> str:
    return html.escape(text)


# ------------------------------------------------------------------
# HTML template (self-contained with embedded CSS)
# ------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audit Report — {run_id}</title>
<style>
  :root {{
    --green: #22c55e; --green-bg: #f0fdf4;
    --orange: #f59e0b; --orange-bg: #fffbeb;
    --red: #ef4444; --red-bg: #fef2f2;
    --gray: #6b7280; --light: #f9fafb; --border: #e5e7eb;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         line-height: 1.6; color: #1f2937; max-width: 1100px; margin: 0 auto; padding: 2rem; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
  h2 {{ font-size: 1.4rem; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--border); }}
  h3 {{ font-size: 1.15rem; margin: 1.5rem 0 0.75rem; }}
  .meta {{ color: var(--gray); font-size: 0.9rem; margin-bottom: 1.5rem; }}

  /* Executive summary */
  .summary {{ display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 1rem 0; }}
  .score-ring {{ width: 120px; height: 120px; border-radius: 50%; display: flex;
                 align-items: center; justify-content: center; font-size: 2rem; font-weight: 700;
                 color: white; flex-shrink: 0; }}
  .score-ring.green {{ background: var(--green); }}
  .score-ring.orange {{ background: var(--orange); }}
  .score-ring.red {{ background: var(--red); }}
  .summary-stats {{ display: flex; flex-direction: column; justify-content: center; gap: 0.3rem; }}
  .summary-stats span {{ font-size: 0.95rem; }}

  /* Dashboard */
  .dashboard {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.75rem; }}
  .metric-card {{ background: var(--light); border: 1px solid var(--border); border-radius: 8px;
                  padding: 0.75rem 1rem; display: flex; justify-content: space-between; align-items: center; }}
  .metric-card .label {{ font-size: 0.85rem; color: var(--gray); }}
  .badge {{ padding: 2px 10px; border-radius: 12px; font-weight: 600; font-size: 0.9rem; color: white; }}
  .badge-green {{ background: var(--green); }}
  .badge-orange {{ background: var(--orange); }}
  .badge-red {{ background: var(--red); }}

  /* Category sections */
  .category-section {{ margin: 1rem 0; padding: 1rem; background: var(--light);
                       border-radius: 8px; border: 1px solid var(--border); }}
  .example {{ margin: 0.75rem 0; padding: 0.75rem; border-radius: 6px; border-left: 4px solid; }}
  .example-good {{ border-color: var(--green); background: var(--green-bg); }}
  .example-bad {{ border-color: var(--red); background: var(--red-bg); }}
  .example h4 {{ font-size: 0.85rem; text-transform: uppercase; margin-bottom: 0.3rem; color: var(--gray); }}
  .example .question, .example .answer {{ font-size: 0.9rem; margin: 0.2rem 0; }}
  .example .meta {{ font-size: 0.8rem; }}

  /* Tables */
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.5rem 0; }}
  th {{ background: var(--light); text-align: left; padding: 0.5rem; border-bottom: 2px solid var(--border); }}
  td {{ padding: 0.5rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tr.hallucinated {{ background: var(--red-bg); }}
  tr.failed {{ background: #fef2f2; }}

  /* Recommendations */
  .recommendations {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 1rem 1rem 1rem 1.5rem; }}
  .recommendations ol {{ margin-left: 1rem; }}
  .recommendations li {{ margin: 0.4rem 0; font-size: 0.95rem; }}

  /* Collapsible appendix */
  details {{ margin: 1rem 0; }}
  details summary {{ cursor: pointer; font-weight: 600; padding: 0.5rem; background: var(--light);
                     border-radius: 6px; }}
  details[open] summary {{ margin-bottom: 0.5rem; }}
</style>
</head>
<body>

<h1>Audit Report</h1>
<p class="meta">
  Run: <strong>{run_id}</strong> | Date: {timestamp} | Model: <code>{model}</code><br>
  Categories: {categories} | Total probes: {total_probes}
</p>

<h2>Executive Summary</h2>
<div class="summary">
  <div class="score-ring {overall_color}">{overall_score}</div>
  <div class="summary-stats">
    <span>Probes passed: <strong>{passed_count}/{total_probes}</strong></span>
    <span>Hallucination rate: <strong>{hallucination_rate}</strong></span>
    <span>Groundedness: <strong>{groundedness}</strong></span>
    <span>Avg latency: <strong>{avg_latency}</strong></span>
  </div>
</div>

<h2>Metrics Dashboard</h2>
<div class="dashboard">
  <div class="metric-card"><span class="label">P1 Factual accuracy</span> {accuracy_p1}</div>
  <div class="metric-card"><span class="label">P2 Refusal rate</span> {refusal_p2}</div>
  <div class="metric-card"><span class="label">P3 Ambiguity detection</span> {ambiguity_p3}</div>
  <div class="metric-card"><span class="label">P4 Contradiction detection</span> {contradiction_p4}</div>
  <div class="metric-card"><span class="label">P5 Completeness</span> {completeness_p5}</div>
  <div class="metric-card"><span class="label">P6 Adversarial robustness</span> {adversarial_p6}</div>
  <div class="metric-card"><span class="label">P7 Calibration</span> {calibration_p7}</div>
  <div class="metric-card"><span class="label">Hallucination rate</span> {hallucination_badge}</div>
  <div class="metric-card"><span class="label">Groundedness</span> {groundedness_badge}</div>
</div>

<h2>Analysis by Category</h2>
{category_sections}

<h2>Critical Cases</h2>
<table>
  <thead><tr>
    <th>#</th><th>Cat</th><th>Question</th><th>Answer (excerpt)</th>
    <th>Score</th><th>Halluc.</th><th>Ungrounded Claims</th>
  </tr></thead>
  <tbody>
    {critical_rows}
  </tbody>
</table>

<h2>Recommendations</h2>
<div class="recommendations">
  <ol>{recommendations}</ol>
</div>

<h2>Appendix</h2>
<details>
  <summary>Full Probe Log ({total_probes} probes)</summary>
  <table>
    <thead><tr>
      <th>#</th><th>Cat</th><th>Question</th><th>Result</th>
      <th>Score</th><th>Halluc.</th><th>Latency</th>
    </tr></thead>
    <tbody>
      {log_rows}
    </tbody>
  </table>
</details>

<p class="meta" style="margin-top:2rem; text-align:center;">
  Generated by <strong>agentprobe</strong> v0.1.0
</p>
</body>
</html>"""
