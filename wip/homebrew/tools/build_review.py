"""Build a complete, reviewable source disposition map from editorial rules."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "wip/homebrew"
CITIES = {"espoo", "helsinki", "kauniainen", "vaasa", "vantaa"}
TOPIC_PURPOSES = {
    "education": "Education system, pathways, student rights, public support and institutional roles.",
    "family": "Family law, children's rights, family forms, public support and protections.",
    "finnish-and-swedish": "National languages, language rights and language education's civic role.",
    "health": "Health and welfare institutions, access to services, patient rights and public prevention.",
    "housing": "Housing contracts, rights/duties, public support, environmental responsibility and safety.",
    "leisure": "Public services, civil society, cultural participation and rights/responsibilities in nature.",
    "moving-to-finland": "Residence/status distinctions, public-authority roles, registration and legal protections only.",
    "settling-in-finland": "Integration, citizenship, public-authority roles and access to national institutions.",
    "work-and-enterprise": "Labour-market institutions, work/enterprise rights and duties, taxation and social protection.",
}
TEXTBOOK_CHAPTERS = {
    "1.1": ["hb-c01"], "1.2": ["hb-c01", "hb-c05"], "1.3": ["hb-c03"],
    "1.4": ["hb-c02"], "1.5": ["hb-c03"], "2.1": ["hb-c07", "hb-c10"],
    "2.2": ["hb-c02", "hb-c10"], "2.3": ["hb-c04"], "2.4": ["hb-c07"],
    "3.1": ["hb-c12"], "3.2": ["hb-c12", "hb-c11"], "3.3": ["hb-c11"],
    "3.4": ["hb-c12"], "4.1": ["hb-c09"], "4.2": ["hb-c09"],
    "4.3": ["hb-c09"], "4.4": ["hb-c09", "hb-c08"], "4.5": ["hb-c09"],
    "4.6": ["hb-c10"], "4.7": ["hb-c09", "hb-c12"], "5.1": ["hb-c08", "hb-c02"],
    "5.2": ["hb-c08"], "5.3": ["hb-c08"], "6.1": ["hb-c07"],
    "6.2": ["hb-c07"], "6.3": ["hb-c07"], "6.4": ["hb-c07"],
    "6.5": ["hb-c07"], "7.1": ["hb-c10"], "7.2": ["hb-c10"],
    "7.3": ["hb-c10"], "7.4": ["hb-c10"], "7.5": ["hb-c10"],
    "7.6": ["hb-c09"], "7.7": ["hb-c09"], "8.1": ["hb-c06"],
    "8.2": ["hb-c05"], "8.3": ["hb-c05"], "8.4": ["hb-c06"],
    "8.5": ["hb-c06"], "9.1": ["hb-c04"], "9.2": ["hb-c02", "hb-c04"],
    "9.3": ["hb-c04"], "9.4": ["hb-c04"], "9.5": ["hb-c04"],
}
TEXTBOOK_FILTERS = {
    "1.1": "Clothing/lifestyle advice and undated present-day statistics.",
    "1.2": "Undated present-day population figures; retain minority/language explanations.",
    "2.3": "Institutional descriptions contradicted by newer local sources, including municipal healthcare responsibility.",
    "2.4": "Undated economic statistics presented as current.",
    "3.1": "Permit/citizenship application procedures and superseded or unresolved eligibility rules.",
    "3.2": "Bank/account/application checklists; retain registration, authority roles and identification concepts.",
    "3.3": "Apartment search and shopping instructions; retain housing law, duties and institutions.",
    "3.4": "Emotional adaptation coaching; retain integration concepts, services and participation.",
    "4.2": "Wedding/application procedures; retain eligibility, marriage/cohabitation rights and property rules.",
    "4.4": "Benefit application details and superseded entitlements; retain child rights and service roles.",
    "4.6": "Personal treatment/lifestyle instructions and service directories.",
    "4.7": "Adjustment coaching; preserve children's interests, family roles and access to support where additive.",
    "5.2": "Superseded compulsory-education endpoint (printed p. 65) and other contradicted rules.",
    "5.3": "Application steps, outdated sums and unresolved support conditions.",
    "6.2": "CV, interview, job-board and networking coaching; preserve employment-service and recruitment-rights facts.",
    "6.3": "Dated tax figures and tax-form walkthroughs.",
    "6.4": "Application steps and unresolved benefit/authority details.",
    "6.5": "Business-plan coaching and registration walkthroughs; retain business forms and entrepreneur duties.",
    "7.1": "General medical/lifestyle coaching without Finnish civic relevance.",
    "7.2": "Superseded organization of public healthcare, appointment procedures and unresolved entitlements.",
    "7.3": "Generic health/lifestyle advice and undated statistics.",
    "7.4": "Unresolved amounts, retirement ages and application instructions.",
    "7.5": "Care-provider directories and application instructions.",
    "7.6": "Funeral booking and transport procedures; retain cultural/legal principles.",
    "7.7": "Estate filing steps and unresolved monetary thresholds; retain inheritance rights and duties.",
    "9.3": "Old election dates and omissions arising from the older administration structure.",
    "9.4": "Dated officeholders and seat counts presented as current; retain party system and supported historical context.",
}


def textbook_units(document: dict) -> list:
    """Read the PDF's actual TOC, including excluded front matter and exercises."""
    entries = []
    major = 0
    minor = 0
    for page in document["pages"][1:3]:
        for line in page["text"].splitlines():
            match = re.match(r"^(.*?)\s*\.{2,}\s*(\d+)\s*$", line.strip())
            if not match:
                continue
            title, printed = match.group(1).strip(), int(match.group(2))
            chapter = re.match(r"^(\d+)\. ", title)
            if chapter:
                major, minor = int(chapter.group(1)), 0
                continue
            if title == "Förord":
                unit_id = "frontmatter"
            elif title.startswith("Frågor"):
                unit_id = f"discussion-{major}"
            else:
                minor += 1
                unit_id = f"{major}.{minor}"
            entries.append({"id": f"textbook:{unit_id}", "title": title,
                            "printed_page_start": printed,
                            "pdf_page_start": printed + 1})
    for i, entry in enumerate(entries):
        end = entries[i + 1]["pdf_page_start"] if i + 1 < len(entries) else document["page_count"]
        if entry["id"] == "textbook:frontmatter":
            entry["pdf_page_start"] = 1
        entry["pdf_page_end_inclusive"] = end
        entry["locator_note"] = "Candidate page window includes the next heading's page; isolate the named heading before quoting. Chapter-opening introductions belong to the first subsection."
    return entries


