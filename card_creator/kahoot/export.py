#!/usr/bin/env python3
"""
Export Anki-style MCQ decks from `cards/` into Kahoot-compatible XLSX files.

This script mirrors the directory structure from `cards/` into `kahoot/`.
For every `cards/**/*.txt` file, it generates one or more Kahoot XLSX files
under `kahoot/`:
- If the deck has <= 30 questions: `kahoot/**/deck.xlsx`
- If the deck has > 30 questions: `kahoot/**/deck__0001.xlsx`,
  `kahoot/**/deck__0002.xlsx`, ...

Chunking rule (to avoid tiny tail files):
- Files are split into 20-question chunks until the remainder is <= 30; the
  last chunk may therefore contain 21-30 questions.

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
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


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


_ZIP_DT = (1980, 1, 1, 0, 0, 0)


def _normalize_core_xml(xml_text: str) -> str:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return xml_text

    ns = {"dcterms": "http://purl.org/dc/terms/"}
    created_el = root.find(".//dcterms:created", ns)
    modified_el = root.find(".//dcterms:modified", ns)
    if created_el is None or modified_el is None:
        return xml_text

    if created_el.text:
        modified_el.text = created_el.text

    return ET.tostring(root, encoding="utf-8", xml_declaration=False).decode("utf-8")


def normalize_xlsx(path: Path) -> None:
    """
    Make XLSX output deterministic across runs.

    OpenPyXL writes ZIP entry timestamps based on current time and also updates
    `docProps/core.xml`'s `dcterms:modified` field. Both cause noisy diffs.

    This function rewrites the XLSX file in place:
    - sets all ZIP entry timestamps to a fixed value
    - normalizes `dcterms:modified` to match `dcterms:created`
    """
    with zipfile.ZipFile(path, "r") as src:
        entries = sorted(src.infolist(), key=lambda i: i.filename)
        with tempfile.NamedTemporaryFile(
            dir=str(path.parent),
            delete=False,
            prefix=path.name + ".",
            suffix=".tmp",
        ) as tmp_f:
            tmp_path = Path(tmp_f.name)

        try:
            with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_STORED) as dst:
                for info in entries:
                    data = src.read(info.filename)
                    if info.filename == "docProps/core.xml":
                        text = data.decode("utf-8")
                        data = _normalize_core_xml(text).encode("utf-8")

                    zi = zipfile.ZipInfo(filename=info.filename, date_time=_ZIP_DT)
                    zi.compress_type = zipfile.ZIP_STORED
                    zi.external_attr = info.external_attr
                    zi.create_system = 0
                    dst.writestr(zi, data)
        except Exception:
            tmp_path.unlink(missing_ok=True)
            raise

    tmp_path.replace(path)

def _chunk_ranges(total: int) -> List[Tuple[int, int]]:
    """
    Split `total` questions into ranges.

    Rules:
    - If total <= 30: one chunk (0..total).
    - Otherwise: emit 20-question chunks until the remainder is <= 30.
      This means the last chunk may be 21-30 questions.
    """
    if total <= 0:
        return []
    if total <= 30:
        return [(0, total)]

    ranges: List[Tuple[int, int]] = []
    start = 0
    remaining = total
    while remaining > 30:
        end = start + 20
        ranges.append((start, end))
        start = end
        remaining = total - start

    ranges.append((start, total))
    return ranges


_SUFFIX_RE = re.compile(r"__\d{4}$")


def _split_output_paths(base_xlsx_out: Path, *, question_count: int) -> List[Path]:
    ranges = _chunk_ranges(question_count)
    if len(ranges) <= 1:
        return [base_xlsx_out]
    return [
        base_xlsx_out.with_name(f"{base_xlsx_out.stem}__{i:04d}{base_xlsx_out.suffix}")
        for i in range(1, len(ranges) + 1)
    ]


def _cleanup_stale_outputs(base_xlsx_out: Path, desired: Sequence[Path]) -> None:
    """
    Remove stale XLSX files from previous runs for the same deck.

    - If we now produce a single file (no suffix), delete any `__0001`-style files.
    - If we now produce split files, delete the unsuffixed base file.
    - Always delete split files that are no longer needed (e.g., old higher indices).
    """
    desired_set = {p.resolve() for p in desired}
    parent = base_xlsx_out.parent

    existing_split = []
    for p in parent.glob(f"{base_xlsx_out.stem}__*.xlsx"):
        # Keep only the exact suffix form we generate: <stem>__0001.xlsx
        if p.suffix != base_xlsx_out.suffix:
            continue
        stem = p.stem
        if not stem.startswith(base_xlsx_out.stem + "__"):
            continue
        suffix_part = stem[len(base_xlsx_out.stem) :]
        if _SUFFIX_RE.fullmatch(suffix_part):
            existing_split.append(p)

    if len(desired) == 1:
        # Keep/overwrite base_xlsx_out; remove any split outputs.
        for p in existing_split:
            p.unlink(missing_ok=True)
        return

    # Split outputs: remove the base file if present.
    base_xlsx_out.unlink(missing_ok=True)
    for p in existing_split:
        if p.resolve() not in desired_set:
            p.unlink(missing_ok=True)


def export_deck(
    *,
    cards_path: Path,
    out_root: Path,
    repo_root: Path,
    time_limit: int,
) -> List[Path]:
    relative = cards_path.relative_to(repo_root / "cards")
    base_xlsx_out = out_root / relative.with_suffix(".xlsx")

    rows: List[ParsedRow] = []
    with cards_path.open("r", encoding="utf-8") as f:
        for idx, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            rows.append(parse_anki_mcq_line(line, source=cards_path, line_num=idx))

    if not rows:
        return []

    from kahoot_generator import generate_quiz_xlsx

    xlsx_out_paths = _split_output_paths(base_xlsx_out, question_count=len(rows))
    _cleanup_stale_outputs(base_xlsx_out, xlsx_out_paths)

    ranges = _chunk_ranges(len(rows))
    if len(ranges) != len(xlsx_out_paths):
        raise RuntimeError("internal error: chunk range count does not match output path count")

    for (start, end), out_path in zip(ranges, xlsx_out_paths):
        questions = build_questions(rows[start:end], time_limit=time_limit)
        generate_quiz_xlsx(questions=questions, output_path=out_path)
        normalize_xlsx(out_path)

    return xlsx_out_paths


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
        help="Skip exporting cards/ALL.txt (default behavior).",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include cards/ALL.txt in Kahoot exports.",
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

    exported_decks = 0
    exported_files = 0
    skipped_decks = 0
    skip_all = args.skip_all or not args.include_all
    for deck_path in decks:
        if skip_all and deck_path.resolve() == (cards_dir / "ALL.txt").resolve():
            continue
        xlsx_paths = export_deck(
            cards_path=deck_path,
            out_root=out_dir,
            repo_root=repo_root,
            time_limit=args.time_limit,
        )
        if not xlsx_paths:
            skipped_decks += 1
            print(f"[WARN] {deck_path.relative_to(repo_root)} -> no questions; skipped")
            continue
        exported_decks += 1
        exported_files += len(xlsx_paths)

        deck_rel = deck_path.relative_to(repo_root)
        if len(xlsx_paths) == 1:
            print(f"[OK] {deck_rel} -> {xlsx_paths[0].relative_to(repo_root)}")
        else:
            first = xlsx_paths[0].relative_to(repo_root)
            last = xlsx_paths[-1].relative_to(repo_root)
            print(f"[OK] {deck_rel} -> {first} ... {last} ({len(xlsx_paths)} files)")

    print(
        f"[OK] Exported {exported_decks} deck(s) ({exported_files} file(s)) "
        f"to: {out_dir.relative_to(repo_root)}"
    )
    if skipped_decks:
        print(f"[WARN] Skipped {skipped_decks} deck(s) with no questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
