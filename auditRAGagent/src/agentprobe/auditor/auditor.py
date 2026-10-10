"""Main audit orchestrator — generates probes, runs them, evaluates, reports."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from agentprobe.auditor.evaluator import AutomaticEvaluator, EvaluationResult, LLMJudgeEvaluator
from agentprobe.auditor.hallucination import HallucinationChecker, HallucinationResult, extract_retrieved_chunks
from agentprobe.auditor.metrics import AuditMetrics
from agentprobe.auditor.probes import Probe, ProbeCategory, parse_categories
from agentprobe.auditor.test_generator import TestGenerator
from agentprobe.llm.base import LLMProvider
from agentprobe.target_agent.agent import AgentResponse, TargetAgent
from agentprobe.target_agent.retriever import Retriever


@dataclass
class ProbeResult:
    """Complete result for a single probe: agent response + evaluation + hallucination."""

    probe: Probe
    agent_response: AgentResponse
    evaluation: EvaluationResult
    hallucination: HallucinationResult

    def to_dict(self) -> dict:
        return {
            "probe": self.probe.to_dict(),
            "agent_response": {
                "answer": self.agent_response.answer,
                "sources": self.agent_response.sources,
                "tool_calls_made": self.agent_response.tool_calls_made,
                "latency_ms": self.agent_response.latency_ms,
                "total_input_tokens": self.agent_response.total_input_tokens,
                "total_output_tokens": self.agent_response.total_output_tokens,
            },
            "evaluation": self.evaluation.to_dict(),
            "hallucination": self.hallucination.to_dict(),
        }


@dataclass
class AuditRun:
    """Complete audit run with all results and metrics."""

    run_id: str
    timestamp: str
    config: dict
    categories: list[str]
    probe_results: list[ProbeResult] = field(default_factory=list)
    metrics: AuditMetrics = field(default_factory=AuditMetrics)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "config": self.config,
            "categories": self.categories,
            "metrics": self.metrics.to_dict(),
            "probe_results": [pr.to_dict() for pr in self.probe_results],
        }

    @classmethod
    def from_dict(cls, d: dict) -> AuditRun:
        run = cls(
            run_id=d["run_id"],
            timestamp=d["timestamp"],
            config=d.get("config", {}),
            categories=d.get("categories", []),
            metrics=AuditMetrics.from_dict(d.get("metrics", {})),
        )
        # Reconstruct probe_results minimally for comparison purposes
        for pr_dict in d.get("probe_results", []):
            run.probe_results.append(
                ProbeResult(
                    probe=Probe.from_dict(pr_dict["probe"]),
                    agent_response=_reconstruct_agent_response(pr_dict.get("agent_response", {})),
                    evaluation=EvaluationResult.from_dict(pr_dict["evaluation"]),
                    hallucination=HallucinationResult.from_dict(pr_dict["hallucination"]),
                )
            )
        return run

    def save(self, output_dir: str | Path) -> Path:
        """Persist the full run to a JSON file."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{self.run_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> AuditRun:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)


