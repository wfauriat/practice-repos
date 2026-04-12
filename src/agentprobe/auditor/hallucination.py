"""Hallucination detection via grounding and factual verification."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class HallucinationResult:
    """Result of hallucination analysis for a single agent response."""

    probe_id: str
    is_hallucinated: bool
    groundedness_score: float  # 0.0 (fully hallucinated) – 1.0 (fully grounded)
    ungrounded_claims: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "probe_id": self.probe_id,
            "is_hallucinated": self.is_hallucinated,
            "groundedness_score": self.groundedness_score,
            "ungrounded_claims": self.ungrounded_claims,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, d: dict) -> HallucinationResult:
        return cls(**d)


class HallucinationChecker:
    """Two-pass hallucination detection.

    Pass 1 — **Grounding**: every claim in the agent's answer is compared
    (via embedding similarity) to the chunks the agent actually retrieved.
    Claims with no close match are flagged as ungrounded.

    Pass 2 — **Factual**: if ``ground_truth`` is available, check that the
    key facts in the answer match the expected answer.
    """

    DEFAULT_GROUNDING_THRESHOLD = 0.35  # cosine distance; lower = more similar

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        grounding_threshold: float = DEFAULT_GROUNDING_THRESHOLD,
    ):
        self._model = SentenceTransformer(embedding_model)
        self._threshold = grounding_threshold

    def check(
        self,
        probe_id: str,
        answer: str,
        retrieved_chunks: list[str],
        ground_truth: str | None = None,
    ) -> HallucinationResult:
        """Run both grounding and factual checks."""
        claims = self._split_claims(answer)
        if not claims or not retrieved_chunks:
            return HallucinationResult(
                probe_id=probe_id,
                is_hallucinated=False,
                groundedness_score=1.0 if not claims else 0.0,
                details={"reason": "no claims or no chunks to compare"},
            )

        # --- Pass 1: Grounding check ---
        grounding_scores, ungrounded = self._grounding_check(claims, retrieved_chunks)
        groundedness = grounding_scores.mean().item() if len(grounding_scores) else 1.0

        # --- Pass 2: Factual check (if ground truth is available) ---
        factual_penalty = 0.0
        factual_details: dict = {}
        if ground_truth:
            factual_penalty, factual_details = self._factual_check(answer, ground_truth)

        # Combine
        combined_score = max(0.0, groundedness - factual_penalty)
        is_hallucinated = combined_score < (1.0 - self._threshold) or len(ungrounded) > 0

        return HallucinationResult(
            probe_id=probe_id,
            is_hallucinated=is_hallucinated,
            groundedness_score=round(combined_score, 4),
            ungrounded_claims=ungrounded,
            details={
                "per_claim_grounding": [round(s, 4) for s in grounding_scores.tolist()] if len(grounding_scores) else [],
                "factual": factual_details,
            },
        )

    # ------------------------------------------------------------------
    # Pass 1: Grounding
    # ------------------------------------------------------------------

    def _grounding_check(
        self, claims: list[str], chunks: list[str]
    ) -> tuple[np.ndarray, list[str]]:
        """Compare each claim to retrieved chunks via cosine similarity.

        Returns per-claim grounding scores (1 = grounded) and the list of
        ungrounded claim texts.
        """
        claim_embs = self._model.encode(claims, normalize_embeddings=True)
        chunk_embs = self._model.encode(chunks, normalize_embeddings=True)

        # cosine similarity matrix: (n_claims, n_chunks)
        sim_matrix = claim_embs @ chunk_embs.T
        best_sim = sim_matrix.max(axis=1)  # best chunk match per claim

        # Convert similarity to a 0–1 grounding score (sim already in [−1,1])
        grounding_scores = np.clip(best_sim, 0, 1)

        ungrounded: list[str] = []
        for i, score in enumerate(grounding_scores):
            if score < (1.0 - self._threshold):
                ungrounded.append(claims[i])

        return grounding_scores, ungrounded

    # ------------------------------------------------------------------
    # Pass 2: Factual verification
    # ------------------------------------------------------------------

    def _factual_check(self, answer: str, ground_truth: str) -> tuple[float, dict]:
        """Check if key facts from ground_truth appear in answer.

        Returns a penalty (0.0 = all facts present, higher = missing facts)
        and a details dict.
        """
        gt_facts = self._extract_facts(ground_truth)
        if not gt_facts:
            return 0.0, {"extracted_facts": [], "missing": []}

        answer_lower = answer.lower()
        missing: list[str] = []
        for fact in gt_facts:
            if fact.lower() not in answer_lower:
                missing.append(fact)

        penalty = len(missing) / len(gt_facts) * 0.5  # cap at 0.5
        return penalty, {"extracted_facts": gt_facts, "missing": missing}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    # Patterns that are not factual claims about the corpus
    _NON_CLAIM_PATTERNS = re.compile(
        r"(?i)"
        r"(?:based on (?:the|my) (?:search|retrieved))"
        r"|(?:I (?:don'?t know|was unable|cannot|could not|can provide|found the))"
        r"|(?:the (?:available |retrieved )?documentation (?:does not|focuses|I found|provides))"
        r"|(?:the documents? I (?:found|searched))"
        r"|(?:let me search)"
        r"|(?:here (?:is|are) (?:the|what))"
        r"|(?:the search results (?:show|contain|indicate|do not))"
        r"|(?:you would need to (?:obtain|consult|check|refer))"
        r"|(?:to make this comparison)"
        r"|(?:\*{0,2}sources?\*{0,2}\s*:)"
    )

    @staticmethod
    def _split_claims(text: str) -> list[str]:
        """Split an answer into individual claim-bearing sentences.

        Filters out refusal phrases and meta-commentary that are not
        factual claims about the corpus.
        """
        # Remove source citations section (handles **Sources:** markdown formatting)
        text = re.split(r"\n\s*\*{0,2}sources?\*{0,2}\s*:", text, flags=re.IGNORECASE)[0]
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        # Filter out very short, non-claim, or meta-commentary sentences
        claims: list[str] = []
        for s in sentences:
            s = s.strip()
            if len(s) <= 20:
                continue
            if HallucinationChecker._NON_CLAIM_PATTERNS.search(s):
                continue
            claims.append(s)
        return claims

    @staticmethod
    def _extract_facts(text: str) -> list[str]:
        """Pull verifiable facts: numbers, measurements, dates, proper nouns."""
        facts: list[str] = []
        # Numbers with units
        facts.extend(re.findall(r"\d+[\d,.]*\s*(?:°C|°F|hPa|Pa|ppm|ppb|µg/m³|%|mm|m|g|kg|mW|µW|V|mA|MHz|GB|MB|KB|USD|\$|hours|months|years|seconds|minutes)", text))
        # Specific model numbers
        facts.extend(re.findall(r"MI-[A-Z]+\d+(?:-[A-Z]+)?", text))
        # Deduplicate
        return list(dict.fromkeys(facts))


def extract_retrieved_chunks(tool_calls_log: list[dict]) -> list[str]:
    """Pull chunk content strings from the agent's tool call log.

    Expects log entries like ``{"tool": "search_documents", "result": "..."}``.
    """
    chunks: list[str] = []
    for entry in tool_calls_log:
        if entry.get("tool") != "search_documents":
            continue
        raw = entry.get("result", "")
        try:
            hits = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        for hit in hits:
            content = hit.get("content", "")
            if content:
                chunks.append(content)
    return chunks
