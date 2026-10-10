# softTrain — Curriculum / ROADMAP

> **Provisional.** This is a living backlog, not a fixed syllabus. Topics are listed because they're worth learning eventually — order is rough, scope is fuzzy. Re-read it occasionally and reorganise as priorities shift.

The repo has four ways to engage with a topic:

| Mode      | Where it lives          | When                                           |
|-----------|-------------------------|------------------------------------------------|
| Kata      | `kata/<lang>/<topic>/`  | Build muscle memory for a small idiom          |
| Project   | `projects/<name>/`      | Multi-day end-to-end work with a real goal     |
| Tutorial  | `tutorials/<lang>/...`  | Fill-in-the-blanks Socratic session w/ Claude  |
| Craft lab | `craft/<topic>/...`     | Interactive sandbox session (git, shell, docker) |
| Lecture   | `lectures/<area>/...`   | Prose primer + Socratic discussion of the *why* |

Each entry below tags a **Next concrete action** so you always have something to actually start.

---

## 1. Software fundamentals

### Testing strategies
The test pyramid (unit / integration / e2e) is folklore — when does it actually hold, and when does it become a ritual? What makes a unit test *worthwhile* vs. just rephrasing the implementation?
- **Next:** lecture `software-engineering/02-test-pyramid-debate.md` (covers Kent Beck's `tcr`, integration-first schools, contract testing). Pair with a kata that re-implements the same function under TDD vs. test-after to feel the difference.

### Dependency injection (without a framework)
DI is misunderstood as "use a container." The core idea is *passing collaborators in*. Then everything is testable.
- **Next:** tutorial `tutorials/python/01-fastapi-dependencies/` (already seeded). Then a kata where you refactor a tightly-coupled function into a DI form and write a test that uses a fake collaborator.

### Error handling
The five strategies (return-value, exceptions, sum types / `Result`, panic / abort, signal) and when each fits. Why "let it crash" beats defensive coding inside a supervised system.
- **Next:** lecture `software-engineering/03-error-handling-strategies.md`. Project: take the FastAPI scaffold and convert one route from exception-based to explicit `Result`-style.

### Logging & observability
Structured logging, log levels as design (not severity feelings), correlation IDs, the metric-log-trace triangle. The mental shift from "logs = printf" to "logs = events".
- **Next:** lecture `software-engineering/04-observability-mindset.md`. Project: instrument the FastAPI scaffold with structlog + a request-id middleware + one Prometheus counter, run under load, read your own logs.

### Packaging & distribution
Python packaging (pyproject.toml, build backends, entry points, console scripts) vs. npm packaging (exports field, module/main, types). Publishing to PyPI / npm; semver in practice.
- **Next:** project — turn `python-cli-typer` into a publishable package, build a wheel, install it from a local file URL.

### CI basics
What runs on every push? What runs only on main? Caching dependencies, matrix builds, status checks vs. required checks, branch protection.
- **Next:** project — add a `.github/workflows/ci.yml` to one scaffold that runs lint + tests on push, with sensible caching.

### Code review as design
Code review isn't gatekeeping; it's a design conversation. What makes a review valuable vs. a pile of nits? Why "approve with comments" is usually wrong.
- **Next:** lecture `software-engineering/05-code-review-as-design.md`.

### Feature flags & continuous delivery
Decoupling deploy from release. The mental model where every merge could ship. Kill switches, canary, gradual rollout, removing flags as a discipline.
- **Next:** lecture `software-engineering/06-feature-flags-and-cd.md`.

### Technical debt as risk management
Why "we'll clean it up later" doesn't mean what you think. Debt as deliberate vs. accidental, the four-quadrant model (Fowler), the cost-of-delay framing.
- **Next:** lecture `software-engineering/07-technical-debt-as-risk.md`.

### Debugging methodology
Systematic bug-hunting: forming hypotheses, binary-search isolation, reading stack traces, using `pdb`/`ipdb`. The skill that separates engineers who find bugs from those who randomly change things until they disappear.
- **Next:** lecture `software-engineering/NN-debugging-methodology.md`, then lab `craft/debug/exercises/01-pdb-basics/`.

---

## 2. Python deep-dives

### Python production primer
The gap between "Python that runs" and "Python someone else can maintain": project structure, type hints, logging (not `print`), error handling with custom exceptions, context managers.
- **Next:** lecture `software-engineering/04-python-production-primer.md`, then tutorial `tutorials/python/02-python-production-primer/`.

### Typing & generics in modern Python
`TypeVar`, `ParamSpec`, `Protocol`, `Generic[T]`, variance, the `Self` type. When to reach for `Protocol` over an ABC.
- **Next:** kata `kata/python/types/typed_cache.py` — generic LRU cache with full type signatures.

### Async — really understanding it
Event loops, the `await` sequence, structured concurrency (`asyncio.TaskGroup`), cancellation, common deadlocks. Why "just add async" usually slows things down.
- **Next:** tutorial `tutorials/python/02-async-fundamentals/`. Kata: implement a bounded-concurrency `gather` from primitives.

### Dataclasses vs Pydantic vs attrs
When validation matters, when it doesn't. Performance overhead. The "models everywhere" anti-pattern.
- **Next:** kata that converts a `dataclass` to a `pydantic.BaseModel` and benchmarks the validation cost.

### Performance & profiling
`cProfile`, `py-spy`, `scalene`, line_profiler. Reading flame graphs. The 80/20 of Python perf wins (avoid attribute lookup in hot loops, prefer comprehensions, watch GIL contention in threads).
- **Next:** project — pick a slow notebook from `python-data-notebook` (or write one), profile it, get a 5x speedup.

### Packaging with pip + venv (modern style)
`pyproject.toml` with `setuptools` or `hatchling`, `requirements.lock.txt` discipline, splitting runtime vs dev deps. When pyenv helps and when it confuses.
- **Next:** project — restructure a scaffold to use `pip-tools` for compiled, hash-pinned lockfiles. Compare the workflow.

---

## 3. TypeScript / JS deep-dives

### Type narrowing & generics
Discriminated unions, the `satisfies` operator, conditional types, mapped types. Where TS's structural typing trips you up.
- **Next:** kata `kata/typescript/types/discriminated-unions.ts` (already in the seed set).

### React rendering model
Reconciliation, the difference between a re-render and a DOM update, why `useMemo` rarely matters, the new compiler's promises. `useState` vs `useReducer` vs derived state.
- **Next:** tutorial `tutorials/typescript/01-react-state-patterns/` (already seeded).

### State management beyond `useState`
TanStack Query, Zustand, Jotai, the case for keeping it in URL/server state. When global state is a smell.
- **Next:** mini-project — build the same little app twice, once with TanStack Query as state, once with Zustand. Diff the experience.

### Build tools (esbuild, swc, tsc, Vite, Bun)
What each does, what they share, why "just use Vite" is right 90% of the time.
- **Next:** lecture `software-engineering/08-js-build-tools-landscape.md`.

---

## 4. Systems / Computer science

### SQL fundamentals
JOINs (left/right/inner/full/anti/semi), `GROUP BY` + `HAVING`, window functions, CTEs vs subqueries.
- **Next:** kata pack — a series of SQL drills against a sample SQLite DB. Include `EXPLAIN QUERY PLAN` reading.

### Indexes & query plans
B-trees, hash indexes, covering indexes, why your `LIKE '%foo'` is slow. Reading `EXPLAIN ANALYZE`.
- **Next:** lecture `software-engineering/09-indexes-and-query-plans.md`.

### HTTP semantics & caching
Idempotency, safe methods, `Cache-Control` vs `ETag`, the difference between proxy cache and browser cache. CORS as a deliberate (not gratuitous) design.
- **Next:** lecture. Project: add proper caching headers to the FastAPI scaffold and verify with `curl -v`.

### Basic concurrency
Mutexes, channels, the actor model, the four ways to share state (don't share, copy, lock, lock-free). Why most "concurrent" bugs are actually shared-state bugs.
- **Next:** lecture `software-engineering/10-concurrency-mental-models.md`.

### Data structures refreshers
Hash maps in practice, balanced trees, heaps, tries, when each one is the right answer.
- **Next:** kata pack. Implement an LRU from scratch. Implement a trie. Implement a min-heap.

---

## 5. Data / DS

### Pandas idioms
The big four: `groupby`, `merge`, `pivot_table`, `apply`. When to drop down to numpy. The `.loc` vs `.iloc` mental model.
- **Next:** kata pack against a small CSV, gradually getting harder. Includes "you should not use `apply` for this — what should you do?" prompts.

### Plotting decisions
Choosing the right chart for the data and the audience. The Cleveland-McGill ranking. Small multiples vs. one-big-chart. Why most dashboards are bad.
- **Next:** lecture `data-engineering/01-plotting-decisions.md` (yes, it's a software thing too).

### Basic stats for engineers
The handful of tests you'll actually use (t-test, chi-squared, Mann-Whitney), confidence intervals as ranges, p-values as the most-misused number in tech.
- **Next:** lecture + Jupyter walkthrough.

### Simple ML pipelines
Train / val / test split, the leakage you don't notice, baselines as the most underrated tool, when to bother with cross-validation.
- **Next:** mini-project in `python-data-notebook` — build a model end-to-end with a deliberate baseline first.

---

## 6. Craft (drills, not theory)

### Git mastery
Rebase, interactive rebase, conflict resolution, bisect, reflog recovery, cherry-pick, stash workflows, `--fixup` + `--autosquash`.
- **Next:** lecture `software-engineering/03-git-mental-model.md` (commits as objects, refs as pointers, the index, rebase vs merge tradeoffs), then work through `craft/git/exercises/01..08` in order.

### IDE fluency (VS Code)
The 20 keybindings to know cold; rename-symbol, extract-function, run-nearest-test, debugging a pytest, multi-cursor, multi-root workspaces.
- **Next:** read `craft/ide/vscode/keybindings.md` and drill the 20.

### Shell power
`grep`, `find` + `xargs`, `awk`, `sed`, `jq`, process substitution.
- **Next:** work through `craft/shell/exercises/01..06`.

### Docker fluency
Writing minimal Dockerfiles, multi-stage builds, layer caching, compose, debugging.
- **Next:** work through `craft/docker/exercises/01..05`.

### Terminal & multiplexer
`tmux` or `zellij`, session-per-project workflow, persistent SSH sessions, named windows / panes.
- **Next:** lecture `software-engineering/11-terminal-workflow.md` (low priority — pick this up if/when you start spending serious time in remote shells).

---

## 7. Theory / lectures (the prose branch)

These are the "big idea" topics. Each is a 1500-3000 word read with discussion prompts at the end.

### Already seeded
- `software-engineering/01-agile-fundamentals.md`
- `software-engineering/02-senior-engineer-mindset.md`
- `software-engineering/05-devops-mindset.md`
- `mlops/01-mlops-mindset.md`

### Software-engineering backlog
- 03 — The test pyramid debate
- 04 — Error handling strategies
- 05 — Observability mindset
- 06 — Code review as design
- 07 — Feature flags & continuous delivery
- 08 — Technical debt as risk management
- 09 — Coupling vs cohesion (the two-axis lens)
- 10 — Naming and the cost of premature abstraction
- 11 — Idempotency and at-least-once thinking
- 12 — Blameless postmortems and incident response
- 13 — Trunk-based development vs GitFlow
- 14 — Modular monolith vs microservices
- 15 — Evolutionary architecture (Fowler)
- 16 — Writing RFCs / design docs
- 17 — Estimation under uncertainty
- 18 — JS build tools landscape
- 19 — Indexes & query plans
- 20 — Concurrency mental models
- 21 — Terminal workflow
- 22 — Containerization mental model (Docker vs VMs, image layers, the 12-factor angle)
- 23 — Shape Up vs Scrum vs XP vs Kanban (what each gets right)

### MLOps backlog
- 02 — Experiment tracking (MLflow, W&B, the cheap-and-cheerful CSV approach)
- 03 — Deployment patterns (batch, online, streaming, embedded)
- 04 — Monitoring ML systems (data drift, prediction drift, performance drift)
- 05 — Feature stores (when they earn their cost, when they don't)
- 06 — Training/serving skew
- 07 — Retraining cadence as a product decision

### Architecture backlog
- 01 — Layered vs hexagonal vs onion (what they share, where they disagree)
- 02 — The CAP theorem in practice (and why "AP vs CP" is rarely the real choice)
- 03 — Event-driven vs request-response (when you really need a queue)

### Data-engineering backlog
- 01 — Plotting decisions
- 02 — Schema-on-read vs schema-on-write
- 03 — The lakehouse compromise (Iceberg / Delta / Hudi)

---

## How to grow this document

When you (or Claude) discover a topic worth pursuing later, add it here as a one-liner with a **Next concrete action**. The action is the important part — it converts "I should learn X someday" into "tomorrow I will write `kata/python/foo/bar.py`."

When a topic is *done* (or done enough), strike it through here and link to the artifact (lecture file, project archive, etc.) so the doc records the path you actually walked.
