"""Print a colorful, read-only overview of local Homebrew chapter coverage."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import sys
import textwrap
import unicodedata

import yaml

from study.app.translations import reviewed_records

ROOT = Path(__file__).resolve().parent
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DATA_ERRORS = (OSError, ValueError, KeyError, TypeError, yaml.YAMLError)
COUNTS = ("parts", "translations", "cards", "videos", "russian_audio")


@dataclass
class ChapterStatus:
    """Count subchapters with each resource, rather than individual assets."""

    title: str
    parts: int = 0
    translations: int = 0
    cards: int = 0
    videos: int = 0
    russian_audio: int = 0


def read_yaml(path: Path):
    """Use the safe C loader when available for the large translation corpus."""
    return yaml.load(path.read_text(encoding="utf-8"), Loader=YAML_LOADER)


def translation_available(base: Path, identity: str, kind: str, source: dict, terms: dict) -> bool:
    """Apply the study reader's checks for complete, current, reviewed Russian."""
    try:
        records = reviewed_records(base, identity, kind, source, terms, read_yaml)
        return bool(records) and all(
            isinstance(record.get("ru"), str) and record["ru"].strip() for record in records.values()
        )
    except DATA_ERRORS:
        return False


def section_source(section: dict) -> dict:
    """Include the section heading and every paragraph/list-item sentence."""
    source = {section["id"]: section["title"]}
    for block in section["blocks"]:
        for unit in block.get("items", [block]):
            for sentence in unit["sentences"]:
                source[sentence["id"]] = unit["text"][sentence["start"]:sentence["end"]]
    return source


def has_bytes(path: Path) -> bool:
    """Exclude missing files, directories and empty media placeholders."""
    return path.is_file() and path.stat().st_size > 0


def collect_status(root: Path) -> list[ChapterStatus]:
    """Inspect the manifest, reviewed translations, section decks and local media."""
    data = root / "data/homebrew"
    russian = data / "ru"
    manifest = read_yaml(data / "manifest.yaml")
    try:
        terms = {term["id"]: term for term in read_yaml(russian / "glossary.yaml")["entries"]}
    except DATA_ERRORS:
        terms = None
    rows = []
    for entry in sorted(manifest["chapters"], key=lambda item: item["order"]):
        chapter = read_yaml(data / entry["path"])
        row = ChapterStatus(f'{entry["order"]}. {chapter["title"]}', len(chapter["sections"]))
        heading_available = terms is not None and translation_available(
            russian, chapter["id"], "headings", {chapter["id"]: chapter["title"]}, terms,
        )
        for number, section in enumerate(chapter["sections"], 1):
            row.translations += heading_available and translation_available(
                russian, section["id"], "sections", section_source(section), terms,
            )
            deck = root / "cards/homebrew" / chapter["id"] / f'{section["id"]}.txt'
            row.cards += deck.is_file() and bool(deck.read_text(encoding="utf-8").strip())
            slug = section["id"].removeprefix(chapter["id"] + "-")
            video = root / "videos/homebrew" / f'{chapter["id"]}-{number:02d}-{slug}.mp4'
            # The packager can replace an MP4 with one shared HLS video stream.
            hls = video.with_suffix("")
            packaged = all(has_bytes(hls / name) for name in ("master.m3u8", "video.m3u8", "video.m4s"))
            available = has_bytes(video) or packaged
            row.videos += available
            row.russian_audio += available and (
                has_bytes(video.with_suffix(".ru.m4a"))
                or (packaged and all(has_bytes(hls / name) for name in ("master-ru.m3u8", "ru.m3u8", "ru.m4s")))
            )
        rows.append(row)
    return rows


