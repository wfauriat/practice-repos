# lectures/

Theory branch. Verbose, narrative primers (~1500-3000 words) on conceptual topics where the value is **understanding the why and the tradeoffs**, not building reflexes.

Distinct from:

- `kata/` — drills (build muscle memory).
- `craft/` — interactive labs (run things in sandboxes).
- `reference/` — pure cheatsheets (look up syntax).
- `tutorials/` — fill-in-the-blanks coding (apply concepts).

A lecture lives once you've read it; you come back to it not to *re-read*, but to *re-discuss*.

## Anatomy of a lecture file

Every lecture follows this skeleton:

1. **Abstract** — 1-2 sentence summary.
2. **Motivation** — why this matters, where it bites you in practice.
3. **Core concepts** — the substance, with concrete examples.
4. **Tradeoffs / counterpoints** — when the idea fails or is misapplied. *This is the most valuable section.*
5. **Further reading** — 2-5 canonical sources (books, posts, papers — not blog noise).
6. **Discussion prompts** — 3-5 open-ended questions that act as Socratic seeds.

## Two modes of engagement with Claude

### Read & discuss

You: *"Let's go through `lectures/software-engineering/01-agile-fundamentals.md`."*

Claude **does not re-summarise** (you read it). Claude jumps to the **Discussion prompts** at the bottom and runs them Socratically — pushing back on your reasoning, surfacing where intuition is shaky, naming counter-examples.

### Generate on demand

You: *"Write me a lecture on backpressure in async systems."*

Claude writes a new markdown file in the appropriate subdirectory (`software-engineering/`, `mlops/`, `architecture/`, `data-engineering/`) using the skeleton above. It becomes a future-you artifact.

## Topics

Topics live in `curriculum/ROADMAP.md`. Seeded so far:

- [`software-engineering/01-agile-fundamentals.md`](./software-engineering/01-agile-fundamentals.md)
- [`software-engineering/02-senior-engineer-mindset.md`](./software-engineering/02-senior-engineer-mindset.md)
- [`mlops/01-mlops-mindset.md`](./mlops/01-mlops-mindset.md)
