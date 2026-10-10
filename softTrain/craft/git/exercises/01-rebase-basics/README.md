# Lab 01 — rebase basics

## Setup

```bash
bash craft/git/exercises/01-rebase-basics/setup.sh
cd craft/git/_sandbox/01-rebase-basics
```

## Scenario

You're on a `feature` branch. You started it 3 commits ago, when `main` was at the older commit "shared base". Since then, **`main` has moved forward** with two unrelated commits. Your team prefers a **linear history** on `main`, so a merge is not an option.

Run `git log --oneline --all --graph` to see the divergence.

## Goal

End up with `main` containing all the work in `feature` as **the most recent commits**, in a linear sequence — as if `feature` had been branched off the latest `main`. No merge commits.

## Hints (don't peek if you've never done this)

- Look at `git rebase` and its `--onto` option (you may not need `--onto` for this one).
- After the rebase, you'll need to update `main` itself to point to the new commits.
- The "fast-forward" merge is your friend at the end.
