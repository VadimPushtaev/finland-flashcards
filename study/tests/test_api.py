"""Exercise real anthology fidelity, search and API/static routing."""
import unittest

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