def html_decision(group: str, document: dict, rules: dict) -> dict:
    """Apply reviewed category decisions and explicit topic overrides."""
    base = "data/orientation/sv/" if group == "orientation" else "data/infofinland/content/"
    relative = document["path"].removeprefix(base).removesuffix(".html")
    result = {"id": f"{group}:{relative}", "path": document["path"], "title": document["title"]}
    if group == "orientation":
        if not relative.startswith("laromedel/"):
            result.update(decision="exclude", chapters=[],
                          omit="Trainer guidance, site administration/news, or navigation/duplicate indexes; not standalone subject reading.")
        else:
            topic = relative.removeprefix("laromedel/")
            category = topic.split("/")[0]
            chapters = rules["orientation_categories"][category]
            if "/" not in topic:
                result.update(decision="partial", chapters=chapters,
                              keep="Any substantive introductory civic facts not repeated in the detailed lessons.",
                              omit="Learning objectives, course framing, activities and instructional case-story framing.")
            else:
                result.update(decision="include", chapters=chapters,
                              keep="Substantive lesson explanations and useful glossary definitions; add other sources only for extra facts or nuance.")
            result.update(rules["orientation_overrides"].get(topic, {}))
    else:
        category = relative.split("/")[0]
        if category in CITIES:
            target = relative.split("/")[-1]
            candidate = next((name for name in TOPIC_PURPOSES if target.startswith(name)), None)
            replacements = rules["infofinland_categories"].get(candidate, ["hb-c12"])
            result.update(decision="exclude", chapters=[],
                          omit="Municipal service directory, local addresses and local arrangements.",
                          safeguard="National civic facts are covered in nationwide source pages. Before final exclusion, compare any unique rights/duties statements with those pages.",
                          safeguard_chapters=replacements)
        elif category not in rules["infofinland_categories"]:
            result.update(decision="exclude", chapters=[],
                          omit="Site administration, navigation, licensing, translation or publisher information; preserve relevant provenance/license notices in metadata.")
        elif "/" not in relative:
            result.update(decision="duplicate", chapters=rules["infofinland_categories"][category],
                          omit="Category index/teaser; substantive topics are represented by its detailed articles.")
        else:
            result.update(decision="partial", chapters=rules["infofinland_categories"][category],
                          keep=TOPIC_PURPOSES.get(category, "Civic facts within this article's topic where additive."),
                          omit="Local/provider directories, external-link cards, application walkthroughs and unrelated personal advice. Compare time-sensitive claims before use.")
        result.update(rules["infofinland_overrides"].get(relative, {}))
    return result


