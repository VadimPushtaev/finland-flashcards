#!/usr/bin/env python3
"""
Combine all deck files under the repository's `cards/` directory into a single
`cards/ALL.txt` file. The order of files is stable and deterministic, using a
lexicographic sort of POSIX-style paths (akin to a sorted `find`).

Usage (from repo root):
    poetry run python card_creator/combine_all_cards.py

This script is invoked by `make`.
"""

from __future__ import annotations

from pathlib import Path


def list_card_files(cards_dir: Path) -> list[Path]:
    """Return a stably ordered list of card files to include.

    - Recurses under `cards_dir`.
    - Includes only `.txt` files.
    - Excludes the combined output file `ALL.txt`.
    - Sorted lexicographically by POSIX path for stability.
    """
    all_txt = list(cards_dir.rglob("*.txt"))
    out_path = cards_dir / "ALL.txt"
    filtered = [p for p in all_txt if p.resolve() != out_path.resolve()]
    # Stable, deterministic order similar to a sorted `find` listing
    filtered.sort(key=lambda p: p.as_posix())
    return filtered


def combine_cards(repo_root: Path) -> Path:
    """Combine all card files into `cards/ALL.txt` and return the output path."""
    cards_dir = repo_root / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    files = list_card_files(cards_dir)
    out_path = cards_dir / "ALL.txt"

    # Stream lines from each file in order to the output
    with out_path.open("w", encoding="utf-8", newline="\n") as out_f:
        first = True
        for fp in files:
            with fp.open("r", encoding="utf-8") as in_f:
                for line in in_f:
                    # Ensure lines end with a single newline
                    if line.endswith("\n"):
                        out_f.write(line)
                    else:
                        out_f.write(line + "\n")
            # Do not insert extra blank lines between files; content carries newlines
            first = False

    return out_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = combine_cards(repo_root)
    print(f"[OK] Wrote combined deck: {out_path}")


if __name__ == "__main__":
    main()

