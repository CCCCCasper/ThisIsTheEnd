#!/usr/bin/env python3
"""
create_db.py

Simple script to create a SQLite database from `init.sql`.
Usage (PowerShell):
  python .\Database\create_db.py

This will create `Database/bowling.db` next to this script.
"""
import sqlite3
from pathlib import Path
import sys
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / 'init.sql'
DB_FILE = ROOT / 'bowling.db'

if not SQL_FILE.exists():
    print('Could not find init.sql at', SQL_FILE)
    sys.exit(1)

sql = SQL_FILE.read_text(encoding='utf8')

if DB_FILE.exists():
    # create a timestamped backup instead of deleting immediately
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    backup = DB_FILE.with_name(f"{DB_FILE.name}.bak.{ts}")
    try:
        shutil.copy2(DB_FILE, backup)
        print(f'Existing DB backed up to: {backup}')
    except Exception as e:
        print('Warning: could not backup existing DB:', e)
    try:
        DB_FILE.unlink()
        print(f'Removed existing DB: {DB_FILE}')
    except Exception as e:
        print('Error removing existing DB:', e)

try:
    conn = sqlite3.connect(str(DB_FILE))
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()
    print('Created database:', DB_FILE)

    # show summary: list tables and counts for users and lane_* tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print('Tables created:', ', '.join(tables))

    # users count
    if 'users' in tables:
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]
        print(f'users: {users}')

    # lane tables
    lane_tables = [t for t in tables if t.startswith('lane_')]
    if lane_tables:
        for lt in lane_tables:
            cur.execute(f"SELECT COUNT(*) FROM {lt}")
            cnt = cur.fetchone()[0]
            print(f'{lt}: {cnt} reservations')

except Exception as e:
    print('Error creating database:', e)
    sys.exit(1)
finally:
    try:
        conn.close()
    except Exception:
        pass
