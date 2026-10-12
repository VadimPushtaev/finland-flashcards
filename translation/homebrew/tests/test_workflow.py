"""Meaningful fixtures for context completeness, alignment, and stale reviews."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import yaml

MODULE = Path(__file__).resolve().parents[1] / 'tools/workflow.py'
SPEC = importlib.util.spec_from_file_location('workflow', MODULE)
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)


def seal(document, terms, status='complete'):
    """Create test review metadata for a known reviewed fixture."""
    used = sorted({v['glossary_id'] for r in document['records'] for v in r['vocabulary'] if 'glossary_id' in v})
    def hashed(value):
        return w.digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    return {'schema_version': 1, 'source_id': document['source_id'],
            'result_sha256': hashed(document), 'glossary_sha256': hashed([terms[k] for k in used]),
            'status': status, 'review_mode': 'independent', 'reviewer': 'fixture-reviewer',
            'checks': {k: True for k in ('fidelity', 'one_to_one', 'natural_russian', 'vocabulary', 'terminology', 'headings')},
            'issues': [], 'references': []}


class ValidationTests(unittest.TestCase):
    def setUp(self):
        fixture = w.read(Path(__file__).parent / 'fixtures/example.yaml')
        self.source = fixture['source']
        self.terms = w.glossary_entries({'schema_version': 1, 'entries': [fixture['term']]})
        self.doc = {'schema_version': 1, 'language': 'ru', 'source_id': 'demo-heading',
                    'source_sha256': w.fingerprint(self.source), 'records': fixture['records']}
        self.review = seal(self.doc, self.terms)

    def validate(self):
        w.validate_document(self.doc, self.source, self.terms, self.review)

    def test_unicode_discontinuous_expression_compound_and_fragment(self):
        self.validate()
        # The pronoun is deliberately omitted, the intervening adverb retained.
        words = self.doc['records'][1]['vocabulary']
        self.assertEqual([v['lemma'] for v in words], ['tycka om', 'verkligen', 'samhällskunskap'])

    def test_missing_duplicate_unknown_and_reordered_records(self):
        original = deepcopy(self.doc)
        variants = [original['records'][:-1], original['records'] + original['records'][:1],
                    list(reversed(original['records']))]
        for variant in variants:
            with self.subTest(variant=variant):
                self.doc = dict(original, records=variant)
                with self.assertRaisesRegex(ValueError, 'source records'):
                    self.validate()
        self.doc = deepcopy(original)
        self.doc['records'][0]['source_id'] = 'unknown'
        with self.assertRaises(ValueError):
            self.validate()

    def test_bad_offsets_surface_and_overlap(self):
        original = deepcopy(self.doc)
        for field, value in [('start', -1), ('start', True), ('end', 999), ('text', 'wrong')]:
            self.doc = deepcopy(original)
            self.doc['records'][1]['vocabulary'][0]['spans'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate()
        self.doc = deepcopy(original)
        self.doc['records'][1]['vocabulary'].append(deepcopy(self.doc['records'][1]['vocabulary'][0]))
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            self.validate()

    def test_source_changes_invalidate_translation(self):
        self.source['demo-fragment'] += '!'
        with self.assertRaisesRegex(ValueError, 'Stale source'):
            self.validate()

    def test_translation_changes_invalidate_review(self):
        self.doc['records'][0]['ru'] = 'Труд'
        with self.assertRaisesRegex(ValueError, 'Review does not match result'):
            self.validate()

    def test_glossary_conflicts_and_changes(self):
        self.doc['records'][1]['vocabulary'][2]['general_ru'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'Glossary general'):
            self.validate()
        self.doc['records'][1]['vocabulary'][2]['general_ru'] = 'обществознание'
        self.terms['samhalls-civics']['note'] = 'Changed decision'
        with self.assertRaisesRegex(ValueError, 'Review does not match glossary'):
            self.validate()
        with self.assertRaisesRegex(ValueError, 'Duplicate/conflicting'):
            w.glossary_entries({'schema_version': 1, 'entries': list(self.terms.values()) * 2})

    def test_blocking_issue_prevents_completion_but_allows_draft(self):
        self.review['issues'] = [{'source_id': 'demo-sentence', 'blocking': True,
                                  'resolved': False, 'note': 'Ambiguous sense'}]
        with self.assertRaisesRegex(ValueError, 'Unresolved blocking'):
            self.validate()
        self.review['status'] = 'draft'
        self.validate()

    def test_incomplete_review_cannot_be_complete(self):
        self.review['checks']['vocabulary'] = False
        with self.assertRaisesRegex(ValueError, 'Incomplete language review'):
            self.validate()

    def test_unknown_fields_and_empty_meaning(self):
        self.doc['records'][0]['vocabulary'][0]['examples'] = []
        with self.assertRaisesRegex(ValueError, 'Invalid fields'):
            self.validate()
        del self.doc['records'][0]['vocabulary'][0]['examples']
        self.doc['records'][0]['vocabulary'][0]['context_ru'] = ''
        with self.assertRaisesRegex(ValueError, 'nonempty'):
            self.validate()


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / 'data/homebrew'
        self.chapter = {'id': 'hb-c01', 'title': 'Arbete', 'sections': [
            {'id': 'hb-c01-demo', 'title': 'Åland', 'blocks': [
                {'id': 'unit', 'type': 'paragraph', 'text': 'Arbete.',
                 'sentences': [{'id': 'sentence', 'start': 0, 'end': 7}]}]}]}
        self.write('manifest.yaml', {'chapters': [{'path': 'sv/chapters/01.yaml'}]})
        self.write('sv/chapters/01.yaml', self.chapter)
        self.write('ru/glossary.yaml', {'schema_version': 1, 'entries': []})
        self.write('metadata/01_editorial_review.yaml', {'note': 'Archived claim'})
        self.write('metadata/attribution.yaml', {'credit': 'Fixture source'})
        source = self.root / 'source.html'
        source.write_text('<main><p>Before.</p><p>Arbete.</p><p>After.</p></main>', encoding='utf-8')
        self.provenance = {'units': {'unit': {'source_path': 'source.html',
                            'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}}}
        self.write('metadata/01_provenance.yaml', self.provenance)

    def write(self, path, data):
        target = self.base / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')

    def test_context_includes_whole_chapter_outline_sources_editorial_and_glossary(self):
        context = w.prepare_context(self.root, 'hb-c01-demo')
        self.assertEqual(context['parent_chapter'], self.chapter)
        self.assertEqual(context['book_outline'][0]['sections'][0]['id'], 'hb-c01-demo')
        self.assertIn('Before.', context['archived_context'][0]['context'])
        self.assertIn('After.', context['archived_context'][0]['context'])
        self.assertEqual(context['editorial_review']['note'], 'Archived claim')
        self.assertEqual(context['glossary']['entries'], [])
        self.assertEqual(context['target_records']['sentence'], 'Arbete.')
        self.assertEqual(context['chapter_heading_records'], {'hb-c01': 'Arbete'})

    def test_missing_or_changed_archives_fail(self):
        (self.root / 'source.html').write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Changed archived'):
            w.prepare_context(self.root, 'hb-c01-demo')
        (self.root / 'source.html').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            w.prepare_context(self.root, 'hb-c01-demo')

    def test_empty_collection_is_explicit_and_unknown_target_fails(self):
        result = w.validate_output(self.root)
        self.assertEqual((result['available'], result['total_targets']), (0, 2))
        with self.assertRaisesRegex(ValueError, 'Unknown source'):
            w.prepare_context(self.root, 'unknown')
        with self.assertRaises(OSError):
            w.validate_output(self.root, 'hb-c01-demo')

    def test_section_completion_requires_heading_and_context_reuses_completed_output(self):
        for section in (None, self.chapter['sections'][0]):
            records = w.source_records(self.chapter, section)
            identity = next(iter(records))
            doc = {'schema_version': 1, 'language': 'ru', 'source_id': identity,
                   'source_sha256': w.fingerprint(records),
                   'records': [{'source_id': k, 'ru': 'Перевод.', 'vocabulary': []} for k in records]}
            kind = 'sections' if section else 'headings'
            self.write(f'ru/{kind}/{identity}.yaml', doc)
            self.write(f'ru/reviews/{identity}.yaml', seal(doc, {}))
        self.assertEqual(w.validate_output(self.root)['available'], 2)
        context = w.prepare_context(self.root, 'hb-c01-demo')
        self.assertEqual(len(context['completed_same_chapter']), 1)
        self.assertEqual(len(context['completed_translation_index']), 1)
        (self.base / 'ru/headings/hb-c01.yaml').unlink()
        with self.assertRaises(OSError):
            w.validate_output(self.root, 'hb-c01-demo', True)

    def test_orphan_review_is_rejected(self):
        self.write('ru/reviews/unknown.yaml', {})
        with self.assertRaisesRegex(ValueError, 'Orphan'):
            w.validate_output(self.root)


if __name__ == '__main__':
    unittest.main()
