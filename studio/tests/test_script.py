"""Regression checks for source fidelity and safe episode authoring."""
import copy
from pathlib import Path
import tempfile
import unittest

from studio.tools import script as workflow


class ScriptTests(unittest.TestCase):
    """Exercise real reviewed source content without mutating the repository."""

    @classmethod
    def setUpClass(cls):
        cls.context = workflow.load_context('hb-c01-lage')
        cls.episode = workflow.read(
            workflow.ROOT / 'studio/episodes/hb-c01-lage/script.yaml')

    def setUp(self):
        self.script = copy.deepcopy(self.episode)

    def test_complete_episode(self):
        workflow.validate(self.script, self.context, ready=True)

    def test_missing_duplicate_and_reordered_sentences(self):
        for mutation in ('missing', 'duplicate', 'reordered'):
            with self.subTest(mutation=mutation):
                candidate = copy.deepcopy(self.script)
                rows = candidate['sentences']
                if mutation == 'missing':
                    rows.pop()
                elif mutation == 'duplicate':
                    rows.append(copy.deepcopy(rows[0]))
                else:
                    rows[0], rows[1] = rows[1], rows[0]
                with self.assertRaisesRegex(ValueError, 'sentence ID'):
                    workflow.validate(candidate, self.context, ready=True)

    def test_altered_swedish_or_russian(self):
        for language in ('sv', 'ru'):
            with self.subTest(language=language):
                candidate = copy.deepcopy(self.script)
                candidate['sentences'][0][language] += ' altered'
                with self.assertRaisesRegex(ValueError, 'Changed Swedish or Russian'):
                    workflow.validate(candidate, self.context, ready=True)

    def test_stale_fingerprints(self):
        for key in ('source_section_sha256', 'translation_file_sha256'):
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.script)
                candidate[key] = '0' * 64
                with self.assertRaisesRegex(ValueError, key):
                    workflow.validate(candidate, self.context, ready=True)

    def test_partial_example_cannot_be_production(self):
        self.script['example_only'] = True
        with self.assertRaisesRegex(ValueError, 'partial example'):
            workflow.validate(self.script, self.context)

    def test_unknown_asset_and_missing_fallback(self):
        self.script['sentences'][0]['asset_ids'] = ['nonexistent']
        with self.assertRaisesRegex(ValueError, 'Unknown asset'):
            workflow.validate(self.script, self.context, ready=True)
        self.script = copy.deepcopy(self.episode)
        self.script['asset_requests'][0]['fallback'] = ''
        with self.assertRaisesRegex(ValueError, 'fallback'):
            workflow.validate(self.script, self.context, ready=True)

    def test_highlight_cannot_introduce_new_text(self):
        self.script['sentences'][0]['text_highlights'] = ['Invented population: 100']
        with self.assertRaisesRegex(ValueError, 'Highlight'):
            workflow.validate(self.script, self.context, ready=True)

    def test_segment_cannot_drop_translation(self):
        row = self.script['sentences'][0]
        row['display_segments'] = [dict(sv=row['sv'], ru='')]
        with self.assertRaisesRegex(ValueError, 'segments.*ru'):
            workflow.validate(self.script, self.context, ready=True)

    def test_reversed_timing(self):
        row = self.script['sentences'][0]
        row.update(start_seconds=3, end_seconds=2)
        with self.assertRaisesRegex(ValueError, 'audio timing'):
            workflow.validate(self.script, self.context, ready=True)

    def test_empty_visual_plan_is_not_ready(self):
        self.script['sentences'][0]['visual_cue'] = ''
        with self.assertRaisesRegex(ValueError, 'visual plan'):
            workflow.validate(self.script, self.context, ready=True)

    def test_scene_order_is_checked(self):
        self.script['scenes'].reverse()
        with self.assertRaisesRegex(ValueError, 'consecutive'):
            workflow.validate(self.script, self.context, ready=True)

    def test_unresolved_script_decision_is_not_ready(self):
        self.script['episode_decisions'][0]['status'] = 'deferred'
        with self.assertRaisesRegex(ValueError, 'Unresolved script-stage'):
            workflow.validate(self.script, self.context, ready=True)

    def test_speech_expansion_needs_reason(self):
        self.script['sentences'][0]['speech_override'] = dict(
            text='Different TTS input', reason='', review_status='pending')
        with self.assertRaisesRegex(ValueError, 'text and reason'):
            workflow.validate(self.script, self.context, ready=True)

    def test_initializer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            episode = Path(directory) / 'episode'
            workflow.initialize(self.context, episode)
            script_path = episode / 'script.yaml'
            script_path.write_text('editorial work to preserve', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                workflow.initialize(self.context, episode)
            self.assertEqual(script_path.read_text(), 'editorial work to preserve')

    def test_scaffold_requires_editorial_work(self):
        candidate = workflow.scaffold(self.context)
        workflow.validate(candidate, self.context)
        with self.assertRaisesRegex(ValueError, 'visual plan'):
            workflow.validate(candidate, self.context, ready=True)
        self.assertEqual(len(candidate['sentences']), 14)

    def test_readable_copy_preserves_all_text_and_is_deterministic(self):
        document = workflow.review_markdown(self.script, self.context)
        self.assertEqual(document, workflow.review_markdown(self.script, self.context))
        for row in self.script['sentences']:
            self.assertIn(row['sv'], document)
            self.assertIn(row['ru'], document)
        self.assertIn('source-validated script', document)


if __name__ == '__main__':
    unittest.main()
