-- Init script for bowling sqlite database
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL,
  display_name TEXT
);
-- Create 8 separate tables, one per bowling lane (no central reservations table)
-- Each lane table stores reservations for that specific lane.

-- Example table name: lane_1, lane_2, ... lane_8

-- Note: using separate tables for each lane is a denormalized design but
-- follows the requested structure. Consider a single reservations table
-- with a lane_id column for normalized data in production.

-- Create lane tables
CREATE TABLE IF NOT EXISTS lane_1 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_3 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_4 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_5 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_6 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_7 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lane_8 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL
);

-- Insert demo accounts: one client and one employee
INSERT OR IGNORE INTO users (username, password, role, display_name) VALUES ('client', 'client123', 'client', 'Demo Client');
INSERT OR IGNORE INTO users (username, password, role, display_name) VALUES ('employee', 'employee123', 'employee', 'Demo Employee');