class Auditor:
    """Orchestrates the full audit: generate → run → evaluate → metrics."""

    def __init__(
        self,
        target_agent: TargetAgent,
        auditor_llm: LLMProvider,
        evaluator_llm: LLMProvider,
        retriever: Retriever,
        corpus_dir: str | Path,
        *,
        probes_per_category: int = 20,
        concurrency: int = 5,
        use_llm_judge: bool = True,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self._target = target_agent
        self._auditor_llm = auditor_llm
        self._evaluator_llm = evaluator_llm
        self._retriever = retriever
        self._corpus_dir = Path(corpus_dir)
        self._n = probes_per_category
        self._concurrency = concurrency
        self._use_llm_judge = use_llm_judge

        self._generator = TestGenerator(auditor_llm, retriever, corpus_dir, probes_per_category)
        self._auto_eval = AutomaticEvaluator()
        self._llm_judge = LLMJudgeEvaluator(evaluator_llm) if use_llm_judge else None
        self._hallucination_checker = HallucinationChecker(embedding_model=embedding_model)

    async def run(
        self,
        categories: str | list[ProbeCategory] = "all",
        *,
        config_snapshot: dict | None = None,
        progress_callback=None,
    ) -> AuditRun:
        """Execute a full audit run.

        Parameters
        ----------
        categories:
            Which probe categories to run (``"all"`` or a list).
        config_snapshot:
            Optional config dict to store with the run for reproducibility.
        progress_callback:
            Optional ``callback(done: int, total: int, probe_id: str)`` for
            progress reporting.
        """
        if isinstance(categories, str):
            cats = parse_categories(categories)
        else:
            cats = categories

        run_id = f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        audit = AuditRun(
            run_id=run_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            config=config_snapshot or {},
            categories=[c.value for c in cats],
        )

        # 1. Generate probes
        probes = await self._generator.generate(cats)

        # 2. Run probes against target with concurrency control
        sem = asyncio.Semaphore(self._concurrency)
        total = len(probes)

        async def _run_single(idx: int, probe: Probe) -> ProbeResult:
            async with sem:
                result = await self._execute_probe(probe)
                if progress_callback:
                    progress_callback(idx + 1, total, probe.id)
                return result

        tasks = [_run_single(i, p) for i, p in enumerate(probes)]
        audit.probe_results = await asyncio.gather(*tasks)

        # 3. Compute metrics
        audit.metrics = AuditMetrics.compute(
            evaluations=[pr.evaluation.to_dict() for pr in audit.probe_results],
            hallucination_results=[pr.hallucination.to_dict() for pr in audit.probe_results],
            agent_stats=[
                {
                    "latency_ms": pr.agent_response.latency_ms,
                    "tool_calls_made": pr.agent_response.tool_calls_made,
                }
                for pr in audit.probe_results
            ],
        )

        return audit

    async def _execute_probe(self, probe: Probe) -> ProbeResult:
        """Run a single probe end-to-end: agent → evaluate → hallucination."""
        # Run agent
        agent_resp = await self._target.answer(probe.question)

        # Evaluate
        eval_result = self._auto_eval.evaluate(probe, agent_resp.answer)
        if self._llm_judge:
            llm_eval = await self._llm_judge.evaluate(probe, agent_resp.answer)
            # Use LLM judge result if auto eval is uncertain (score between 0.3-0.7)
            if 0.3 <= eval_result.score <= 0.7:
                eval_result = llm_eval

        # Hallucination check
        retrieved = extract_retrieved_chunks(agent_resp.tool_calls_log)
        hall_result = self._hallucination_checker.check(
            probe_id=probe.id,
            answer=agent_resp.answer,
            retrieved_chunks=retrieved,
            ground_truth=probe.ground_truth,
        )

        return ProbeResult(
            probe=probe,
            agent_response=agent_resp,
            evaluation=eval_result,
            hallucination=hall_result,
        )


def compare_runs(run_a: AuditRun, run_b: AuditRun) -> dict:
    """Compare two audit runs and return a diff of metrics."""
    ma = run_a.metrics.to_dict()
    mb = run_b.metrics.to_dict()
    diff: dict = {
        "run_a": run_a.run_id,
        "run_b": run_b.run_id,
        "deltas": {},
    }
    for key in ma:
        va, vb = ma[key], mb[key]
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            delta = vb - va
            diff["deltas"][key] = {
                "run_a": round(va, 4) if isinstance(va, float) else va,
                "run_b": round(vb, 4) if isinstance(vb, float) else vb,
                "delta": round(delta, 4) if isinstance(delta, float) else delta,
                "direction": "improved" if delta > 0 else "regressed" if delta < 0 else "unchanged",
            }
    return diff


def _reconstruct_agent_response(d: dict) -> AgentResponse:
    return AgentResponse(
        answer=d.get("answer", ""),
        sources=d.get("sources", []),
        tool_calls_made=d.get("tool_calls_made", 0),
        latency_ms=d.get("latency_ms", 0),
        total_input_tokens=d.get("total_input_tokens", 0),
        total_output_tokens=d.get("total_output_tokens", 0),
    )
