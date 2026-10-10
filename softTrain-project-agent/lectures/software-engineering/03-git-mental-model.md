# Git mental model

## Abstract

Git is not a tool for saving files. It is a content-addressable object database with a thin layer of branch pointers on top. Every confusing git behaviour — detached HEAD, rebase rewriting history, fast-forward vs. merge commit — becomes obvious once you see the underlying data model. This lecture builds that model from the ground up.

## Motivation

Most developers learn git as a set of commands: `add`, `commit`, `push`, `pull`, `merge`. This works until it doesn't. When a rebase goes wrong, when HEAD detaches unexpectedly, when `git pull` creates a merge commit nobody wanted, the command-level mental model offers no help. You poke randomly until it works — or you blow away the branch and start over.

The data model takes thirty minutes to learn. It explains every command in the tool, makes error messages readable, and lets you reason your way out of any state rather than guessing. It is the highest-return investment in the git curriculum.

## Core concepts

### The object database

Git stores everything in `.git/objects/`. There are four object types. Each is identified by the SHA-1 hash of its contents — the hash *is* the identity.

**Blob** — the contents of a single file at a single point in time. No filename, no path, just bytes.

**Tree** — a directory listing: names, modes, and pointers to blobs (files) or other trees (subdirectories). A tree is a snapshot of a directory.

**Commit** — the central object. Contains:
- a pointer to one tree (the root snapshot for this commit)
- a pointer to one or more parent commits (zero for the first commit)
- author, committer, timestamp, message

**Tag** — a named pointer to a commit, optionally with a message and signature. Not covered further here.

The key insight: **git never stores diffs**. Every commit is a full snapshot of the entire repository at that moment. Diffs are computed on the fly by comparing two snapshots. This is the opposite of what most people assume, and it explains why `git log -p` and `git diff` are fast regardless of history length.

### Commits form a DAG

Because each commit points to its parent(s), the commit history is a Directed Acyclic Graph — a chain with possible branches and merges:

```
A ← B ← C ← D      ← main
              ↑
              E ← F  ← feature
```

Arrows point *backward* (each commit knows its parent, not its children). This matters: git can traverse history by following parent pointers, but it cannot traverse forward without extra bookkeeping.

### Refs: branches, tags, HEAD

A **branch** is nothing more than a file in `.git/refs/heads/` containing a single 40-character SHA-1. That's it. `main` is a file containing the hash of the most recent commit on main.

When you make a new commit, git:
1. Creates the commit object
2. Updates the branch file to point to the new commit hash

A branch is a movable pointer. It costs nothing. Creating a branch is writing 40 bytes to disk.

**HEAD** is a special ref stored in `.git/HEAD`. Normally it contains the *name* of a branch (`ref: refs/heads/main`), not a hash. HEAD is how git knows which branch to advance when you commit.

**Detached HEAD** occurs when HEAD contains a raw hash instead of a branch name. Git is pointing directly at a commit. If you commit in this state, the new commit has no branch tracking it — it becomes orphaned the moment you switch away.

```
# Normal state
HEAD → main → abc1234

# Detached HEAD
HEAD → abc1234  (no branch involved)
```

### The three areas

Git tracks changes across three areas:

```
Working directory  →  Staging area (index)  →  Repository (.git/objects)
                   git add                   git commit
```

**Working directory** — your actual files on disk. Git knows what they look like but doesn't track them until you act.

**Staging area (index)** — a prepared snapshot of what the *next* commit will look like. `git add` copies file state into the index. The index can hold a different version of a file than both the working directory and the last commit simultaneously.

**Repository** — the object database. `git commit` takes the current index and permanently stores it as a new commit object.

This three-way split is why you can `git add -p` to stage only part of a file, or why `git diff` (working vs. index) and `git diff --cached` (index vs. last commit) show different things.

### Rebase vs. merge: two ways to integrate branches

Given this state:

```
A ← B ← C          ← main
    ↑
    D ← E           ← feature
```

**Merge** creates a new commit with two parents:

```
A ← B ← C ← M      ← main
    ↑        ↑
    D ← E ────
```

`M` is a merge commit. The original commits `D` and `E` are unchanged (same hashes). History is preserved exactly as it happened. The graph has a fork and a join.

**Rebase** replays feature's commits on top of main's tip:

