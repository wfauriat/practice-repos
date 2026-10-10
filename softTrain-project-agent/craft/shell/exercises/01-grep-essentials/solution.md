# Solution — grep essentials

```bash
LOG=craft/shell/data/access.log
USERS=craft/shell/data/users.csv
```

### 1. Count of 5xx responses

```bash
grep -cE ' 5[0-9]{2} ' "$LOG"
```

`-c` prints just the count. The leading/trailing space anchors the status field so you don't match bytes-sent that happen to start with `5`.

### 2. Show 5xx lines + the line before each

```bash
grep -B1 -E ' 5[0-9]{2} ' "$LOG"
```

`-B1` (before) shows 1 line of context before each match. `-A1` for after, `-C1` for both.

### 3. Extract method + path

```bash
grep -oE '"[A-Z]+ /[^ ]*' "$LOG" | tr -d '"'
```

`-o` prints only the matching part. `tr` removes the leading quote.

### 4. Unique IPs hitting /admin

```bash
grep '/admin' "$LOG" | awk '{print $1}' | sort -u
```

`awk '{print $1}'` is a common idiom — print the first whitespace-separated field.

### 5. Status code counts, sorted

```bash
awk '{print $9}' "$LOG" | sort | uniq -c | sort -rn
```

Slightly cheating with `awk`, but `grep` alone can't do counts. The pattern `sort | uniq -c | sort -rn` is muscle memory worth having.

### 6. UK users

```bash
grep ',UK,' "$USERS"
```

Anchoring with the surrounding commas avoids matching "UK" in someone's name.

### 7. Names without header

```bash
tail -n +2 "$USERS" | cut -d, -f2
```

Or with grep:

```bash
grep -v '^id,' "$USERS" | cut -d, -f2
```

### 8. Log lines from 08:25 — 08:27

```bash
grep -E ':08:2[567]:' "$LOG"
```

### 9. POST 5xx (probable retries)

```bash
grep -E '"POST [^"]*" 5[0-9]{2}' "$LOG"
```

You can see `192.0.2.10` retried `POST /api/items` 3 times in a row.

### 10. The kube-probe noise

```bash
grep 'kube-probe' "$LOG"
# Or, when analysing a real log, suppress it:
grep -v 'kube-probe' "$LOG"
```

## Power-user notes

- **Use `-E` (or `egrep`)** for regex with `+`, `?`, `|`. Without it, those are literal characters.
- **Use `-F` (`fgrep`)** when searching for a literal string with no regex. Faster and avoids accidental metacharacters.
- **`-l` lists matching files** instead of matching lines. Handy: `grep -lE 'foo' src/**/*.py | xargs $EDITOR`.
- **`-c` counts**, but **`grep -c '' file | head`** to count *lines* in a file is overkill; use `wc -l`.
- **`grep --color=always | less -R`** preserves colour through the pager.
- **`grep -P`** enables PCRE for fancy regex (lookbehinds, etc.). Use sparingly — it's a GNU extension that won't work everywhere.
- **`rg` (ripgrep)** is what you actually want for codebase-scale search. Same flags mostly, much faster, respects `.gitignore` by default.
