# softTrain — Personal practice + pattern library

## Context

`softTrain` will become a personal training ground with two purposes:

1. **Build muscle memory and good practices** in software engineering (primary) and computer/data science (secondary), across three axes:
   - **Code practice** — short drills, multi-day mini-projects, guided "fill-in-the-blanks" tutoring.
   - **Craft practice** — the meta-skills around the code: git fluency, IDE/shell power-use, day-to-day tricks. Interactive sessions and a living trick journal.
   - **Theory / lectures** — verbose, prose primers on conceptual topics where the value isn't muscle memory but understanding (Agile, MLOps mindset, architecture, code review culture). Read, discuss, generate on demand.
2. **Serve as a pattern dictionary** — a small, curated set of working scaffolds (Python API, React frontend, CLI, etc.) you can copy when starting something new.

Stacks in scope: **Python** (backend, scripting, data) and **TypeScript/JavaScript** (frontend + Node).
Cadence: lightweight to start — bootstrap a handful of common patterns, then plan a longer curriculum together.

The repo is currently empty and not under version control. The plan covers the initial structure, 5 starter scaffolds, three practice modes (kata, mini-projects, tutored exercises), and a `ROADMAP.md` to grow into a curriculum.

---

## Top-level layout

```
softTrain/
├── README.md                  # How to use this repo (entry point)
├── CLAUDE.md                  # Conventions / instructions for Claude
├── .gitignore                 # Top-level ignores (envs, caches, OS junk)
├── scaffolds/                 # Pattern dictionary — copy-paste starters
│   ├── README.md              # Index + how to clone a scaffold
│   ├── python-fastapi-crud/
│   ├── python-cli-typer/
│   ├── python-data-notebook/
│   ├── ts-react-vite/
│   └── ts-node-api/
├── kata/                      # Short drills (re-solve repeatedly)
│   ├── README.md
│   ├── python/
│   │   ├── _solutions/
│   │   └── strings/, collections/, async/, ...
│   └── typescript/
├── projects/                  # Multi-day mini-projects
│   ├── README.md              # Index + ideas backlog
│   └── _archive/              # Completed projects move here
├── tutorials/                 # "Fill-in-the-blanks" guided sessions w/ Claude
│   ├── README.md              # The tutoring protocol (see below)
│   ├── python/
│   │   └── 01-fastapi-dependencies/
│   └── typescript/
│       └── 01-react-state-patterns/
├── craft/                     # Meta-skills practice (non-code)
│   ├── README.md              # The lab protocol (shared by all sub-tracks)
│   ├── git/                   # Interactive git labs (sandbox repos)
│   ├── ide/                   # VS Code power-use (keybindings, snippets, workflows)
│   ├── shell/                 # grep/find/awk/sed/jq drills with sample data
│   ├── docker/                # Container labs + the shared sandbox image
│   └── tricks/                # Dated "today I learned" journal
├── lectures/                  # Theory — prose primers + Socratic discussion
│   ├── README.md
│   ├── software-engineering/
│   ├── mlops/
│   ├── architecture/
│   └── data-engineering/
├── reference/                 # Pure cheatsheets — fast lookup, no drills
│   ├── README.md
│   ├── python/, typescript/, sql/, regex/
├── tools/                     # Helper scripts (bash)
│   ├── from-scaffold.sh       # Copy a scaffold to a new location
│   ├── new-kata.sh            # Stub a new kata file from template
│   ├── new-project.sh         # Stub a new mini-project from template
│   ├── new-trick.sh           # Append a dated entry to craft/tricks/<YYYY-MM>.md
│   └── sandbox.sh             # Run any command in the craft/docker/sandbox image
└── curriculum/
    └── ROADMAP.md             # Provisional list of topics to study/practice
```

Each scaffold is its own self-contained mini-project (own `pyproject.toml` / `package.json`). They share the umbrella repo but not dependencies.

---

## The 5 starter scaffolds

Modern, opinionated, runnable with one command. Each ships with a `README.md`, working code, passing tests, and a `Justfile` with the canonical commands (`just run`, `just test`, `just lint`).

