"""Build or check one ALL.txt deck per Homebrew chapter with available cards."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def combined_decks(repo_root: Path) -> dict[Path, bytes]:
    """Concatenate available section decks in anthology order, excluding ALL.txt."""
    cards_dir = repo_root / "cards/homebrew"
    data_dir = repo_root / "data/homebrew"
    manifest = yaml.safe_load((data_dir / "manifest.yaml").read_text(encoding="utf-8"))
    chapters = {chapter["id"]: chapter for chapter in manifest["chapters"]}
    outputs = {}
    for chapter_dir in sorted(cards_dir.glob("*")):
        if not chapter_dir.is_dir():
            continue
        inputs = {path for path in chapter_dir.glob("*.txt") if path.name != "ALL.txt"}
        if not inputs:
            continue
        if chapter_dir.name not in chapters:
            raise ValueError(f"Unknown Homebrew chapter: {chapter_dir.name}")
        source_path = data_dir / chapters[chapter_dir.name]["path"]
        source = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        ordered = [chapter_dir / f"{section['id']}.txt" for section in source["sections"]]
        unexpected = inputs - set(ordered)
        if unexpected:
            names = ", ".join(sorted(path.name for path in unexpected))
            raise ValueError(f"Unknown section decks in {chapter_dir.name}: {names}")
        rows = [
            line
            for path in ordered if path in inputs
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if rows:
            outputs[chapter_dir / "ALL.txt"] = ("\n".join(rows) + "\n").encode("utf-8")
    return outputs


def combine_chapters(repo_root: Path, *, check: bool = False) -> int:
    """Refresh derived decks, or return 1 on drift without writing in check mode."""
    outputs = combined_decks(repo_root)
    existing = set((repo_root / "cards/homebrew").glob("*/ALL.txt"))
    stale = False
    for path in sorted(set(outputs) | existing):
        expected = outputs.get(path)
        current = path.read_bytes() if path.exists() else None
        label = path.relative_to(repo_root)
        if current == expected:
            print(f"[OK] {label} is up to date")
            continue
        stale = True
        if check:
            reason = "obsolete" if expected is None else "missing" if current is None else "stale"
            print(f"[FAIL] {label} is {reason}")
        elif expected is None:
            path.unlink()
            print(f"[OK] Removed {label}: no chapter cards remain")
        else:
            path.write_bytes(expected)
            print(f"[OK] Wrote {label} ({len(expected.splitlines())} cards)")
    if check and stale:
        print("Run make combine-homebrew and commit the generated chapter decks.")
        return 1
    return 0


def main(argv=None) -> int:
    """Rebuild chapter decks by default; --check only verifies existing output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail on missing or stale outputs without writing")
    args = parser.parse_args(argv)
    try:
        return combine_chapters(ROOT, check=args.check)
    except (OSError, ValueError, yaml.YAMLError) as error:
        parser.exit(1, f"Homebrew combine error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
