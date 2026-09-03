import sqlite3
import os
import re
import threading

from config import SQLITE_PATH

_local = threading.local()

DB_PATH = os.path.abspath(SQLITE_PATH)


def _ensure_db_dir():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


def _get_connection():
    if not hasattr(_local, "conn") or _local.conn is None:
        _ensure_db_dir()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def _convert_params(sql):
    """Convert MySQL %s placeholders to SQLite ? placeholders."""
    return re.sub(r"%s", "?", sql)


def init_db():
    _ensure_db_dir()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT,
            email TEXT UNIQUE,
            mobile TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            dob TEXT,
            gender TEXT,
            city TEXT,
            plan TEXT DEFAULT 'free',
            scans_today INTEGER DEFAULT 0,
            total_scans INTEGER DEFAULT 0,
            last_scan_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            verdict TEXT NOT NULL,
            ai_score REAL DEFAULT 0,
            real_score REAL DEFAULT 0,
            confidence TEXT DEFAULT 'MEDIUM',
            model_used TEXT DEFAULT 'CNN v2.1',
            processing_time TEXT DEFAULT '',
            status TEXT DEFAULT 'completed',
            error_message TEXT DEFAULT '',
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()


def query(sql, params=None, fetch=False):
    """
    fetch=False  -> INSERT / UPDATE / DELETE (returns lastrowid or rowcount)
    fetch=True   -> SELECT (returns list of dicts)
    fetch='one'  -> SELECT single row (returns dict or None)
    """
    conn = _get_connection()
    sqlite_sql = _convert_params(sql)
    try:
        cursor = conn.cursor()
        cursor.execute(sqlite_sql, params or ())

        if fetch == "one":
            row = cursor.fetchone()
            return dict(row) if row else None
        elif fetch:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Query Error: {e}")
        conn.rollback()
        return None