### 1. `scaffolds/python-fastapi-crud/`
- **Why:** the canonical Python web pattern; covers HTTP, validation, DB, tests in one place.
- **Stack:** FastAPI · Pydantic v2 · SQLAlchemy 2.x · SQLite (file) · Alembic · pytest · ruff · pip + venv
- **Demo:** `Item` resource with `GET/POST/PATCH/DELETE`, paginated list, integration tests via `httpx.AsyncClient`.
- **Layout:** `app/{main.py, models.py, schemas.py, db.py, routes/}` + `tests/` + `alembic/` + multi-stage `Dockerfile` + `compose.yml`.

### 2. `scaffolds/python-cli-typer/`
- **Why:** scripting and automation is a daily software-engineer reflex.
- **Stack:** Typer · Rich (pretty output) · pytest · ruff · pip + venv
- **Demo:** a CLI with subcommands (`add`, `list`, `done`) backed by a JSON file; demonstrates flags, options, exit codes, `Annotated[..., typer.Option]`, testable command functions.

### 3. `scaffolds/python-data-notebook/`
- **Why:** the standard reproducible-analysis layout; touches the data-science axis.
- **Stack:** Jupyter · pandas · numpy · matplotlib · seaborn · pip + venv · `papermill` for parametrised runs
- **Demo:** one notebook (`01-eda.ipynb`) doing EDA on a tiny built-in dataset, plus a `src/loaders.py` showing how to factor reusable code out of notebooks.

### 4. `scaffolds/ts-react-vite/`
- **Why:** today's default frontend starter.
- **Stack:** Vite · React 18 · TypeScript · Tailwind v4 · Vitest + Testing Library · ESLint · pnpm
- **Demo:** counter + simple data-fetching component (TanStack Query); shows component test, hook test, and a small form with controlled inputs.

### 5. `scaffolds/ts-node-api/`
- **Why:** completes the TS picture; pairs naturally with `ts-react-vite` for full-stack work.
- **Stack:** Hono (lightweight, modern) · TypeScript · Zod · Vitest · pnpm · `tsx` for dev
- **Demo:** same `Item` CRUD as the FastAPI scaffold, in-memory store, request validation via Zod, integration tests with `app.request()`. Multi-stage `Dockerfile` + a `compose.yml` that pairs it with `python-fastapi-crud` to demonstrate inter-container networking.

> Each scaffold's `README.md` includes a **"When to reach for this"** section so future-you remembers when it's the right pick.

---

## Practice modes

### Kata (short drills)
Convention: each kata is one source file. Header docstring contains the problem statement and example I/O. Tests live at the bottom (`pytest` for Python, `vitest` inline `if (import.meta.vitest)` for TS).

```
kata/python/strings/reverse_words.py     # the prompt (no solution)
kata/python/_solutions/strings/reverse_words.py
```

Workflow: open the prompt file → solve it → run tests → diff against `_solutions/`. `tools/new-kata.sh <lang> <topic> <name>` stamps a new file from the template.

### Mini-projects
A `projects/` directory. Each project = its own folder with its own `README.md` (goal, learning aims, stretch goals, retrospective). The top-level `projects/README.md` keeps a backlog of ideas. Finished projects move to `_archive/`.

### Tutored sessions ("fill-in-the-blanks" with Claude)
A tutorial is a directory with this layout:

```
tutorials/python/01-fastapi-dependencies/
├── README.md       # Concept explanation, what you'll learn
├── exercise.py     # Skeleton with `# TUTOR: ...` blanks
├── solution.py     # Reference solution
└── notes.md        # Power-user tricks, idioms, gotchas (read AFTER)
```

The protocol (documented in `tutorials/README.md` and `CLAUDE.md`):
- **Marker:** lines containing `# TUTOR: <hint>` (or `// TUTOR:` for TS) are the blanks.
- **You** open `exercise.py` and ask Claude: *"Tutor me through this."*
- **Claude** explains the goal, asks Socratic questions, lets you attempt each blank, then confirms or corrects. Claude does **not** dump the solution; it nudges.
- After all blanks are filled, **Claude reveals `notes.md`** — the power-user tricks for that topic (e.g. `Annotated[Depends(...)]` patterns, `lru_cache` on dependency factories, etc.).