def display_width(text: str) -> int:
    """Account for the two-column emoji markers when padding the table."""
    return sum(0 if unicodedata.combining(char) else
               2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def render_report(rows: list[ChapterStatus], *, color: bool = False,
                  plain: bool = False, width: int = 120) -> str:
    """Render a wrapping table with status markers that also work without ANSI."""
    color = color and not plain

    def paint(text, code):
        return f"\033[{code}m{text}\033[0m" if color else text

    def marker(count, total):
        state = 0 if total and count == total else 1 if count else 2
        symbols = ("+", "~", "-") if plain else ("\U0001f7e2", "\U0001f7e1", "\u26aa")
        return symbols[state], ("32", "33", "90")[state]

    total = ChapterStatus("Total", **{key: sum(getattr(row, key) for row in rows) for key in COUNTS})
    headers = ["Chapter", "Parts", "RU text", "Cards", "Videos", "RU audio"]
    cells = []
    styles = []
    for row in [*rows, total]:
        values, codes = [row.title, str(row.parts)], ["", ""]
        for key in COUNTS[1:]:
            count = getattr(row, key)
            symbol, code = marker(count, row.parts)
            values.append(f"{symbol} {count}/{row.parts}")
            codes.append(code)
        cells.append(values)
        styles.append(codes)
    widths = [max(display_width(values[i]) for values in [headers, *cells]) for i in range(len(headers))]
    widths[0] = max(14, min(widths[0], width - sum(widths[1:]) - 3 * len(headers) - 1))
    vertical = "|" if plain else "\u2502"

    def border(kind):
        chars = ("+", "+", "+", "-") if plain else {
            "top": ("\u256d", "\u252c", "\u256e", "\u2500"),
            "middle": ("\u251c", "\u253c", "\u2524", "\u2500"),
            "bottom": ("\u2570", "\u2534", "\u256f", "\u2500"),
        }[kind]
        left, joint, right, line = chars
        return paint(left + joint.join(line * (size + 2) for size in widths) + right, "36")

    def table_row(values, codes, bold=False):
        columns = []
        for i, (value, size, code) in enumerate(zip(values, widths, codes)):
            padding = " " * (size - display_width(value))
            if i >= 2 and code and value:
                symbol, count = value.split(" ", 1)
                padded = symbol + " " + padding + count
            else:
                padded = value + padding if i == 0 else padding + value
            style = ";".join(part for part in ("1" if bold else "", code) if part)
            columns.append(paint(padded, style) if style else padded)
        edge = paint(vertical, "36")
        return edge + " " + (" " + edge + " ").join(columns) + " " + edge

    title = "Homebrew progress" if plain else "\U0001f4da Homebrew progress"
    output = ["", paint(title, "1;36"), "Subchapters with each resource / all subchapters", "", border("top"),
              table_row(headers, [""] * len(headers), bold=True), border("middle")]
    for index, (values, codes) in enumerate(zip(cells, styles)):
        is_total = index == len(rows)
        if is_total:
            output.append(border("middle"))
        lines = textwrap.wrap(values[0], width=widths[0]) or [""]
        output.append(table_row([lines[0], *values[1:]], codes, bold=is_total))
        for line in lines[1:]:
            output.append(table_row([line, *([""] * (len(headers) - 1))], codes))
    output.extend([border("bottom"), ""])
    labels = []
    for count, label in ((2, "complete"), (1, "some ready"), (0, "none yet")):
        symbol, code = marker(count, 2)
        labels.append(paint(f"{symbol} {label}", code))
    output.append("   ".join(labels))
    output.extend([
        "RU text: reviewed and current. Cards: at least one card in the subchapter deck.",
        "Videos and RU audio: local files; RU audio requires a matching video.",
        "",
    ])
    return "\n".join(output)


def main(argv=None) -> int:
    """Print the report without changing files or contacting a server."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plain", action="store_true", help="Use ASCII borders and markers, without ANSI colors")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto",
                        help="ANSI colors (default: auto; respects NO_COLOR)")
    args = parser.parse_args(argv)
    color = args.color == "always" or (
        args.color == "auto" and sys.stdout.isatty() and "NO_COLOR" not in os.environ
        and os.environ.get("TERM") != "dumb"
    )
    try:
        rows = collect_status(ROOT)
    except DATA_ERRORS as error:
        parser.exit(1, f"Homebrew status error: {error}\n")
    print(render_report(rows, color=color, plain=args.plain,
                        width=shutil.get_terminal_size(fallback=(120, 24)).columns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
