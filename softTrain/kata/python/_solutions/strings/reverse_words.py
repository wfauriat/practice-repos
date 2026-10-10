"""Reference solution for strings/reverse_words."""

import re


def reverse_words(s: str) -> str:
    # Split keeping the whitespace runs as separate tokens, reverse only the word tokens.
    return "".join(tok[::-1] if tok.strip() else tok for tok in re.split(r"(\s+)", s))
