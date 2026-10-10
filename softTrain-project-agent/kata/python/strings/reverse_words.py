"""
Reverse each word in a string but preserve word order.

>>> reverse_words("hello world")
'olleh dlrow'
>>> reverse_words("  multiple   spaces  ")
'  elpitlum   secaps  '
>>> reverse_words("")
''
"""


def reverse_words(s: str) -> str:
    raise NotImplementedError


# --- tests ---
import pytest


def test_basic():
    assert reverse_words("hello world") == "olleh dlrow"


def test_empty():
    assert reverse_words("") == ""


def test_single_word():
    assert reverse_words("racecar") == "racecar"


def test_preserves_whitespace_runs():
    # multiple spaces between words must be preserved
    assert reverse_words("a  b") == "a  b"


def test_unicode():
    assert reverse_words("café noir") == "éfac rion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
