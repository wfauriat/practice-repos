# Lab 02 — interactive rebase

## Setup

```bash
bash craft/git/exercises/02-interactive-rebase/setup.sh
cd craft/git/_sandbox/02-interactive-rebase
```

## Scenario

You've been working on a `feature` branch, committing freely as you went — WIP saves,
typo fixes, a reminder note you forgot to remove. The history is honest but messy:

```
add auth section
wip
more auth stuff
add authz section (typo fix incoming)
fix typo in header
rbac notes
temp: reminder note, remove before merge
```

Before merging to `main`, your team expects clean, meaningful commits. Nobody wants
to see `wip` or `fix typo in header` in the permanent history.

Run `git log --oneline --all --graph` to see the current state.

## Goal

Rewrite the feature branch history into **exactly 3 commits**:

1. `feat: authentication notes` — the auth section + wip content + token detail, as one unit
2. `feat: authorization notes` — the authz section + typo fix + rbac, as one unit
3. *(the temp reminder should be gone entirely)*

`main` should then fast-forward to the cleaned-up `feature` tip.

## Hints (don't peek if you've never done this)

- `git rebase -i <base>` opens an editor listing your commits. You pick what to do with each one.
- The actions you'll need: `squash` (or `s`) folds a commit into the one above it; `drop` (or `d`) deletes a commit entirely; `reword` (or `r`) lets you rename a commit.
- Set your editor if needed: `GIT_EDITOR=nano git rebase -i ...`
- After cleaning history, use `git merge --ff-only feature` from `main` to advance the pointer.
