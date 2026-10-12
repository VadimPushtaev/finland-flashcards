"""Validate Homebrew content structure, exact local provenance and review inputs."""

from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup
from pypdf import PdfReader

from build_pilot import CHAPTER_FILE, DEST, ROOT, WORK, load_sources, read_yaml, render
from extract_sources import normalize


def keys(value, required, optional=()):
    """Reject unexpected metadata in reader content as well as missing fields."""
    assert isinstance(value, dict)
    assert set(required) <= set(value), f"Missing keys: {set(required) - set(value)}"
    assert set(value) <= set(required) | set(optional), f"Unexpected keys: {set(value) - set(required) - set(optional)}"


def validate_chapter(chapter, asset_root=DEST):
    """Check schema v1 including sentences, rectangular tables and local images."""
    ids, units, assets = set(), {}, {}

    def identity(value):
        assert isinstance(value, str) and re.fullmatch(r"hb-[a-z0-9-]+", value), value
        assert value not in ids, f"Duplicate ID: {value}"
        ids.add(value)

    def label(value):
        assert isinstance(value, str) and value.strip() == value and value

    def leaf(value, paragraph=False):
        keys(value, ["id", "text", "sentences"] + (["type"] if paragraph else []))
        identity(value["id"])
        text = value["text"]
        label(text)
        assert not re.search(r"(?:Läs mer|Mer information|I videon nedan|På InfoFinlands sida|Lisätietoa)", text), value["id"]
        assert isinstance(value["sentences"], list) and value["sentences"]
        previous = 0
        for sentence in value["sentences"]:
            keys(sentence, ["id", "start", "end"])
            identity(sentence["id"])
            start, end = sentence["start"], sentence["end"]
            assert type(start) is int and type(end) is int
            assert previous <= start < end <= len(text), value["id"]
            assert not text[previous:start].strip(), f"Unsegmented text in {value['id']}"
            assert text[start:end] == text[start:end].strip(), value["id"]
            previous = end
        assert not text[previous:].strip(), f"Missing sentence tail in {value['id']}"
        units[value["id"]] = value

    keys(chapter, ["schema_version", "id", "language", "title", "sections"])
    assert chapter["schema_version"] == 1 and chapter["language"] == "sv"
    identity(chapter["id"])
    label(chapter["title"])
    assert isinstance(chapter["sections"], list) and chapter["sections"]
    for section in chapter["sections"]:
        keys(section, ["id", "title", "blocks"])
        identity(section["id"])
        label(section["title"])
        assert isinstance(section["blocks"], list) and section["blocks"]
        for block in section["blocks"]:
            kind = block["type"]
            if kind == "paragraph":
                leaf(block, paragraph=True)
                continue
            identity(block["id"])
            if kind == "list":
                keys(block, ["id", "type", "ordered", "items"])
                assert type(block["ordered"]) is bool
                assert isinstance(block["items"], list) and block["items"]
                for item in block["items"]:
                    leaf(item)
            elif kind == "table":
                keys(block, ["id", "type", "header_rows", "rows"])
                rows = block["rows"]
                assert isinstance(rows, list) and rows and rows[0]
                assert type(block["header_rows"]) is int and 0 <= block["header_rows"] <= len(rows)
                for row in rows:
                    assert isinstance(row, list) and len(row) == len(rows[0])
                    for cell in row:
                        leaf(cell)
            elif kind == "image":
                keys(block, ["id", "type", "path", "alt"], ["caption"])
                label(block["alt"])
                path = (asset_root / block["path"]).resolve()
                assert path.is_relative_to(asset_root.resolve()) and path.is_file(), "Image must be local"
                assert block["path"].startswith("assets/"), "Image must be a collection asset"
                assets[block["id"]] = block
                if "caption" in block:
                    leaf(block["caption"])
            else:
                raise AssertionError(f"Unknown block type: {kind}")
    return units, assets, ids


