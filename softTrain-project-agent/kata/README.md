# kata/

Short drills you re-solve repeatedly to build muscle memory. Each kata is a single source file: the problem statement is in the docstring/comment header, tests are at the bottom, the solution body is missing.

## Convention

```
kata/<lang>/<topic>/<name>.{py,ts}        # the prompt — solution is missing
kata/<lang>/_solutions/<topic>/<name>.{py,ts}  # the canonical solution
```

When you drill a kata you've done before, consider deleting your previous attempt first so you face the blank file fresh.

## Workflow

```bash
# Stamp a new kata
tools/new-kata.sh python strings palindrome

# Solve it
$EDITOR kata/python/strings/palindrome.py

# Run tests
pytest kata/python/strings/palindrome.py
# (or `vitest run kata/typescript/...` for TS)

# Compare with the canonical
diff -u kata/python/{,_solutions/}strings/palindrome.py
```

## Seed katas

### Python (`kata/python/`)
- `strings/reverse_words.py` — reverse each word in a string but preserve word order
- `collections/group_by.py` — implement a generic `group_by(items, key)` returning `dict[K, list[V]]`
- `async/parallel_fetch.py` — fetch a list of URLs with bounded concurrency using `asyncio`

### TypeScript (`kata/typescript/`)
- `arrays/chunk.ts` — split an array into chunks of size `n`
- `types/discriminated-unions.ts` — exhaustive `switch` on a discriminated union, with `never` for safety
- `async/promise-pool.ts` — run an array of async tasks with bounded concurrency

## Tips

- **Drill the same kata multiple times**, not for the answer (you remember it) — for the *feel* of typing it. The goal is for "group by" to be a 30-second reflex, not a 5-minute think.
- **When you drill a familiar kata, set a timer.** Watch your time go down across sessions.
- **If you keep reaching for the solution, the gap to the prompt is too large.** Add a smaller kata one step before it.
