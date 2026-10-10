# Solution — interactive rebase

```bash
# 1. From the feature branch, open the interactive rebase editor.
#    HEAD~7 = the 7 commits on the branch (or use the base commit hash).
git switch feature
git rebase -i HEAD~7
```

The editor opens with a list like:

```
pick <hash> add auth section
pick <hash> wip
pick <hash> more auth stuff
pick <hash> add authz section (typo fix incoming)
pick <hash> fix typo in header
pick <hash> rbac notes
pick <hash> temp: reminder note, remove before merge
```

Edit it to:

```
reword <hash> add auth section
squash <hash> wip
squash <hash> more auth stuff
reword <hash> add authz section (typo fix incoming)
squash <hash> fix typo in header
squash <hash> rbac notes
drop   <hash> temp: reminder note, remove before merge
```

Git will pause twice to let you write the final commit messages:
- First pause: write `feat: authentication notes`
- Second pause: write `feat: authorization notes`

```bash
# 2. Fast-forward main to the cleaned tip.
git switch main
git merge --ff-only feature

# 3. Verify — should show exactly 3 commits above the base.
git log --oneline --all --graph
```

## Power-user notes

### `fixup` instead of `squash`
`squash` opens the editor so you can write a combined message.
`fixup` (or `f`) silently discards the folded commit's message — faster when the
commit being folded is noise (e.g. "wip", "fix typo").

### `--fixup` + `--autosquash`
Instead of editing the rebase todo list by hand, you can flag cleanup commits at
creation time:

```bash
git commit --fixup <hash-of-commit-to-fix>
# later:
git rebase -i --autosquash HEAD~N
```

Git pre-arranges the todo list for you — `fixup!` commits are automatically placed
below their target and marked `fixup`. Saves manual reordering.

### Aborting safely
If you make a mess inside an interactive rebase:

```bash
git rebase --abort    # returns to the state before you started
```

### `git reflog` as a safety net
Rebase rewrites history but the old commits aren't deleted immediately. If you finish
and realise you squashed the wrong things:

```bash
git reflog            # find the hash of the branch tip before the rebase
git reset --hard <that-hash>   # restore it
```

You have a window of ~30 days (until `git gc`) to recover this way.
