"""Extract fixed repository sources for Homebrew editorial review, without network I/O.

Run from any directory with Poetry. JSON is an intermediate evidence format, not
the final chapter interface. Original HTML/PDF files are never modified.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "wip/homebrew/extracted"
EVIDENCE = [
    "news/files/valtioneuvosto_lag_andring_av_medborgarskapslagen_sv_2026-06-16.pdf",
    "news/files/finlex_laki_552_2026_kansalaisuuslain_muuttamisesta.pdf",
    "news/files/finlex_rp_54_2026_medborgarskapslagen_sv.pdf",
    "news/files/snapshot_2026-06-24_finlex_lag_552_2026_medborgarskapslagen_sv.html",
    "news/files/snapshot_2026-08-27_migri_citizenship_act_amendments_2027_sv.html",
    "news/files/snapshot_2026-08-27_migri_citizenship_test_faq_direct_sv.html",
]


def normalize(text: str) -> str:
    """Normalize whitespace only; never repair or paraphrase wording implicitly."""
    return re.sub(r"\s+", " ", text).strip()


def fingerprint(path: Path) -> dict:
    """Identify exact source bytes using a repository-relative path and SHA-256."""
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def locator(node: Tag) -> str:
    """Build a CSS locator against the original HTML, before removing furniture."""
    parts = []
    while isinstance(node, Tag) and node.name != "[document]":
        siblings = [x for x in node.previous_siblings
                    if isinstance(x, Tag) and x.name == node.name]
        parts.append(f"{node.name}:nth-of-type({len(siblings) + 1})")
        node = node.parent
    return " > ".join(reversed(parts))


def extract_html(path: Path) -> dict:
    """Preserve article text, glossary, activities and assets with explicit roles."""
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    source = soup.find("meta", attrs={"name": "source"})
    record = dict(fingerprint(path), title=soup.title.get_text(strip=True) if soup.title else path.stem,
                  source_url=source.get("content") if source else None,
                  extraction="html-whitespace-normalized-v1", blocks=[], images=[])
    # Save selectors before removing any DOM nodes.
    locations = {id(tag): locator(tag) for tag in soup.find_all(True)}
    for tag in soup.select("script, style, nav, header, footer, svg, button, noscript"):
        tag.decompose()
    articles = soup.select(".journal-content-article")
    if articles:
        roots = articles
    elif "infofinland" in path.parts:
        roots = soup.select(".ifu-block--article, .ifu-block--hero h1")
        roots = [tag for tag in roots if not any(parent in roots for parent in tag.parents)]
    else:
        roots = [soup.find("main") or soup.body or soup]
    for root in roots:
        asset_title = root.get("data-analytics-asset-title", "")
        role = "content"
        for suffix, value in [("sanasto", "glossary"), ("keskustelukysymykset", "activity"),
                              ("tiivistelmä", "introduction"), ("hero", "illustration")]:
            if asset_title.lower().endswith(suffix):
                role = value
        if re.search(r" - (keskustelukysymykset|teht[äa])", asset_title.lower()):
            role = "activity"
        if "tapauskertomus" in asset_title.lower():
            role = "case_study"
        for img in root.find_all("img"):
            record["images"].append({"locator": locations[id(img)],
                                     "src": img.get("src"), "alt": img.get("alt", ""),
                                     "downloaded": False})
        candidates = root.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "table"])
        if root.name in {"h1", "h2", "h3", "p", "li", "table"}:
            candidates.insert(0, root)
        if not candidates and normalize(root.get_text(" ", strip=True)):
            candidates = [root]
        for node in candidates:
            # A list item includes nested prose/lists; tables include their cells.
            if any(parent.name in {"p", "li", "table"} for parent in node.parents
                   if parent is not root):
                continue
            text = normalize(node.get_text(" ", strip=True))
            if not text:
                continue
            kind = "heading" if re.fullmatch(r"h[1-6]", node.name) else node.name
            if kind == "heading" and text == "Lärandemål":
                role = "learning_objectives"
            block = {"id": f"b{len(record['blocks']) + 1:04d}", "kind": kind,
                     "role": role, "text": text, "locator": locations[id(node)]}
            if asset_title:
                block["article"] = asset_title
            if kind == "heading":
                block["level"] = int(node.name[1])
            if node.name == "table":
                block["rows"] = [[normalize(cell.get_text(" ", strip=True))
                                   for cell in row.find_all(["th", "td"], recursive=False)]
                                  for row in node.find_all("tr")]
            links = [{"text": normalize(a.get_text(" ", strip=True)), "href": a.get("href")}
                     for a in node.find_all("a", href=True)]
            if links:
                block["links"] = links
            record["blocks"].append(block)
    record["visible_dates"] = sorted(set(re.findall(
        r"\b\d{2}\.\d{2}\.\d{4}\b", soup.get_text(" ", strip=True))))
    record["word_count"] = sum(len(b["text"].split()) for b in record["blocks"])
    return record


def extract_pdf(path: Path) -> dict:
    """Retain page boundaries and unmodified extracted text for later verification."""
    pdf = PdfReader(path)
    pages = []
    for i, page in enumerate(pdf.pages):
        pages.append({"pdf_page": i + 1, "text": page.extract_text() or ""})
    return dict(fingerprint(path), extraction="pypdf-default-page-text-v1",
                pdf_metadata={str(k): str(v) for k, v in (pdf.metadata or {}).items()},
                page_count=len(pages), pages=pages)


def write_json(name: str, value: object) -> None:
    """Write deterministic, Unicode-preserving review artifacts."""
    (OUTPUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    """Extract all Swedish archive files, the textbook and selected scope evidence."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for group, directory in [("orientation", "data/orientation/sv"),
                             ("infofinland", "data/infofinland/content")]:
        documents = [extract_html(p) for p in sorted((ROOT / directory).rglob("*.html"))]
        write_json(f"{group}.json", documents)
        print(f"{group}: {len(documents)} files, {sum(d['word_count'] for d in documents)} extracted words")
    textbook = extract_pdf(ROOT / "data/orientation_guide.pdf")
    write_json("textbook.json", textbook)
    print(f"textbook: {textbook['page_count']} PDF pages")
    evidence = [extract_pdf(ROOT / f) if f.endswith(".pdf") else extract_html(ROOT / f) for f in EVIDENCE]
    write_json("evidence.json", evidence)
    print(f"scope evidence: {len(evidence)} files")


if __name__ == "__main__":
    main()
