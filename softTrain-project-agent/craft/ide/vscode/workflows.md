# VS Code — workflows to internalize

These are end-to-end flows worth doing on muscle memory.

## 1. Rename a symbol across the project

1. Land on the symbol (don't worry about which usage — definition or call site, both work).
2. `F2`.
3. Type the new name, `Enter`.

VS Code uses the language server (Pylance / TS) to update every reference. Doesn't fall for false positives like a global find-replace would.

**When this fails**: the language server isn't running, or the symbol crosses runtime boundaries (e.g. a string in a config file). For those, fall back to `Ctrl+Shift+H` (search & replace across files).

## 2. Extract a function

1. Select the lines you want to extract.
2. `Ctrl+.` to open the refactor menu.
3. Pick "Extract function" / "Extract method".
4. Type the new function name.

Works in Python (with Pylance), TypeScript, JavaScript. Saves the dance of cut-paste-add-args.

## 3. Run the nearest test

Install the test extension for your language (Python: built-in via Pylance; TS: Vitest extension).

1. Land your cursor inside a test function.
2. Use the "Run Test" CodeLens that appears above the test, or `Ctrl+Shift+P` → "Run nearest test".

Faster feedback loop than running the whole suite. Combine with `--watch` mode for continuous feedback.

## 4. Debug a failing pytest

1. Set a breakpoint on the failing line (`F9`).
2. Open the "Run and Debug" sidebar (`Ctrl+Shift+D`).
3. "Debug Test" via the CodeLens.
4. Inspect locals, watch expressions, step.

The debugger is *much* better than `print(x); pytest -v` once you're used to it. `F10` step over, `F11` step into, `F5` continue.

## 5. Search across the workspace

- `Ctrl+Shift+F` — search.
- `Ctrl+Shift+H` — search and replace.
- Toggle regex (`.*`) and case-sensitive (`Aa`).
- "files to include" / "files to exclude" — narrow the search to `**/*.py` or away from `node_modules`.

For finding a function definition, prefer `Ctrl+T` (workspace symbol) over text search. For finding a string literal, text search is right.

## 6. `tasks.json` — wire your project's commands into VS Code

```jsonc
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "test",
      "type": "shell",
      "command": "pytest -v",
      "group": { "kind": "test", "isDefault": true },
      "presentation": { "reveal": "always", "panel": "dedicated" }
    },
    {
      "label": "lint",
      "type": "shell",
      "command": "ruff check . && ruff format --check ."
    }
  ]
}
```

Then `Ctrl+Shift+B` runs the default build task; `Ctrl+Shift+P` → "Run Task" lists them all.

## 7. `launch.json` — keep your debug configs in source control

```jsonc
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI dev",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest current file",
      "type": "debugpy",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

Then `F5` runs the selected config in the Debug sidebar.

## 8. Multi-root workspaces

If you're hopping between two projects (e.g. `ts-react-vite` and `ts-node-api` for full-stack work), open them as a *workspace*:

- `File → Add Folder to Workspace…`
- `File → Save Workspace As…` — produces a `.code-workspace` file.

Each folder gets its own LSP context, but you have one window for both. Search runs across both. Saves a lot of window-switching.

## 9. `Ctrl+Shift+P` — when in doubt

The command palette is the universal fallback. Forgot a keybinding? Type its name. Want to install an extension? "Extensions: Install". Want to change a setting? "Preferences: Open Settings (UI)".

If you can't remember the keybinding for *anything*, you can still drive the editor entirely from the palette.