Two tutorials seeded at the start:
- `python/01-fastapi-dependencies/` — DI, scopes, testability.
- `typescript/01-react-state-patterns/` — `useState` vs `useReducer` vs derived state, when to lift.

---

## Craft practice (`craft/`)

The non-code half of the workbench. These are interactive sessions you run *with* Claude — Claude sets up sandboxes, asks you to perform an action, observes the outcome, then explains the trick or gotcha. Distinct from `reference/`, which is pure lookup.

### `craft/git/` — interactive git labs
Each lab is a directory with a `setup.sh` that builds a throwaway sandbox repo with the exact history/state needed (conflicts, detached HEAD, broken bisect range, etc.), a `README.md` describing the goal, and a `solution.md` revealed at the end.

```
craft/git/
├── README.md                       # The lab protocol (see below)
├── _sandbox/                       # Where setup.sh writes scratch repos (gitignored)
└── exercises/
    ├── 01-rebase-basics/           # Linearise a feature branch
    ├── 02-interactive-rebase/      # Squash, reword, reorder, drop
    ├── 03-conflict-resolution/     # Resolve a real merge/rebase conflict
    ├── 04-bisect/                  # Binary-search a regression
    ├── 05-reflog-recovery/         # Recover a "lost" commit
    ├── 06-cherry-pick/
    ├── 07-stash-workflows/
    └── 08-fixup-and-autosquash/    # `commit --fixup` + `rebase -i --autosquash`
```

**Lab protocol** (documented in `craft/README.md` and `CLAUDE.md`):
1. User: *"Let's do git lab N."*
2. Claude runs `setup.sh` (rebuilds the sandbox cleanly each time).
3. Claude states the goal in plain English. Does **not** give the commands.
4. User attempts; Claude watches `git status`/`git log --oneline --graph` between steps and corrects gently.
5. After success, Claude reveals `solution.md` plus power-user tips (`--autostash`, `--update-refs`, `rerere`, `git switch -c`, etc.).

### `craft/ide/` — editor power-use (VS Code)

```
craft/ide/
├── README.md                # Capture-what for any editor (in case you add another later)
└── vscode/
    ├── keybindings.md       # 20 shortcuts to know cold + drill prompts
    ├── snippets/            # Sample user snippets: python.json, typescript.json
    ├── workflows.md         # Rename across project, extract fn, run nearest test, debug a pytest, tasks/launch.json
    └── extensions.md        # Must-have extensions for Python + TS, one-line "why" each
```

`keybindings.md` covers: command palette, multi-cursor, symbol/file nav, go-to-definition, rename symbol, refactor menu, split editor, zen mode, integrated terminal toggle, debugger step controls. Default Linux keymap — if you remap, we adjust.

### `craft/shell/` — terminal fluency drills
Sample data files plus exercises against them. Same lab pattern as git: each exercise has a goal, a sandbox of input data, and a `solution.md` with the canonical pipeline + alternates.

```
craft/shell/
├── README.md
├── data/                    # CSV/JSON/log fixtures
└── exercises/
    ├── 01-grep-essentials/        # -E, -A/-B/-C, -o, -l
    ├── 02-find-and-xargs/
    ├── 03-awk-basics/             # field splitting, simple aggregations
    ├── 04-sed-substitutions/
    ├── 05-jq-pipelines/
    └── 06-piping-and-process-substitution/
```

### `craft/docker/` — containers + the shared sandbox image
Two purposes in one directory: (a) interactive labs to build Docker fluency, and (b) a base image used to run *risky* exercises elsewhere in the repo without endangering the host.

```
craft/docker/
├── README.md
├── sandbox/                  # The shared sandbox image (used by tools/sandbox.sh)
│   └── Dockerfile            # Linux base + git/jq/awk/sed/python/node + safe defaults
└── exercises/
    ├── 01-first-image/       # Minimal Dockerfile, build, run, layers
    ├── 02-multi-stage/       # Slim production images, separating build vs runtime
    ├── 03-layer-caching/     # Diagnose and fix slow rebuilds
    ├── 04-compose-networking/ # Two services, internal DNS, healthchecks
    └── 05-debug-images/      # `docker inspect`, exec, build cache, dive
```

