"""Archive the English Samfunnskunnskap course with resumable, serial requests."""

import argparse
import hashlib
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


BASE = "https://samfunnskunnskap.no"
START = BASE + "/en/index.html"
TEACHER = ".meta-larerinnhold, .expandable-teacher-content, .lesson-teacher-content"


def save_json(path, value):
    """Replace a checkpoint atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def text_of(element):
    """Read visible text, excluding scripts and UI controls."""
    copy = BeautifulSoup(str(element), "html.parser")
    for node in copy.select("script, style, button, svg"):
        node.decompose()
    return copy.get_text(" ", strip=True)


def extract(raw, url):
    """Separate course text from teacher notes and interactive exercise markup."""
    soup = BeautifulSoup(raw, "html.parser", from_encoding="utf-8")
    main = soup.find("main")
    if main is None:
        raise ValueError("No main course content")
    heading = main.find("h1")
    result = {
        "url": url,
        "title": heading.get_text(" ", strip=True) if heading else "",
        "kind": "lesson" if main.select(".pane") else "overview",
        "reading": [],
        "discussion": [],
        "exercises": [],
        "teacher_notes": [],
        "links": [],
        "embeds": [],
    }
    for a in main.select("a[href]"):
        result["links"].append({
            "url": urljoin(url, a["href"]),
            "label": a.get_text(" ", strip=True),
        })
    for frame in main.select("iframe[src]"):
        result["embeds"].append(urljoin(url, frame["src"]))
    # Remove outermost teacher containers only; nested containers duplicate text.
    for node in list(main.select(TEACHER)):
        if node.parent is not None:
            result["teacher_notes"].append(text_of(node))
            node.decompose()
    panes = main.select(".pane")
    for pane in panes:
        if pane.get("id") == "leksjondel-introduksjon":
            continue
        heading = pane.find(["h1", "h2"])
        title = heading.get_text(" ", strip=True) if heading else ""
        if title == "Talk together":
            result["discussion"].append(text_of(pane))
        elif not title:
            result["exercises"].append(text_of(pane))
        elif title != "Watch the film":
            result["reading"].extend(text_of(n) for n in pane.select(".bt-tekst"))
    if not panes:
        result["reading"].extend(text_of(n) for n in main.select(".bt-tekst"))
    result["word_counts"] = {
        key: sum(len(t.split()) for t in result[key])
        for key in ("reading", "discussion", "exercises", "teacher_notes")
    }
    return result


def course_links(raw, url):
    """Follow English course HTML only, not search, other languages or other sites."""
    soup = BeautifulSoup(raw, "html.parser", from_encoding="utf-8")
    main = soup.find("main")
    if main is None:
        return []
    found = []
    for a in main.select("a[href]"):
        target = urljoin(url, a["href"]).split("#")[0]
        parsed = urlparse(target)
        if (
            parsed.netloc == "samfunnskunnskap.no"
            and parsed.path.startswith("/en/")
            and parsed.path.endswith(".html")
            and parsed.path != "/en/sok.html"
            and not parsed.query
        ):
            found.append(target)
    return list(dict.fromkeys(found))


def main():
    """Download, checkpoint and extract a dated English-only snapshot."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    root = args.snapshot
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        "source": BASE,
        "language": "en",
        "scope": "English course HTML; linked supplements and embeds inventoried, not downloaded",
        "files": {},
    }
    files = manifest["files"]
    session = requests.Session()
    session.headers["User-Agent"] = "FinlandFlashcardsResearch/1.0 (English course archival; serial requests)"
    last_request = 0.0

    def fetch(url):
        nonlocal last_request
        path = root / "raw" / unquote(urlparse(url).path.lstrip("/"))
        if url in files and path.exists():
            content = path.read_bytes()
            if hashlib.sha256(content).hexdigest() != files[url]["sha256"]:
                raise ValueError("Checksum mismatch: " + str(path))
            return content
        if args.offline:
            raise ValueError("Not archived: " + url)
        for attempt in range(3):
            time.sleep(max(0, args.delay - (time.monotonic() - last_request)))
            last_request = time.monotonic()
            try:
                response = session.get(url, timeout=(8, 35))
                if response.status_code in (429, 503):
                    wait = response.headers.get("Retry-After", "15")
                    time.sleep(min(60, max(15, int(wait) if wait.isdigit() else 15)))
                response.raise_for_status()
                if urlparse(response.url).netloc != "samfunnskunnskap.no":
                    raise ValueError("Unexpected redirect: " + response.url)
                content = response.content
                if len(content) > 10_000_000:
                    raise ValueError("HTML exceeded 10 MB")
                if url.endswith(".html"):
                    extract(content, url)  # Do not checkpoint challenge/error HTML.
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                files[url] = {
                    "path": str(path.relative_to(root)),
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "final_url": response.url,
                    "status": response.status_code,
                    "content_type": response.headers.get("Content-Type"),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
                save_json(manifest_path, manifest)
                print("Saved " + url, flush=True)
                return content
            except requests.RequestException as error:
                print(f"Attempt {attempt + 1}: {url}: {type(error).__name__}", flush=True)
                if attempt == 2:
                    raise
                time.sleep(5 * (attempt + 1))

    queue = deque([START])
    seen = set()
    failures = {}
    pages = []
    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        if len(seen) > 200:
            raise ValueError("Unexpected course growth: more than 200 URLs")
        try:
            raw = fetch(url)
            page = extract(raw, url)
            pages.append(page)
            rel = Path(unquote(urlparse(url).path.lstrip("/"))).with_suffix(".json")
            save_json(root / "extracted" / rel, page)
            text_path = root / "reading" / rel.with_suffix(".txt")
            text_path.parent.mkdir(parents=True, exist_ok=True)
            text_path.write_text(
                page["title"] + "\n" + url + "\n\n"
                + "\n\n".join(page["reading"]) + "\n"
            )
            queue.extend(u for u in course_links(raw, url) if u not in seen)
        except (requests.RequestException, ValueError) as error:
            failures[url] = str(error)
        save_json(root / "progress.json", {
            "saved_course_pages": len(pages), "queued": len(queue), "failures": failures,
        })
    supplements = {}
    for page in pages:
        for link in page["links"]:
            if ".pdf" in urlparse(link["url"]).path.lower():
                entry = supplements.setdefault(link["url"], {
                    "url": link["url"], "labels": [], "linked_from": [],
                    "status": "link_only; language/content not verified as English",
                })
                if link["label"] not in entry["labels"]:
                    entry["labels"].append(link["label"])
                if page["url"] not in entry["linked_from"]:
                    entry["linked_from"].append(page["url"])
    save_json(root / "supplements.json", list(supplements.values()))
    save_json(root / "index.json", [{
        k: p[k] for k in ("url", "title", "kind", "word_counts", "embeds")
    } for p in pages])
    summary = {
        "course_pages": len(pages),
        "lessons": sum(p["kind"] == "lesson" for p in pages),
        "overviews": sum(p["kind"] == "overview" for p in pages),
        "word_counts": {k: sum(p["word_counts"][k] for p in pages)
                        for k in ("reading", "discussion", "exercises", "teacher_notes")},
        "linked_pdfs": len(supplements),
        "failures": failures,
        "complete_html_traversal": not failures,
    }
    save_json(root / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
