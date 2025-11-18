# Database

This folder contains SQL and a small script to create a SQLite database for the bowling app.

Files:
- `init.sql` - creates tables and seeds 8 lanes and 2 demo users (passwords are plaintext for demo).
- `create_db.py` - Python script that runs `init.sql` and writes `bowling.db` into this folder.

Create the database (requires Python 3):

PowerShell (from project root):
```powershell
python .\Database\create_db.py
```

Output: `Database\bowling.db` will be created. If it already exists it will be overwritten.

Security note: replace plaintext passwords with hashed values before using in production.
