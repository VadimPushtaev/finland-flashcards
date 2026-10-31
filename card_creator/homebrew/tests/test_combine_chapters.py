"""Check chapter aggregation, read-only freshness checks and export selection."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from card_creator.combine_all_cards import list_card_files
from card_creator.homebrew.combine_chapters import combine_chapters
from card_creator.kahoot import export


class ChapterDeckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="homebrew-combine-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cards = self.root / "cards/homebrew"
        self.data = self.root / "data/homebrew"
        self.data.mkdir(parents=True)
        chapters = []
        for chapter_id in ("hb-c01", "hb-c02", "hb-c03"):
            chapter_path = f"{chapter_id}.yaml"
            chapters.append({"id": chapter_id, "path": chapter_path})
            # Book order deliberately differs from filename order.
            document = {"sections": [{"id": f"{chapter_id}-zeta"},
                                     {"id": f"{chapter_id}-alpha"}]}
            (self.data / chapter_path).write_text(yaml.safe_dump(document), encoding="utf-8")
        (self.data / "manifest.yaml").write_text(yaml.safe_dump({"chapters": chapters}), encoding="utf-8")

    def write_deck(self, chapter, name, content):
        path = self.cards / chapter / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
        return path

    def run_combine(self, *, check=False):
        with redirect_stdout(StringIO()):
            return combine_chapters(self.root, check=check)

    def test_chapters_are_isolated_ordered_and_idempotent(self):
        first = "Fraga A|Kategori|2|A|B|C|D||1 0 0 0|2"
        second = "Fraga B|Kategori|2|A|B|C|D||0 1 0 0|2"
        third = "Fraga C|Kategori|2|A|B|C|D||0 0 1 0|2"
        self.write_deck("hb-c01", "hb-c01-alpha.txt", second + "\r\n\r\n")
        self.write_deck("hb-c01", "hb-c01-zeta.txt", first)
        out = self.write_deck("hb-c01", "ALL.txt", "old aggregate must not be input\n")
        self.write_deck("hb-c02", "hb-c02-alpha.txt", third + "\n")
        self.assertEqual(self.run_combine(), 0)
        self.assertEqual(out.read_bytes(), (first + "\n" + second + "\n").encode("utf-8"))
        self.assertEqual((self.cards / "hb-c02/ALL.txt").read_bytes(), (third + "\n").encode("utf-8"))
        self.assertFalse((self.cards / "hb-c03/ALL.txt").exists())
        before = out.read_bytes()
        self.assertEqual(self.run_combine(), 0)
        self.assertEqual(out.read_bytes(), before)
        self.assertEqual(self.run_combine(check=True), 0)
        # Chapter aggregates and their inputs remain excluded from the global deck.
        legacy = self.root / "cards/legacy.txt"
        legacy.write_text(first + "\n", encoding="utf-8")
        self.assertEqual(list_card_files(self.root / "cards"), [legacy])

    def test_check_detects_missing_and_stale_outputs_without_writing(self):
        source = self.write_deck("hb-c01", "hb-c01-zeta.txt", "first\n")
        out = source.parent / "ALL.txt"
        self.assertEqual(self.run_combine(check=True), 1)
        self.assertFalse(out.exists())
        self.run_combine()
        source.write_text("changed\n", encoding="utf-8")
        self.assertEqual(self.run_combine(check=True), 1)
        self.assertEqual(out.read_bytes(), b"first\n")
        self.assertEqual(self.run_combine(), 0)
        self.assertEqual(out.read_bytes(), b"changed\n")

    def test_empty_chapters_and_obsolete_outputs(self):
        self.assertEqual(self.run_combine(check=True), 0)
        source = self.write_deck("hb-c01", "hb-c01-zeta.txt", "first\n")
        self.run_combine()
        out = source.parent / "ALL.txt"
        source.unlink()
        self.assertEqual(self.run_combine(check=True), 1)
        self.assertTrue(out.exists())
        self.assertEqual(self.run_combine(), 0)
        self.assertFalse(out.exists())
        self.write_deck("hb-c02", "hb-c02-alpha.txt", "\n\n")
        self.assertEqual(self.run_combine(), 0)
        self.assertFalse((self.cards / "hb-c02/ALL.txt").exists())

    def test_unknown_decks_fail_before_any_output_is_written(self):
        self.write_deck("hb-c01", "hb-c01-zeta.txt", "first\n")
        self.write_deck("hb-c02", "misspelled-section.txt", "second\n")
        with self.assertRaisesRegex(ValueError, "Unknown section decks"):
            self.run_combine()
        self.assertFalse((self.cards / "hb-c01/ALL.txt").exists())

    def test_kahoot_skips_all_aggregates_unless_requested(self):
        section = self.write_deck("hb-c01", "hb-c01-zeta.txt", "first\n")
        combined = self.write_deck("hb-c01", "ALL.txt", "first\n")
        global_deck = self.root / "cards/ALL.txt"
        global_deck.write_text("legacy\n", encoding="utf-8")

        def fake_export(**kwargs):
            relative = kwargs["cards_path"].relative_to(self.root / "cards")
            return [kwargs["out_root"] / relative.with_suffix(".xlsx")]

        for args, expected in (([], {section}),
                               (["--include-all"], {section, combined, global_deck}),
                               (["--cards-dir", "cards/homebrew"], {section}),
                               (["--include-all", "--skip-all"], {section})):
            with self.subTest(args=args), \
                    patch.object(export, "_repo_root", return_value=self.root), \
                    patch.object(export, "_ensure_kahoot_generator_importable"), \
                    patch.object(export, "export_deck", side_effect=fake_export) as exporter, \
                    redirect_stdout(StringIO()):
                self.assertEqual(export.main(args), 0)
                self.assertEqual({call.kwargs["cards_path"] for call in exporter.call_args_list}, expected)


if __name__ == "__main__":
    unittest.main()
