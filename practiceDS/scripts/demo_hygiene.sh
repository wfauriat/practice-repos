#!/bin/bash

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

count_lines() {
    local file="${1:?usage: count_lines <file>}"
    wc -l < "$file"
}

echo "hello" > "$TMP/a.txt"
echo -e "one\ntwo\nthree" > "$TMP/b.txt"

echo "TMP dir: $TMP"
echo "a.txt lines: $(count_lines "$TMP/a.txt")"
echo "b.txt lines: $(count_lines "$TMP/b.txt")"

echo "--- calling without arg to trigger the guard ---"
count_lines
