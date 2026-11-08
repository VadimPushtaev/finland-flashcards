"""Persistent account storage and versioned SQLite initialization."""
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3

DEFAULT_PATH = Path(__file__).resolve().parents[1] / 'state' / 'study.sqlite3'
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
 user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 size INTEGER NOT NULL DEFAULT 20, serif INTEGER NOT NULL DEFAULT 1,
 dark INTEGER NOT NULL DEFAULT 0, last_chapter TEXT, last_section TEXT
);
CREATE TABLE IF NOT EXISTS bookmarks (
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 unit_id TEXT NOT NULL, PRIMARY KEY (user_id, unit_id)
);
CREATE TABLE IF NOT EXISTS completed (
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 section_id TEXT NOT NULL, PRIMARY KEY (user_id, section_id)
);
CREATE TABLE IF NOT EXISTS login_attempts (address TEXT NOT NULL, attempted_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS login_attempt_address ON login_attempts(address, attempted_at);
PRAGMA user_version = 1;
"""


PRACTICE_SCHEMA = """
CREATE TABLE IF NOT EXISTS practice_preferences (
 user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 desired_retention REAL NOT NULL DEFAULT 0.90
 CHECK (desired_retention >= 0.70 AND desired_retention <= 0.99)
);
CREATE TABLE IF NOT EXISTS practice_cards (
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 card_id TEXT NOT NULL, chapter_id TEXT NOT NULL,
 fsrs_json TEXT NOT NULL, due_at TEXT NOT NULL,
 PRIMARY KEY (user_id, card_id)
);
CREATE INDEX IF NOT EXISTS practice_cards_chapter
 ON practice_cards(user_id, chapter_id, due_at);
CREATE TABLE IF NOT EXISTS practice_events (
 event_id TEXT PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 card_id TEXT NOT NULL, chapter_id TEXT NOT NULL,
 reviewed_at TEXT NOT NULL, option INTEGER NOT NULL,
 correct_option INTEGER NOT NULL, correct INTEGER NOT NULL,
 translation_used INTEGER NOT NULL, suggested_grade INTEGER NOT NULL,
 final_grade INTEGER NOT NULL, kind TEXT NOT NULL,
 due_at TEXT NOT NULL, fsrs_log TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS practice_events_card
 ON practice_events(user_id, card_id, reviewed_at);
PRAGMA user_version = 2;
"""

@contextmanager
def database():
    """Open a transactional connection; never substitute ephemeral storage."""
    path = Path(os.environ.get('STUDY_DATABASE_PATH', DEFAULT_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch(mode=0o600, exist_ok=True)
    if (path.stat().st_mode & 0o777) != 0o600:
        path.chmod(0o600)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.execute('PRAGMA journal_mode = WAL')
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        if version == 0:
            connection.executescript('BEGIN IMMEDIATE;\n' + SCHEMA + '\n' + PRACTICE_SCHEMA + '\nCOMMIT;')
        elif version == 1:
            connection.executescript('BEGIN IMMEDIATE;\n' + PRACTICE_SCHEMA + '\nCOMMIT;')
        elif version != 2:
            raise RuntimeError(f'Unsupported study database version: {version}')
        with connection:
            yield connection
    finally:
        connection.close()


def state(connection, user_id):
    """Return one account's complete reader state."""
    row = connection.execute('SELECT * FROM settings WHERE user_id = ?', (user_id,)).fetchone()
    return {
        'completed': [r[0] for r in connection.execute(
            'SELECT section_id FROM completed WHERE user_id = ? ORDER BY section_id', (user_id,))],
        'bookmarks': [r[0] for r in connection.execute(
            'SELECT unit_id FROM bookmarks WHERE user_id = ? ORDER BY unit_id', (user_id,))],
        'last': {'chapter': row['last_chapter'], 'section': row['last_section']} if row['last_chapter'] else None,
        'size': row['size'], 'serif': bool(row['serif']), 'dark': bool(row['dark']),
    }
