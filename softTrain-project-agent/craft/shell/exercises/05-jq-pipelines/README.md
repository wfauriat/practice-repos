# Exercise 05 — jq pipelines

Goal: learn to extract, transform, and aggregate JSON with `jq`. Use `craft/shell/data/events.json`.

```bash
DATA=craft/shell/data/events.json
```

## Tasks

1. **Print just the array of users** (with duplicates).
2. **Print the unique users**, sorted.
3. **Count of events**.
4. **Count events by type** (`event` field).
5. **All `page_view` events**, but only their `path` and `duration_ms` fields.
6. **Total page_view duration per user**, sorted descending.
7. **The single longest page view** — return the user, path, and duration.
8. **For each user, the path of their FIRST page view.**
9. **Users who visited both `/home` and `/pricing`.**
10. **Group events by user**, returning `{user, event_count, paths_visited}` for each.

## Hints

- `jq '.[]'` — iterate over an array.
- `jq 'group_by(.field)'` — group; result is an array of arrays.
- `jq '. | length'` — get a count.
- `jq -r` — raw output (strings without quotes).
