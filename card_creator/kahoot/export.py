#!/usr/bin/env python3
"""
Export Anki-style MCQ decks from `cards/` into Kahoot-compatible XLSX files.

This script mirrors the directory structure from `cards/` into `kahoot/`.
For every `cards/**/*.txt` file, it generates:
- `kahoot/**/*.xlsx`  (Kahoot import template filled with questions)

The conversion expects the repository's pipe-delimited Anki MCQ row format:
    Question|Category|2|Opt1|Opt2|Opt3|Opt4||0 1 0 0|2
where the "0 1 0 0" segment marks the correct answer(s).

XLSX generation uses the `third/kahoot-generator` submodule (imported from
`third/kahoot-generator/src`). Ensure you've initialized submodules and
installed deps:
  - git submodule update --init --recursive
  - poetry install
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class ParsedRow:
    question: str
    answers: Tuple[str, str, str, str]
    correct_flags: Tuple[bool, bool, bool, bool]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_kahoot_generator_importable(repo_root: Path) -> None:
    try:
        import kahoot_generator  # noqa: F401
        return
    except ImportError:
        pass

    src_dir = repo_root / "third" / "kahoot-generator" / "src"
    if not src_dir.is_dir():
        raise RuntimeError(
            f"kahoot-generator submodule not found at {src_dir}. "
            "Run: git submodule update --init --recursive"
        )

    sys.path.insert(0, str(src_dir))

    import kahoot_generator  # noqa: F401  # pylint: disable=unused-import


def _parse_correct_flags(flags: str) -> Optional[Tuple[bool, bool, bool, bool]]:
    parts = [p for p in (flags or "").strip().split() if p]
    if len(parts) != 4:
        return None
    if any(p not in {"0", "1"} for p in parts):
        return None
    return tuple(p == "1" for p in parts)  # type: ignore[return-value]


def parse_anki_mcq_line(line: str, *, source: Path, line_num: int) -> ParsedRow:
    parts = line.rstrip("\n").split("|")
    if len(parts) < 7:
        raise ValueError(f"{source}:{line_num}: expected at least 7 fields, got {len(parts)}")

    question = (parts[0] or "").strip()
    if not question:
        raise ValueError(f"{source}:{line_num}: empty question")

    answers_raw = parts[3:7]
    if len(answers_raw) != 4:
        raise ValueError(f"{source}:{line_num}: expected 4 answer options, got {len(answers_raw)}")

    answers = tuple((a or "").strip() for a in answers_raw)
    if any(not a for a in answers):
        raise ValueError(f"{source}:{line_num}: answer options must be non-empty")

    correct_flags: Optional[Tuple[bool, bool, bool, bool]] = None
    if len(parts) >= 9:
        correct_flags = _parse_correct_flags(parts[8])

    if correct_flags is None and len(parts) >= 10:
        last = (parts[9] or "").strip()
        if last.isdigit():
            idx = int(last)
            if 1 <= idx <= 4:
                correct_flags = tuple((i + 1) == idx for i in range(4))  # type: ignore[assignment]

    if correct_flags is None:
        raise ValueError(
            f"{source}:{line_num}: could not parse correct answer flags "
            "(expected '0 1 0 0' field or a final 1-4 correct index)"
        )

    if not any(correct_flags):
        raise ValueError(f"{source}:{line_num}: at least one answer must be correct")

    return ParsedRow(
        question=question,
        answers=answers,  # type: ignore[arg-type]
        correct_flags=correct_flags,
    )


def build_questions(rows: Sequence[ParsedRow], *, time_limit: int):
    from kahoot_generator import AnswerOption, Question

    questions = []
    for row in rows:
        answers = [
            AnswerOption(text=row.answers[i], is_correct=row.correct_flags[i])
            for i in range(4)
        ]
        questions.append(Question(text=row.question, answers=answers, time_limit=time_limit))
    return questions


def export_deck(
    *,
    cards_path: Path,
    out_root: Path,
    repo_root: Path,
    time_limit: int,
) -> Path:
    relative = cards_path.relative_to(repo_root / "cards")
    xlsx_out = out_root / relative.with_suffix(".xlsx")

    rows: List[ParsedRow] = []
    with cards_path.open("r", encoding="utf-8") as f:
        for idx, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            rows.append(parse_anki_mcq_line(line, source=cards_path, line_num=idx))

    from kahoot_generator import generate_quiz_xlsx

    questions = build_questions(rows, time_limit=time_limit)
    generate_quiz_xlsx(questions=questions, output_path=xlsx_out)
    return xlsx_out


def list_card_decks(cards_dir: Path) -> List[Path]:
    decks = [p for p in cards_dir.rglob("*.txt") if p.is_file()]
    decks.sort(key=lambda p: p.as_posix())
    return decks


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export cards/ decks into kahoot/ XLSX files.")
    parser.add_argument(
        "--cards-dir",
        type=Path,
        default=Path("cards"),
        help="Input cards directory (default: cards).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("kahoot"),
        help="Output directory (default: kahoot).",
    )
    parser.add_argument(
        "--time-limit",
        type=int,
        default=20,
        help="Per-question time limit in seconds (default: 20).",
    )
    parser.add_argument(
        "--skip-all",
        action="store_true",
        help="Skip exporting cards/ALL.txt.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    repo_root = _repo_root()
    _ensure_kahoot_generator_importable(repo_root)

    args = build_arg_parser().parse_args(list(argv) if argv is not None else None)
    cards_dir: Path = (repo_root / args.cards_dir).resolve()
    out_dir: Path = (repo_root / args.out_dir).resolve()

    if not cards_dir.is_dir():
        raise RuntimeError(f"cards dir not found: {cards_dir}")

    decks = list_card_decks(cards_dir)
    if not decks:
        print(f"[WARN] No decks found under: {cards_dir}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)

    exported = 0
    for deck_path in decks:
        if args.skip_all and deck_path.resolve() == (cards_dir / "ALL.txt").resolve():
            continue
        xlsx_path = export_deck(
            cards_path=deck_path,
            out_root=out_dir,
            repo_root=repo_root,
            time_limit=args.time_limit,
        )
        exported += 1
        print(f"[OK] {deck_path.relative_to(repo_root)} -> {xlsx_path.relative_to(repo_root)}")

    print(f"[OK] Exported {exported} deck(s) to: {out_dir.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
