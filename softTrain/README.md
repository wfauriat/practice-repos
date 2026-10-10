# softTrain

A personal training ground and pattern library. See [`original_plan.md`](./original_plan.md) for the full design rationale.

## What's here

| Directory     | Purpose                                                                       |
|---------------|-------------------------------------------------------------------------------|
| `scaffolds/`  | Working starter projects — copy via `tools/from-scaffold.sh`                  |
| `kata/`       | Short drills (re-solve repeatedly to build muscle memory)                     |
| `projects/`   | Multi-day mini-projects with goals, learning aims, retrospectives             |
| `tutorials/`  | "Fill-in-the-blanks" Socratic sessions with Claude (`# TUTOR:` markers)       |
| `craft/`      | Non-code practice — git, VS Code, shell, Docker labs + a daily-trick journal  |
| `lectures/`   | Prose primers on theory (Agile, MLOps, architecture) for read & discuss       |
| `reference/`  | Pure cheatsheets — fast lookup, no drills                                     |
| `tools/`      | Helper scripts — see `tools/*.sh --help`                                      |
| `curriculum/` | [`ROADMAP.md`](./curriculum/ROADMAP.md) — provisional list of topics to study |

## Common tasks

```bash
# Start a new project from a scaffold
tools/from-scaffold.sh python-fastapi-crud ~/code/my-new-api

# Drill a kata
tools/new-kata.sh python strings palindrome

# Capture a daily trick
tools/new-trick.sh "git switch -c is shorter than checkout -b"

# Run a risky command in a sandbox container
tools/sandbox.sh git reset --hard HEAD~5
```

## Engaging with Claude

This repo has [`CLAUDE.md`](./CLAUDE.md) wired up. Common entry phrases:

- *"Tutor me through `tutorials/python/01-fastapi-dependencies/exercise.py`"* → Socratic tutoring
- *"Let's do git lab 1"* → interactive sandbox lab in `craft/git/exercises/01-rebase-basics/`
- *"Let's go through `lectures/software-engineering/01-agile-fundamentals.md`"* → discussion via the lecture's prompts
- *"Write me a lecture on observability for Python services"* → Claude generates a new lecture artifact
- *"Add a trick: `xargs -I{}` is clearer than backticks"* → appends to the current month's trick journal
- *"Scaffold a new Hono API for me at `~/code/foo`"* → uses `tools/from-scaffold.sh`

## Stacks

- **Python** — `pip` + `venv` (each scaffold pinned with `requirements.lock.txt`)
- **TypeScript / Node** — `pnpm`
- **Containers** — `docker` + `docker compose v2`
- **Task runner** — `just` (each scaffold has a `Justfile`; `just --list` shows the targets)
