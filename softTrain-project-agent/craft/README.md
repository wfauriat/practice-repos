# craft/

Practice on the **non-code** parts of being a software engineer: git, the editor, the shell, Docker. Plus a daily-trick journal to capture the small wins.

## Sub-tracks

| Track            | What it covers                                         |
|------------------|--------------------------------------------------------|
| `git/`           | Interactive labs in throwaway sandbox repos            |
| `ide/`           | VS Code keybindings, snippets, workflows               |
| `shell/`         | `grep`, `find`, `awk`, `sed`, `jq` drills against fixtures |
| `docker/`        | Dockerfile authoring + a shared sandbox runtime image  |
| `tricks/`        | Dated journal of small wins                            |

## The lab protocol (shared by `git/`, `shell/`, `docker/`)

Each lab is a directory with this shape:

```
craft/<topic>/exercises/NN-name/
├── README.md     # The goal in plain English
├── setup.sh      # Builds a fresh sandbox / fixture for this exercise
└── solution.md   # Canonical answer + power-user notes (read AFTER)
```

### How a session goes

1. **You:** "let's do git lab 1" / "let's drill awk" / "let's do docker lab 2".
2. **Claude:** runs `bash craft/<topic>/exercises/NN-name/setup.sh` to (re)build the sandbox.
3. **Claude:** states the lab's *goal* in plain English. Does **not** show you the commands.
4. **You:** attempt. Claude watches state with read-only inspections (`git status`, `ls`, `cat`) between your tries.
5. **Once you succeed:** Claude reveals `solution.md` plus the power-user tips for that topic.

The `setup.sh` scripts are deliberately re-runnable — feel free to `bash setup.sh` again any time you want a fresh sandbox.

## Why this format

Reading docs about `git bisect` doesn't teach you `git bisect`. Doing it on a real (toy) regression does. Same with `awk`. Same with multi-stage Dockerfiles. The labs are the cheapest way to put your fingers on the keys without endangering a real repo.