def dump_yaml(path: Path, value: object) -> None:
    """Write human-readable Unicode YAML without aliases or reordered keys."""
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")


def main() -> None:
    """Generate source fingerprints, dispositions and a readable coverage table."""
    rules = yaml.safe_load((WORK / "selection_rules.yaml").read_text())
    outline = yaml.safe_load((WORK / "outline.yaml").read_text())
    scope_by_chapter = {c["id"]: c["scope"] for c in outline["chapters"]}
    files, dispositions = [], []
    for group in ["orientation", "infofinland"]:
        documents = json.loads((WORK / "extracted" / f"{group}.json").read_text())
        for document in documents:
            row = html_decision(group, document, rules)
            files.append({k: document[k] for k in ["path", "sha256", "bytes", "title", "source_url", "visible_dates", "word_count"]})
            row["scope"] = sorted({s for c in row["chapters"] for s in scope_by_chapter[c]})
            row["source_headings"] = [b["text"] for b in document["blocks"] if b["kind"] == "heading"]
            row["passage_audit"] = "pending_after_outline_review"
            dispositions.append(row)
    textbook = json.loads((WORK / "extracted/textbook.json").read_text())
    files.append({k: textbook[k] for k in ["path", "sha256", "bytes", "page_count", "pdf_metadata"]})
    for unit in textbook_units(textbook):
        key = unit["id"].split(":")[1]
        row = dict(unit, path=textbook["path"])
        if key in TEXTBOOK_CHAPTERS:
            row.update(chapters=TEXTBOOK_CHAPTERS[key],
                       decision="partial" if key in TEXTBOOK_FILTERS else "include",
                       keep="Substantive civic explanation and historical context, where it contributes beyond the orientation website.",
                       omit=TEXTBOOK_FILTERS.get(key, "Duplicate explanation and common non-reading material only."))
        else:
            row.update(chapters=[], decision="exclude", omit="Publisher/course framing or classroom discussion questions.")
        row["scope"] = sorted({s for c in row["chapters"] for s in scope_by_chapter[c]})
        row["passage_audit"] = "pending_after_outline_review"
        dispositions.append(row)
    for document in json.loads((WORK / "extracted/evidence.json").read_text()):
        files.append(dict({k: document[k] for k in ["path", "sha256", "bytes"]}, role="scope_evidence_only"))
    # Freeze auxiliary metadata relied on, too.
    from extract_sources import fingerprint
    for filename in ["data/orientation/LICENSE", "data/infofinland/LICENSE", "news/all-we-know.md"]:
        files.append(dict(fingerprint(ROOT / filename), role="metadata_or_discovery_only"))
    dump_yaml(WORK / "source_inventory.yaml", {"schema_version": 1, "policy": "Repository snapshots only; visible dates may describe events, not publication. File hashes define the snapshot.", "files": files})
    counts = dict(Counter(row["decision"] for row in dispositions))
    dump_yaml(WORK / "coverage.yaml", {"schema_version": 1, "status": "proposed_for_checkpoint_1", "counts": counts,
              "decision_meaning": "include retains substantive topic coverage, subject to common omissions; partial identifies substantive cuts; duplicate routes to other passages; gap is unavailable source content. Exact passage selection is not yet approved or complete.",
              "common_omissions": rules["common_omissions"], "common_retention": rules["common_retention"], "sources": dispositions})
    lines = ["# Source coverage and exclusion map", "", "Proposed for checkpoint 1. Exact passage choices and duplicate resolution follow outline review.", "", "See `coverage.yaml` for source headings, safeguards and PDF locators, and `selection_rules.yaml` for common rules.", ""]
    for group in ["orientation", "infofinland", "textbook"]:
        lines.extend([f"## {group}", "", "| Source unit | Decision | Destination | Keep / omit |", "| --- | --- | --- | --- |"])
        for row in dispositions:
            if not row["id"].startswith(group + ":"):
                continue
            detail = " ".join(f"{label}: {row[key]}" for key, label in [("keep", "Keep"), ("omit", "Omit"), ("safeguard", "Safeguard")] if key in row)
            values = [row["id"], row["decision"], ", ".join(row["chapters"]) or "-", detail]
            lines.append("| " + " | ".join(v.replace("|", "\\|").replace("\n", " ") for v in values) + " |")
        lines.append("")
    (WORK / "COVERAGE.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Inventory: {len(files)} source files; coverage: {len(dispositions)} units; {counts}")


if __name__ == "__main__":
    main()
