# Python idiom audit — `ollama_backend.py`

*Date: 2026-05-27*

A step-back assessment of which Python concepts the current file has exercised, and which are conspicuously missing given the project's stated practice areas (Python design: SOLID, proper abstractions, dependency injection, logging, testing).

---

## What's been exercised solidly

The file is, despite being ~100 lines, surprisingly dense on *interface-design* Python:

- **Typing**: `list[dict]`, `httpx.Client | None`, `-> ChatResult`, `-> None`. Modern 3.10+ shape.
- **Function signatures** with `*,` keyword-only separator and default values referencing module constants.
- **`None`-sentinel injection pattern** (the `client: httpx.Client | None = None` idiom).
- **Exception design**: custom hierarchy, `raise X from e` chaining, two-clause flat `try`.
- **`@dataclass(frozen=True)`** for value objects, with construction-from-dict.
- **Context manager consumption** (`with httpx.Client()`).
- **Docstrings** with a `Raises:` section that matches the type contract.
- **Module-level constant convention**, `if __name__ == "__main__":` entry-point split.
- Subtle: `[*messages, user_msg]` shallow-copy-and-append, implicit string concat inside parens.

That's a real foundation. Many junior Python codebases never get to "function with keyword-only args, dependency-injected client, frozen result type, custom exception hierarchy".

---

## Conspicuously missing — and project-relevant

In rough order of how soon they'd hurt:

### 1. Iteration beyond `while True`

Zero `for` loops, zero comprehensions. That's striking. Any moment now you'll want `next_user_msg = next(m for m in messages if m["role"] == "user")` or `[m["content"] for m in messages]` and it'll feel unfamiliar. List / dict / generator comprehensions are core Pythonic glue.

### 2. Testing

`CLAUDE.md` lists testing as one of the three crafts. Zero tests exist. `pytest` is the standard, but the gap isn't just "use pytest" — it's the broader question of *what to test* in a network-backed wrapper: fakes for `httpx.Client`, parametrised tests, exception assertions. The DI seam on `client=` was added partly *for* testability and is being unused.

### 3. Logging

Same — explicitly in `CLAUDE.md`'s practice list. Currently all output is `print()`. The `logging` module's structured concepts (levels, loggers per module, handlers, formatters) aren't touched. The moment you want to debug a flaky network call without spamming stdout, you'll feel this.

### 4. Environment variables

`os.getenv("ANTHROPIC_API_KEY")` is going to be the very first line of the second backend. Zero exposure yet.

### 5. Protocols / ABCs

Parked, but the second backend will pull on this. Worth knowing *both* options before deciding — duck-typed `typing.Protocol` (structural) vs `abc.ABC` (nominal). The choice has real consequences.

### 6. `typing` deeper

The message dict is currently `dict` — fine, but `TypedDict` would let you type the `{"role": ..., "content": ...}` shape. And `role` is currently a free string; `Literal["system", "user", "assistant"]` would catch typos at check-time. Both are non-runtime — they only help if you run pyright.

---

## Mid-term gaps that aren't urgent but are real

- **Async.** `httpx.AsyncClient`, `async def`, `await`, `asyncio.run`. Most production LLM code is async-first — multiple concurrent tool calls, streaming, parallel agents. Not needed for a REPL, but a real conceptual gap.
- **Regular expressions.** `re` module. Will land when you actually want to strip qwen3's `<think>...</think>` blocks.
- **File I/O + `pathlib`.** Will land if you persist conversations or load config from disk.
- **Writing your own decorators / context managers.** Both are *used*; neither is *authored*. Decorator authoring shows up the moment you want middleware (retry-on-transient-error, log-time-of-call, etc.).
- **`functools.partial`, `lru_cache`.** Will appear as soon as you bind arguments (e.g. wrap `chat()` with a fixed model/client into a callable for a tool dispatcher).

---

## Smaller idiom gaps

- `match` statement (3.10+) — could replace the quit check, though `if`/`elif`/`else` is fine for two cases.
- `set` literal — `if prompt in {"quit", "/quit"}` is the canonical Pythonic membership check (faster than tuple for many items; same shape for two).
- `enum.Enum` — for `role` if you wanted strict types.
- `dataclasses.replace()` for evolving frozen instances.
- `__post_init__` for dataclass validation (e.g. enforce `tokens_in >= 0`).
- `else` clause on `try`/`except` — runs only if no exception fired. Mildly underused idiom.

---

## What I'd flag as the actual gap

If I had to pick the *one* missing axis that's most out of step with the project's stated craft list, it's **testing**. `CLAUDE.md` says "Python design: SOLID, proper abstractions, dependency injection, logging, testing." The DI seam is built and unused; the test suite is empty; the logging story is `print()`. None of this is bad — the file is small, the practice is deliberately incremental — but it means the *current* file has been over-rotated toward design-of-interface and under-rotated toward observability-of-runtime.

The second-biggest gap is more philosophical: **all iteration is `while True`**. That's not Python a Python programmer writes day-to-day. Comprehensions and `for` loops are the most common things in real code, and the file has zero. That'll resolve naturally as features land, but if you ever wanted to do a small *deliberate* exercise (filter, map, summarise the message history), that's the highest-leverage warm-up.
