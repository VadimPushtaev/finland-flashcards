"""Meaningful regression checks for passage fidelity, identity and content structure."""

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from build_pilot import (CHAPTER_FILE, DEST, WORK, build, load_sources,
                         read_yaml, sentence_ranges)
from validate_pilot import validate_chapter, verify_provenance


def leaf(identity, text):
    """Create a small sentence-bearing fixture."""
    return {"id": identity, "text": text, "sentences": [
        {"id": identity + "-s001", "start": 0, "end": len(text)}]}


class SentenceTests(unittest.TestCase):
    """Use Unicode code points and protect meaningful Swedish punctuation."""

    def test_abbreviations_initials_decimals_quotes_and_fragments(self):
        text = 'Åsa möter A. Lind kl. 12.30 den 12.10.2026. Hon nämner t.ex. Åland. ”Ja!” Nästa rad'
        self.assertEqual([text[a:b] for a, b in sentence_ranges(text)], [
            'Åsa möter A. Lind kl. 12.30 den 12.10.2026.',
            'Hon nämner t.ex. Åland.', '”Ja!”', 'Nästa rad'])
        text = 'Flerfaldigt, d.v.s. flera medborgarskap. Nästa mening.'
        self.assertEqual([text[a:b] for a, b in sentence_ranges(text)], [
            'Flerfaldigt, d.v.s. flera medborgarskap.', 'Nästa mening.'])

    def test_unicode_and_multiline_offsets(self):
        text = 'Åland är en ö.\n\nNästa mening 😀.'
        spans = sentence_ranges(text)
        self.assertEqual(spans, [(0, 14), (16, len(text))])
        self.assertEqual(text[spans[1][0]:spans[1][1]], 'Nästa mening 😀.')


class PilotTests(unittest.TestCase):
    """Reject plausible-looking corruptions and preserve identity on reordering."""

    @classmethod
    def setUpClass(cls):
        cls.chapter = read_yaml(DEST / CHAPTER_FILE)
        cls.registry = read_yaml(WORK / "pilot_sentences.yaml")
        cls.selection = read_yaml(WORK / "pilot_selection.yaml")
        cls.documents = load_sources()

    def test_build_matches_committed_pilot(self):
        chapter, _ = build(self.selection, copy.deepcopy(self.registry), self.documents)
        self.assertEqual(chapter, self.chapter)

    def test_reordering_preserves_all_ids_and_sentence_ranges(self):
        selection = copy.deepcopy(self.selection)
        selection["sections"].reverse()
        for section in selection["sections"]:
            section["blocks"].reverse()
        chapter, _ = build(selection, copy.deepcopy(self.registry), self.documents)
        before, _, _ = validate_chapter(self.chapter)
        after, _, _ = validate_chapter(chapter)
        self.assertEqual(before, after)

    def test_changed_text_requires_explicit_id_migration(self):
        registry = copy.deepcopy(self.registry)
        registry["units"][next(iter(registry["units"]))]["text_sha256"] = "changed"
        with self.assertRaisesRegex(AssertionError, "Text changed"):
            build(self.selection, registry, self.documents, initialize=True)

    def test_missing_text_sentence_gaps_and_duplicate_ids_rejected(self):
        for corrupt in ["gap", "overlap", "duplicate", "metadata"]:
            chapter = copy.deepcopy(self.chapter)
            paragraph = chapter["sections"][0]["blocks"][0]
            if corrupt == "gap":
                paragraph["sentences"][0]["start"] = 1
            elif corrupt == "overlap":
                paragraph["sentences"][1]["start"] = 0
            elif corrupt == "duplicate":
                paragraph["sentences"][1]["id"] = paragraph["sentences"][0]["id"]
            else:
                paragraph["source_url"] = "Source metadata does not belong in reading content"
            with self.subTest(corrupt=corrupt), self.assertRaises(AssertionError):
                validate_chapter(chapter)

    def test_provenance_checks_real_bytes_and_exact_words(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "data/infofinland/content/example.html"
            path.parent.mkdir(parents=True)
            path.write_text('<p>Alla har rätt. Ingen glöms.</p>', encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            text = 'Alla har rätt. Ingen glöms.'
            unit = leaf('hb-test-unit', text)
            source = {"path": path.relative_to(root).as_posix(), "sha256": digest}
            origin = {"source_path": source["path"], "sha256": digest,
                      "normalization": "whitespace_only", "repairs": [],
                      "range_basis": "normalized_html_block", "source_role": "content",
                      "locator": "p", "source_range": {"start": 0, "end": len(text)},
                      "extracted_passage": text}
            provenance = {"units": {unit["id"]: origin}}
            sources = {"sources": [source]}
            verify_provenance({unit["id"]: unit}, provenance, sources, root)
            unit["text"] = text.replace('Alla', 'Några')
            with self.assertRaisesRegex(AssertionError, 'Source mismatch'):
                verify_provenance({unit["id"]: unit}, provenance, sources, root)
            unit["text"] = text
            path.write_text('<p>Changed source</p>', encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_provenance({unit["id"]: unit}, provenance, sources, root)

    def test_tables_ordered_lists_and_local_image_shapes(self):
        table = {"id": "hb-test-table", "type": "table", "header_rows": 1,
                 "rows": [[leaf('hb-test-header', 'År')], [leaf('hb-test-cell', '2000')]]}
        ordered = {"id": "hb-test-list", "type": "list", "ordered": True,
                   "items": [leaf('hb-test-item', 'En punkt.') ]}
        chapter = {"schema_version": 1, "id": "hb-test", "language": "sv", "title": "Prov",
                   "sections": [{"id": "hb-test-section", "title": "Del", "blocks": [table, ordered]}]}
        validate_chapter(chapter)
        table["rows"][1].append(leaf('hb-test-extra', 'Extra'))
        with self.assertRaises(AssertionError):
            validate_chapter(chapter)
        table["rows"][1].pop()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'assets').mkdir()
            (root / 'assets/figure.svg').write_text('<svg/>', encoding='utf-8')
            image = {"id": "hb-test-image", "type": "image", "path": "assets/figure.svg", "alt": "Figur"}
            chapter["sections"][0]["blocks"].append(image)
            validate_chapter(chapter, root)
            image["path"] = "../outside.svg"
            with self.assertRaises(AssertionError):
                validate_chapter(chapter, root)


if __name__ == "__main__":
    unittest.main()
