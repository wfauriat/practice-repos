"""Probe definitions and category taxonomy."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProbeCategory(str, Enum):
    """The seven probe categories targeting specific agent weaknesses."""

    P1_FACTUAL = "P1"
    P2_OUT_OF_SCOPE = "P2"
    P3_AMBIGUOUS = "P3"
    P4_CONTRADICTION = "P4"
    P5_COMPOSITE = "P5"
    P6_ADVERSARIAL = "P6"
    P7_CERTAINTY = "P7"

    @property
    def label(self) -> str:
        return _CATEGORY_LABELS[self]

    @property
    def expected_behavior(self) -> str:
        return _CATEGORY_BEHAVIORS[self]


_CATEGORY_LABELS: dict[ProbeCategory, str] = {
    ProbeCategory.P1_FACTUAL: "Direct factual questions (baseline)",
    ProbeCategory.P2_OUT_OF_SCOPE: "Out-of-scope questions",
    ProbeCategory.P3_AMBIGUOUS: "Ambiguous questions",
    ProbeCategory.P4_CONTRADICTION: "Intra-corpus contradictions",
    ProbeCategory.P5_COMPOSITE: "Composite multi-document questions",
    ProbeCategory.P6_ADVERSARIAL: "Adversarial reformulations",
    ProbeCategory.P7_CERTAINTY: "Certainty and confidence calibration",
}

_CATEGORY_BEHAVIORS: dict[ProbeCategory, str] = {
    ProbeCategory.P1_FACTUAL: "correct_answer",
    ProbeCategory.P2_OUT_OF_SCOPE: "refusal",
    ProbeCategory.P3_AMBIGUOUS: "ambiguity_flag",
    ProbeCategory.P4_CONTRADICTION: "contradiction_flag",
    ProbeCategory.P5_COMPOSITE: "complete_multi_source",
    ProbeCategory.P6_ADVERSARIAL: "robust_answer",
    ProbeCategory.P7_CERTAINTY: "calibrated_confidence",
}

ALL_CATEGORIES: list[ProbeCategory] = list(ProbeCategory)


@dataclass
class Probe:
    """A single test probe to be run against the target agent."""

    id: str
    category: str  # P1–P7
    question: str
    expected_behavior: str
    ground_truth: str | None = None
    difficulty: str = "medium"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "question": self.question,
            "expected_behavior": self.expected_behavior,
            "ground_truth": self.ground_truth,
            "difficulty": self.difficulty,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Probe:
        return cls(**d)


def parse_categories(spec: str) -> list[ProbeCategory]:
    """Parse a category spec like ``"all"`` or ``"P1,P2,P6"``."""
    spec = spec.strip()
    if spec.lower() == "all":
        return ALL_CATEGORIES
    parts = [s.strip().upper() for s in spec.split(",")]
    cats: list[ProbeCategory] = []
    for p in parts:
        try:
            cats.append(ProbeCategory(p))
        except ValueError:
            raise ValueError(f"Unknown probe category: {p!r}. Valid: {', '.join(c.value for c in ProbeCategory)}")
    return cats
