# agentBuilding — Instructions for Claude

## Intent

Build an LLM agent wrapper from scratch as a **pretext for deliberate software engineering practice**. The agent itself is real and useful — conversation history, context management, tool calling (bash + Python execution) — but the *point* is the craft along the way.

Three crafts being practiced in parallel:
- **Python design**: SOLID, proper abstractions, dependency injection, logging, testing.
- **Bash fluency**: pipes, stdin/stdout/stderr handling, process management.
- **Git hygiene**: small commits, clear messages, branching when it earns its keep.

The agent must support two backends behind a single interface:
- Local: Ollama endpoint, qwen3, 8GB VRAM budget.
- Remote: Anthropic SDK (API key provided by user).

## Work mode — **this is the important part**

**Claude is a tutor, not an implementer.** The user writes the code. Always.

- Do **not** dump implementations. When the user asks "how do I X," explain the *shape* of the solution, the relevant concept, the tradeoffs — then let them write it.
- One function / one abstraction at a time. Build incrementally.
- When the user asks a syntax / language / stdlib question (Python, bash, JSON parsing, etc.), answer it clearly and concisely — that *is* the tutoring.
- When the user proposes a design, push back if it's shaky. Surface the tradeoff. Don't rubber-stamp.
- After the user gets something working, *then* mention the power-user idiom or stdlib shortcut they could have used. Not before.
- Don't plan far ahead. The roadmap emerges from the work.

If the user explicitly says "just write it" or "show me the code," then write it — but that's the exception.

## Security posture

Relaxed for now. The user is on a low-privilege account with little sensitive data exposure. We'll add sandboxing / allowlists / confirmation prompts when the agent starts executing real things, but don't preemptively over-engineer guardrails. Note risks when they're relevant, don't gate progress on them.

## Scope discipline

- No premature frameworks. No `src/` + `tests/` + `docs/` + `Makefile` scaffolding on day one.
- Start with a single file. Split when the seams become obvious.
- The agent is the vehicle; the practice is the destination.

## Session log

Keep a lightweight running log at `projects/agentBuilding/SESSIONS.md`. Claude maintains it; the user doesn't have to ask.

- Append a dated entry at natural checkpoints: when a meaningful piece lands, when a design decision is made, when a difficulty is hit (and how it was resolved or where it was parked).
- At the end of a working session, if no checkpoint entry was written during it, write a short close-out entry.
- Format per entry: `### YYYY-MM-DD — <short topic>` then 3–8 bullets. Cover *what was built*, *what was decided and why*, *what was hard*, *what's next*. Not a transcript — a memory aid.
- Past entries are append-only history. Don't rewrite them to look tidier.

## Git

This project lives on its own branch (`project/agent-building`) inside the larger training repo. Commit small and often, with clear messages. Don't merge back to `main` without an explicit ask.
