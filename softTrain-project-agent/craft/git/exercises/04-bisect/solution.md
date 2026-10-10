# Solution — git bisect

## Manual bisect

```bash
git bisect start
git bisect bad                # current HEAD (main) is broken
git bisect good $(git rev-list --max-parents=0 HEAD)   # first commit is the known good

# git checks out a commit halfway. Run the test:
bash test.sh && git bisect good || git bisect bad

# Repeat until git announces the first bad commit.

git bisect reset              # restore your previous HEAD
```

Expected result: commit `07: refactor calc — looks innocent, breaks behaviour`.

Run `git show <SHA>` on it: you'll see `return x * 2` → `return x + 2`. The "refactor" was a behaviour change.

## Automatic bisect with `git bisect run`

```bash
git bisect start
git bisect bad
git bisect good $(git rev-list --max-parents=0 HEAD)
git bisect run bash test.sh
git bisect reset
```

`git bisect run` checks out each candidate, runs the command, marks good/bad based on exit code, and announces the result. For long-running test suites this is the only sane option.

## Power-user notes

### Bisect with a hash range, not just `good`/`bad` aliases

```bash
git bisect start <bad> <good>
```

Cleaner than two separate calls. The first arg is bad, the second is good.

### Skip commits that won't build

Sometimes the bisect lands on a commit that doesn't compile / has unrelated breakage. Use:

```bash
git bisect skip
```

git will pick a different candidate.

### `git log --bisect`

While in the middle of a bisect, this shows only the commits still being considered. Helpful when you want to read the messages of candidates.

### Bisect needs a deterministic test

If your test has flaky failures, `bisect run` will mislead you. Wrap flaky tests in a retry loop:

```bash
git bisect run bash -c 'for i in 1 2 3; do bash test.sh && exit 0; done; exit 1'
```

### Why this is so much faster than reading the diff

12 commits is small enough to eyeball, but `bisect` finds the answer in `log2(12) ≈ 4` test runs. With 1000 commits it's `~10` test runs. The win compounds dramatically.

The discipline this builds: **make every commit testable on its own**. If you can't `bash test.sh` at any commit and get a meaningful pass/fail, bisect won't help you. This is the real reason to keep commits atomic.

### Bisect with file-level pickiness

```bash
git bisect start -- src/calc.py
```

git will only consider commits that touched `src/calc.py`. Rarely needed, but very useful when 90% of the noise is in unrelated files.
