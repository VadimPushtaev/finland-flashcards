"""Canonical Homebrew YAML must reproduce every checked-in legacy TXT byte."""
import tempfile
import unittest
from pathlib import Path

from card_creator.homebrew.render_decks import rendered_decks, render, ROOT


class CanonicalCardTests(unittest.TestCase):
    def test_every_existing_section_deck_matches_generated_yaml(self):
        generated = rendered_decks(ROOT)
        self.assertEqual(len(generated), 184)
        self.assertEqual(sum(len(data.splitlines()) for data in generated.values()), 1034)
        for path, data in generated.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_bytes(), data)
        self.assertEqual(render(ROOT, check=True), 0)

    def test_check_mode_reports_drift_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data/homebrew/cards").mkdir(parents=True)
            (root / "data/homebrew/sv").mkdir(parents=True)
            (root / "cards/homebrew/hb-c01").mkdir(parents=True)
            (root / "data/homebrew/manifest.yaml").write_text(
                "chapters:\n- id: hb-c01\n  path: sv/chapter.yaml\n")
            (root / "data/homebrew/sv/chapter.yaml").write_text(
                "sections:\n- id: hb-c01-test\n  title: Test\n")
            (root / "data/homebrew/cards/hb-c01.yaml").write_text(
                'schema_version: 1\nchapter_id: hb-c01\nlanguage: sv\ncards:\n'
                '- id: hb-c01-test-0001\n  section_id: hb-c01-test\n  category: Test\n'
                '  question: What?\n  options:\n'
                '  - {id: a0, text: A}\n  - {id: a1, text: B}\n'
                '  - {id: a2, text: C}\n  - {id: a3, text: D}\n'
                '  correct_option_id: a1\n')
            output = root / "cards/homebrew/hb-c01/hb-c01-test.txt"
            self.assertEqual(render(root, check=True), 1)
            self.assertFalse(output.exists())
            self.assertEqual(render(root), 0)
            self.assertEqual(render(root, check=True), 0)
            self.assertEqual(output.read_text(), 'What?|Test|2|A|B|C|D||0 1 0 0|2\n')


if __name__ == "__main__":
    unittest.main()
