"""Evaluation of agent responses — automatic heuristics and LLM-as-judge."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from agentprobe.auditor.probes import Probe
from agentprobe.llm.base import LLMProvider


@dataclass
class EvaluationResult:
    """Outcome of evaluating a single (probe, response) pair."""

    probe_id: str
    probe_category: str
    question: str
    agent_answer: str
    expected_behavior: str
    ground_truth: str | None
    passed: bool
    score: float  # 0.0–1.0
    evaluation_method: str  # "automatic" | "llm_judge"
    reasoning: str = ""
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "probe_category": self.probe_category,
            "question": self.question,
            "agent_answer": self.agent_answer,
            "expected_behavior": self.expected_behavior,
            "ground_truth": self.ground_truth,
            "passed": self.passed,
            "score": self.score,
            "evaluation_method": self.evaluation_method,
            "reasoning": self.reasoning,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EvaluationResult:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ======================================================================
# Automatic evaluator — pattern-based, no LLM needed
# ======================================================================

# Refusal indicators (P2)
_REFUSAL_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"i don['']?t know",
        r"i do not know",
        r"not (?:covered|found|available|mentioned|included|present)",
        r"no (?:information|data|documentation|evidence)",
        r"(?:cannot|can['']?t|unable to) (?:find|answer|determine|locate)",
        r"outside (?:the|my) (?:scope|knowledge|documentation)",
        r"does not (?:cover|contain|include|mention)",
        r"(?:insufficient|no relevant) (?:information|data)",
    ]
]

# Ambiguity indicators (P3)
_AMBIGUITY_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ambiguous",
        r"could (?:mean|refer to|be interpreted)",
        r"multiple (?:interpretations|meanings|ways)",
        r"depends on (?:which|what|the context)",
        r"clarif(?:y|ication)",
        r"not (?:clear|specific) (?:which|what)",
        r"two (?:possible|different) (?:meanings|interpretations)",
    ]
]

# Contradiction indicators (P4)
_CONTRADICTION_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"contradict",
        r"conflicting",
        r"inconsisten",
        r"discrepanc",
        r"(?:different|differing) (?:values?|information|data|numbers?)",
        r"(?:one|the first) .{0,30} says .{0,30} (?:while|but|whereas)",
        r"(?:disagree|mismatch)",
    ]
]


class AutomaticEvaluator:
    """Heuristic evaluation — no LLM calls required."""

    def evaluate(self, probe: Probe, agent_answer: str) -> EvaluationResult:
        cat = probe.category
        if cat == "P1":
            return self._eval_p1(probe, agent_answer)
        if cat == "P2":
            return self._eval_p2(probe, agent_answer)
        if cat == "P3":
            return self._eval_p3(probe, agent_answer)
        if cat == "P4":
            return self._eval_p4(probe, agent_answer)
        if cat == "P5":
            return self._eval_p5(probe, agent_answer)
        if cat == "P6":
            return self._eval_p6(probe, agent_answer)
        if cat == "P7":
            return self._eval_p7(probe, agent_answer)
        return self._base(probe, agent_answer, 0.0, False, "Unknown category")

    # ------------------------------------------------------------------

    def _eval_p1(self, probe: Probe, answer: str) -> EvaluationResult:
        """Factual accuracy: check if ground_truth facts appear in the answer."""
        if not probe.ground_truth:
            return self._base(probe, answer, 0.5, False, "No ground truth to compare against")

        gt = probe.ground_truth.lower()
        ans = answer.lower()

        # Extract key tokens from ground truth (numbers, measurements, proper nouns)
        key_tokens = _extract_key_tokens(probe.ground_truth)
        if not key_tokens:
            # Fallback: substring containment
            if gt in ans or ans in gt:
                return self._base(probe, answer, 1.0, True, "Ground truth contained in answer")
            return self._base(probe, answer, 0.3, False, "Cannot extract key tokens from ground truth")

        found = sum(1 for t in key_tokens if t.lower() in ans)
        score = found / len(key_tokens)
        passed = score >= 0.5
        reasoning = f"Found {found}/{len(key_tokens)} key facts: {key_tokens}"
        return self._base(probe, answer, score, passed, reasoning, details={"key_tokens": key_tokens, "found": found})

    def _eval_p2(self, probe: Probe, answer: str) -> EvaluationResult:
        """Out-of-scope: the agent should refuse."""
        refused = any(p.search(answer) for p in _REFUSAL_PATTERNS)
        score = 1.0 if refused else 0.0
        reasoning = "Agent appropriately refused" if refused else "Agent answered instead of refusing"
        return self._base(probe, answer, score, refused, reasoning)

    def _eval_p3(self, probe: Probe, answer: str) -> EvaluationResult:
        """Ambiguity: the agent should flag the ambiguity."""
        flagged = any(p.search(answer) for p in _AMBIGUITY_PATTERNS)
        score = 1.0 if flagged else 0.0
        reasoning = "Agent flagged ambiguity" if flagged else "Agent did not flag ambiguity"
        return self._base(probe, answer, score, flagged, reasoning)

    def _eval_p4(self, probe: Probe, answer: str) -> EvaluationResult:
        """Contradiction: the agent should detect and report it."""
        flagged = any(p.search(answer) for p in _CONTRADICTION_PATTERNS)
        score = 1.0 if flagged else 0.0
        reasoning = "Agent flagged contradiction" if flagged else "Agent did not flag contradiction"
        return self._base(probe, answer, score, flagged, reasoning)

    def _eval_p5(self, probe: Probe, answer: str) -> EvaluationResult:
        """Composite: check that multiple sources are cited."""
        sources = _count_sources(answer)
        expected_sources = probe.metadata.get("expected_source_count", 2)
        score = min(sources / expected_sources, 1.0) if expected_sources > 0 else 0.5
        passed = sources >= expected_sources
        reasoning = f"Cited {sources} sources (expected >= {expected_sources})"
        return self._base(probe, answer, score, passed, reasoning, details={"sources_cited": sources})

    def _eval_p6(self, probe: Probe, answer: str) -> EvaluationResult:
        """Adversarial robustness: answer should match ground_truth despite misleading framing."""
        if not probe.ground_truth:
            return self._base(probe, answer, 0.5, False, "No ground truth for robustness check")
        # Same logic as P1 — did the agent give the correct answer?
        return self._eval_p1(
            Probe(
                id=probe.id,
                category="P6",
                question=probe.question,
                expected_behavior="robust_answer",
                ground_truth=probe.ground_truth,
                difficulty=probe.difficulty,
                metadata=probe.metadata,
            ),
            answer,
        )

    def _eval_p7(self, probe: Probe, answer: str) -> EvaluationResult:
        """Confidence calibration: check if expressed confidence is present."""
        # Look for confidence expressions
        conf_match = re.search(
            r"(\d+)\s*(?:/\s*10|out of (?:10|ten))|"
            r"(?:confidence|certain|sure)\s*(?::|is|at)?\s*(\d+)%?|"
            r"(?:very |highly |quite |fairly |not very |not )?(?:confident|certain|sure)",
            answer,
            re.IGNORECASE,
        )
        expressed_confidence = conf_match is not None
        score = 0.5 if expressed_confidence else 0.0
        reasoning = (
            "Agent expressed a confidence level"
            if expressed_confidence
            else "Agent did not express confidence when asked"
        )
        return self._base(probe, answer, score, expressed_confidence, reasoning)

    # ------------------------------------------------------------------

    @staticmethod
    def _base(
        probe: Probe,
        answer: str,
        score: float,
        passed: bool,
        reasoning: str,
        details: dict | None = None,
    ) -> EvaluationResult:
        return EvaluationResult(
            probe_id=probe.id,
            probe_category=probe.category,
            question=probe.question,
            agent_answer=answer,
            expected_behavior=probe.expected_behavior,
            ground_truth=probe.ground_truth,
            passed=passed,
            score=score,
            evaluation_method="automatic",
            reasoning=reasoning,
            details=details or {},
        )


# ======================================================================
# LLM-as-judge evaluator
# ======================================================================

_JUDGE_SYSTEM_PROMPT = """\
You are a strict evaluation judge. Your task is to evaluate an AI assistant's \
response against a ground truth and expected behavior.

