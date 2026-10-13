"""Exercise real anthology fidelity, search and API/static routing."""
import unittest
from unittest.mock import patch
from copy import deepcopy

from fastapi.testclient import TestClient
from app.main import app, DATA_DIR, read_yaml


class StudyApiTests(unittest.TestCase):
    """Keep the reader tied to the actual archived collection."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_all_chapters_keep_exact_original_sections(self):
        manifest = read_yaml(DATA_DIR / "manifest.yaml")
        listing = self.client.get("/api/library").json()
        self.assertEqual(len(listing["chapters"]), 12)
        for entry in manifest["chapters"]:
            with self.subTest(chapter=entry["id"]):
                response = self.client.get(f'/api/chapters/{entry["id"]}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["sections"], read_yaml(DATA_DIR / entry["path"])["sections"])

    def test_reviewed_translation_matches_exact_sentences_and_spans(self):
        result = self.client.get('/api/chapters/hb-c01/sections/hb-c01-lage/translation').json()
        self.assertTrue(result['available'])
        self.assertEqual(len(result['records']), 16)
        for record in result['records'].values():
            self.assertTrue(record['ru'])
            for word in record['vocabulary']:
                for span in word['spans']:
                    self.assertEqual(record['sv'][span['start']:span['end']], span['text'])
        def missing_translation(path):
            if path.parent.name == 'sections' and path.name == 'hb-c01-regioner.yaml':
                raise FileNotFoundError(path)
            return read_yaml(path)
        with patch('app.main.read_yaml', side_effect=missing_translation):
            missing = self.client.get('/api/chapters/hb-c01/sections/hb-c01-regioner/translation').json()
        self.assertFalse(missing['available'])
        self.assertEqual(missing['records'], {})
        self.assertEqual(self.client.get('/api/chapters/hb-c01/sections/hb-c02-forhistoria/translation').status_code, 404)

    def test_chapter_one_translation_status_and_sentence_coverage(self):
        chapter = self.client.get('/api/chapters/hb-c01').json()
        for section in chapter['sections']:
            with self.subTest(section=section['id']):
                review = read_yaml(DATA_DIR / 'ru/reviews' / f"{section['id']}.yaml")
                result = self.client.get(f"/api/chapters/hb-c01/sections/{section['id']}/translation").json()
                self.assertEqual(result['available'], review['status'] == 'complete')
                if result['available']:
                    expected = {chapter['id'], section['id']}
                    for block in section['blocks']:
                        for unit in block.get('items', [block]):
                            expected.update(sentence['id'] for sentence in unit['sentences'])
                    self.assertEqual(set(result['records']), expected)

    def test_draft_or_changed_translation_is_not_published(self):
        for change in ('draft', 'text', 'source', 'glossary'):
            def changed_read(path):
                data = deepcopy(read_yaml(path))
                if path.name == 'hb-c01-lage.yaml' and path.parent.name == 'reviews' and change == 'draft':
                    data['status'] = 'draft'
                if path.name == 'hb-c01-lage.yaml' and path.parent.name == 'sections':
                    if change == 'text':
                        data['records'][0]['ru'] = 'Unreviewed text'
                    if change == 'source':
                        data['source_sha256'] = 'stale'
                if path.name == 'glossary.yaml' and change == 'glossary':
                    data['entries'][0]['ru'] = 'Changed glossary'
                return data
            with self.subTest(change=change), patch('app.main.read_yaml', side_effect=changed_read):
                response = self.client.get('/api/chapters/hb-c01/sections/hb-c01-lage/translation')
                self.assertEqual(response.status_code, 200)
                self.assertFalse(response.json()['available'])

    def test_swedish_search_is_case_insensitive_and_paginates(self):
        lower = self.client.get("/api/search", params={"q": "rösträtt", "limit": 2}).json()
        upper = self.client.get("/api/search", params={"q": "RÖSTRÄTT", "limit": 2}).json()
        self.assertEqual(lower, {**upper, "query": "rösträtt"})
        self.assertGreater(lower["total"], 2)
        next_page = self.client.get("/api/search", params={"q": "rösträtt", "limit": 2, "offset": 2}).json()
        self.assertTrue(set(r["unit_id"] for r in lower["results"]).isdisjoint(r["unit_id"] for r in next_page["results"]))
        for result in lower["results"]:
            resolved = self.client.get(f'/api/passages/{result["unit_id"]}').json()
            self.assertEqual(resolved, result)

    def test_search_requires_all_terms_and_bounds_requests(self):
        result = self.client.get("/api/search", params={"q": "Finland barn"}).json()
        self.assertTrue(result["results"])
        for unit in result["results"]:
            self.assertIn("finland", unit["text"].casefold())
            self.assertIn("barn", unit["text"].casefold())
        self.assertEqual(self.client.get("/api/search", params={"q": "a"}).status_code, 422)
        self.assertEqual(self.client.get("/api/search", params={"q": "Finland", "limit": 1000}).status_code, 422)

    def test_unknown_ids_and_api_routes_do_not_return_spa_html(self):
        for route in ["/api/chapters/missing", "/api/passages/missing", "/api/missing"]:
            self.assertEqual(self.client.get(route).status_code, 404)

    def test_credits_and_passage_sources_are_available(self):
        self.assertEqual(set(self.client.get("/api/sources").json()), {"orientation", "infofinland", "textbook"})
        sources = self.client.get("/api/chapters/hb-c01/sources").json()
        self.assertIn("hb-c01-u0001", sources)
        self.assertTrue(sources["hb-c01-u0001"]["title"])
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok", "chapters": 12})


if __name__ == "__main__":
    unittest.main()