def verify_provenance(units, provenance, sources, root=ROOT):
    """Re-read original HTML/PDF bytes rather than trusting extraction caches."""
    assert set(units) == set(provenance["units"]), "Every text unit needs exactly one origin"
    source_records = {s["path"]: s for s in sources["sources"]}
    parsed = {}
    for source_path, record in source_records.items():
        assert source_path == "data/orientation_guide.pdf" or source_path.startswith(("data/orientation/sv/", "data/infofinland/content/"))
        path = (root / source_path).resolve()
        assert path.is_relative_to(root.resolve())
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == record["sha256"], source_path
        parsed[source_path] = PdfReader(path) if path.suffix == ".pdf" else BeautifulSoup(data, "html.parser")
    for identity, unit in units.items():
        origin = provenance["units"][identity]
        path = origin["source_path"]
        assert origin["sha256"] == source_records[path]["sha256"]
        assert origin["normalization"] == "whitespace_only" and origin["repairs"] == []
        if origin["range_basis"] == "normalized_html_block":
            assert origin["source_role"] not in {"activity", "learning_objectives"}
            matches = parsed[path].select(origin["locator"])
            assert len(matches) == 1, identity
            raw = normalize(matches[0].get_text(" ", strip=True))
        else:
            assert origin["range_basis"] == "raw_pdf_page"
            raw = parsed[path].pages[origin["pdf_page"] - 1].extract_text()
        start, end = origin["source_range"]["start"], origin["source_range"]["end"]
        assert 0 <= start < end <= len(raw)
        assert raw[start:end] == origin["extracted_passage"], identity
        assert normalize(raw[start:end]) == unit["text"], f"Source mismatch: {identity}"


def main():
    """Validate the pilot and its review/attribution packaging."""
    manifest = read_yaml(DEST / "manifest.yaml")
    assert manifest["status"] == "pilot_pending_review"
    assert manifest["chapters"] == [{"id": "hb-c05", "order": 5, "path": CHAPTER_FILE}]
    for value in manifest["metadata"].values():
        for path in value if isinstance(value, list) else [value]:
            resolved = (DEST / path).resolve()
            assert resolved.is_relative_to(DEST.resolve()) and resolved.is_file()
    chapter = read_yaml(DEST / CHAPTER_FILE)
    units, assets, ids = validate_chapter(chapter)
    assert not assets, "Pilot has no essential local visual; asset provenance needed before adding one"
    provenance = read_yaml(DEST / "metadata/05_provenance.yaml")
    assert provenance["chapter_id"] == chapter["id"]
    sources = read_yaml(DEST / "metadata/sources.yaml")
    verify_provenance(units, provenance, sources)
    registry = read_yaml(WORK / "pilot_sentences.yaml")["units"]
    assert set(registry) == set(units)
    for identity, unit in units.items():
        assert registry[identity]["text_sha256"] == hashlib.sha256(unit["text"].encode("utf-8")).hexdigest()
        assert registry[identity]["sentences"] == unit["sentences"]
    assert (WORK / "PILOT.sv.md").read_text(encoding="utf-8") == render(chapter)
    attribution = read_yaml(DEST / "metadata/attribution.yaml")["sources"]
    assert {s["source_group"] for s in sources["sources"]} <= set(attribution)
    for record in attribution.values():
        notice = ROOT / record["local_notice"]
        assert notice.is_file()
        assert hashlib.sha256(notice.read_bytes()).hexdigest() == record["local_notice_sha256"]
    for source in sources["sources"]:
        assert source["attribution_record"] == source["source_group"]
    review = read_yaml(DEST / "metadata/05_editorial_review.yaml")
    coverage = read_yaml(WORK / "coverage.yaml")
    expected = {s["id"] for s in coverage["sources"] if "hb-c05" in s["chapters"]}
    assert expected <= {s["id"] for s in review["source_audit"]}
    audited_units = set()
    for row in review["source_audit"]:
        assert row["decision"] and row["reason"]
        for identity in row["selected_unit_ids"]:
            assert identity in units and provenance["units"][identity]["source_path"] == row["path"]
            audited_units.add(identity)
    assert audited_units == set(units), "Source audit must account for every selected passage"
    documents = load_sources()
    for path, decisions in review["primary_block_audit"].items():
        block_ids = [d["source_block"] for d in decisions]
        assert len(block_ids) == len(set(block_ids))
        assert set(block_ids) == {b["id"] for b in documents[path]["blocks"]}
        assert all(d["decision"] and d["reason"] for d in decisions)
    outline = read_yaml(WORK / "outline.yaml")
    topics = next(c["topics"] for c in outline["chapters"] if c["id"] == "hb-c05")
    assert set(topics) == set(review["topic_coverage"])
    for destinations in review["topic_coverage"].values():
        assert destinations and set(destinations) <= ids
    for gap in review["gaps"]:
        assert gap["reason"] and gap["source_refs"]
    print(f"PASS: {len(units)} verbatim text units, {sum(len(u['sentences']) for u in units.values())} sentence ranges, "
          f"{len(sources['sources'])} original source files; schema, provenance, attribution and topic audit")


if __name__ == "__main__":
    main()
