#!/usr/bin/env python3
# =====================================
# create_db.py
# =====================================
# Dit script maakt de SQLite database aan op basis van init.sql.
# Gebruik: python .\Database\create_db.py
# De database wordt aangemaakt in de map Database/ naast dit script.
# =====================================
import sqlite3
from pathlib import Path
import sys
from datetime import datetime
import shutil

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / 'init.sql'
DB_FILE = ROOT / 'bowling.db'


# Controleren of het SQL-init bestand bestaat
if not SQL_FILE.exists():
    print('Could not find init.sql at', SQL_FILE)
    sys.exit(1)

sql = SQL_FILE.read_text(encoding='utf8')


# Als de database al bestaat, maak een backup met timestamp
if DB_FILE.exists():
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
    # Verbinding maken met de database en tabellen aanmaken
    conn = sqlite3.connect(str(DB_FILE))
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()
    print('Created database:', DB_FILE)

    # Overzicht tonen: tabellen en aantal records
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print('Tables created:', ', '.join(tables))

    # Aantal users tonen
    if 'users' in tables:
        cur.execute("SELECT COUNT(*) FROM users")
        users = cur.fetchone()[0]
        print(f'users: {users}')

    # Aantal reserveringen per baan tonen
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
