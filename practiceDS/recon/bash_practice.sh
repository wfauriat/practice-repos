#!/usr/bin/bash

set -eu pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/""../scripts/lib.sh"

DATA_DIR="$SCRIPT_DIR"/../data/seed_42

cd "$DATA_DIR"

section() { printf "\033[0;31m=====%s=====\033[0m\n" "$1"; }
section "RECON SCRIPT"
echo "at: " "$SCRIPT_DIR"


section "Row counts"
for f in *; do
    printf '%-18s %s\n' "$(basename "$f")" "$(count_rows "$f" || echo n/a)"
done

find web_events -type f -name '*.gz' -exec zcat {} + | wc -l


section "Files sizes"
for f in *; do
    [ -f "$f" ] && wc -l "$f" | awk -v b="$(basename "$f")" '{print b, $1}'
done


section "customers file"
head -3 customers.csv
tail -n+2 customers.csv | cut -d, -f3 | sort | uniq -c | sort -rn
total=$(cut -d, -f1 customers.csv | wc -l)
unique=$(cut -d, -f1 customers.csv | sort -u | wc -l)
[ "$total" -eq "$unique" ] && echo "PK OK" \
    || echo "PK VIOLATED: $((total - unique)) dupes"

section "table customers"
head customers.csv | column -t -s,

section "labels file"
head -3 labels.csv

section "orders file"
head -3 orders.jsonl
head -3 orders.jsonl | jq -c 'keys'