```
A ← B ← C ← D' ← E'    ← feature (then fast-forward main)
```

`D'` and `E'` are *new commits* — same diffs as `D` and `E`, but different parents, different hashes. The original `D` and `E` become orphaned. History looks like feature was always built on top of the latest main.

Neither is universally correct. The choice is about what story you want the history to tell.

### Fast-forward

When the target branch is a direct ancestor of the source, a merge requires no new commit — git just slides the branch label forward:

```
Before:  A ← B ← C    ← main
                  ↑
                  D ← E  ← feature

After:   A ← B ← C ← D ← E
                          ↑  ↑
                        main  feature
```

Fast-forward is why "rebase then merge" produces a clean linear history with no merge commits.

`git merge --ff-only` enforces this: it refuses to create a merge commit, erroring out if a fast-forward is not possible. A useful safety rail.

## Tradeoffs / counterpoints

### Rebase rewrites history — when does that matter?

Rebase is safe on commits that exist only on your local machine. Once you push and someone else pulls, those commits are shared. Rebasing shared commits creates divergent histories: your rewritten `D'` and their original `D` are different objects. The next `git pull` produces a confusing merge, or requires a force push that overwrites their copy.

**Rule:** rebase local, unshared work freely. Never rebase commits that have been pushed to a shared branch.

The corollary: if your team uses `git pull --rebase` (or `git config pull.rebase true`), your local commits are rebased onto the remote on every pull — which is usually cleaner than the default merge pull. But it means you should understand rebase before turning this on.

### Merge commits as documentation

The case for merge commits is not just "it's easier." A merge commit records *that a batch of work landed as a unit*, with a named branch, at a specific moment. Tools like `git log --merges` and `git bisect` can use this structure. In a busy repository, a linear history of 500 individual commits is harder to scan than 50 merge commits each grouping a feature.

The squash-merge is a third option: one commit per feature on main (like rebase), but the feature's internal commits are discarded entirely (like merge). Clean main history, no rewrite of feature commits, but you lose granularity. GitHub's "Squash and merge" button does this.

### The staging area is a feature, not friction

New users often treat `git add` as an annoying step between editing and committing. It is actually one of git's most powerful design choices. It lets you:

- Commit part of your changes while leaving others in progress
- Craft a commit that is logically clean, even if you wrote the code messily
- Review exactly what will land before it lands (`git diff --cached`)

`git add -p` (patch mode) lets you stage individual hunks within a file. This is the professional way to work: write freely, commit thoughtfully.

### SHA-1 is not a security guarantee

Git uses SHA-1 to identify objects, but SHA-1 is cryptographically broken. In practice, git's security model does not rely on SHA-1 collision resistance — it relies on the *social* guarantee that commits are signed by known authors (GPG signing). The hash is an integrity check, not an authentication mechanism. GitHub and GitLab both support SHA-256 repositories, but migration is slow.

## Further reading

- **Pro Git** by Chacon & Straub (free at git-scm.com) — Chapter 10 "Git Internals" is the canonical deep-dive on the object model. Chapters 3 and 7 cover branching and rewriting history.
- **`git cat-file -p <hash>`** — run this on any object in `.git/objects/` to read its raw contents. Five minutes of exploration teaches more than an hour of reading.
- **gitvisualizer.com** and **learngitbranching.js.org** — interactive visualisations of the DAG model. Useful for building intuition quickly.

## Discussion prompts

1. You and a colleague both push to `feature`. You then run `git rebase main` and force-push. Your colleague does `git pull` and gets a mess. Walk through exactly what happened in terms of object hashes and ref pointers — why did the histories diverge?

2. `git reset --hard HEAD~3` and `git rebase -i HEAD~3` followed by dropping all three commits produce the same working tree. Are they equivalent? What's different, and when would you prefer one over the other?

3. A teammate argues that squash-merges are strictly better than rebase because "you get a clean main without rewriting history." Is this claim accurate? What does squash-merge actually do to the feature branch's commits?

4. You run `git diff` and see nothing. You run `git diff HEAD` and see changes. What does this tell you about the state of your staging area, and how did you get there?

5. The staging area (index) is described as "a prepared snapshot of the next commit." Can the index ever contain a state that doesn't correspond to any commit and can't be produced by any combination of your working directory files? If so, how?
