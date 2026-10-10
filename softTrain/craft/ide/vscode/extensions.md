# VS Code — recommended extensions

For the stacks in this repo (Python + TypeScript). Install them once; they pay for themselves.

## Python

- **Python** (`ms-python.python`) — official; required for everything else.
- **Pylance** (`ms-python.vscode-pylance`) — fast type-aware language server. Strict mode in settings: `"python.analysis.typeCheckingMode": "basic"` (or `"strict"` if you're feeling brave).
- **Ruff** (`charliermarsh.ruff`) — linting + formatting in one. Replaces black / isort / flake8.
- **Python Test Explorer** — built into Python ext now; no extra install needed.

## TypeScript / JavaScript / React

- **ESLint** (`dbaeumer.vscode-eslint`) — official lint integration. Lint-on-save with `"editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }`.
- **Vitest** (`vitest.explorer`) — test runner explorer for Vitest.
- **ES7+ React/Redux/React-Native snippets** (`dsznajder.es7-react-js-snippets`) — fast component scaffolding. Use sparingly; the kind of repetition snippets save you from is also the kind worth practicing.
- **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`) — class-name autocomplete + hover info.

## Git

- **GitLens** (`eamodio.gitlens`) — line-level blame, annotations, history viewer. The `Toggle Git Blame Annotations` command is the killer feature.
- **Git Graph** (`mhutchie.git-graph`) — visual log; nicer than `git log --graph`.

## Docker

- **Docker** (`ms-azuretools.vscode-docker`) — Dockerfile syntax, container/image management, attach to running containers.

## General productivity

- **Error Lens** (`usernamehw.errorlens`) — inline error messages so you don't have to hover. Polarising — try it for a week.
- **Path Intellisense** (`christian-kohler.path-intellisense`) — autocompletes file paths in imports.
- **TODO Tree** (`gruntfuggly.todo-tree`) — collects all TODOs / FIXMEs / TUTORs in the workspace into a sidebar.
- **EditorConfig** (`editorconfig.editorconfig`) — respects `.editorconfig` files in repos.

## Themes (optional, but matter for fatigue)

- **Default Dark Modern** (built-in) is solid.
- **One Dark Pro** if you want more colour.
- **Solarized** if you prefer low-contrast light.

## How to install in bulk

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
# ...
```

Or commit a `.vscode/extensions.json` to your repos so VS Code suggests them automatically:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff"
  ]
}
```