Same lab protocol as git/shell: `setup.sh` builds the scenario, Claude states the goal, you attempt, `solution.md` is revealed at the end with experienced-user notes.

**Sandbox dual-purpose:** the `craft/docker/sandbox/` image isn't only a learning artifact — it's also the runtime for any drill that's potentially destructive (forced `git reset`, `rm -rf` experiments, untrusted scripts, OS-level shell exploration). Run via `tools/sandbox.sh <command>`, which spins up a fresh container with the current dir mounted at `/work`.

### `craft/tricks/` — daily-trick journal
A dated journal of small wins. One markdown file per month: `2026-05.md`. Each entry: 1-3 lines on the trick, why it matters, where you encountered it. Claude appends here when you say *"add a trick: ..."* — keeping it low-friction enough to actually maintain.

---

## Lectures (`lectures/`) — the theory branch

Distinct from drills, labs, and cheatsheets: this is **prose**. Verbose, narrative primers (~1500-3000 words) on conceptual topics where the goal is understanding the *why* and the tradeoffs — not building reflexes.

### Anatomy of a lecture file

A single markdown file with this skeleton:

1. **Abstract** — 1-2 sentence summary.
2. **Motivation** — why this matters, where it bites you in practice.
3. **Core concepts** — the substance, with concrete examples.
4. **Tradeoffs / counterpoints** — when this idea fails or is misapplied (this is the most valuable section and the most often missing).
5. **Further reading** — 2-5 books / posts / papers (canonical sources, not blog noise).
6. **Discussion prompts** — 3-5 open-ended questions at the bottom. These are the seeds of a conversation with Claude.

### Two modes of engagement

1. **Read & discuss.** You: *"let's go through `lectures/software-engineering/01-agile-fundamentals.md`."* Claude does **not** re-summarise the whole thing (you just read it) — Claude jumps straight to the discussion prompts and runs them Socratically, pushing back, surfacing where your intuition is shaky.
2. **Generate on demand.** You: *"write me a lecture on backpressure in async systems."* Claude writes the markdown into the appropriate subdirectory using the skeleton above, so it stays as an artifact for future-you (or for re-discussion later).

### Seeded lectures (initial)
- `software-engineering/01-agile-fundamentals.md` — what Agile actually means vs the cargo-culted standup-and-Jira version; failure modes (Scrum theatre, story-point inflation); divergent schools (Shape Up, XP, Kanban).
- `mlops/01-mlops-mindset.md` — model-as-artifact → system-as-product: reproducibility, tracking, deployment, monitoring, drift, retraining cadence.

Further topics live in `curriculum/ROADMAP.md`.

---

## Helper scripts (`tools/`)

Small, dependency-free bash scripts. Behaviour is deliberately minimal — they exist to remove friction, not to hide what's going on.

- **`tools/from-scaffold.sh <scaffold> <target-dir>`** — `cp -r` a scaffold, swap its name in `pyproject.toml`/`package.json`, re-init git inside. Echoes next-step commands.
- **`tools/new-kata.sh <python|typescript> <topic> <name>`** — creates `kata/<lang>/<topic>/<name>.{py,ts}` from a template, plus the empty `_solutions/...` stub.
- **`tools/new-project.sh <name>`** — creates `projects/<name>/` with a `README.md` template (goal, learning aims, retro).
- **`tools/new-trick.sh <one-line description>`** — appends a dated entry to `craft/tricks/<YYYY-MM>.md` (creates the file if missing). For low-friction journaling.
- **`tools/sandbox.sh <command...>`** — runs `<command>` inside a fresh container from the `craft/docker/sandbox/` image with the current dir mounted at `/work`. The right tool for destructive git, fs experiments, untrusted scripts.

---

## `CLAUDE.md` (top-level)

