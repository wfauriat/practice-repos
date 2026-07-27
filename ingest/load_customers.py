import csv
import argparse
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--db", help="path to the write db", required=True)
parser.add_argument("--src", help="path to the source file", required=True)

DATA_ROOT = Path(__file__).resolve().parents[1] / "data"

def main(argv=None):
    args = parser.parse_args(argv)
    _src_file = str(Path(args.src).resolve().relative_to(DATA_ROOT))

    currtime = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(args.db)) as conn, open(args.src) as f:
        reader = csv.DictReader(f)
        FIELDS = ("customer_id", "signup_date", "country", "city",
            "segment", "lifetime_value_cents", "is_active")
        ALL_COLS = FIELDS + ("_src_file", "_src_line", "_ingested_at")

        if reader.fieldnames != list(FIELDS):
            raise ValueError(
                f"unexpected header in {args.src}: {reader.fieldnames}")

        rows = ([row[k] for k in FIELDS] + [args.src, i, currtime]
            for i, row in enumerate(reader, start=2))
        sql = (f"INSERT INTO raw_customers ({', '.join(ALL_COLS)}) "
               f"VALUES ({', '.join('?' * len(ALL_COLS))})")
        with conn:
            cur = conn.executemany(sql, rows)
        print(f"loaded {cur.rowcount} rows from {args.src}")

if __name__ == "__main__":
    main()