# Python idiom audit — follow-up

*Date: 2026-05-29*
*Follows: `audit_python_idoms.md` (2026-05-27, scoped to `ollama_backend.py`)*

A re-assessment of Python concept coverage across the `agentAPI/` package. The
first audit predated **both** the class refactor and any tests — so a large part
of its "missing" list has since moved. Current-state claims below are
grep-confirmed against the package (tests included).

---

## Added since the 2026-05-27 audit

| First-audit item | Status now | Evidence |
|---|---|---|
| **Testing** (its #1 flagged gap) | **Closed, comprehensively** | pytest harness (`pyproject.toml`), 9 tests across 2 files, hand-rolled fakes (duck-typed + `collections.namedtuple`), `pytest.raises`, exception + `__cause__` assertions, request-capture tests, `xfail(strict=True)`. The audit's specific jab — *"the DI seam on `client=` was added partly for testability and is being unused"* — is resolved: every test injects through it. |
| **Protocols / ABCs** (#5) | **Decided + implemented** | `Backend(typing.Protocol)`, chosen over ABC/nothing via a two-seams argument (backend seam *and* client seam), mypy-verified for conformance. |
| **Environment variables** (#4) | **Covered** (different route) | `load_dotenv()` + SDK auto-read of `ANTHROPIC_API_KEY`. Via `python-dotenv`, *not* the raw `os.getenv(...)` the first audit predicted. |

Plus a cluster the first audit could not have listed (the file was a single free
function then):

- **Classes / OOP** — constructor-vs-method split, dependency injection via the constructor.
- **Packaging** — `__init__` re-exports + `__all__`, `__main__.py`, relative imports, `python -m` execution.
- **`argparse`** — backend selector with `choices=`.
- **`collections.namedtuple`** — lightweight response fakes in tests.
- **Decorator *use*** — `@dataclass`, `@pytest.mark.xfail`.
- **mypy as a workflow** — reading overload errors; the dict-splat-collapses-to-`object` insight.

---

## Still missing (grep-confirmed)

| Item | Status | Note |
|---|---|---|
| **Logging** (#3, on the craft list) | **Untouched** | Still `print()` — 10 sites, all in `__main__.py`. Zero `logging`. |
| **Iteration / comprehensions** (#1, the first audit's #2 "actual gap") | **Still literally zero** | No `for`, no comprehensions anywhere. All `while True` + `.append`. |
| **Deeper typing — `TypedDict` / `Literal`** (#6) | **Untouched, now *pressured*** | The parked mypy finding (`messages: list[dict]` ≠ `Iterable[MessageParam]`) *is* a TypedDict gap. Elevated from "nice to have" to "blocking a real error." |
| Mid-term: async, `re`, file I/O / `pathlib`, **authoring** decorators / context managers, `functools` | Untouched | Mostly fine — none pulled by a feature yet. |
| Small idioms: `match`, `set`-membership, `Enum`, `dataclasses.replace()`, `__post_init__`, `try/else` | Untouched | The quit check is still `== … or ==` rather than `in {…}`. |
| pytest depth: `parametrize`, `fixture`, `monkeypatch` / `mock` | Not yet | Testing landed, but these specific tools haven't — fakes are hand-rolled by choice. |

---

## Prioritization

Lens: weight by (a) on the project's craft list, (b) under active pressure now,
(c) double-duty with an in-flight thread.

### 1. `Message` TypedDict + `Literal` role — top pick

The single highest-leverage move: one concept closes the most-glaring typing gap
(#6), **resolves the parked mypy finding** (`messages: list[dict]` vs
`Iterable[MessageParam]`), and is cross-cutting design work — it threads through
the `Backend` Protocol and both backends, so it doubles as abstraction practice.
`role: Literal["system", "user", "assistant"]` rides along for free. Double-duty:
missing idiom **and** live error.

### 2. Logging — strongest pure craft-list gap

Explicitly listed, totally untouched. The first audit's core verdict was
"over-rotated on interface-design, under-rotated on observability-of-runtime."
Self-contained, with an obvious insertion point: a per-module logger, levels, a
formatter; convert the backends' would-be debug output to `logger.debug`, keep
user-facing REPL text as `print`. Teaches a whole stdlib subsystem not yet touched.

### 3. Finish the Anthropic error model — completes a parked story

The `xfail` (`APIStatusError → BackendResponseError`) plus the
`response.content[0].text` narrowing (the second mypy finding → revive
`BackendContractError`). Lower *new-idiom* content (exceptions are well-exercised
already), but it picks up `isinstance`-narrowing, flips the xfail, and clears the
second mypy error. Natural to pair with #1 — both touch Anthropic response handling.

### Falls out naturally / defer

- **Iteration & comprehensions** — the first audit itself said these resolve as features land. A deliberate "summarise message history" warm-up is the cheap way to front-load it if desired.
- **Client-seam Protocols** — the remaining duck-typed-`FakeClient` warnings; two narrow Protocols (httpx vs anthropic clients have different shapes). Do when next touching that area.
- **async, regex, `match`, `Enum`, file I/O, decorator authoring, `functools`** — defer until a feature pulls them.

**Recommendation:** start with the `Message` TypedDict — the one item that is
simultaneously a missing idiom, a live mypy fix, and genuine abstraction practice.
