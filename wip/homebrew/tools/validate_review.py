"""Validate checkpoint-one evidence completeness and traceability without mutation."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from build_review import TEXTBOOK_CHAPTERS, textbook_units
from extract_sources import normalize

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "wip/homebrew"


def validate_coverage(coverage: dict, outline: dict, expected: set) -> None:
    """Reject missing sources, dangling destinations and unexplained exclusions."""
    rows = coverage["sources"]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "Duplicate source IDs"
    assert set(ids) == expected, f"Coverage mismatch: {expected.symmetric_difference(ids)}"
    chapters = {c["id"] for c in outline["chapters"]}
    used = set()
    for row in rows:
        assert row["decision"] in {"include", "partial", "exclude", "duplicate", "gap"}
        assert set(row["chapters"]) <= chapters, row["id"]
        assert row.get("keep") or row.get("omit"), row["id"]
        if row["decision"] in {"include", "partial", "gap"}:
            assert row["chapters"] and row["scope"], row["id"]
        if row["decision"] == "partial":
            assert row.get("keep") and row.get("omit"), row["id"]
        if row["decision"] == "exclude":
            assert not row["chapters"] and row.get("omit"), row["id"]
        used.update(row["chapters"])
    assert used == chapters, "A proposed chapter has no source support"
    assert dict(Counter(r["decision"] for r in rows)) == coverage["counts"]


def main() -> None:
    """Check every frozen file and every extracted HTML block against its source."""
    inventory = yaml.safe_load((WORK / "source_inventory.yaml").read_text())
    paths = [r["path"] for r in inventory["files"]]
    assert len(paths) == len(set(paths)), "Duplicate inventory paths"
    for record in inventory["files"]:
        path = ROOT / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], record["path"]
        assert path.stat().st_size == record["bytes"], record["path"]
    expected, count = set(), 0
    for group, base in [("orientation", "data/orientation/sv"), ("infofinland", "data/infofinland/content")]:
        records = json.loads((WORK / "extracted" / f"{group}.json").read_text())
        assert {r["path"] for r in records} == {p.relative_to(ROOT).as_posix() for p in (ROOT / base).rglob("*.html")}
        for record in records:
            relative = record["path"].removeprefix(base + "/").removesuffix(".html")
            expected.add(f"{group}:{relative}")
            soup = BeautifulSoup((ROOT / record["path"]).read_text(), "html.parser")
            for tag in soup.select("script, style, nav, header, footer, svg, button, noscript"):
                tag.decompose()
            whole = normalize(soup.get_text(" ", strip=True))
            ids = [b["id"] for b in record["blocks"]]
            assert len(ids) == len(set(ids)), record["path"]
            for block in record["blocks"]:
                assert block["text"] in whole, (record["path"], block["id"], "Text absent from source")
                assert block["locator"], (record["path"], block["id"])
                count += 1
    textbook = json.loads((WORK / "extracted/textbook.json").read_text())
    units = textbook_units(textbook)
    assert {u["id"].split(":")[1] for u in units if u["id"].split(":")[1] in TEXTBOOK_CHAPTERS} == set(TEXTBOOK_CHAPTERS)
    assert textbook["page_count"] == 135 and len(textbook["pages"]) == 135
    assert all(p["text"].strip() for p in textbook["pages"]), "Empty PDF extraction"
    expected.update(u["id"] for u in units)
    coverage = yaml.safe_load((WORK / "coverage.yaml").read_text())
    outline = yaml.safe_load((WORK / "outline.yaml").read_text())
    validate_coverage(coverage, outline, expected)
    assert {s for c in outline["chapters"] for s in c["scope"]} == {"society", "rights", "legislation", "equality", "history", "culture"}
    # Ensure the known missing archive is disclosed, rather than treated as evidence.
    holiday = next(r for r in coverage["sources"] if r["id"] == "orientation:laromedel/manniskorna-och-kulturen/hogtider-och-traditioner")
    assert holiday["decision"] == "gap" and holiday.get("safeguard")
    print(f"PASS: {len(paths)} frozen files, {count} HTML blocks verified against local text, {len(expected)} coverage units, {len(outline['chapters'])} supported chapters, 135 PDF pages.")


if __name__ == "__main__":
    main()
