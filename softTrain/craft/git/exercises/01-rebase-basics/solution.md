# Solution — rebase basics

```bash
# 1. From the feature branch, rebase onto the current main.
git switch feature
git rebase main

# (If there were conflicts, you'd resolve them, `git add`, then `git rebase --continue`.
# This lab has no conflicts because main and feature touched different files.)

# 2. Now feature points to the linearised history. Fast-forward main to it.
git switch main
git merge --ff-only feature

# 3. (Optional) delete the feature branch.
git branch -d feature
```

Verify with `git log --oneline --all --graph`. You should see a single line.

## Power-user notes

### Keep your local work safe with `--autostash`

If you have uncommitted changes when you start a rebase:

```bash
git rebase --autostash main
```

git stashes them, rebases, and pops the stash. No "fatal: cannot rebase: you have unstaged changes" dance.

### `git switch -c <new>` instead of `git checkout -b`

`git switch` is the modern, lower-cognitive-load command for branch operations. `git checkout` does too many things; `git switch` and `git restore` split them.

### `git rebase --update-refs`

If you have stacked branches (feature → feature-2 built on top), this option updates all the dependent branches in one go instead of you re-pointing each manually.

### Why "rebase + fast-forward" instead of "merge --no-ff"?

Two schools of thought:

- **Linear history** ("rebase + ff") is easier to read with `git log`. `git bisect` works cleanly because every commit is a real, sequential point in the history.
- **Merge commits preserved** ("merge --no-ff") keep the *grouping* of feature work explicit. You can see "this batch of commits was the foo PR".

Many teams use squash-merges as a third compromise: one commit per PR on `main`, with the original feature commits visible only on the (eventually-deleted) branch.

There's no universal right answer; pick a convention with the team and stick to it.

### When NOT to rebase

**Never rebase commits that have been pushed to a shared branch.** Rebase rewrites SHAs, which means anyone else who pulled the old SHAs now has a diverged history. The rule of thumb: rebase your own un-pushed work freely; never force-push to `main`/`master`/shared branches.

`git config --global pull.rebase true` makes `git pull` rebase your local work onto `origin/main` instead of merging — usually the cleaner default.
