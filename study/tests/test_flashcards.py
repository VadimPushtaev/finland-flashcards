"""Validate canonical YAML card identities and the unchanged Anki export format."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
import yaml

from app.flashcards import CHAPTER_IDS, load_chapter, parse_chapter
from app.main import app

COUNTS = (44, 57, 112, 75, 79, 56, 109, 73, 112, 86, 128, 103)
SAMPLE = {
    'schema_version': 1, 'chapter_id': 'hb-c01', 'language': 'sv',
    'cards': [{'id': 'hb-c01-lage-0001', 'section_id': 'hb-c01-lage',
               'category': 'Finland i Norden', 'question': 'Vad heter huvudstaden?',
               'options': [{'id': 'a0', 'text': 'Åbo'},
                           {'id': 'a1', 'text': 'Helsingfors'},
                           {'id': 'a2', 'text': 'Tammerfors'},
                           {'id': 'a3', 'text': 'Vasa'}],
               'correct_option_id': 'a1'}]
}


def encode(document):
    return yaml.safe_dump(document, allow_unicode=True, sort_keys=False)


class CardParserTests(unittest.TestCase):
    def test_stable_ids_survive_edits_and_reordering(self):
        sample = copy.deepcopy(SAMPLE)
        second = copy.deepcopy(sample['cards'][0])
        second['id'] = 'hb-c01-lage-0002'
        second['question'] = 'En annan fråga'
        sample['cards'].append(second)
        original = parse_chapter('hb-c01', encode(sample))
        edited = copy.deepcopy(sample)
        edited['cards'][0]['question'] = 'Ny formulering'
        edited['cards'].reverse()
        changed = parse_chapter('hb-c01', encode(edited))
        self.assertEqual({c['id'] for c in original}, {c['id'] for c in changed})
        self.assertEqual(original[0]['id'], 'hb-c01-lage-0001')
        self.assertEqual(changed[1]['question'], 'Ny formulering')

    def test_bad_schema_duplicate_ids_and_wrong_choices_fail(self):
        bad = []
        for field, value in (('chapter_id', 'hb-c02'), ('language', 'en'),
                             ('schema_version', 99), ('cards', [])):
            item = copy.deepcopy(SAMPLE)
            item[field] = value
            bad.append(item)
        for field, value in (('id', 'bad'), ('correct_option_id', 'a9'),
                             ('question', '')):
            item = copy.deepcopy(SAMPLE)
            item['cards'][0][field] = value
            bad.append(item)
        item = copy.deepcopy(SAMPLE)
        item['cards'].append(copy.deepcopy(item['cards'][0]))
        bad.append(item)
        for document in bad:
            with self.subTest(document=document), self.assertRaises(ValueError):
                parse_chapter('hb-c01', encode(document))
        with self.assertRaises(ValueError):
            parse_chapter('missing', encode(SAMPLE))

    def test_all_real_chapters_have_explicit_unique_ids(self):
        self.assertEqual(len(CHAPTER_IDS), 12)
        for chapter, expected in zip(CHAPTER_IDS, COUNTS):
            with self.subTest(chapter=chapter):
                cards = load_chapter(chapter)
                self.assertEqual(len(cards), expected)
                self.assertEqual(len({c['id'] for c in cards}), expected)
                self.assertTrue(all(c['id'].startswith(chapter + '-') for c in cards))
                self.assertTrue(all(len(c['options']) == 4 and
                                    0 <= c['correct_option'] < 4 for c in cards))
        self.assertEqual(sum(COUNTS), 1034)


class CardApiTests(unittest.TestCase):
    def test_question_catalog_has_no_answer_keys(self):
        with TestClient(app) as client:
            listing = client.get('/api/practice/chapters')
            self.assertEqual(listing.status_code, 200)
            self.assertEqual([x['total'] for x in listing.json()['chapters']], list(COUNTS))
            response = client.get('/api/practice/chapters/hb-c01/cards')
            self.assertEqual(response.status_code, 200)
            cards = response.json()['cards']
            self.assertEqual(len(cards), COUNTS[0])
            self.assertNotIn('correct_option', cards[0])
            self.assertEqual(len(cards[0]['options']), 4)

    def test_server_checks_answer_with_stable_id(self):
        card = load_chapter('hb-c01')[0]
        url = f"/api/practice/chapters/hb-c01/cards/{card['id']}/check"
        with TestClient(app) as client:
            correct = client.post(url, json={'option': card['correct_option']})
            wrong = client.post(url, json={'option': (card['correct_option'] + 1) % 4})
            self.assertEqual(correct.json(),
                             {'correct': True, 'correct_option': card['correct_option']})
            self.assertFalse(wrong.json()['correct'])
            self.assertEqual(client.post(url, json={'option': 4}).status_code, 422)
            self.assertEqual(client.post(url.replace(card['id'], 'missing'),
                                         json={'option': 0}).status_code, 404)
            self.assertEqual(client.get('/api/practice/chapters/missing/cards').status_code, 404)

    def test_missing_yaml_returns_service_error(self):
        with tempfile.TemporaryDirectory() as root, patch('app.flashcards.CARDS_DIR', Path(root)):
            load_chapter.cache_clear()
            try:
                with TestClient(app) as client:
                    self.assertEqual(client.get('/api/practice/chapters/hb-c01/cards').status_code, 503)
            finally:
                load_chapter.cache_clear()


if __name__ == '__main__':
    unittest.main()
