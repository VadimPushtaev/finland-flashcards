"""Prevent text cards, background duplication and short-scene quota gaming."""
import copy
import unittest

from studio.tools.picture_coverage import measure


class PictureCoverageTests(unittest.TestCase):
    def setUp(self):
        self.script = {'render': {'background_image': 'background.jpg'}, 'sentences': [
            {'sentence_id': 'a', 'render_image': 'photo.jpg'},
            {'sentence_id': 'b', 'render_image': 'card.png'},
        ]}
        self.assets = [
            {'kind': 'background', 'source_url': 'background-source',
             'files': [{'path': 'background.jpg', 'sha256': 'background'}]},
            {'kind': 'foreground', 'visual_type': 'photograph', 'source_url': 'photo-source',
             'files': [{'path': 'photo.jpg', 'sha256': 'photo'}]},
            {'kind': 'foreground', 'visual_type': 'text_card',
             'files': [{'path': 'card.png', 'sha256': 'card'}]},
        ]
        self.timeline = [{'kind': 'title', 'frames': 1000},
                         {'kind': 'sentence', 'sentence_id': 'a', 'frames': 24},
                         {'kind': 'sentence', 'sentence_id': 'b', 'frames': 216},
                         {'kind': 'credits', 'frames': 1000}]

    def test_uses_duration_not_sentence_count_and_excludes_title_credits(self):
        report = measure(self.script, self.assets, self.timeline, 24)
        self.assertEqual(report['picture_sentences'], 1)
        self.assertEqual(report['body_seconds'], 10)
        self.assertEqual(report['picture_fraction'], .1)
        self.assertFalse(report['meets_target'])

    def test_background_duplicate_and_unclassified_card_do_not_count(self):
        self.assets[1]['files'][0]['sha256'] = 'background'
        self.assets[2].pop('visual_type')
        self.assertEqual(measure(self.script, self.assets, self.timeline, 24)['picture_seconds'], 0)
        self.assets[1]['files'][0]['sha256'] = 'recropped-background'
        self.assets[1]['source_url'] = 'background-source'
        self.assertEqual(measure(self.script, self.assets, self.timeline, 24)['picture_seconds'], 0)

    def test_missing_asset_and_reordered_timeline_fail(self):
        with self.assertRaisesRegex(ValueError, 'Unregistered'):
            measure(self.script, self.assets[:2], self.timeline, 24)
        timeline = copy.deepcopy(self.timeline)
        timeline[1], timeline[2] = timeline[2], timeline[1]
        with self.assertRaisesRegex(ValueError, 'source order'):
            measure(self.script, self.assets, timeline, 24)

    def test_file_level_map_classification_and_exact_half(self):
        self.assets[2]['files'][0]['visual_type'] = 'map'
        self.script['sentences'][0]['render_image'] = None
        self.timeline[1]['frames'] = 216
        self.assertTrue(measure(self.script, self.assets, self.timeline, 24)['meets_target'])


if __name__ == '__main__':
    unittest.main()
