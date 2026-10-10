# craft/git/ — interactive git labs

Sandbox-based drills for the git operations you should know cold.

## How to run a lab

```bash
bash craft/git/exercises/01-rebase-basics/setup.sh
cd craft/git/_sandbox/01-rebase-basics
# ...do the exercise...
```

`_sandbox/` is gitignored — feel free to nuke it any time. Re-run `setup.sh` to get a fresh copy.

Or just say to Claude: *"let's do git lab 1"* and Claude will follow the lab protocol from `craft/README.md`.

## Seeded labs

| #   | Topic                          | What you practice                                              |
|-----|--------------------------------|----------------------------------------------------------------|
| 01  | rebase-basics                  | Linearise a feature branch onto an updated `main`              |
| 04  | bisect                         | Binary-search a regression                                     |

(More labs to seed: 02 interactive-rebase, 03 conflict-resolution, 05 reflog-recovery, 06 cherry-pick, 07 stash-workflows, 08 fixup-and-autosquash. Add them as you progress through the curriculum.)