A short file telling Claude how to behave in this repo:
- This is a learning repo — **prefer Socratic / minimal-spoiler responses** over dumping full solutions. When in `tutorials/`, `kata/`, or `craft/<topic>/exercises/`, do not write the answer unless asked twice.
- When the user starts a **tutoring session** (opens an `exercise.py`/`.ts`), follow the tutorial protocol.
- When the user starts a **craft lab** ("let's do git lab N", "let's drill awk"), follow the lab protocol: run `setup.sh`, state the goal in English, watch their attempts, reveal `solution.md` only after success.
- When the user opens a **lecture** ("let's discuss `lectures/.../X.md`"), do NOT re-summarise — assume they read it. Jump to the discussion prompts and run them Socratically, pushing back on shaky intuition.
- When the user asks for a **new lecture** ("write me a lecture on ..."), write a markdown file into `lectures/<area>/` following the documented skeleton (abstract → motivation → core concepts → tradeoffs → further reading → discussion prompts).
- When the user says **"add a trick: ..."**, append to `craft/tricks/<YYYY-MM>.md` via `tools/new-trick.sh` — fast, no ceremony.
- When the user says "scaffold X for me," reach for `tools/from-scaffold.sh` rather than writing from scratch.
- For anything **potentially destructive** (forced `git reset/clean`, `rm -rf`, untrusted scripts, system tweaks), suggest running through `tools/sandbox.sh` instead of the host. Don't run it directly without confirming.
- The `ROADMAP.md` is living — update it when you and the user discuss new directions.

---

## `curriculum/ROADMAP.md`

A markdown doc seeded with a backlog of topics across:
- **Software fundamentals**: testing strategies, dependency injection, error handling, logging, observability, packaging/distribution, CI basics.
- **Python deep-dives**: typing & generics, async, dataclasses vs Pydantic, performance (profiling), packaging with pip + venv.
- **TS/JS deep-dives**: type narrowing, generics, React rendering model, state management, build tools.
- **Systems / CS**: SQL fundamentals, indexes & query plans, HTTP & caching, basic concurrency, data structures refreshers.
- **Data / DS**: pandas idioms, plotting decisions, basic stats, simple ML pipelines.
- **Craft**: git mastery (rebase/bisect/reflog), IDE fluency (refactors, multi-cursor, debugger), shell power (jq, awk, find), terminal/multiplexer workflows, Docker (Dockerfile authoring, layer caching, compose, debugging).
- **Theory / lectures**: Agile (and its discontents), Shape Up, code review as design, technical debt as risk management, observability mindset, feature flags & continuous delivery, the test pyramid debate, **containerization mental model** (Docker vs VMs, image layers, the 12-factor angle); **MLOps**: model-as-system thinking, experiment tracking, deployment patterns (batch/online/streaming), monitoring & drift, feature stores, training/serving skew, retraining cadence.

Each topic has a one-line "next concrete action" (a kata to write, a project to attempt, a tutorial to seed). The doc grows as we plan the curriculum together — explicitly marked as **provisional**.

---

## Initialization steps (in order)

1. **`git init`** the repo, add a top-level `.gitignore` (Python caches, `node_modules`, `.venv`, `dist`, `.DS_Store`, `*.sqlite`, `.ipynb_checkpoints`, etc.).
2. Create the directory tree above with `README.md` placeholders so navigation is obvious from day one.
3. Write the **5 scaffolds** as fully working, tested mini-projects.
4. Write `tools/` scripts; `chmod +x` them.
5. Seed the **2 tutorials** (one Python, one TS).
6. Seed `kata/` with **3 example kata per language** (one per topic folder) so the pattern is visible.
7. Seed `craft/`:
   - 2 git labs (`01-rebase-basics`, `04-bisect`) with working `setup.sh` scripts.
   - 2 shell exercises (`01-grep-essentials`, `05-jq-pipelines`) with sample data in `craft/shell/data/`. Targets **bash + GNU coreutils**.
   - `craft/ide/vscode/{keybindings.md, workflows.md, extensions.md, snippets/}` for VS Code on Linux (default keymap).
   - `craft/docker/sandbox/Dockerfile` (the shared sandbox image) + 2 docker labs (`01-first-image`, `02-multi-stage`).
   - `craft/tricks/2026-05.md` with one seed entry.
8. Seed `lectures/`: the two initial lectures (`software-engineering/01-agile-fundamentals.md`, `mlops/01-mlops-mindset.md`).
9. Write `CLAUDE.md`, top-level `README.md`, `curriculum/ROADMAP.md`.

---

## Critical files to create

