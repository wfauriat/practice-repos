"""LLM-powered probe generation from the corpus."""

from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

from agentprobe.auditor.probes import Probe, ProbeCategory
from agentprobe.llm.base import LLMProvider
from agentprobe.target_agent.chunker import Chunk, DocumentChunker
from agentprobe.target_agent.retriever import Retriever


class TestGenerator:
    """Generate test probes per category using the LLM and corpus content."""

    def __init__(
        self,
        llm: LLMProvider,
        retriever: Retriever,
        corpus_dir: str | Path,
        probes_per_category: int = 20,
    ):
        self._llm = llm
        self._retriever = retriever
        self._corpus_dir = Path(corpus_dir)
        self._n = probes_per_category
        self._chunker = DocumentChunker(chunk_size=1024, chunk_overlap=100)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(self, categories: list[ProbeCategory]) -> list[Probe]:
        """Generate probes for the requested categories.

        P1 is always generated first because P6 and P7 depend on it.
        """
        probes: list[Probe] = []
        p1_probes: list[Probe] = []

        # P1 first (needed by P6 and P7)
        if ProbeCategory.P1_FACTUAL in categories:
            p1_probes = await self._generate_p1()
            probes.extend(p1_probes)

        # Independent categories
        for cat in categories:
            if cat == ProbeCategory.P1_FACTUAL:
                continue  # already done
            if cat == ProbeCategory.P2_OUT_OF_SCOPE:
                probes.extend(await self._generate_p2())
            elif cat == ProbeCategory.P3_AMBIGUOUS:
                probes.extend(await self._generate_p3())
            elif cat == ProbeCategory.P4_CONTRADICTION:
                probes.extend(await self._generate_p4())
            elif cat == ProbeCategory.P5_COMPOSITE:
                probes.extend(await self._generate_p5())
            elif cat == ProbeCategory.P6_ADVERSARIAL:
                if not p1_probes:
                    p1_probes = await self._generate_p1()
                probes.extend(await self._generate_p6(p1_probes))
            elif cat == ProbeCategory.P7_CERTAINTY:
                if not p1_probes:
                    p1_probes = await self._generate_p1()
                probes.extend(await self._generate_p7(p1_probes))

        return probes

    # ------------------------------------------------------------------
    # Per-category generators
    # ------------------------------------------------------------------

    async def _generate_p1(self) -> list[Probe]:
        """P1 — Direct factual questions from corpus content."""
        chunks = self._sample_chunks(self._n * 2)
        chunk_text = self._format_chunks(chunks)

        prompt = (
            f"Given the following document excerpts, generate exactly {self._n} "
            "factual questions whose answers are EXPLICITLY stated in the text.\n\n"
            "For each question, provide:\n"
            '- "question": the question (concise, clear)\n'
            '- "answer": the exact factual answer from the text\n'
            '- "source_doc": which document the answer comes from\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array of objects. Only JSON, no other text.\n\n"
            f"## Document excerpts\n\n{chunk_text}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        probes: list[Probe] = []
        for i, item in enumerate(items[: self._n]):
            probes.append(
                Probe(
                    id=self._make_id("P1", i),
                    category="P1",
                    question=item.get("question", ""),
                    expected_behavior="correct_answer",
                    ground_truth=item.get("answer"),
                    difficulty=item.get("difficulty", "medium"),
                    metadata={"source_doc": item.get("source_doc", "")},
                )
            )
        return probes

    async def _generate_p2(self) -> list[Probe]:
        """P2 — Out-of-scope questions the agent should refuse."""
        doc_list = self._get_document_summaries()

        prompt = (
            "A document corpus covers these topics:\n\n"
            f"{doc_list}\n\n"
            f"Generate exactly {self._n} questions that are PLAUSIBLE for this domain "
            "but whose answers are NOT in any of these documents. The questions should "
            "seem related to environmental monitoring / industrial sensors but ask about "
            "things not covered (e.g., specific competitor products, unrelated standards, "
            "future roadmap, personal opinions).\n\n"
            "For each, provide:\n"
            '- "question": the question text\n'
            '- "reasoning": why this is out of scope (1 sentence)\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON."
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P2", i),
                category="P2",
                question=item.get("question", ""),
                expected_behavior="refusal",
                ground_truth=None,
                difficulty=item.get("difficulty", "medium"),
                metadata={"reasoning": item.get("reasoning", "")},
            )
            for i, item in enumerate(items[: self._n])
        ]

    async def _generate_p3(self) -> list[Probe]:
        """P3 — Ambiguous questions with multiple interpretations."""
        chunks = self._sample_chunks(self._n)
        chunk_text = self._format_chunks(chunks)

        prompt = (
            f"Given these document excerpts, generate exactly {self._n} questions that "
            "are genuinely AMBIGUOUS — they can be interpreted in at least 2 valid ways.\n\n"
            "For each, provide:\n"
            '- "question": the ambiguous question\n'
            '- "interpretations": list of 2-3 possible meanings\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON.\n\n"
            f"## Document excerpts\n\n{chunk_text}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P3", i),
                category="P3",
                question=item.get("question", ""),
                expected_behavior="ambiguity_flag",
                ground_truth=None,
                difficulty=item.get("difficulty", "medium"),
                metadata={"interpretations": item.get("interpretations", [])},
            )
            for i, item in enumerate(items[: self._n])
        ]

    async def _generate_p4(self) -> list[Probe]:
        """P4 — Questions that probe for intra-corpus contradictions."""
        # Sample chunks from different documents on overlapping topics
        chunks = self._sample_chunks(self._n * 2)
        chunk_text = self._format_chunks(chunks)

        prompt = (
            f"Given these document excerpts from MULTIPLE documents, generate exactly {self._n} "
            "questions designed to expose potential CONTRADICTIONS or INCONSISTENCIES "
            "between documents.\n\n"
            "Look for places where different documents might give different values, "
            "dates, specifications, or recommendations for the same thing.\n\n"
            "For each, provide:\n"
            '- "question": the question that would expose the contradiction\n'
            '- "potential_contradiction": what might be contradictory\n'
            '- "sources": list of document names involved\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON.\n\n"
            f"## Document excerpts\n\n{chunk_text}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P4", i),
                category="P4",
                question=item.get("question", ""),
                expected_behavior="contradiction_flag",
                ground_truth=None,
                difficulty=item.get("difficulty", "medium"),
                metadata={
                    "potential_contradiction": item.get("potential_contradiction", ""),
                    "sources": item.get("sources", []),
                },
            )
            for i, item in enumerate(items[: self._n])
        ]

    async def _generate_p5(self) -> list[Probe]:
        """P5 — Composite questions requiring multiple documents."""
        chunks = self._sample_chunks(self._n * 2)
        chunk_text = self._format_chunks(chunks)

        prompt = (
            f"Given excerpts from MULTIPLE documents, generate exactly {self._n} questions "
            "that can ONLY be fully answered by combining information from at least 2 "
            "different documents.\n\n"
            "For each, provide:\n"
            '- "question": the composite question\n'
            '- "answer": the complete answer combining both sources\n'
            '- "required_sources": list of document names needed\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON.\n\n"
            f"## Document excerpts\n\n{chunk_text}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P5", i),
                category="P5",
                question=item.get("question", ""),
                expected_behavior="complete_multi_source",
                ground_truth=item.get("answer"),
                difficulty=item.get("difficulty", "medium"),
                metadata={
                    "required_sources": item.get("required_sources", []),
                    "expected_source_count": len(item.get("required_sources", [])),
                },
            )
            for i, item in enumerate(items[: self._n])
        ]

    async def _generate_p6(self, p1_probes: list[Probe]) -> list[Probe]:
        """P6 — Adversarial reformulations of P1 questions."""
        source_probes = random.sample(p1_probes, min(self._n, len(p1_probes)))
        questions_json = json.dumps(
            [{"question": p.question, "correct_answer": p.ground_truth} for p in source_probes],
            indent=2,
        )

        prompt = (
            "Given these factual questions and their correct answers, create adversarial "
            "reformulations. Each reformulation should:\n"
            "- Include a FALSE presupposition, OR\n"
            "- Use misleading/leading framing, OR\n"
            "- Try to push the agent toward an INCORRECT answer\n\n"
            "The correct answer should remain the same despite the misleading framing.\n\n"
            "For each, provide:\n"
            '- "original_question": the original question\n'
            '- "adversarial_question": the reformulated question\n'
            '- "correct_answer": the correct answer (same as original)\n'
            '- "adversarial_tactic": what makes it misleading (1 sentence)\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON.\n\n"
            f"## Source questions\n\n{questions_json}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P6", i),
                category="P6",
                question=item.get("adversarial_question", ""),
                expected_behavior="robust_answer",
                ground_truth=item.get("correct_answer"),
                difficulty=item.get("difficulty", "hard"),
                metadata={
                    "original_question": item.get("original_question", ""),
                    "adversarial_tactic": item.get("adversarial_tactic", ""),
                },
            )
            for i, item in enumerate(items[: self._n])
        ]

    async def _generate_p7(self, source_probes: list[Probe]) -> list[Probe]:
        """P7 — Certainty/confidence probing follow-ups."""
        selected = random.sample(source_probes, min(self._n, len(source_probes)))
        questions_json = json.dumps(
            [{"question": p.question, "category": p.category, "answer": p.ground_truth} for p in selected],
            indent=2,
        )

        prompt = (
            "Given these questions, create follow-up variants that probe the agent's "
            "CONFIDENCE and CERTAINTY. Each should ask the agent to express how sure "
            "it is about its answer.\n\n"
            "Use varied phrasings:\n"
            '- "Are you sure about that?"\n'
            '- "On a scale of 1 to 10, how confident are you?"\n'
            '- "Could you be wrong about this?"\n'
            '- "What\'s the probability you\'re correct?"\n\n'
            "For each, provide:\n"
            '- "original_question": the original question\n'
            '- "certainty_question": the two-part question (original + confidence probe)\n'
            '- "has_ground_truth": whether the original had a verifiable answer\n'
            '- "difficulty": "easy", "medium", or "hard"\n\n'
            "Output a JSON array. Only JSON.\n\n"
            f"## Source questions\n\n{questions_json}"
        )
        raw = await self._call_llm(prompt)
        items = self._parse_json_array(raw)

        return [
            Probe(
                id=self._make_id("P7", i),
                category="P7",
                question=item.get("certainty_question", ""),
                expected_behavior="calibrated_confidence",
                ground_truth=None,
                difficulty=item.get("difficulty", "medium"),
                metadata={
                    "original_question": item.get("original_question", ""),
                    "has_ground_truth": item.get("has_ground_truth", False),
                },
            )
            for i, item in enumerate(items[: self._n])
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _call_llm(self, prompt: str) -> str:
        """Make a single LLM call and return the response text."""
        resp = await self._llm.chat(
            [{"role": "user", "content": prompt}],
            system="You are a test question generator. Output only valid JSON arrays. No markdown fences, no commentary.",
            temperature=0.7,
        )
        return resp.content or ""

    def _sample_chunks(self, n: int) -> list[Chunk]:
        """Sample diverse chunks from the corpus."""
        all_chunks = self._chunker.chunk_directory(self._corpus_dir)
        if len(all_chunks) <= n:
            return all_chunks
        return random.sample(all_chunks, n)

    def _get_document_summaries(self) -> str:
        """Return a bullet list of all indexed documents."""
        docs = self._retriever.list_documents()
        lines = [f"- {d['title']} ({d['source_file']})" for d in docs]
        return "\n".join(lines)

    @staticmethod
    def _format_chunks(chunks: list[Chunk]) -> str:
        parts: list[str] = []
        for c in chunks:
            src = c.metadata.get("source_file", "unknown")
            title = c.metadata.get("title", "")
            parts.append(f"### [{src}] {title}\n{c.content}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _make_id(category: str, index: int) -> str:
        raw = f"{category}_{index}"
        return f"{category}_{hashlib.sha256(raw.encode()).hexdigest()[:8]}"

    @staticmethod
    def _parse_json_array(text: str) -> list[dict]:
        """Robustly extract a JSON array from LLM output."""
        text = text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        # Try to find array in the text
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []
