"""Build the reviewed local-source pilot and its separate provenance metadata.

Selections and sentence IDs are committed editorial inputs. This builder never
allocates IDs during a normal rebuild; --initialize-sentences is a one-time step
for new text units and refuses to silently change existing sentence records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml

from extract_sources import ROOT, normalize

WORK = ROOT / "wip/homebrew"
DEST = ROOT / "data/homebrew"
CHAPTER_FILE = "sv/chapters/05_rattigheter_jamlikhet_och_skyldigheter.yaml"


def read_yaml(path):
    """Read a UTF-8 YAML document."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(path, value):
    """Write deterministic, Unicode-preserving YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False,
                                  width=100), encoding="utf-8")


def sentence_ranges(text):
    """Suggest boundaries for Swedish text; committed ranges are reviewed input.

    Protect common abbreviations, initials and decimals. Fragments count as one
    segment. This is deliberately not a claim of general linguistic parsing.
    """
    protected = set()
    abbreviations = r"\b(?:t\.\s*ex\.|bl\.\s*a\.|dvs\.|d\.\s*v\.\s*s\.|s\.\s*k\.|m\.\s*fl\.|m\.\s*m\.|fr\.\s*o\.\s*m\.|t\.\s*o\.\s*m\.|ca\.|kl\.|nr\.)"
    for match in re.finditer(abbreviations, text, re.I):
        protected.update(range(match.start(), match.end()))
    ranges = []
    start = 0
    for match in re.finditer(r'[.!?]+[\u201d\u201c"\u00bb)]*(?=\s|$)', text):
        pos = match.start()
        if pos in protected:
            continue
        if text[pos] == "." and re.search(r"\b[A-ZÅÄÖ]$", text[:pos]):
            continue
        end = match.end()
        if start < end:
            ranges.append((start, end))
        start = end
        while start < len(text) and text[start].isspace():
            start += 1
    if start < len(text):
        ranges.append((start, len(text)))
    return ranges


def load_sources():
    """Load frozen extraction intermediates; validate bytes before using them."""
    documents = {}
    for group in ["orientation", "infofinland"]:
        for document in json.loads((WORK / f"extracted/{group}.json").read_text(encoding="utf-8")):
            documents[document["path"]] = document
    textbook = json.loads((WORK / "extracted/textbook.json").read_text(encoding="utf-8"))
    documents[textbook["path"]] = textbook
    return documents


def selected_text(selection, documents):
    """Resolve a source passage and explicit source range without paraphrasing."""
    source = documents[selection["source_path"]]
    if "source_block" in selection:
        block = next(b for b in source["blocks"] if b["id"] == selection["source_block"])
        assert block["role"] not in {"activity", "learning_objectives"}
        assert block["kind"] not in {"heading", "table"}
        raw = block["text"]
        location = {"source_block": block["id"], "locator": block["locator"],
                    "source_kind": block["kind"], "source_role": block["role"]}
        previous = source["blocks"][:source["blocks"].index(block)]
        location["heading"] = next((b["text"] for b in reversed(previous)
                                    if b["kind"] == "heading"), source["title"])
    else:
        page = selection["pdf_page"]
        raw = source["pages"][page - 1]["text"]
        location = {"pdf_page": page, "printed_page": page - 1}
    start, end = selection.get("source_range", [0, len(raw)])
    assert 0 <= start < end <= len(raw)
    excerpt = raw[start:end]
    text = normalize(excerpt)
    if "expected_text" in selection:
        assert text == selection["expected_text"], selection["id"]
    return text, {"source_path": selection["source_path"], "sha256": source["sha256"],
                  **location, "source_range": {"start": start, "end": end},
                  "range_basis": "normalized_html_block" if "source_block" in selection else "raw_pdf_page",
                  "extracted_passage": excerpt, "normalization": "whitespace_only",
                  "repairs": [], "selection": selection.get("selection_reason", "Complete source paragraph or list item.")}


def build(selection, registry, documents, initialize=False):
    """Build learner content and provenance with stable, previously allocated IDs."""
    chapter = {"schema_version": 1, "id": selection["chapter_id"],
               "language": selection["language"], "title": selection["title"], "sections": []}
    provenance = {"schema_version": 1, "chapter_id": chapter["id"], "units": {}}
    used = set()

    def leaf(item):
        identity = item["id"]
        text, origin = selected_text(item, documents)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if identity not in registry["units"]:
            assert initialize, f"Allocate and review sentence IDs for {identity} explicitly"
            registry["units"][identity] = {
                "text_sha256": digest,
                "sentences": [{"id": f"{identity}-s{i:03d}", "start": a, "end": b}
                              for i, (a, b) in enumerate(sentence_ranges(text), 1)]}
        frozen = registry["units"][identity]
        assert frozen["text_sha256"] == digest, f"Text changed for {identity}; review sentence ID migration"
        assert identity not in used, identity
        used.add(identity)
        provenance["units"][identity] = origin
        return {"id": identity, "text": text, "sentences": frozen["sentences"]}

    for section in selection["sections"]:
        out = {"id": section["id"], "title": section["title"], "blocks": []}
        for block in section["blocks"]:
            if block["kind"] == "paragraph":
                out["blocks"].append({"type": "paragraph", **leaf(block)})
            elif block["kind"] == "list":
                out["blocks"].append({"id": block["id"], "type": "list", "ordered": block["ordered"],
                                      "items": [leaf(item) for item in block["items"]]})
            else:
                raise ValueError(f"Unsupported editorial selection kind: {block['kind']}")
        chapter["sections"].append(out)
    assert used == set(registry["units"]), "Retire removed units explicitly in the sentence registry"
    return chapter, provenance


def render(chapter):
    """Create the readable review copy directly from learner YAML, without metadata."""
    lines = [f"# {chapter['title']}", ""]
    for section in chapter["sections"]:
        lines.extend([f"## {section['title']}", ""])
        for block in section["blocks"]:
            if block["type"] == "paragraph":
                lines.extend([block["text"], ""])
            elif block["type"] == "list":
                lines.extend([f"{'1.' if block['ordered'] else '-'} {item['text']}" for item in block["items"]])
                lines.append("")
            else:
                raise ValueError("Pilot renderer supports paragraph/list blocks only")
    return "\n".join(lines)


def main():
    """Compatibility entry point; refresh the collection without losing chapters."""
    from build_collection import main as collection_main
    collection_main()


if __name__ == "__main__":
    main()