- `README.md`, `CLAUDE.md`, `.gitignore` (top-level)
- `scaffolds/README.md` + 5 scaffold subtrees (each with `README.md`, source, tests, `Justfile`, lockfile)
- `kata/README.md` + per-language template + ~6 seed katas (3 Py, 3 TS) + `_solutions/`
- `projects/README.md` (backlog) + project template
- `tutorials/README.md` (protocol) + 2 seed tutorials
- `craft/README.md` (lab protocol) + `craft/git/exercises/{01,04}` + `craft/shell/exercises/{01,05}` + `craft/shell/data/` + `craft/ide/vscode/{keybindings.md, workflows.md, extensions.md, snippets/{python.json, typescript.json}}` + `craft/docker/sandbox/Dockerfile` + `craft/docker/exercises/{01,02}` + `craft/tricks/2026-05.md`
- `lectures/README.md` (anatomy + engagement modes) + `lectures/software-engineering/01-agile-fundamentals.md` + `lectures/mlops/01-mlops-mindset.md`
- `reference/README.md` + a few starter cheatsheets (e.g. `python/regex.md`, `sql/joins.md`)
- `tools/from-scaffold.sh`, `tools/new-kata.sh`, `tools/new-project.sh`, `tools/new-trick.sh`, `tools/sandbox.sh`
- `curriculum/ROADMAP.md`

No existing files to edit (empty repo).

---

## Tooling assumptions

- **Python**: `python -m venv .venv` + `pip`. Each scaffold has `requirements.txt` (runtime) and `requirements-dev.txt` (pytest, ruff, etc.). Pinning via `pip freeze > requirements.lock.txt` after install — explicit, no extra tooling.
- **TS/JS**: `pnpm` for package management; `tsx` for running TS directly in dev.
- **Containers**: `docker` + `docker compose` v2. The `craft/docker/sandbox/` image is the shared runtime for `tools/sandbox.sh`.
- **Task runner**: `just` (one-line `Justfile` per scaffold). If absent, scaffolds fall back to plain shell snippets in each `README.md`.

Assumed present: Python + `pip`. Implementation step prompts for installs of `pnpm`, `just`, `docker` if missing.

---

## Verification

After implementation, run end-to-end smoke tests for each scaffold:

| Scaffold | Smoke test |
|---|---|
| `python-fastapi-crud` | `cd scaffolds/python-fastapi-crud && python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && .venv/bin/pytest && .venv/bin/uvicorn app.main:app &` then `curl localhost:8000/items` |
| `python-cli-typer` | (after the same venv + install) `.venv/bin/python -m mycli add "first task" && .venv/bin/python -m mycli list && .venv/bin/pytest` |
| `python-data-notebook` | (after venv + install) `.venv/bin/jupyter nbconvert --to notebook --execute notebooks/01-eda.ipynb` |
| `ts-react-vite` | `pnpm install && pnpm test && pnpm build` |
| `ts-node-api` | `pnpm install && pnpm test && pnpm dev` then `curl localhost:3000/items` |

Helpers:
- `tools/from-scaffold.sh python-cli-typer /tmp/clitest` should produce a working copy that runs out of the box.
- `tools/new-kata.sh python strings palindrome` creates `kata/python/strings/palindrome.py` + matching `_solutions/` stub.
- `tools/new-trick.sh "git switch -c is shorter than checkout -b"` appends a dated entry to `craft/tricks/2026-05.md`.

Craft labs smoke test:
- `bash craft/git/exercises/01-rebase-basics/setup.sh` should produce a clean sandbox repo at `craft/git/_sandbox/01-rebase-basics/` ready for the exercise.
- `bash craft/shell/exercises/05-jq-pipelines/check.sh` (or running the documented pipeline against `craft/shell/data/...json`) should match expected output.
- `docker build -t softtrain-sandbox craft/docker/sandbox/` should succeed; `tools/sandbox.sh ls /work` should list the repo from inside a container.

Protocol smoke tests (manual): open a tutorial `exercise.py` and ask Claude to tutor — confirm Socratic behaviour, no spoilers, `notes.md` revealed only at the end. Same for "let's do git lab 1" — confirm Claude runs `setup.sh`, states the goal in English, withholds commands until you've tried.
