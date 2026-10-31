"""Validate Homebrew Anki rows and enforce the project's Kahoot text limits."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from card_creator.kahoot.export import parse_anki_mcq_line


def validate_line(line, *, source, line_num, category=None):
    """Reject malformed cards that the permissive legacy exporter would accept."""
    label = f'{source}:{line_num}'
    fields = line.split('|')
    if len(fields) != 10 or fields[2] != '2' or fields[7] != '' or fields[9] != '2':
        raise ValueError(f'{label}: expected Question|Category|2|A|B|C|D||flags|2')
    if any(value != value.strip() for value in fields):
        raise ValueError(f'{label}: leading/trailing field whitespace')
    if not fields[1] or (category is not None and fields[1] != category):
        raise ValueError(f'{label}: missing or incorrect section-title category')
    flags = fields[8].split()
    if len(flags) != 4 or any(f not in ('0', '1') for f in flags) or flags.count('1') != 1:
        raise ValueError(f'{label}: exactly four binary flags and one correct answer required')
    row = parse_anki_mcq_line(line, source=source, line_num=line_num)
    if len(row.question) > 120:
        raise ValueError(f'{label}: question exceeds 120 characters')
    if any(len(answer) > 70 for answer in row.answers):
        raise ValueError(f'{label}: answer exceeds 70 characters')
    if len({answer.casefold() for answer in row.answers}) != 4:
        raise ValueError(f'{label}: answer options must be distinct')
    return row


def validate_file(path, *, category=None):
    """Return valid parsed rows; reject empty decks and repeated question stems."""
    rows, seen = [], set()
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        row = validate_line(line, source=path, line_num=number, category=category)
        identity = row.question.casefold()
        if identity in seen:
            raise ValueError(f'{path}:{number}: duplicate question stem')
        seen.add(identity)
        rows.append(row)
    if not rows:
        raise ValueError(f'{path}: empty deck; record no eligible cards instead of creating a placeholder')
    return rows


def main():
    """Check supplied decks without modifying their content."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('decks', type=Path, nargs='+')
    parser.add_argument('--category', help='Require this exact Swedish section title')
    args = parser.parse_args()
    try:
        count = sum(len(validate_file(path, category=args.category)) for path in args.decks)
        print(f'Validated {count} cards in {len(args.decks)} decks (120/70 character limits).')
    except (ValueError, OSError) as error:
        parser.exit(1, f'Card validation error: {error}\n')


if __name__ == '__main__':
    main()
