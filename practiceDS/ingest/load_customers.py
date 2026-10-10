import csv
import argparse
import logging
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "sql" / "raw_schema.sql"

parser = argparse.ArgumentParser()
parser.add_argument("--db", help="path to the write db", required=True)
parser.add_argument("--src", help="path to the source file", required=True)
parser.add_argument("--init-db", help="init the db from schema",
                    action="store_true", default=False)

log = logging.getLogger(__name__)

def main(argv=None):
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = parser.parse_args(argv)
    _src_file = Path(args.src).resolve().name
                   
    currtime = datetime.now(timezone.utc).isoformat()
    with (
        open(args.src, newline='', encoding='utf-8-sig') as f,
        closing(sqlite3.connect(args.db)) as conn,
    ):
        if args.init_db:
            conn.executescript(SCHEMA.read_text(encoding="utf-8"))

        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='raw_customers'"
        ).fetchone()
        if exists is None:
            raise RuntimeError(
                f"table raw_customers missing in {args.db} — rerun with --init-db"
    )

        reader = csv.DictReader(f)
        FIELDS = ("customer_id", "signup_date", "country", "city",
            "segment", "lifetime_value_cents", "is_active")
        ALL_COLS = FIELDS + ("_src_file", "_src_line", "_ingested_at")

        if reader.fieldnames != list(FIELDS):
            raise ValueError(
                f"unexpected header in {_src_file}: {reader.fieldnames}")

        rows = ([row[k] for k in FIELDS] + [_src_file, i, currtime]
            for i, row in enumerate(reader, start=2))
        sql = (f"INSERT INTO raw_customers ({', '.join(ALL_COLS)}) "
               f"VALUES ({', '.join('?' * len(ALL_COLS))})")
        with conn:
            cur = conn.executemany(sql, rows)
        log.info("loaded %d rows from %s into %s",
                  cur.rowcount, _src_file, args.db)

if __name__ == "__main__":
    main()