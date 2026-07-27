# shellcheck shell=bash
# Shared helpers for the recon scripts. Source it, don't execute it:
#     source "$SCRIPT_DIR/lib.sh"
#
# Deliberately does NOT set shell options -- that is the caller's business.

PYTHON="${PYTHON:-/opt/venvs/pyDS/bin/python}"

# count_rows <path> -- print the number of data rows to stdout.
# CSV counts exclude the header. Directories are summed recursively;
# files of unknown type are skipped with a warning on stderr.
count_rows() {
    local path="${1:?usage: count_rows <path>}"
    local n total=0 f

    [[ -e $path ]] || { printf 'count_rows: no such path: %s\n' "$path" >&2; return 1; }

    if [[ -d $path ]]; then
        while IFS= read -r -d '' f; do
            if n=$(count_rows "$f"); then
                total=$(( total + n ))
            else
                printf 'count_rows: skipped %s\n' "$f" >&2
            fi
        done < <(find "$path" -type f -print0)
        printf '%d\n' "$total"
        return 0
    fi

    case "$path" in
        *.gz)
            zcat < "$path" | wc -l
            ;;
        *.parquet)
            "$PYTHON" -c 'import sys, pyarrow.parquet as pq
print(pq.ParquetFile(sys.argv[1]).metadata.num_rows)' "$path"
            ;;
        *.csv)
            n=$(wc -l < "$path")
            printf '%d\n' "$(( n > 0 ? n - 1 : 0 ))"
            ;;
        *.jsonl)
            wc -l < "$path"
            ;;
        *)
            printf 'count_rows: unknown type: %s\n' "$path" >&2
            return 1
            ;;
    esac
}
