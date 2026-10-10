# projects/

Multi-day mini-projects: deliberate, end-to-end work where the value is the *journey*, not just the artifact.

## How a project differs from a kata

| Kata                                     | Project                                          |
|------------------------------------------|--------------------------------------------------|
| ~30 minutes, one source file             | Multi-day, multi-file                            |
| Re-solved repeatedly                     | Solved once (or shipped once), then archived     |
| Goal: muscle memory                      | Goal: end-to-end practice + a real artifact      |
| Tests provided                           | You design what "done" looks like                |

## Workflow

```bash
tools/new-project.sh my-thing
$EDITOR projects/my-thing/README.md   # fill in goal + learning aims
# ...hack...
# When done, write the retrospective and move it:
mv projects/my-thing projects/_archive/
```

The `README.md` template has fields for: **Goal**, **Learning aims**, **Stretch goals**, **Working notes** (append-only), and **Retrospective**. The retro is where the real value is — fill it in honestly when you ship (or abandon).

## Backlog of project ideas

Pull from here when you don't have your own idea. None of these are urgent — they're prompts.

### Backend / API
- **URL shortener** — counter-pressure, db design, slug collisions. Use `python-fastapi-crud` as the start.
- **Personal habit tracker** — same scaffold; learning aims are about modelling streaks and aggregation queries.
- **RSS reader** — fetch feeds on a schedule, store, deduplicate. Practices async + scheduling.

### CLI tools
- **`gh-prs`** — list your open GitHub PRs across orgs. Practices Typer + auth + caching.
- **Project bootstrapper** — wraps `tools/from-scaffold.sh` with interactive prompts (clone target, GitHub remote, etc.).
- **`logtail-tui`** — a small TUI over `tail -f` with filter/highlight. Practices terminal control.

### Frontend
- **Markdown notes app** — local-only, IndexedDB. Practices controlled forms + `useReducer`.
- **Pomodoro timer** — stretches into Web Workers + Notification API.
- **Github contribution heatmap clone** — practices SVG, layout, data shaping.

### Full-stack
- **Bookmark manager** — `ts-react-vite` + `ts-node-api` paired via the included `compose.yml`. Add tags, search, import/export.
- **Tiny status page** — periodic health checks of a list of URLs, history per service.

### Data
- **Bike share EDA** — pick a public dataset (Capital Bikeshare, NYC Citi Bike), do a real EDA in the notebook scaffold. Make it reproducible.
- **Personal expense classifier** — small dataset, simple classifier, write up the bias/error analysis.

### Craft / DX
- **Dotfiles repo with bootstrap script** — your own configs, idempotent install. Practices shell + git submodules.
- **Self-rebuilding cheatsheet** — a markdown cheatsheet that auto-extracts from your `craft/tricks/*.md` history.

## Picking a project

Pick something **you'd use**. Toy projects are demotivating. Pick something **smaller than feels exciting** — finishing teaches you more than starting big.

State the **learning aims** explicitly before you start. If you can't articulate what you're trying to learn, the project is too vague.
