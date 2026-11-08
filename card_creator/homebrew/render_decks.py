"""Generate Anki/Kahoot-compatible Homebrew TXT decks from canonical YAML.

The editable source of truth is data/homebrew/cards/hb-cNN.yaml.
Generated TXT files must never be edited by hand.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
CARD_ID = re.compile(r"^hb-c\d{2}-[a-z0-9-]+-\d{4}$")


def _valid_text(value, limit, name):
    if (not isinstance(value, str) or not value or value.strip() != value
            or len(value) > limit or any(c in value for c in "|\r\n")):
        raise ValueError(f"Invalid {name}: {value!r}")
    return value


def rendered_decks(repo_root: Path) -> dict[Path, bytes]:
    """Validate YAML and render each per-section legacy deck in source order."""
    data = repo_root / "data/homebrew"
    manifest = yaml.safe_load((data / "manifest.yaml").read_text(encoding="utf-8"))
    chapters = manifest["chapters"]
    yaml_dir = data / "cards"
    expected = {f"{chapter['id']}.yaml" for chapter in chapters}
    actual = {p.name for p in yaml_dir.glob("*.yaml")}
    if actual != expected:
        raise ValueError(f"Canonical YAML files differ: missing={expected - actual}, extra={actual - expected}")
    result = {}
    all_ids = set()
    for chapter in chapters:
        chapter_id = chapter["id"]
        source = yaml.safe_load((data / chapter["path"]).read_text(encoding="utf-8"))
        sections = {s["id"]: s["title"] for s in source["sections"]}
        document = yaml.safe_load((yaml_dir / f"{chapter_id}.yaml").read_text(encoding="utf-8"))
        if (not isinstance(document, dict) or document.get("schema_version") != 1
                or document.get("chapter_id") != chapter_id
                or document.get("language") != "sv" or not isinstance(document.get("cards"), list)):
            raise ValueError(f"Invalid canonical document for {chapter_id}")
        by_section = {section_id: [] for section_id in sections}
        seen_question = {section_id: set() for section_id in sections}
        for card in document["cards"]:
            if not isinstance(card, dict):
                raise ValueError(f"{chapter_id}: invalid card")
            identity, section = card.get("id"), card.get("section_id")
            if (not isinstance(identity, str) or not CARD_ID.fullmatch(identity)
                    or section not in sections or not identity.startswith(section + "-")
                    or identity in all_ids):
                raise ValueError(f"{chapter_id}: missing, reused, or invalid stable card ID: {identity}")
            all_ids.add(identity)
            category = _valid_text(card.get("category"), 120, "category")
            if category != sections[section]:
                raise ValueError(f"{identity}: category must match the section title")
            question = _valid_text(card.get("question"), 120, "question")
            if question.casefold() in seen_question[section]:
                raise ValueError(f"{identity}: duplicate question")
            seen_question[section].add(question.casefold())
            choices = card.get("options")
            if not isinstance(choices, list) or len(choices) != 4:
                raise ValueError(f"{identity}: exactly four answer options required")
            option_ids = [choice.get("id") for choice in choices if isinstance(choice, dict)]
            if option_ids != ["a0", "a1", "a2", "a3"]:
                raise ValueError(f"{identity}: expected answer IDs a0 through a3")
            options = [_valid_text(choice.get("text"), 70, "option") for choice in choices]
            if len({option.casefold() for option in options}) != 4:
                raise ValueError(f"{identity}: duplicate answer options")
            correct = card.get("correct_option_id")
            if correct not in option_ids:
                raise ValueError(f"{identity}: correct answer ID must select an option")
            flags = " ".join("1" if c == correct else "0" for c in option_ids)
            by_section[section].append("|".join(
                [question, category, "2", *options, "", flags, "2"]))
        for section, rows in by_section.items():
            if rows:
                result[repo_root / "cards/homebrew" / chapter_id / f"{section}.txt"] = (
                    "\n".join(rows) + "\n").encode("utf-8")
    return result


def render(repo_root: Path, *, check: bool = False) -> int:
    """Write derived TXT files, or report drift without modifying any files."""
    outputs = rendered_decks(repo_root)
    folder = repo_root / "cards/homebrew"
    existing = {p for p in folder.glob("*/*.txt") if p.name != "ALL.txt"}
    stale = False
    for path in sorted(set(outputs) | existing):
        expected = outputs.get(path)
        current = path.read_bytes() if path.is_file() else None
        if current == expected:
            continue
        stale = True
        print(f"[{'FAIL' if check else 'OK'}] {path.relative_to(repo_root)}: "
              + ("obsolete" if expected is None else "missing" if current is None else "stale"))
        if not check:
            if expected is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(expected)
    if check and stale:
        print("Run make combine-homebrew to regenerate derived Homebrew TXT decks.")
    return int(check and stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing")
    args = parser.parse_args()
    try:
        return render(ROOT, check=args.check)
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        parser.exit(1, f"Canonical Homebrew card export error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
