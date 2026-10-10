# VS Code — the 20 keybindings to know cold

Linux defaults. (On macOS, swap `Ctrl` for `Cmd` where indicated.)

> **Drill format**: each shortcut has a tiny task you should be able to do in one fluent motion. If you have to look at the menu, you don't know it yet.

## Tier 1 — every minute, every day

| #   | Shortcut          | What                                  | Drill                                                                         |
|-----|-------------------|---------------------------------------|-------------------------------------------------------------------------------|
| 1   | `Ctrl+Shift+P`    | Command palette                       | Open palette, type "format", run "Format Document". Don't reach for the mouse. |
| 2   | `Ctrl+P`          | Quick file open                       | Open `kata/python/strings/reverse_words.py` in two keystrokes (after `Ctrl+P`). |
| 3   | `Ctrl+Shift+O`    | Quick symbol jump (current file)      | Open a multi-fn file. Jump to the third function without scrolling.            |
| 4   | `Ctrl+T`          | Workspace symbol jump                 | Jump to `add_task` from any file. (Requires LSP to be running.)               |
| 5   | `Ctrl+S`          | Save                                  | Save reflexively. (Combine with format-on-save in settings.)                  |
| 6   | `Ctrl+/`          | Toggle line comment                   | Comment three lines, uncomment them, all from the keyboard.                   |
| 7   | `Alt+↑` / `Alt+↓` | Move line up / down                   | Reorder a 5-line block without selecting it.                                  |
| 8   | `Ctrl+D`          | Add next occurrence to multi-cursor   | Rename `foo` to `bar` 4 times in a paragraph. No find-replace.                |

## Tier 2 — several times a day

| #   | Shortcut                     | What                              | Drill                                                                    |
|-----|------------------------------|-----------------------------------|--------------------------------------------------------------------------|
| 9   | `F12`                        | Go to definition                  | From a call site, jump to the definition. `Alt+←` to come back.          |
| 10  | `Shift+F12`                  | Find all references               | Refactor: see who's calling a function before renaming it.               |
| 11  | `F2`                         | Rename symbol (project-wide)      | Rename a function across the whole project, not just current file.       |
| 12  | `Ctrl+.`                     | Quick fix / refactor menu         | Land on a TypeScript red squiggle, hit `Ctrl+.`, accept the fix.         |
| 13  | `` Ctrl+` ``                 | Toggle integrated terminal        | Open / close the terminal without the mouse.                             |
| 14  | `Ctrl+B`                     | Toggle sidebar                    | Hide for focus, show to navigate.                                         |
| 15  | `Ctrl+\`                     | Split editor                      | Open the same file side-by-side; useful for header/impl style work.      |

## Tier 3 — power moves

| #   | Shortcut                          | What                                      | Drill                                                              |
|-----|-----------------------------------|-------------------------------------------|---------------------------------------------------------------------|
| 16  | `Ctrl+K Z`                        | Zen mode                                  | Hide everything but the editor. `Esc Esc` to leave.                |
| 17  | `Ctrl+Shift+\`                    | Jump to matching bracket                  | Long function — jump from `{` to its closing `}` without scrolling. |
| 18  | `Alt+Click`                       | Add cursor at click position              | Place 3 cursors on different lines, type once, edit all 3.          |
| 19  | `Ctrl+G`                          | Go to line                                | Jump to a stack trace line: `Ctrl+G 142 Enter`.                    |
| 20  | `F5` / `F9` / `F10` / `F11`       | Debug: start / breakpoint / step over / step into | Set a breakpoint and step through one of the kata solutions.        |

## How to drill

Pick **3 shortcuts a week**. For each one:

1. Read the row.
2. Do the drill three times in a row, deliberately.
3. The next 5 times you naturally need it, **don't reach for the mouse** — even if it's slower at first.

After 2-3 weeks of this, they're reflex.

## Settings worth setting once

```jsonc
// ~/.config/Code/User/settings.json
{
  "editor.formatOnSave": true,
  "editor.linkedEditing": true,             // auto-renames matching JSX/HTML tags
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": "active",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "workbench.editor.enablePreview": false,  // single-click opens permanently
  "explorer.compactFolders": false
}
```
