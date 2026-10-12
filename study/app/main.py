"""Serve the archived Swedish anthology and the compiled study frontend."""
from functools import lru_cache
import math
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yaml

DATA_DIR = Path(os.environ.get("HOMEBREW_DATA_DIR", Path(__file__).resolve().parents[2] / "data/homebrew"))
STATIC_DIR = Path(os.environ.get("HOMEBREW_STATIC_DIR", Path(__file__).resolve().parents[1] / "frontend/dist"))
app = FastAPI(title="Homebrew study", docs_url=None, redoc_url=None)


def read_yaml(path):
    """Read an archived document without modifying it."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def units(section):
    """Yield complete paragraphs and list items in their original order."""
    for block in section["blocks"]:
        yield from block.get("items", [block])


@lru_cache(maxsize=1)
def library():
    """Load the fixed collection once, including a searchable passage index."""
    manifest = read_yaml(DATA_DIR / "manifest.yaml")
    chapters, passages = {}, []
    for entry in manifest["chapters"]:
        chapter = read_yaml(DATA_DIR / entry["path"])
        chapter["order"] = entry["order"]
        chapter["word_count"] = sum(len(u["text"].split()) for s in chapter["sections"] for u in units(s))
        chapter["minutes"] = math.ceil(chapter["word_count"] / 200)
        chapters[chapter["id"]] = chapter
        for section in chapter["sections"]:
            for unit in units(section):
                passages.append({"chapter_id": chapter["id"], "chapter_title": chapter["title"],
                                 "order": chapter["order"], "section_id": section["id"],
                                 "section_title": section["title"], "unit_id": unit["id"], "text": unit["text"]})
    return manifest, chapters, passages


@app.get("/api/health")
def health():
    """Check that the collection can be loaded, not merely that Python runs."""
    _, chapters, _ = library()
    return {"status": "ok", "chapters": len(chapters)}


@app.get("/api/library")
def collection():
    """Return a compact chapter and section index."""
    manifest, chapters, _ = library()
    return {"title": manifest["title"], "language": manifest["language"], "chapters": [
        {"id": c["id"], "order": c["order"], "title": c["title"], "minutes": c["minutes"],
         "word_count": c["word_count"], "sections": [{"id": s["id"], "title": s["title"]} for s in c["sections"]]}
        for c in chapters.values()]}


@app.get("/api/chapters/{chapter_id}")
def get_chapter(chapter_id: str):
    """Return verbatim reader content, including its stable IDs."""
    _, chapters, _ = library()
    if chapter_id not in chapters:
        raise HTTPException(404, "Kapitlet finns inte.")
    return chapters[chapter_id]


@app.get("/api/search")
def search(q: str = Query(min_length=2, max_length=120), limit: int = Query(default=40, ge=1, le=100),
           offset: int = Query(default=0, ge=0)):
    """Match all query terms, preserving complete original text in results."""
    _, _, passages = library()
    terms = q.casefold().split()
    matches = [p for p in passages if all(term in p["text"].casefold() for term in terms)] if terms else []
    return {"query": q, "total": len(matches), "results": matches[offset:offset + limit]}


@app.get("/api/passages/{unit_id}")
def get_passage(unit_id: str):
    """Resolve bookmarks directly without fetching every chapter."""
    _, _, passages = library()
    passage = next((p for p in passages if p["unit_id"] == unit_id), None)
    if passage is None:
        raise HTTPException(404, "Textstycket finns inte.")
    return passage


@app.get("/api/sources")
def sources():
    """Preserve the collection's credits, original links and reuse terms."""
    return read_yaml(DATA_DIR / "metadata/attribution.yaml")["sources"]


@app.get("/api/chapters/{chapter_id}/sources")
def chapter_sources(chapter_id: str):
    """Return exact source locations for optional source inspection."""
    get_chapter(chapter_id)
    number = chapter_id.removeprefix("hb-c")
    provenance = read_yaml(DATA_DIR / f"metadata/{number}_provenance.yaml")["units"]
    records = {s["path"]: s for s in read_yaml(DATA_DIR / "metadata/sources.yaml")["sources"]}
    return {identity: {"title": records[u["source_path"]].get("title", "Finland – Lärobok i samhällsorientering"),
                       "url": records[u["source_path"]].get("source_url"),
                       "group": records[u["source_path"]]["source_group"],
                       "page": u.get("printed_page"), "heading": u.get("heading")}
            for identity, u in provenance.items()}


if (STATIC_DIR / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/{path:path}")
def frontend(path: str):
    """Serve SPA routes while keeping unknown API paths genuine 404s."""
    if path.startswith("api/"):
        raise HTTPException(404, "Endpoint not found")
    if not (STATIC_DIR / "index.html").is_file():
        raise HTTPException(503, "Build the frontend with npm run build, or use the Vite dev server.")
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})
