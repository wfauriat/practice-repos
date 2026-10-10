# Solution — jq pipelines

```bash
DATA=craft/shell/data/events.json
```

### 1. Array of users

```bash
jq '[.[] | .user]' "$DATA"
```

Or, more idiomatically, `jq '[.[].user]'` or `jq 'map(.user)'`.

### 2. Unique users, sorted

```bash
jq 'map(.user) | unique' "$DATA"
```

### 3. Count of events

```bash
jq 'length' "$DATA"
```

### 4. Event counts by type

```bash
jq 'group_by(.event) | map({event: .[0].event, count: length})' "$DATA"
```

This idiom — `group_by(.x) | map({x: .[0].x, count: length})` — is the bread and butter of jq aggregation.

### 5. page_view path + duration

```bash
jq '[.[] | select(.event == "page_view") | {path, duration_ms}]' "$DATA"
```

`select()` filters; `{path, duration_ms}` shorthands `{path: .path, duration_ms: .duration_ms}`.

### 6. Total page_view duration per user, sorted desc

```bash
jq '
  [.[] | select(.event == "page_view")]
  | group_by(.user)
  | map({user: .[0].user, total_ms: (map(.duration_ms) | add)})
  | sort_by(-.total_ms)
' "$DATA"
```

`add` sums an array of numbers. The negation in `sort_by(-.total_ms)` is the standard descending trick.

### 7. The longest page view

```bash
jq '[.[] | select(.event == "page_view")] | max_by(.duration_ms) | {user, path, duration_ms}' "$DATA"
```

### 8. First page_view path per user

```bash
jq '
  [.[] | select(.event == "page_view")]
  | group_by(.user)
  | map({user: .[0].user, first_path: .[0].path})
' "$DATA"
```

(Relies on the array being already in chronological order — true here.)

### 9. Users who visited both /home and /pricing

```bash
jq '
  [.[] | select(.event == "page_view") | {user, path}]
  | group_by(.user)
  | map(select(any(.[]; .path == "/home") and any(.[]; .path == "/pricing")) | .[0].user)
' "$DATA"
```

A bit verbose. Easier to read in two steps with shell:

```bash
HOME=$(jq -r '.[] | select(.path == "/home" and .event == "page_view") | .user' "$DATA" | sort -u)
PRICING=$(jq -r '.[] | select(.path == "/pricing" and .event == "page_view") | .user' "$DATA" | sort -u)
comm -12 <(echo "$HOME") <(echo "$PRICING")
```

### 10. Per-user summary

```bash
jq '
  group_by(.user)
  | map({
      user: .[0].user,
      event_count: length,
      paths_visited: ([.[] | .path] | unique)
    })
' "$DATA"
```

## Power-user notes

- **`-r` for raw output** when you're piping to other shell tools. Without it, strings come out with quotes.
- **`-c` for compact output** (one JSON value per line) when you're piping to `xargs` or another `jq`.
- **`@csv` and `@tsv`** as filters convert arrays-of-arrays to CSV/TSV. Killer combo: `jq -r '.[] | [.user, .path] | @tsv'`.
- **`--arg name value` and `--argjson name value`** pass shell vars into jq cleanly. `--arg` for strings, `--argjson` for parsed JSON (numbers, bools, objects).
- **`paths`** lists every path in a JSON document — `jq 'paths' file.json` is the fastest way to learn an unknown JSON schema.
- **`add` works on arrays of arrays too** — flattening one level: `jq '. | add'` on `[[1,2],[3,4]]` → `[1,2,3,4]`.
- **`reduce`** is the escape hatch for everything `group_by` can't do: `reduce .[] as $x ({}; .[$x.user] += 1)`.
- **`gron`** (separate tool) flattens JSON into greppable lines: `gron file.json | grep something`. Faster to find what you need before reaching for jq.
