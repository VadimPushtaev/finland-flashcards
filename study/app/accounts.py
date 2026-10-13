"""Host-managed accounts with Argon2 password hashing."""
import unicodedata
from pwdlib import PasswordHash
from app.database import database

passwords = PasswordHash.recommended()


def username_key(username):
    """Treat account names case-insensitively and reject whitespace/control names."""
    name = unicodedata.normalize('NFKC', username).strip().casefold()
    if not 1 <= len(name) <= 64 or any(c.isspace() or unicodedata.category(c).startswith('C') for c in name):
        raise ValueError('Username must contain 1–64 characters without spaces or control characters.')
    return name


def password_hash(password):
    """Validate host-supplied passwords before hashing them."""
    if not 8 <= len(password) <= 1024:
        raise ValueError('Password must contain 8–1024 characters.')
    return passwords.hash(password)


def create_user(username, password):
    """Create an account atomically; duplicate names never overwrite accounts."""
    name, hashed = username_key(username), password_hash(password)
    with database() as db:
        cursor = db.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (name, hashed))
        db.execute('INSERT INTO settings (user_id) VALUES (?)', (cursor.lastrowid,))


def reset_password(username, password):
    """Replace a password and revoke all existing sessions in one transaction."""
    name, hashed = username_key(username), password_hash(password)
    with database() as db:
        user = db.execute('SELECT id FROM users WHERE username = ?', (name,)).fetchone()
        if user is None:
            raise ValueError('Account does not exist.')
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed, user['id']))
        db.execute('DELETE FROM sessions WHERE user_id = ?', (user['id'],))
