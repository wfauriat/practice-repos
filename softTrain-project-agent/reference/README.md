# reference/

Pure cheatsheets — fast lookup, no drills, no narrative.

Distinct from `craft/` (which is *practice*) and `lectures/` (which is *narrative*). This is "I can't quite remember the syntax for X" material.

## Layout

```
reference/
├── python/
├── typescript/
├── sql/
└── regex/
```

Add new cheatsheets as `<area>/<topic>.md`. Aim for one screen per cheatsheet — when it gets longer than that, it's becoming a tutorial and should move.

## Style guide

- **Examples first, prose second.** A code block beats a paragraph of explanation.
- **Group by task, not by feature.** "How do I X?" headings, not "The `foo` operator."
- **One concrete tip per line where possible.** Easy to skim.
- **Link out to canonical docs.** This isn't trying to replace the official reference.

## Seeded

- [`python/regex.md`](./python/regex.md)
- [`sql/joins.md`](./sql/joins.md)
