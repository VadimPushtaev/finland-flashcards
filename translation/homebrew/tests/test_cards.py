"""Exercise card scope, complete surface coverage and app-compatible review hashes."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from translation.homebrew.tools import cards as c
from translation.homebrew.tools import workflow as w
from study.app.translations import fingerprint


class CardTranslationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = 'hb-c01-demo-0001'
        self.put('manifest.yaml', {'chapters': [{'path': 'sv/demo.yaml'}]})
        self.put('sv/demo.yaml', {'id': 'hb-c01', 'sections': [{'id': 'hb-c01-demo'}]})
        self.card = {'id': self.identity, 'section_id': 'hb-c01-demo',
                     'question': 'Vilket språk?', 'correct_option_id': 'a0',
                     'options': [{'id': f'a{i}', 'text': text} for i, text in
                                 enumerate(['Svenska', 'Finska', 'Ryska', 'Engelska'])]}
        self.save_card()
        self.put('ru/glossary.yaml', {'schema_version': 1, 'entries': []})
        self.records = c.catalog(self.root)[0][self.identity]['source_records']
        self.doc = {'schema_version': 1, 'language': 'ru', 'source_id': self.identity,
                    'source_sha256': w.fingerprint(self.records),
                    'records': [{'source_id': key, 'ru': text, 'vocabulary': []} for key, text in
                                zip(self.records, ['Какой язык?', 'Шведский', 'Финский', 'Русский', 'Английский'])]}
        self.review = {'schema_version': 1, 'source_id': self.identity, 'status': 'complete',
                       'review_mode': 'self_review', 'reviewer': 'test fixture',
                       'glossary_sha256': fingerprint([], sort_keys=True), 'issues': [], 'references': [],
                       'checks': {key: True for key in ('fidelity', 'one_to_one', 'natural_russian',
                                                       'vocabulary', 'terminology', 'headings')}}
        self.seal()

    def put(self, relative, data):
        path = self.root / 'data/homebrew' / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(w.yaml.safe_dump(data, allow_unicode=True, sort_keys=False))

    def save_card(self):
        self.put('cards/hb-c01.yaml', {'schema_version': 1, 'chapter_id': 'hb-c01',
                                      'language': 'sv', 'cards': [self.card]})

    def seal(self):
        self.review['result_sha256'] = fingerprint(self.doc, sort_keys=True)
        self.put(f'ru/cards/{self.identity}.yaml', self.doc)
        self.put(f'ru/reviews/{self.identity}.yaml', self.review)

    def test_scopes_app_compatibility_and_lesson_coexistence(self):
        result = c.validate(self.root, ['hb-c01', 'hb-c01-demo', self.identity], True)
        self.assertEqual(result['validated_count'], 1)
        # Card review files must not break the separate lesson collection check.
        self.assertEqual(w.validate_output(self.root)['available'], 0)
        with patch.object(w, 'prepare_context', return_value={'archived_context': 'full fixture'}) as prep:
            bundle = c.prepare(self.root, ['hb-c01-demo'])
        prep.assert_called_once_with(self.root, 'hb-c01-demo')
        self.assertEqual(bundle['cards'][0]['source_records'], self.records)
        self.assertEqual(bundle['section_contexts']['hb-c01-demo']['archived_context'], 'full fixture')
        with self.assertRaisesRegex(ValueError, 'Unknown target'):
            c.validate(self.root, ['typo'])

    def test_missing_is_not_complete_and_orphan_review_is_rejected(self):
        (self.root / f'data/homebrew/ru/cards/{self.identity}.yaml').unlink()
        with self.assertRaises(OSError):
            c.validate(self.root, ['hb-c01'], True)
        with self.assertRaisesRegex(ValueError, 'Orphan'):
            c.validate(self.root)

    def test_reject_stale_answers_drafts_partial_blank_and_invalid_spans(self):
        original_doc, original_review = deepcopy(self.doc), deepcopy(self.review)
        for case in ('stale', 'draft', 'partial', 'blank', 'span'):
            with self.subTest(case=case):
                self.doc, self.review = deepcopy(original_doc), deepcopy(original_review)
                if case == 'stale':
                    self.doc['source_sha256'] = 'old'
                elif case == 'draft':
                    self.review['status'] = 'draft'
                elif case == 'partial':
                    self.doc['records'].pop()
                elif case == 'blank':
                    self.doc['records'][1]['ru'] = ' '
                else:
                    self.doc['records'][1]['vocabulary'] = [{
                        'lemma': 'svenska', 'pos': 'NOUN', 'context_ru': 'шведский',
                        'general_ru': 'шведский', 'spans': [{'start': 0, 'end': 99, 'text': 'Svenska'}]}]
                self.seal()
                with self.assertRaises(ValueError):
                    c.validate(self.root, ['hb-c01'], True)
        self.doc, self.review = original_doc, original_review
        self.seal()
        self.card['options'][1]['text'] = 'Changed option'
        self.save_card()
        with self.assertRaisesRegex(ValueError, 'Stale'):
            c.validate(self.root, ['hb-c01'], True)


if __name__ == '__main__':
    unittest.main()
