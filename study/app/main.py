"""Serve the archived Swedish anthology and the compiled study frontend."""
from functools import lru_cache
import math
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yaml

from app.translations import reviewed_records
from app.database import database
from app.auth import install_routes

DATA_DIR = Path(os.environ.get("HOMEBREW_DATA_DIR", Path(__file__).resolve().parents[2] / "data/homebrew"))
STATIC_DIR = Path(os.environ.get("HOMEBREW_STATIC_DIR", Path(__file__).resolve().parents[1] / "frontend/dist"))
VIDEO_DIR = Path(os.environ.get("HOMEBREW_VIDEO_DIR", Path(__file__).resolve().parents[2] / "videos/homebrew"))
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
    with database() as db:
        db.execute('SELECT 1 FROM users LIMIT 1').fetchone()
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
    chapter = chapters[chapter_id]
    videos = {}
    for section in chapter["sections"]:
        path = video_path(chapter, section["id"])
        if path.is_file():
            base = f'/api/chapters/{chapter_id}/sections/{section["id"]}'
            videos[section["id"]] = {"url": base + "/video",
                                     "credits_url": base + "/video/credits" if path.with_suffix(".CREDITS.md").is_file() else None}
    return {**chapter, "videos": videos}


def video_path(chapter, section_id):
    """Resolve an export from a known section's number and stable slug."""
    for number, section in enumerate(chapter["sections"], 1):
        if section["id"] == section_id:
            slug = section_id.removeprefix(chapter["id"] + "-")
            return VIDEO_DIR / f'{chapter["id"]}-{number:02d}-{slug}.mp4'
    raise HTTPException(404, "Avsnittet finns inte.")


@app.get("/api/chapters/{chapter_id}/sections/{section_id}/video")
@app.get("/api/chapters/{chapter_id}/sections/{section_id}/video/credits")
def section_video(chapter_id: str, section_id: str, request: Request):
    """Serve available exports with byte-range support for seeking."""
    path = video_path(get_chapter(chapter_id), section_id)
    if not path.is_file():
        raise HTTPException(404, "Videon finns inte.")
    credits = request.url.path.endswith("/credits")
    if credits:
        path = path.with_suffix(".CREDITS.md")
    if not path.is_file():
        raise HTTPException(404, "Videons källor finns inte.")
    return FileResponse(path, media_type="text/plain; charset=utf-8" if credits else "video/mp4")


@app.get("/api/chapters/{chapter_id}/sections/{section_id}/translation")
def section_translation(chapter_id: str, section_id: str):
    """Return current reviewed Russian data, or an explicit unavailable state."""
    chapter = get_chapter(chapter_id)
    section = next((s for s in chapter["sections"] if s["id"] == section_id), None)
    if section is None:
        raise HTTPException(404, "Avsnittet finns inte.")
    unavailable = {"available": False, "language": "ru", "records": {}}
    source = {section["id"]: section["title"]}
    for unit in units(section):
        for sentence in unit["sentences"]:
            source[sentence["id"]] = unit["text"][sentence["start"]:sentence["end"]]
    base = DATA_DIR / "ru"
    try:
        terms = {entry["id"]: entry for entry in read_yaml(base / "glossary.yaml")["entries"]}
        records = reviewed_records(base, section_id, "sections", source, terms, read_yaml)
        heading = reviewed_records(base, chapter_id, "headings", {chapter_id: chapter["title"]}, terms, read_yaml)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
        return unavailable
    if records is None or heading is None:
        return unavailable
    return {"available": True, "language": "ru", "records": {**heading, **records}}


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


install_routes(app, get_chapter, get_passage)

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
