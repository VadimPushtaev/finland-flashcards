"""Focused extraction and coverage regression tests for the Homebrew work area."""

from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

import extract_sources
from validate_review import validate_coverage


class ExtractionTests(unittest.TestCase):
    """Protect substantive text while identifying page furniture and activities."""

    def test_article_glossary_activity_lists_and_table(self):
        html = '''<html><head><title>Rights</title></head><body>
        <nav><p>Navigation must not become lesson text.</p></nav>
        <div class="journal-content-article" data-analytics-asset-title="Rights - sanasto">
        <h2>Centrala begrepp</h2><p><b>Rätt:</b> En möjlighet.</p></div>
        <div class="journal-content-article" data-analytics-asset-title="Rights">
        <p>Åland har självstyre. <em>Alla</em> är lika.</p>
        <ul><li>En rätt.<p>En viktig begränsning.</p></li></ul>
        <table><tr><th>År</th><th>Händelse</th></tr><tr><td>1917</td><td>Självständighet</td></tr></table>
        <img src="/missing.svg" alt="Diagram"/></div>
        <div class="journal-content-article" data-analytics-asset-title="Rights - tehtäviä sv">
        <h2>Uppgifter</h2><p>Diskutera.</p></div></body></html>'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "page.html"
            path.write_text(html, encoding="utf-8")
            with patch.object(extract_sources, "ROOT", root):
                record = extract_sources.extract_html(path)
        blocks = record["blocks"]
        text = " ".join(b["text"] for b in blocks)
        self.assertNotIn("Navigation must", text)
        self.assertIn("Åland har självstyre. Alla är lika.", text)
        self.assertEqual(text.count("En viktig begränsning."), 1)
        self.assertEqual(next(b for b in blocks if b["text"] == "Rätt: En möjlighet.")["role"], "glossary")
        self.assertEqual(next(b for b in blocks if b["text"] == "Diskutera.")["role"], "activity")
        table = next(b for b in blocks if b["kind"] == "table")
        self.assertEqual(table["rows"][1], ["1917", "Självständighet"])
        self.assertFalse(record["images"][0]["downloaded"])
        original = BeautifulSoup(html, "html.parser")
        for block in blocks:
            self.assertIsNotNone(original.select_one(block["locator"]))

    def test_pdf_page_identity_and_unicode(self):
        root = Path(__file__).resolve().parents[3]
        record = extract_sources.extract_pdf(root / "news/files/valtioneuvosto_lag_andring_av_medborgarskapslagen_sv_2026-06-16.pdf")
        self.assertEqual(record["pages"][1]["pdf_page"], 2)
        text = record["pages"][1]["text"]
        self.assertIn("25 a §", text)
        self.assertIn("Medborgarskapsprovets innehåll", text)
        self.assertIn("mänskliga rättigheter", text)

    def test_real_article_keeps_rights_and_provenance(self):
        root = Path(__file__).resolve().parents[3]
        record = extract_sources.extract_html(root / "data/orientation/sv/laromedel/lag-och-ratt/individens-rattigheter-och-skyldigheter.html")
        self.assertTrue(any("Ingen får dömas till döden" in b["text"] for b in record["blocks"]))
        self.assertTrue(any(b["role"] == "glossary" for b in record["blocks"]))
        self.assertTrue(any(b["role"] == "activity" for b in record["blocks"]))
        self.assertTrue(record["source_url"].startswith("https://yhteiskuntaorientaatio.fi/sv/"))

    def test_legal_scope_quote_matches_archived_law(self):
        root = Path(__file__).resolve().parents[3]
        report = (root / "wip/homebrew/LEGAL_SCOPE.md").read_text(encoding="utf-8")
        quote = next(line[2:] for line in report.splitlines() if line.startswith("> Medborgarskapsprovet"))
        document = extract_sources.extract_pdf(root / "news/files/valtioneuvosto_lag_andring_av_medborgarskapslagen_sv_2026-06-16.pdf")
        self.assertIn(quote, extract_sources.normalize(document["pages"][1]["text"]))


class CoverageTests(unittest.TestCase):
    """Reject coverage gaps and unjustified routing rather than silently accepting them."""

    def setUp(self):
        self.outline = {"chapters": [{"id": "chapter"}]}
        self.coverage = {"counts": {"partial": 1}, "sources": [{
            "id": "source", "decision": "partial", "chapters": ["chapter"],
            "scope": ["rights"], "keep": "Legal protections", "omit": "CV formatting"}]}

    def test_missing_source_rejected(self):
        with self.assertRaises(AssertionError):
            validate_coverage(self.coverage, self.outline, {"source", "forgotten-source"})

    def test_bad_chapter_and_unexplained_cut_rejected(self):
        broken = copy.deepcopy(self.coverage)
        broken["sources"][0]["chapters"] = ["nonexistent"]
        with self.assertRaises(AssertionError):
            validate_coverage(broken, self.outline, {"source"})
        broken = copy.deepcopy(self.coverage)
        del broken["sources"][0]["omit"]
        with self.assertRaises(AssertionError):
            validate_coverage(broken, self.outline, {"source"})


if __name__ == "__main__":
    unittest.main()