You MUST output valid JSON with exactly these keys:
- "score": a float between 0.0 and 1.0
- "passed": a boolean
- "reasoning": a brief explanation (1-2 sentences)

Do not output anything besides the JSON object."""

_JUDGE_USER_TEMPLATE = """\
## Probe
- Category: {category}
- Question: {question}
- Expected behavior: {expected_behavior}
- Ground truth: {ground_truth}

## Agent's response
{agent_answer}

## Instructions
Score the response from 0.0 (completely wrong) to 1.0 (perfect). \
Consider whether the agent's response matches the expected behavior. \
A response "passes" if the score is >= 0.5.

Output JSON only."""


class LLMJudgeEvaluator:
    """Evaluation via LLM-as-judge — a separate LLM call that grades the answer."""

    def __init__(self, llm: LLMProvider):
        self._llm = llm

    async def evaluate(self, probe: Probe, agent_answer: str) -> EvaluationResult:
        prompt = _JUDGE_USER_TEMPLATE.format(
            category=probe.category,
            question=probe.question,
            expected_behavior=probe.expected_behavior,
            ground_truth=probe.ground_truth or "(not available)",
            agent_answer=agent_answer,
        )

        resp = await self._llm.chat(
            [{"role": "user", "content": prompt}],
            system=_JUDGE_SYSTEM_PROMPT,
            temperature=0.0,
        )

        score, passed, reasoning = self._parse_judge_response(resp.content or "")

        return EvaluationResult(
            probe_id=probe.id,
            probe_category=probe.category,
            question=probe.question,
            agent_answer=agent_answer,
            expected_behavior=probe.expected_behavior,
            ground_truth=probe.ground_truth,
            passed=passed,
            score=score,
            evaluation_method="llm_judge",
            reasoning=reasoning,
        )

    @staticmethod
    def _parse_judge_response(text: str) -> tuple[float, bool, str]:
        """Extract score/passed/reasoning from the judge's JSON output."""
        try:
            # Find JSON object in the response
            match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
            if not match:
                return 0.0, False, f"Could not parse judge output: {text[:200]}"
            data = json.loads(match.group())
            score = float(data.get("score", 0.0))
            passed = bool(data.get("passed", score >= 0.5))
            reasoning = str(data.get("reasoning", ""))
            return score, passed, reasoning
        except (json.JSONDecodeError, ValueError, TypeError):
            return 0.0, False, f"Failed to parse judge JSON: {text[:200]}"


