"""
models.py — Database initialization and schema for Smart Task Manager
Creates all tables if they don't exist, and seeds a default admin user.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

if not os.path.exists("database.db"):
    init_db()
    
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db():
    """Return a new database connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables and seed default admin user."""
    conn = get_db()
    cur = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Tasks ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            priority    TEXT    NOT NULL DEFAULT 'Medium',
            deadline    DATE,
            status      TEXT    NOT NULL DEFAULT 'Pending',
            user_id     INTEGER NOT NULL,
            team_id     INTEGER,
            assigned_to INTEGER,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)     REFERENCES users(id),
            FOREIGN KEY (team_id)     REFERENCES teams(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)

    # ── Teams ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name  TEXT    NOT NULL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    # ── Team Members ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            UNIQUE(team_id, user_id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Files ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id   INTEGER NOT NULL,
            file_path TEXT    NOT NULL,
            filename  TEXT    NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    # ── Seed admin user ────────────────────────────────────────────────────
    existing = cur.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    if not existing:
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@example.com", generate_password_hash("admin123"))
        )

    conn.commit()
    conn.close()

if not os.path.exists("database.db"):
    init_db()
    
