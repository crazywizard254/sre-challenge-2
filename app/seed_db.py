#!/usr/bin/env python3
"""Seed the database with the parts table and sample rows.

This script can be run as a one-off job during container startup. It will
attempt to connect to the DB using the same DATABASE_URL envvar as the app.
"""
import sys
import os

try:
    # prefer top-level import (when working dir is /app)
    from parts_service import init_db, get_conn
except Exception:
    # fallback to package import
    from app.parts_service import init_db, get_conn


def apply_migrations():
    """Apply SQL migration files found in app/migrations/ in alphabetical order.
    Each file is executed as a single SQL script using the same DB connection
    parameters the application uses.
    """
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    if not os.path.isdir(migrations_dir):
        print(f"[seed_db] no migrations directory at {migrations_dir}")
        return True
    files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    if not files:
        print("[seed_db] no migration files to apply")
        return True
    # Retry connecting to the DB for a short period to tolerate startup delays
    import time
    conn = None
    max_attempts = int(os.getenv('SEED_DB_RETRY', '30'))
    delay = float(os.getenv('SEED_DB_RETRY_DELAY', '2'))
    for attempt in range(1, max_attempts + 1):
        conn = get_conn()
        if conn:
            break
        print(f"[seed_db] DB not available, attempt {attempt}/{max_attempts} - retrying in {delay}s...", file=sys.stderr)
        time.sleep(delay)
    if not conn:
        print("[seed_db] ERROR: DB not available to apply migrations", file=sys.stderr)
        return False
    try:
        cur = conn.cursor()
        for fname in files:
            path = os.path.join(migrations_dir, fname)
            print(f"[seed_db] applying migration: {fname}")
            with open(path, 'r') as fh:
                sql = fh.read()
            # Execute the SQL script. Some drivers do not support executescript,
            # so split on semicolon and execute individual statements.
            stmt = ''
            for line in sql.splitlines():
                stmt += line + '\n'
                if line.strip().endswith(';'):
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        # Log and continue; CREATE TABLE IF NOT EXISTS is idempotent
                        print(f"[seed_db] migration statement failed: {e}")
                    stmt = ''
            if stmt.strip():
                try:
                    cur.execute(stmt)
                except Exception as e:
                    print(f"[seed_db] migration final statement failed: {e}")
        conn.commit()
        # Optionally import a SQL data-only dump after migrations are applied.
        import_dump = os.getenv('IMPORT_DUMP', 'FALSE').upper() == 'TRUE'
        if import_dump:
            dump_path = os.getenv('DUMP_FILE', os.path.join(migrations_dir, 'db_data.sql'))
            if os.path.isfile(dump_path):
                print(f"[seed_db] importing data dump from: {dump_path}")
                with open(dump_path, 'r') as fh:
                    dump_sql = fh.read()
                stmt = ''
                for line in dump_sql.splitlines():
                    stmt += line + '\n'
                    if line.strip().endswith(';'):
                        try:
                            cur.execute(stmt)
                        except Exception as e:
                            print(f"[seed_db] data import statement failed: {e}")
                        stmt = ''
                if stmt.strip():
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        print(f"[seed_db] data import final statement failed: {e}")
                conn.commit()
            else:
                print(f"[seed_db] data dump file not found at {dump_path}; skipping import")
        return True
    finally:
        conn.close()


def main():
    # First attempt to apply any SQL migrations bundled with the app, then
    # delegate to the existing init_db (which will perform any missing
    # migrations and optionally seed sample data).
    ok_mig = apply_migrations()
    if not ok_mig:
        print("[seed_db] ERROR: failed to apply migrations", file=sys.stderr)
        return 2

    seed = True
    ok = init_db(seed=seed)
    if ok:
        print("[seed_db] OK: DB initialized/seeded")
        return 0
    else:
        print("[seed_db] ERROR: DB not available or failed to initialize", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