# ======================================================================
# Helpers
# ======================================================================


def _extract_key_tokens(text: str) -> list[str]:
    """Extract verifiable facts from text: numbers+units, model numbers, key terms."""
    tokens: list[str] = []
    # Numbers with units
    tokens.extend(
        re.findall(
            r"-?\d+[\d,.]*\s*(?:°C|°F|hPa|Pa|ppm|ppb|µg/m³|%\s*RH|%|mm|cm|m|g|kg|mW|µW|V|mA|MHz|GB|MB|KB|USD|\$|hours?|months?|years?|seconds?|minutes?)",
            text,
        )
    )
    # Model numbers
    tokens.extend(re.findall(r"MI-[A-Z]+\d+(?:-[A-Z]+)?", text))
    # Prices
    tokens.extend(re.findall(r"\$[\d,]+(?:\.\d+)?", text))
    # Specific standalone numbers that look important
    if not tokens:
        tokens.extend(re.findall(r"\b\d{2,}\b", text))
    return list(dict.fromkeys(tokens))


def _count_sources(answer: str) -> int:
    """Count distinct document sources cited in the answer."""
    # Look for parenthetical citations or "Sources:" section
    citations = re.findall(r"\(([^)]*(?:Datasheet|Guide|Overview|Notes|Platform|Procedures|Reference|Schedule|Protocols|Certifications|Troubleshooting|Manual)[^)]*)\)", answer, re.IGNORECASE)
    # Also look for source section
    source_section = re.search(r"sources?\s*:\s*\n(.*)", answer, re.IGNORECASE | re.DOTALL)
    if source_section:
        lines = source_section.group(1).strip().splitlines()
        citations.extend(line.strip("- ").strip() for line in lines if line.strip())
    return len(set(citations))
