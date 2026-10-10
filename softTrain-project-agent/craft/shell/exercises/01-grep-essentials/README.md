# Exercise 01 — grep essentials

Goal: get fluent with `grep` flags that come up daily. Use `craft/shell/data/access.log` and `craft/shell/data/users.csv` as input.

```bash
LOG=craft/shell/data/access.log
USERS=craft/shell/data/users.csv
```

For each task: come up with a one-liner. Don't peek at `solution.md` until you've tried.

## Tasks

1. **Count of 5xx responses** in the log (a single number).
2. **Show all 5xx lines plus the line before each** (so you can see what request preceded the failure).
3. **Extract just the HTTP method + path** from each request line, in the form `GET /api/items`. (Hint: `grep -oE`.)
4. **List the unique IPs** that hit `/admin` paths.
5. **Count requests per status code**, sorted high to low. (You'll need `grep` + `awk` or `sort | uniq -c`. Either is fine.)
6. **Find users from the UK** in the CSV.
7. **Skip the CSV header** when listing names. (Hint: `grep -v` or `tail -n +2`.)
8. **Find log lines from the last 5 minutes of the log** (the timestamp range from `08:25` to `08:27`). Use a regex.
9. **Count POST requests that returned 5xx** — the same client retrying.
10. **List the kube-probe health-check noise** so you can `grep -v` it out for human-facing analysis.
