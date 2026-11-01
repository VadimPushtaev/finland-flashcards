"""Check priority selection, assessment prerequisites, and real Kahoot export."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from card_creator.homebrew import score_sentences as scoring
from card_creator.homebrew import validate_cards as cards
from card_creator.kahoot import export


class ScoringTests(unittest.TestCase):
    def test_formula_and_flags(self):
        values = {'exam_relevance': 2, 'knowledge_value': 2,
                  'question_suitability': 3, 'factual_specificity': 3, 'change_risk': 0}
        self.assertEqual(scoring.score(values), 45)
        self.assertEqual(scoring.score(dict.fromkeys(values, 0)), 0)
        self.assertEqual(scoring.score(dict.fromkeys(values, 3)), 60)
        values['change_risk'] = 3
        self.assertEqual(scoring.score(values), 45)
        record = {'scores': values, 'assessment_confidence': 'low'}
        self.assertEqual(scoring.review_flags(record),
                         ['verify_changeable_fact', 'low_assessment_confidence'])
        for invalid in (True, 4, -1, 1.5, '2', None):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                scoring.score({**values, 'exam_relevance': invalid})

    def test_fixed_boundaries_keep_equal_scores_together(self):
        self.assertEqual([scoring.classify(v) for v in (0, 39, 40, 41, 60)],
                         ['SKIP', 'SKIP', 'SUPPORTING', 'CORE', 'CORE'])
        values = [39] * 136 + [40] * 29 + [41] * 48
        self.assertEqual(scoring.distribution(values, (41, 40)),
                         {'CORE': 48, 'SUPPORTING': 29, 'SKIP': 136})
        self.assertEqual(scoring.distribution([45] * 10, scoring.DEFAULT_CUTOFFS),
                         {'CORE': 10, 'SUPPORTING': 0, 'SKIP': 0})
        for cutoffs in ((40, 41), (41, 41), (62, 40), (41, -1)):
            with self.subTest(cutoffs=cutoffs), self.assertRaises(ValueError):
                scoring.classify(45, *cutoffs)


class AssessmentIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helper = scoring.assessment_helper(scoring.ROOT)
        cls.index = cls.helper.source_index(scoring.ROOT)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='homebrew-card-tests-')
        self.addCleanup(self.temp.cleanup)
        self.data_dir = Path(self.temp.name)
        self.section_id = 'hb-c01-lage'
        self.section = self.index[0][self.section_id]
        self.ids = list(self.section['sentences'])[:3]
        records = []
        for identity, values in zip(self.ids, [(2, 2, 3, 3), (2, 2, 2, 2), (0, 0, 0, 0)]):
            records.append({
                'sentence_id': identity,
                'scores': dict(zip(scoring.WEIGHTS, values), change_risk=3),
                'fact_types': [], 'context_sentence_ids': [], 'duplicate_of': None,
                'assessment_confidence': 'low', 'rationale': 'Synthetic structural test fixture.',
            })
        self.document = {'schema_version': 1, 'section_id': self.section_id,
                         'source_sha256': self.section['source_sha256'], 'assessments': records}
        self.path = self.data_dir / f'{self.section_id}.yaml'
        self.save()

    def save(self):
        self.path.write_text(yaml.safe_dump(self.document), encoding='utf-8')

    def report(self, targets, **kwargs):
        with patch.object(scoring, 'assessment_helper', return_value=self.helper), \
                patch.object(self.helper, 'source_index', return_value=self.index):
            return scoring.make_report(scoring.ROOT, targets, data_dir=self.data_dir, **kwargs)

    def test_core_default_explicit_supporting_and_read_only(self):
        before = self.path.read_bytes()
        report = self.report(self.ids)
        self.assertEqual(report['selected_count'], 1)
        self.assertEqual(report['sentences'][0]['priority'], 'CORE')
        self.assertEqual(report['sentences'][0]['score'], 45)
        self.assertTrue(report['sentences'][0]['review_flags'])
        self.assertEqual(report['requested_counts'], {'CORE': 1, 'SUPPORTING': 1, 'SKIP': 1})
        expanded = self.report(self.ids, cutoffs=(41, 40), tiers=('CORE', 'SUPPORTING'))
        self.assertEqual(expanded['selected_count'], 2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_single_sentence_request_scores_only_that_sentence(self):
        one = self.report(self.ids[:1])
        three = self.report(self.ids)
        self.assertEqual(one['sentences'], three['sentences'])
        self.assertEqual(one['calibration']['mode'], 'fixed_cutoffs')
        self.assertEqual(one['calibration']['assessed_sentences'], 1)
        self.assertEqual(three['calibration']['assessed_sentences'], 3)
        self.assertEqual(one['requested_counts'], {'CORE': 1, 'SUPPORTING': 0, 'SKIP': 0})

    def test_unrelated_assessments_cannot_change_selection(self):
        before = self.report(self.ids)
        section_id = 'hb-c01-natur'
        section = self.index[0][section_id]
        record = {**self.document['assessments'][0],
                  'sentence_id': next(iter(section['sentences'])),
                  'scores': {key: 3 for key in self.document['assessments'][0]['scores']}}
        document = {'schema_version': 1, 'section_id': section_id,
                    'source_sha256': section['source_sha256'], 'assessments': [record]}
        (self.data_dir / f'{section_id}.yaml').write_text(yaml.safe_dump(document))
        self.assertEqual(self.report(self.ids), before)
        all_assessed = self.report([], all_assessed=True)
        self.assertEqual(all_assessed['calibration']['mode'], 'fixed_cutoffs')
        self.assertEqual(all_assessed['calibration']['assessed_sentences'], 4)
        self.assertEqual(all_assessed['calibration']['counts'],
                         {'CORE': 2, 'SUPPORTING': 1, 'SKIP': 1})

    def test_missing_and_stale_assessments_fail(self):
        with self.assertRaisesRegex(ValueError, 'assess-homebrew-sentences'):
            self.report([self.section_id])
        self.document['source_sha256'] = '0' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'stale source fingerprint'):
            self.report(self.ids)

    def test_invalid_unrelated_file_is_reported_only_with_all_assessed(self):
        (self.data_dir / 'unknown-section.yaml').write_text('schema_version: 1\n')
        report = self.report(self.ids)
        self.assertEqual(report['calibration']['assessed_sentences'], 3)
        self.assertEqual(report['excluded_invalid_files'], [])
        expanded = self.report([], all_assessed=True)
        self.assertEqual(len(expanded['excluded_invalid_files']), 1)


class CardExportTests(unittest.TestCase):
    def setUp(self):
        self.fields = ['Vilken färg har snö?', 'Test', '2', 'Vit', 'Blå', 'Röd', 'Grön',
                       '', '1 0 0 0', '2']

    def check(self, fields):
        return cards.validate_line('|'.join(fields), source=Path('test.txt'),
                                   line_num=1, category='Test')

    def test_length_boundaries_and_strict_format(self):
        boundary = self.fields.copy()
        boundary[0] = 'Å' * 120
        boundary[3] = 'Ö' * 70
        self.check(boundary)
        for index, value in ((0, 'Å' * 121), (3, 'Ö' * 71), (3, ''), (4, 'vit'),
                             (8, '1 1 0 0'), (8, '0 0 0 0'), (9, '1'),
                             (2, '1'), (1, 'Other'), (7, 'unexpected'), (3, ' Vit')):
            fields = self.fields.copy()
            fields[index] = value
            with self.subTest(index=index, value=value), self.assertRaises(ValueError):
                self.check(fields)
        with self.assertRaises(ValueError):
            self.check(self.fields + ['extra'])

    def test_duplicate_stems_and_real_kahoot_export(self):
        from openpyxl import load_workbook

        with tempfile.TemporaryDirectory(prefix='homebrew-kahoot-test-') as temp:
            root = Path(temp)
            path = root / 'cards/homebrew/hb-test/hb-test-section.txt'
            path.parent.mkdir(parents=True)
            row = '|'.join(self.fields) + '\n'
            path.write_text(row * 2, encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicate question'):
                cards.validate_file(path)
            path.write_text(row, encoding='utf-8')
            self.assertEqual(len(cards.validate_file(path, category='Test')), 1)
            export._ensure_kahoot_generator_importable(scoring.ROOT)
            outputs = export.export_deck(cards_path=path, out_root=root / 'kahoot',
                                         repo_root=root, time_limit=20)
            self.assertEqual(outputs, [root / 'kahoot/homebrew/hb-test/hb-test-section.xlsx'])
            workbook = load_workbook(outputs[0])
            self.assertEqual(workbook.active['B9'].value, self.fields[0])
            self.assertEqual(workbook.active['C9'].value, 'Vit')
            self.assertEqual(workbook.active['H9'].value, '1')
            workbook.close()


if __name__ == '__main__':
    unittest.main()
