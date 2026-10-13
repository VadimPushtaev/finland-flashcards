"""Verify account isolation, security, administration and durable SQLite state."""
import os
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app
from app.accounts import create_user, reset_password
from app.auth import COOKIE, token_hash
from app.database import database
from app.admin import main as admin_main

HEADERS = {'X-Study-Request': '1'}


class AccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'study.sqlite3'
        self.env = patch.dict(os.environ, {'STUDY_DATABASE_PATH': str(self.path),
                                         'STUDY_LOGIN_LIMIT': '100', 'STUDY_SECURE_COOKIES': 'false',
                                         'STUDY_PUBLIC_ORIGIN': ''})
        self.env.start()
        create_user('Alice', 'test-password-one')
        create_user('bob', 'test-password-two')
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.temp.cleanup()

    def login(self, client=None, username='alice', password='test-password-one'):
        return (client or self.client).post('/api/auth/login', json={
            'username': username, 'password': password}, headers=HEADERS)

    def test_accounts_hash_passwords_and_reject_duplicate_names(self):
        with database() as db:
            hashed = db.execute('SELECT password_hash FROM users WHERE username = ?', ('alice',)).fetchone()[0]
        self.assertTrue(hashed.startswith('$argon2id$'))
        self.assertNotIn('test-password-one', hashed)
        with self.assertRaises(sqlite3.IntegrityError):
            create_user('ALICE', 'another-password')
        with self.assertRaises(ValueError):
            create_user('bad name', 'another-password')
        with self.assertRaises(ValueError):
            create_user('charlie', 'short')

    def test_public_reading_and_private_state(self):
        self.assertEqual(self.client.get('/api/library').status_code, 200)
        self.assertEqual(self.client.get('/api/auth/session').json(), {'user': None})
        self.assertEqual(self.client.get('/api/state').status_code, 401)
        self.assertEqual(self.client.put('/api/state/bookmarks/hb-c01-u0001', json={'saved': True}, headers=HEADERS).status_code, 401)
        self.assertEqual(self.client.post('/api/auth/register', json={}).status_code, 405)

    def test_login_cookie_and_logout_revocation(self):
        result = self.login(username='ALICE')
        self.assertEqual(result.status_code, 200)
        cookie = result.headers['set-cookie']
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite=lax', cookie)
        self.assertIn('Max-Age=31536000', cookie)
        token = self.client.cookies.get(COOKIE)
        with database() as db:
            stored = db.execute('SELECT token_hash FROM sessions').fetchone()[0]
            self.assertEqual(stored, token_hash(token))
            self.assertNotEqual(stored, token)
            db.execute('UPDATE sessions SET created_at = 0')
        self.assertEqual(self.client.get('/api/auth/session').json()['user']['username'], 'alice')
        self.assertEqual(self.client.get('/api/state').status_code, 200)
        self.assertEqual(self.client.post('/api/auth/logout', headers=HEADERS).status_code, 200)
        self.client.cookies.set(COOKIE, token)
        self.assertEqual(self.client.get('/api/state').status_code, 401)

    def test_secure_cookie_and_reset_revokes_all_sessions(self):
        with patch.dict(os.environ, {'STUDY_SECURE_COOKIES': 'true'}):
            self.assertIn('Secure', self.login().headers['set-cookie'])
        self.client.cookies.clear()
        self.login()
        second = TestClient(app)
        self.login(second)
        reset_password('alice', 'updated-test-password')
        self.assertEqual(self.client.get('/api/state').status_code, 401)
        self.assertEqual(second.get('/api/state').status_code, 401)
        self.assertEqual(self.login().status_code, 401)
        self.assertEqual(self.login(password='updated-test-password').status_code, 200)
        second.close()

    def test_login_errors_throttle_and_same_origin(self):
        invalid = self.login(password='wrong-password')
        unknown = self.login(username='unknown', password='wrong-password')
        self.assertEqual(invalid.json(), unknown.json())
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(self.client.post('/api/auth/login', json={'username': 'alice', 'password': 'x'}).status_code, 403)
        self.assertEqual(self.client.post('/api/auth/login', json={'username': 'alice', 'password': 'x'},
                                         headers={**HEADERS, 'Origin': 'https://attacker.example'}).status_code, 403)
        with patch.dict(os.environ, {'STUDY_LOGIN_LIMIT': '2'}):
            result = self.login()
            self.assertEqual(result.status_code, 429)
            self.assertEqual(result.headers['retry-after'], '300')

    def test_state_isolation_idempotency_and_field_updates(self):
        self.login()
        bookmark = '/api/state/bookmarks/hb-c01-u0001'
        for _ in range(2):
            self.assertEqual(self.client.put(bookmark, json={'saved': True}, headers=HEADERS).status_code, 200)
        self.client.put('/api/state/completed/hb-c01-lage', json={'saved': True}, headers=HEADERS)
        self.client.patch('/api/state/preferences', json={'size': 22}, headers=HEADERS)
        self.client.patch('/api/state/preferences', json={'dark': True}, headers=HEADERS)
        self.client.patch('/api/state/position', json={'chapter': 'hb-c01', 'section': 'hb-c01-lage'}, headers=HEADERS)
        saved = self.client.get('/api/state').json()
        self.assertEqual(saved['bookmarks'], ['hb-c01-u0001'])
        self.assertEqual(saved['completed'], ['hb-c01-lage'])
        self.assertEqual(saved['size'], 22)
        self.assertTrue(saved['dark'])
        self.assertEqual(saved['last']['section'], 'hb-c01-lage')
        other = TestClient(app)
        self.login(other, 'bob', 'test-password-two')
        self.assertEqual(other.get('/api/state').json()['bookmarks'], [])
        other.put(bookmark, json={'saved': False}, headers=HEADERS)
        self.assertEqual(self.client.get('/api/state').json()['bookmarks'], ['hb-c01-u0001'])
        self.assertEqual(self.client.patch('/api/state/preferences', json={'size': 19}, headers=HEADERS).status_code, 422)
        self.assertEqual(self.client.patch('/api/state/preferences', json={'user_id': 2}, headers=HEADERS).status_code, 422)
        self.assertEqual(self.client.patch('/api/state/preferences', json={'dark': None}, headers=HEADERS).status_code, 422)
        self.assertEqual(self.client.put('/api/state/bookmarks/missing', json={'saved': True}, headers=HEADERS).status_code, 404)
        self.assertEqual(self.client.patch('/api/state/position', json={'chapter': 'hb-c01', 'section': 'hb-c02-forhistoria'}, headers=HEADERS).status_code, 404)
        self.assertEqual(self.client.patch('/api/state/preferences', json={'dark': False}).status_code, 403)
        self.assertEqual(self.client.get('/api/state', headers={'X-Study-User': 'bob'}).status_code, 401)
        self.assertEqual(self.client.put(bookmark, json={'saved': False}, headers={**HEADERS, 'X-Study-User': 'bob'}).status_code, 401)
        self.assertEqual(self.client.get('/api/state').json()['bookmarks'], ['hb-c01-u0001'])
        other.close()

    def test_connection_reopen_backup_and_host_commands(self):
        self.login()
        self.client.put('/api/state/bookmarks/hb-c01-u0001', json={'saved': True}, headers=HEADERS)
        token = self.client.cookies.get(COOKIE)
        self.client.close()
        self.client = TestClient(app)
        self.client.cookies.set(COOKIE, token)
        self.assertEqual(self.client.get('/api/state').json()['bookmarks'], ['hb-c01-u0001'])
        backup = Path(self.temp.name) / 'backup.sqlite3'
        with patch('sys.argv', ['admin', 'backup-db', str(backup)]):
            admin_main()
        with closing(sqlite3.connect(backup)) as db:
            self.assertEqual(db.execute('SELECT count(*) FROM bookmarks').fetchone()[0], 1)
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        with patch('sys.argv', ['admin', 'create-user', 'charlie']), patch('sys.stdin.isatty', return_value=True), patch('getpass.getpass', return_value='new-test-password'):
            admin_main()
        self.assertEqual(self.login(username='charlie', password='new-test-password').status_code, 200)
        with patch('sys.argv', ['admin', 'reset-password', 'charlie']), patch('sys.stdin.isatty', return_value=True), patch('getpass.getpass', return_value='changed-test-password'):
            admin_main()
        self.assertEqual(self.client.get('/api/state').status_code, 401)

    def test_bad_database_never_falls_back_to_empty_state(self):
        with database() as db:
            db.execute('PRAGMA user_version = 99')
        with self.assertRaises(RuntimeError):
            with database():
                pass
