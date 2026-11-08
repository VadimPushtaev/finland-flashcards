"""Additive database migration and per-account FSRS review tests."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.database import SCHEMA, database
from app.flashcards import load_chapter
from app.accounts import create_user

HEADERS = {'X-Study-Request': '1'}


class PracticeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'study.sqlite3'
        self.env = patch.dict(os.environ, {'STUDY_DATABASE_PATH': str(self.path)})
        self.env.start()
        self.client = TestClient(app)
        with database() as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 2)
        create_user('alice', 'test-password-alice')
        create_user('bob', 'test-password-bob')
        self.client.post('/api/auth/login', headers=HEADERS,
                         json={'username': 'alice', 'password': 'test-password-alice'})

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.temp.cleanup()

    def test_default_retention_and_account_isolation(self):
        first = self.client.get('/api/practice/overview').json()
        self.assertEqual(first['desired_retention'], 0.9)
        self.assertEqual(first['chapters'][0]['new'], 44)
        self.assertEqual(self.client.patch('/api/practice/settings',
                                           json={'desired_retention': 0.95}).status_code, 403)
        self.assertEqual(self.client.patch('/api/practice/settings', headers=HEADERS,
                                           json={'desired_retention': 0.95}).status_code, 200)
        self.client.post('/api/auth/login', headers=HEADERS,
                         json={'username': 'bob', 'password': 'test-password-bob'})
        self.assertEqual(self.client.get('/api/practice/settings').json()['desired_retention'], 0.9)

    def test_review_history_and_idempotency(self):
        question = load_chapter('hb-c01')[0]
        payload = {'event_id': 'practice-test-event-0001', 'card_id': question['id'],
                   'option': question['correct_option'], 'grade': 3, 'translation_used': True}
        url = '/api/practice/chapters/hb-c01/review'
        answer = self.client.post(url, json=payload, headers=HEADERS)
        self.assertEqual(answer.status_code, 200, answer.text)
        self.assertTrue(answer.json()['correct'])
        self.assertEqual(answer.json()['suggested_grade'], 2)
        again = self.client.post(url, json=payload, headers=HEADERS)
        self.assertTrue(again.json()['duplicate'])
        stats = self.client.get(f"/api/practice/cards/{question['id']}/stats").json()
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['correct'], 1)
        self.assertEqual(stats['grades']['Good'], 1)
        self.assertEqual(stats['breakdown']['correct_translated'], 1)
        self.assertEqual(self.client.post(url, headers=HEADERS,
                        json={**payload, 'event_id': 'practice-test-event-0002',
                              'option': 4}).status_code, 422)
        self.client.post('/api/auth/login', headers=HEADERS,
                         json={'username': 'bob', 'password': 'test-password-bob'})
        self.assertEqual(self.client.get(f"/api/practice/cards/{question['id']}/stats").json()['total'], 0)
        self.assertEqual(len(self.client.get('/api/practice/chapters/hb-c01/queue').json()['cards']), 44)

    def test_absent_card_translation_never_breaks_practice(self):
        card = load_chapter('hb-c01')[0]
        with self.client as client:
            response = client.get('/api/practice/chapters/hb-c01/cards/' +
                                  card['id'] + '/translation')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'available': False, 'language': 'ru', 'records': {}})
            self.assertEqual(client.get('/api/practice/chapters/hb-c01/cards/missing/translation').status_code, 404)

    def test_extra_practice_does_not_change_saved_retention(self):
        question = load_chapter('hb-c01')[0]
        url = '/api/practice/chapters/hb-c01/review'
        response = self.client.post(url, headers=HEADERS,
            json={'event_id': 'practice-extra-test-0001', 'card_id': question['id'],
                  'option': question['correct_option'], 'grade': 4})
        self.assertEqual(response.status_code, 200, response.text)
        candidates = self.client.post('/api/practice/chapters/hb-c01/extra', headers=HEADERS,
            json={'threshold': 0.99, 'excluded_ids': []})
        self.assertEqual(candidates.status_code, 200, candidates.text)
        result = candidates.json()
        self.assertIn('count', result)
        self.assertIn('fallback_count', result)
        self.assertEqual(self.client.get('/api/practice/settings').json()['desired_retention'], 0.9)
        self.assertEqual(self.client.get('/api/practice/cards/' + question['id'] + '/stats').json()['total'], 1)
        excluded = self.client.post('/api/practice/chapters/hb-c01/extra', headers=HEADERS,
            json={'threshold': 0.99, 'excluded_ids': [question['id']]})
        self.assertEqual(excluded.status_code, 200)
        self.assertGreaterEqual(excluded.json()['fallback_count'], 1)

    def test_invalid_retention_and_bad_review_do_not_write(self):
        self.assertEqual(self.client.patch('/api/practice/settings', headers=HEADERS,
                                           json={'desired_retention': 1.5}).status_code, 422)
        with database() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM practice_events').fetchone()[0], 0)

    def test_existing_v1_database_upgrades_without_losing_users(self):
        self.client.close()
        with sqlite3.connect(self.path) as conn:
            # Simulate a real legacy database version, with populated reader tables.
            conn.execute('PRAGMA user_version = 1')
            conn.execute('DROP TABLE practice_events')
            conn.execute('DROP TABLE practice_cards')
            conn.execute('DROP TABLE practice_preferences')
            conn.execute('INSERT INTO bookmarks (user_id, unit_id) VALUES (1, "hb-c01-u0001")')
        with database() as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 2)
            self.assertEqual(db.execute('SELECT count(*) FROM users').fetchone()[0], 2)
            self.assertEqual(db.execute('SELECT count(*) FROM bookmarks').fetchone()[0], 1)
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
