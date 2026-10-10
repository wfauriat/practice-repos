# Lab 03 — conflict resolution

## Setup

```bash
bash craft/git/exercises/03-conflict-resolution/setup.sh
cd craft/git/_sandbox/03-conflict-resolution
```

## Scenario

Two engineers edited `config.md` at the same time on different branches.

- **`feature`** increased `timeout` to 60 for a slow upstream service, then added a review sign-off.
- **`main`** tightened `timeout` to 10 and bumped `retries` to 5 for performance reasons.

Both touched the same line (`timeout`). When you rebase `feature` onto `main`, git won't know which value to keep — it'll stop and ask you to decide.

Run `git log --oneline --all --graph` and `git diff main..feature` to understand the divergence before acting.

## Goal

End up with a clean linear history on `main` that includes both branches' intent:
- `timeout: 60` (the slow upstream needs it — feature's reasoning wins)
- `retries: 5` (main's performance improvement is valid)
- The review sign-off commit from feature

No merge commits.

## Hints

- `git rebase main` will pause with a conflict. This is normal — not a failure.
- `git status` tells you which files are conflicted.
- Open the conflicted file. Look for `<<<<<<<`, `=======`, `>>>>>>>` markers.
- Edit the file to the desired final state, remove the markers.
- `git add <file>` to mark it resolved.
- `git rebase --continue` to resume.
- If you want to bail out safely at any point: `git rebase --abort`.
