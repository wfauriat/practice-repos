# craft/shell/ — terminal fluency drills

Drills for `grep`, `find`, `awk`, `sed`, `jq`, and the pipeline glue. Targets **bash + GNU coreutils** on Linux.

## How to run a drill

Each exercise has a `README.md` with a list of tasks against fixtures in `craft/shell/data/`. Try each task in your shell; compare with `solution.md` after.

Or say to Claude: *"let's drill grep"* / *"let's do shell exercise 5"* and Claude will follow the lab protocol.

## Sample data (`craft/shell/data/`)

| File          | What it is                                       |
|---------------|--------------------------------------------------|
| `access.log`  | Synthetic nginx-style access log (~30 lines)     |
| `users.csv`   | Tiny CSV: id, name, email, country, signup_date  |
| `events.json` | JSON array of analytics events                   |

## Seeded exercises

| #  | Topic            | Tools           |
|----|------------------|-----------------|
| 01 | grep-essentials  | `grep -E`, `-A/-B/-C`, `-o`, `-l`, `-c` |
| 05 | jq-pipelines     | `jq` filters, maps, group-by, joins      |

(More to add later: 02 find-and-xargs, 03 awk-basics, 04 sed-substitutions, 06 piping-and-process-substitution.)
