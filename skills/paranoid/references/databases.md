# Databases

## Where am I

Read the host, port, database name and user from the connection string or
environment (`DATABASE_URL`, `PGHOST`, `PGDATABASE`, `MYSQL_HOST` and so
on) and say them back to the user before running anything that writes.

```sql
-- PostgreSQL
SELECT current_database(), current_user, inet_server_addr();
-- MySQL
SELECT DATABASE(), CURRENT_USER(), @@hostname;
```

## Before writing

- Run the same `WHERE` clause as a `SELECT count(*)` and show the count.
  If it is not what the user expects, stop.
- Never run `UPDATE` or `DELETE` without a `WHERE` clause unless the user
  asked to change every row.
- Wrap changes in a transaction where the database supports it, check the
  affected row count, and only then commit:

  ```sql
  BEGIN;
  DELETE FROM orders WHERE created_at < '2020-01-01';
  -- check the reported row count
  ROLLBACK;  -- or COMMIT once the user agrees
  ```

  `DROP`, `TRUNCATE` and most `ALTER TABLE` statements commit implicitly in
  MySQL, so a transaction does not protect them there.

## Statements that need step 4 and step 6

| Statement | Why |
| --- | --- |
| `DROP DATABASE`, `DROP SCHEMA`, `DROP TABLE` | the data is gone |
| `TRUNCATE` | removes every row, usually without a way to roll back |
| `DELETE` / `UPDATE` on many rows | hard to reverse without a backup |
| `ALTER TABLE ... DROP COLUMN` | the column's data is gone |
| type changes and rewrites on large tables | can lock the table for a long time |
| `DROP INDEX` | can make queries slow enough to cause an outage |

## Backups

Take one before destructive work when it is practical:

```bash
pg_dump -Fc -d "$DATABASE_URL" -t orders -f orders-backup.dump
mysqldump --single-transaction mydb orders > orders-backup.sql
```

For managed databases, use the provider's snapshot (see
[cloud.md](cloud.md)).

## Migrations

- Read the migration before running it, including what the framework
  generated.
- Check there is a down migration, and whether it restores data or only
  structure (most only restore structure).
- Run it against a non-production database first.
- Large data migrations on production: batch them and agree on timing with
  the user.
