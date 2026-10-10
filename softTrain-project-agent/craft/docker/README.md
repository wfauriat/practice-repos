# craft/docker/ — containers + the shared sandbox image

Two purposes in one directory:

1. **Interactive labs** to build Docker fluency. Same lab protocol as `craft/git/` and `craft/shell/`.
2. **A sandbox base image** (`craft/docker/sandbox/Dockerfile`) used by `tools/sandbox.sh` to run *risky* commands in isolation. The image has bash, git, jq, awk, sed, python, node, and the standard GNU coreutils.

## Sandbox image — when to use it

Whenever you'd hesitate to run a command on your host:

```bash
# Practice destructive git operations safely
tools/sandbox.sh bash -c 'git init && echo x > a.txt && git add . && git commit -m x && git reset --hard HEAD~99'

# rm -rf experiments
tools/sandbox.sh bash -c 'mkdir -p /tmp/play && rm -rf /tmp/play'

# Untrusted scripts (someone's gist, a CI script you're auditing)
tools/sandbox.sh bash some-script.sh
```

The container is fresh on every run; mutations to `/work` are visible on the host (use carefully), but mutations to `/tmp`, `/etc`, etc. die with the container.

## Seeded labs

| #   | Topic         | What you practice                                              |
|-----|---------------|----------------------------------------------------------------|
| 01  | first-image   | Write a working Dockerfile for a small Python app              |
| 02  | multi-stage   | Slim the image: separate build deps from runtime               |

(Future labs: 03 layer-caching, 04 compose-networking, 05 debug-images.)

## Lab protocol recap

```bash
bash craft/docker/exercises/NN-name/setup.sh
# Read README.md, attempt the task in the sandbox dir,
# compare with solution.md once you have it working.
```
