CREATE TABLE IF NOT EXISTS raw_customers (
    customer_id TEXT,
    signup_date TEXT,
    country     TEXT, 
    city        TEXT,
    segment     TEXT,
    lifetime_value_cents TEXT,
    is_active   TEXT,
    _src_file   TEXT,
    _src_line   INTEGER,
    _ingested_at TEXT
);