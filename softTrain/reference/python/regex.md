# Python — regex cheatsheet

```python
import re
```

## The four functions you actually use

```python
re.search(pattern, text)        # find first match anywhere; returns Match or None
re.match(pattern, text)         # match only at the start
re.findall(pattern, text)       # list of all non-overlapping matches
re.sub(pattern, repl, text)     # substitute matches; repl can be a function
```

## Compile once if you'll use it more than once

```python
ip = re.compile(r"\d{1,3}(?:\.\d{1,3}){3}")
for line in lines:
    if m := ip.search(line):
        ...
```

## Commonly-needed patterns

```python
r"\b\w+\b"          # whole word
r"\s+"              # any whitespace, one or more
r"\S+"              # one or more non-whitespace
r"\d+"              # digits
r"^.*$"             # full line (with re.MULTILINE)
r"[A-Za-z_]\w*"     # identifier
r"https?://\S+"     # URL (rough)
r"#.*"              # python/shell comment to end of line
```

## Capture groups

```python
m = re.search(r"(\w+)=(\d+)", "answer=42")
m.group(0)   # "answer=42"  (whole match)
m.group(1)   # "answer"
m.group(2)   # "42"
m.groups()   # ("answer", "42")
```

## Named groups (recommended)

```python
m = re.search(r"(?P<key>\w+)=(?P<value>\d+)", "answer=42")
m["key"]     # "answer"
m["value"]   # "42"
m.groupdict()  # {"key": "answer", "value": "42"}
```

## Non-capturing group `(?:...)`

```python
re.findall(r"(?:foo|bar)(\w+)", text)   # group 1 is the suffix; the foo/bar isn't captured
```

## Useful flags

```python
re.IGNORECASE   # re.I  — case-insensitive
re.MULTILINE    # re.M  — ^ and $ match line starts/ends, not just string ends
re.DOTALL       # re.S  — . matches newlines
re.VERBOSE      # re.X  — allows whitespace and # comments inside the pattern

re.search(r"foo", text, re.IGNORECASE)
```

## Verbose mode for readability

```python
ip_pattern = re.compile(r"""
    \d{1,3}        # first octet
    (?: \. \d{1,3} ){3}   # three more dotted octets
""", re.VERBOSE)
```

Whitespace and `#` comments are ignored. Only really helpful for patterns longer than ~30 chars.

## Substitutions

```python
re.sub(r"\s+", " ", text)              # collapse whitespace
re.sub(r"(\w+)@(\S+)", r"\1 at \2", text)   # backreferences in repl

# Substitution with a function — the killer feature
def upper_word(m): return m.group(0).upper()
re.sub(r"\b(error|warn|info)\b", upper_word, text)
```

## Walrus + `if`

```python
if m := re.match(r"(\w+):\s*(.*)", line):
    key, value = m.group(1), m.group(2)
```

This idiom — assign-and-test in one — replaces the awkward `m = re.match(...); if m: ...`.

## Common gotchas

- **`re.match` matches only at the start of the string.** Use `re.search` if you want "anywhere".
- **`.` does not match newlines** by default. Use `re.DOTALL` (or `[\s\S]` if you can't pass flags).
- **`^` and `$` match string start/end** by default, not line start/end. Add `re.MULTILINE`.
- **Greedy vs lazy**: `.*` is greedy; `.*?` is lazy (shortest match). Use lazy for `<.*?>` to match individual tags.
- **Raw strings (`r"..."`) are mandatory in practice.** Without them, `"\b"` is a backspace, not a word boundary.

## When regex is the wrong tool

- **HTML / XML parsing** — use a real parser (`lxml`, `BeautifulSoup`).
- **Source code parsing** — use an AST library (`ast` for Python, `tree-sitter` cross-language).
- **JSON parsing** — `json.loads`.
- **Date parsing** — `datetime.strptime` or `dateutil`.

## Further reading

- [Python `re` module docs](https://docs.python.org/3/library/re.html)
- [regex101.com](https://regex101.com) — interactive tester with a Python flavour.
- [The Friedl book — *Mastering Regular Expressions*](https://www.oreilly.com/library/view/mastering-regular-expressions/0596528124/) — the deep dive.
