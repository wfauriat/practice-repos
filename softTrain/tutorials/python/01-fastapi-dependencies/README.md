# Tutorial 01 — FastAPI dependencies

## What this is

A guided practice on FastAPI's **dependency injection** system: how `Depends` works, why it's the right place to put cross-cutting concerns (DB sessions, auth, settings), and how to override it for testing.

## What you'll learn

- The `Depends(...)` mechanic in plain terms (no magic).
- The `Annotated[T, Depends(...)]` modern idiom and why it beats the older default-parameter style.
- Dependency **scopes**: per-request vs cached.
- How to **override** dependencies in tests so your routes can be exercised without a real DB or external service.

## How to engage

Open `exercise.py` and tell Claude: *"Tutor me through this."*

Claude will walk you blank-by-blank. Don't peek at `solution.py` until you're done — you'll learn far more if you struggle a little.

## Prerequisites

You should be roughly comfortable with FastAPI's basics (mounting routes, returning JSON, `pytest` fundamentals). If not, read the [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/) up to the "Dependencies" section first.
