# Solution — conflict resolution

```bash
# 1. Start the rebase — it will pause on the first conflicting commit.
git switch feature
git rebase main
```

Git pauses with a message like:
```
CONFLICT (content): Merge conflict in config.md
error: could not apply <hash>... feat: increase timeout for slow upstream
```

```bash
# 2. Inspect the conflict.
git status           # shows config.md as "both modified"
cat config.md        # shows the conflict markers
```

The file will look like:
```
# Service config

<<<<<<< HEAD
timeout: 10
retries: 5
=======
timeout: 60
retries: 3
>>>>>>> <hash>... feat: increase timeout for slow upstream
log_level: info
```

- `<<<<<<< HEAD` to `=======` — what main has (the new base)
- `=======` to `>>>>>>>` — what your feature commit had

```bash
# 3. Edit config.md to the desired final state — keep both intentions:
```

```
# Service config

timeout: 60
retries: 5
log_level: info
```

Remove all `<<<<<<<`, `=======`, `>>>>>>>` markers.

```bash
# 4. Mark as resolved and continue.
git add config.md
git rebase --continue    # git may open an editor for the commit message — save as-is
```

Git then replays the second commit (`docs: add review sign-off`) cleanly — no conflict there.

```bash
# 5. Fast-forward main.
git switch main
git merge --ff-only feature

# 6. Verify.
git lg
cat config.md
```

Final history should be a straight line:
```
init → perf: tighten timeout → feat: increase timeout → docs: review sign-off
```

## Power-user notes

### `git mergetool`
Instead of editing conflict markers by hand, `git mergetool` opens a three-panel
diff (ours / base / theirs) in a merge tool like `vimdiff`, `meld`, or VS Code.

```bash
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
git mergetool
```

### Multiple conflicts across multiple commits
A rebase replays commits one by one. If 3 commits each conflict, git pauses 3 times.
Each round: resolve → `git add` → `git rebase --continue`.

### `git rebase --skip`
If a commit becomes empty after resolving (its changes are already in main), use
`git rebase --skip` instead of `--continue` to drop it silently.

### Reading conflict markers fast
```
<<<<<<< HEAD          ← "ours" = the new base (main's tip)
...their version...
=======
...our version...
>>>>>>> <hash>        ← "theirs" = the commit being replayed (your feature commit)
```

Counter-intuitive: during a rebase, "ours" is main (the base you're rebasing onto),
not your feature branch. The labels flip compared to a merge. Keep this in mind when
deciding which side to keep.
