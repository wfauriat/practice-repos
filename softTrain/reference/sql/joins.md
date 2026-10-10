# SQL — joins cheatsheet

The seven joins you'll use, with intuition and a Venn-diagram mental model. Examples use these toy tables:

```
users               orders
─────               ──────
id  name            id  user_id  amount
 1  alice            1     1       10
 2  bob              2     1       20
 3  carol            3     2       15
                     4   NULL      99   <-- "anonymous"
```

## INNER JOIN

Rows where both sides match. The default `JOIN`.

```sql
SELECT u.name, o.amount
FROM users u
JOIN orders o ON o.user_id = u.id;
```

Result:
```
alice  10
alice  20
bob    15
```

(carol has no orders → omitted; the anonymous order has no user → omitted.)

## LEFT JOIN

Every row from the left, with NULLs where the right has no match.

```sql
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;
```

Result:
```
alice  10
alice  20
bob    15
carol  NULL    <-- carol kept; her amount is NULL
```

## RIGHT JOIN

Mirror of LEFT — every row from the right, NULLs on missing left. Rarely used; usually rewrite as a LEFT JOIN by swapping table order.

```sql
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON o.user_id = u.id;

-- Equivalent:
SELECT u.name, o.amount
FROM orders o
LEFT JOIN users u ON o.user_id = u.id;
```

## FULL OUTER JOIN

All rows from both sides; NULLs where either side is missing.

```sql
SELECT u.name, o.amount
FROM users u
FULL OUTER JOIN orders o ON o.user_id = u.id;
```

Result:
```
alice  10
alice  20
bob    15
carol  NULL
NULL   99    <-- the anonymous order
```

(Not supported in MySQL or SQLite — you can simulate with `LEFT JOIN UNION RIGHT JOIN`.)

## CROSS JOIN

Cartesian product — every row from the left × every row from the right.

```sql
SELECT u.name, o.amount
FROM users u
CROSS JOIN orders o;
```

Used for: generating a date series, building a dimension grid. Almost never what you want with raw tables — usually a missing `WHERE` or `ON`.

## ANTI JOIN — "in A but not in B"

No `ANTI JOIN` keyword in standard SQL; the idiom is:

```sql
-- "users who have NEVER ordered"
SELECT u.*
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;
```

Or with `NOT EXISTS` (often clearer and faster on big tables):

```sql
SELECT u.*
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

Avoid `NOT IN` with subqueries — it has nasty NULL semantics that produce empty results when you don't expect them.

## SEMI JOIN — "in A and matched in B (but only A's columns)"

```sql
-- "users who have at least one order"
SELECT u.*
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

Or:

```sql
SELECT DISTINCT u.*
FROM users u
JOIN orders o ON o.user_id = u.id;
```

`EXISTS` is preferred — it short-circuits on the first match, doesn't need DISTINCT.

## Self-join

A table joined to itself — e.g. find pairs of users who signed up the same day:

```sql
SELECT a.name, b.name
FROM users a
JOIN users b ON a.signup_date = b.signup_date AND a.id < b.id;
```

The `a.id < b.id` avoids duplicates and self-pairs.

## Multi-table joins — read right-to-left

```sql
SELECT u.name, o.amount, p.method
FROM users u
JOIN orders o   ON o.user_id = u.id
JOIN payments p ON p.order_id = o.id
WHERE p.status = 'completed';
```

Read as: *start with `users`, attach matching `orders`, then attach matching `payments`, then filter.*

## When the JOIN feels wrong

- **The result has more rows than you expected.** Probably a fanout — one row in A matches multiple in B. Common cause: forgetting a uniqueness constraint.
- **The result has fewer rows than you expected.** Probably an INNER where you wanted LEFT.
- **NULLs sneaking in.** Always think about the right side of a LEFT JOIN being absent.

Run `SELECT COUNT(*) FROM …` before vs. after adding a join. Big jumps signal a fanout; drops signal an INNER cutting rows.

## Performance notes

- **Indexed join columns** matter enormously. The query planner picks an index lookup over a sequential scan if there's an index.
- **`EXPLAIN ANALYZE`** (Postgres) or **`EXPLAIN QUERY PLAN`** (SQLite) shows what the planner chose. Read it before optimising.
- **Avoid functions on join columns** in the ON clause. `ON LOWER(a.name) = LOWER(b.name)` defeats indexes.
- **Filter early.** Push `WHERE` conditions into subqueries / CTEs that produce small intermediate sets.

## Further reading

- [PostgreSQL docs — Table Expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)
- [Use The Index, Luke](https://use-the-index-luke.com) — Markus Winand on database indexes; the best free SQL-perf resource.
