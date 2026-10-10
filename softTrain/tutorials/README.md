# tutorials/

"Fill-in-the-blanks" Socratic sessions, run together with Claude.

## Anatomy of a tutorial

```
tutorials/<lang>/<NN-topic>/
├── README.md        # What this is, what you'll learn
├── exercise.py      # Skeleton with `# TUTOR: <hint>` markers — the blanks you fill in
├── solution.py      # Reference solution (don't peek)
└── notes.md         # Power-user tricks, idioms, gotchas — revealed after you finish
```

The `# TUTOR: <hint>` (or `// TUTOR: <hint>` for TS) marker indicates a blank to fill.

## Protocol

1. Open `exercise.py` in your editor.
2. Tell Claude: **"Tutor me through `tutorials/<lang>/<NN-topic>/exercise.py`."**
3. Claude states the goal in one sentence (you've read the README, no need to re-explain).
4. Claude walks you through one TUTOR blank at a time:
   - States *what* the blank should accomplish in plain English.
   - Lets you attempt the code yourself.
   - Gives a small nudge if you're stuck — never the full line.
5. After all blanks are filled correctly, Claude reveals `notes.md` — the experienced-dev tips you couldn't have discovered yourself.

## Why this format works

- The README explains the *concept*. You read it once.
- The exercise forces you to **type** — typing is where the muscle memory lives.
- Claude resists giving you the answer. You have to actually try.
- The `notes.md` payoff is real: idioms, edge cases, and "I've been bitten by this" wisdom you wouldn't find by reading docs.

## Seeded tutorials

| Path                                         | Topic                                           |
|----------------------------------------------|-------------------------------------------------|
| `python/01-fastapi-dependencies/`            | FastAPI dependency injection, scopes, testability |
| `typescript/01-react-state-patterns/`        | `useState` vs `useReducer` vs derived state     |

## Authoring a new tutorial

1. Create the directory: `tutorials/<lang>/<NN-name>/`.
2. Write `README.md` — concept + what they'll learn.
3. Write a working `solution.{py,ts}` first (this is what you're aiming the user toward).
4. Copy it to `exercise.{py,ts}` and replace the meaningful lines with `# TUTOR: <hint>` markers.
5. Write `notes.md` with 3-5 power-user tricks that go *beyond* what the exercise teaches.

Aim for tutorials that take 20-40 minutes including discussion.
