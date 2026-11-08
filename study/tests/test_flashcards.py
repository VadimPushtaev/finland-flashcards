"""Test Homebrew card imports and read-only practice catalog endpoints."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.flashcards import CHAPTER_IDS, load_chapter, parse_chapter
from app.main import app

SAMPLE = ('Vad är Finlands huvudstad?|Städer|2|Åbo|Helsingfors|Tammerfors|Vasa||0 1 0 0|2')
COUNTS = (44, 57, 112, 75, 79, 89, 176, 133, 216, 136, 184, 159)


class CardParserTests(unittest.TestCase):
    def test_content_ids_survive_reordering_but_change_when_edited(self):
        second = SAMPLE.replace('huvudstad', 'nationalitet')
        original = parse_chapter('hb-c01', SAMPLE + '\n' + second)
        reordered = parse_chapter('hb-c01', second + '\n' + SAMPLE)
        self.assertEqual({c['id'] for c in original}, {c['id'] for c in reordered})
        self.assertNotEqual(original[0]['id'], original[1]['id'])
        self.assertEqual(len(parse_chapter('hb-c01', SAMPLE + '\n' + SAMPLE)), 1)

    def test_rejects_broken_rows(self):
        for content in (SAMPLE.replace('||0 1 0 0|2', '||1 1 0 0|2'),
                        SAMPLE.replace('||0 1 0 0|2', '||0 0 0 0|2'),
                        SAMPLE.replace('|Vasa||', '||'), SAMPLE.replace('|Städer|2|', '|')):
            with self.subTest(content=content), self.assertRaises(ValueError):
                parse_chapter('hb-c01', content)
        with self.assertRaises(ValueError):
            parse_chapter('missing', SAMPLE)
        with self.assertRaises(ValueError):
            parse_chapter('hb-c01', '')

    def test_all_real_chapter_decks(self):
        self.assertEqual(len(CHAPTER_IDS), 12)
        for chapter_id, expected in zip(CHAPTER_IDS, COUNTS):
            with self.subTest(chapter=chapter_id):
                cards = load_chapter(chapter_id)
                self.assertEqual(len(cards), expected)
                self.assertEqual(len({c['id'] for c in cards}), expected)
                self.assertTrue(all(len(c['options']) == 4 for c in cards))
                self.assertTrue(all(0 <= c['correct_option'] < 4 for c in cards))
        self.assertEqual(sum(COUNTS), 1460)


class CardApiTests(unittest.TestCase):
    def test_catalog_does_not_reveal_answers(self):
        with TestClient(app) as client:
            listing = client.get('/api/practice/chapters')
            self.assertEqual(listing.status_code, 200)
            self.assertEqual([c['total'] for c in listing.json()['chapters']], list(COUNTS))
            response = client.get('/api/practice/chapters/hb-c01/cards')
            self.assertEqual(response.status_code, 200)
            cards = response.json()['cards']
            self.assertEqual(len(cards), COUNTS[0])
            self.assertNotIn('correct_option', cards[0])
            self.assertIn('question', cards[0])
            self.assertEqual(len(cards[0]['options']), 4)

    def test_server_checks_selected_option(self):
        card = load_chapter('hb-c01')[0]
        url = f"/api/practice/chapters/hb-c01/cards/{card['id']}/check"
        with TestClient(app) as client:
            correct = client.post(url, json={'option': card['correct_option']})
            wrong = client.post(url, json={'option': (card['correct_option'] + 1) % 4})
            self.assertEqual(correct.json(), {'correct': True, 'correct_option': card['correct_option']})
            self.assertEqual(wrong.json()['correct'], False)
            self.assertEqual(client.post(url, json={'option': 4}).status_code, 422)
            self.assertEqual(client.post(url + 'missing', json={'option': 0}).status_code, 404)
            self.assertEqual(client.get('/api/practice/chapters/missing/cards').status_code, 404)

    def test_missing_assets_give_service_error(self):
        with tempfile.TemporaryDirectory() as directory, patch('app.flashcards.CARDS_DIR', Path(directory)):
            load_chapter.cache_clear()
            try:
                with TestClient(app) as client:
                    self.assertEqual(client.get('/api/practice/chapters/hb-c01/cards').status_code, 503)
            finally:
                load_chapter.cache_clear()


if __name__ == '__main__':
    unittest.main()
