"""Verify report counts against a small repository with incomplete resources."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import yaml

import homebrew_status as status
from study.app.translations import fingerprint


class HomebrewStatusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.chapter = {
            "id": "hb-c01", "title": "First chapter", "sections": [
                {"id": f"hb-c01-{slug}", "title": slug, "blocks": [
                    {"type": "list", "items": [
                        {"text": "One. Two.", "sentences": [
                            {"id": f"{slug}-s1", "start": 0, "end": 4},
                            {"id": f"{slug}-s2", "start": 5, "end": 9},
                        ]},
                    ]},
                ]}
                for slug in ("one", "two", "three")
            ],
        }
        self.put_yaml("data/homebrew/manifest.yaml", {"chapters": [
            {"id": "hb-c02", "order": 2, "path": "sv/two.yaml"},
            {"id": "hb-c01", "order": 1, "path": "sv/one.yaml"},
        ]})
        self.put_yaml("data/homebrew/sv/one.yaml", self.chapter)
        self.put_yaml("data/homebrew/sv/two.yaml", {"id": "hb-c02", "title": "Empty chapter", "sections": []})
        self.put_yaml("data/homebrew/ru/glossary.yaml", {"entries": []})
        self.translation("hb-c01", {"hb-c01": "First chapter"}, heading=True)
        for section in self.chapter["sections"]:
            slug = section["title"]
            self.translation(section["id"], {
                section["id"]: slug, f"{slug}-s1": "One.", f"{slug}-s2": "Two.",
            })

    def put(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def put_yaml(self, name, document):
        return self.put(name, yaml.safe_dump(document, allow_unicode=True))

    def translation(self, identity, source, *, heading=False):
        document = {
            "schema_version": 1, "language": "ru", "source_id": identity,
            "source_sha256": fingerprint(list(source.items())),
            "records": [{"source_id": key, "ru": "Translated text", "vocabulary": []} for key in source],
        }
        review = {
            "source_id": identity, "status": "complete", "review_mode": "independent",
            "reviewer": "test reviewer", "issues": [],
            "result_sha256": fingerprint(document, sort_keys=True),
            "glossary_sha256": fingerprint([], sort_keys=True),
            "checks": {key: True for key in (
                "fidelity", "one_to_one", "natural_russian", "vocabulary", "terminology", "headings",
            )},
        }
        kind = "headings" if heading else "sections"
        self.put_yaml(f"data/homebrew/ru/{kind}/{identity}.yaml", document)
        self.put_yaml(f"data/homebrew/ru/reviews/{identity}.yaml", review)

    def test_only_section_decks_and_matching_local_media_count(self):
        self.put("cards/homebrew/hb-c01/ALL.txt", "Combined deck\n")
        self.put("cards/homebrew/hb-c01/hb-c01-one.txt", "First card\nSecond card\n")
        self.put("cards/homebrew/hb-c01/hb-c01-two.txt", " \n\t\n")
        self.put("cards/homebrew/hb-c01/unknown.txt", "Unrelated deck\n")
        self.put("videos/homebrew/hb-c01-01-one.mp4", "video")
        self.put("videos/homebrew/hb-c01-01-one.ru.m4a", "audio")
        self.put("videos/homebrew/hb-c01-02-two.CREDITS.md", "Credits without a video")
        self.put("videos/homebrew/hb-c01-02-two.ru.m4a", "Orphan audio")
        self.put("videos/homebrew/hb-c01-03-three.mp4", "")
        self.put("videos/homebrew/hb-c01-99-three.mp4", "Wrong section number")
        rows = status.collect_status(self.root)
        self.assertEqual(rows, [
            status.ChapterStatus("1. First chapter", 3, 3, 1, 1, 1, [2, 0, 0]),
            status.ChapterStatus("2. Empty chapter"),
        ])

    def test_draft_stale_and_partial_translations_do_not_count(self):
        for change in ("draft", "stale", "missing_sentence", "blank", "missing_review"):
            with self.subTest(change=change):
                identity = "hb-c01-two"
                self.translation(identity, {identity: "two", "two-s1": "One.", "two-s2": "Two."})
                path = self.root / f"data/homebrew/ru/sections/{identity}.yaml"
                review_path = self.root / f"data/homebrew/ru/reviews/{identity}.yaml"
                document, review = status.read_yaml(path), status.read_yaml(review_path)
                if change == "draft":
                    review["status"] = "draft"
                elif change == "stale":
                    document["source_sha256"] = "old source"
                elif change == "missing_sentence":
                    document["records"].pop()
                elif change == "blank":
                    document["records"][1]["ru"] = " "
                review["result_sha256"] = fingerprint(document, sort_keys=True)
                self.put_yaml(str(path.relative_to(self.root)), document)
                self.put_yaml(str(review_path.relative_to(self.root)), review)
                if change == "missing_review":
                    review_path.unlink()
                self.assertEqual(status.collect_status(self.root)[0].translations, 2)

    def test_heading_and_glossary_are_required_for_reader_availability(self):
        for name in ("headings/hb-c01.yaml", "glossary.yaml"):
            with self.subTest(missing=name):
                path = self.root / "data/homebrew/ru" / name
                original = path.read_bytes()
                path.unlink()
                self.assertEqual(status.collect_status(self.root)[0].translations, 0)
                path.write_bytes(original)

    def test_packaged_media_requires_video_and_russian_audio_files(self):
        folder = "videos/homebrew/hb-c01-01-one"
        for name in ("master.m3u8", "video.m3u8", "video.m4s", "master-ru.m3u8", "ru.m3u8"):
            self.put(f"{folder}/{name}", "packaged media")
        row = status.collect_status(self.root)[0]
        self.assertEqual((row.videos, row.russian_audio), (1, 0))
        self.put(f"{folder}/ru.m4s", "Russian audio")
        self.assertEqual(status.collect_status(self.root)[0].russian_audio, 1)
        (self.root / folder / "video.m4s").unlink()
        row = status.collect_status(self.root)[0]
        self.assertEqual((row.videos, row.russian_audio), (0, 0))

    def test_wrapping_totals_colors_and_plain_output(self):
        rows = [status.ChapterStatus("1. A chapter title that needs wrapping " * 2, 8, 8, 4, 0, 0),
                status.ChapterStatus("2. Another chapter", 2, 2, 1, 2, 0)]
        output = status.render_report(rows, color=True, width=80)
        self.assertIn("\033[32m", output)
        self.assertIn("\033[33m", output)
        self.assertIn("\033[90m", output)
        clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
        table_lines = [line for line in clean.splitlines() if line.startswith(("\u2502", "\u256d", "\u251c", "\u2570"))]
        self.assertTrue(all(status.display_width(line) == 80 for line in table_lines))
        totals = next(line for line in table_lines if "Total" in line)
        for value in ("10/10", "5/10", "2/10", "0/10"):
            self.assertIn(value, totals)
        plain = status.render_report(rows, plain=True, color=True, width=80)
        self.assertTrue(plain.isascii())
        self.assertNotIn("\033", plain)
        self.assertIn("+ complete", plain)
        self.assertIn("~ some ready", plain)
        self.assertIn("- none yet", plain)

    def test_cli_is_read_only_and_no_color_is_respected(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        output = StringIO()
        with patch.object(status, "ROOT", self.root), patch.dict("os.environ", {"NO_COLOR": "1"}), \
                redirect_stdout(output), patch.object(output, "isatty", return_value=True):
            self.assertEqual(status.main([]), 0)
        self.assertNotIn("\033", output.getvalue())
        self.assertIn("Total", output.getvalue())
        after = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
