-- Init script for bowling sqlite database
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role TEXT NOT NULL,
  email TEXT
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
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_3 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_4 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_5 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_6 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_7 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);


CREATE TABLE IF NOT EXISTS lane_8 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_iso TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  user_id INTEGER REFERENCES users(id),
  name TEXT NOT NULL,
  extra TEXT,
  email TEXT
);

-- Insert demo accounts: one client and one employee
INSERT OR IGNORE INTO users (username, password, role, email) VALUES ('admin', 'admin', 'admin', 'admin@example.com');
INSERT OR IGNORE INTO users (username, password, role, email) VALUES ('employee', 'employee', 'employee', 'employee@example.com');
INSERT OR IGNORE INTO users (username, password, role, email) VALUES ('client', 'client', 'client', 'client@example.com');

