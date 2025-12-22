# Finland Flashcards

Scripts, data, and workflows to generate Anki multiple‑choice decks from Finnish orientation materials and InfoFinland content.

## Quick Start

- Requires Python 3.9–3.12 and Poetry.
- After cloning, fetch submodules:
  - `git submodule update --init --recursive`
  - If GitHub SSH is not configured, use HTTPS for submodules: `git config --global url."https://github.com/".insteadOf "git@github.com:"`
- Install deps:
  - `poetry install`
- Generate Orientation Guide decks (from committed output):
  - `poetry run python card_creator/orientation_guide/split_cards.py`
- Crawl Swedish InfoFinland content:
  - `poetry run python data/infofinland/crawler.py -o data/infofinland/content`
- Crawl English Yhteiskuntaorientaatio learning materials:
  - `poetry run python data/orientation/crawler.py -l en -o data/orientation/en`
- Combine all decks into a single import file:
  - `make` (creates `cards/ALL.txt`)
- Export decks as Kahoot quizzes (XLSX):
  - `make kahoot` (writes quizzes under `kahoot/` mirroring `cards/`; large decks are split into `__0001` chunks)

## Repository Structure

- `card_creator/` — Tools, prompts, and progress for flashcard creation
  - `orientation_guide/` — ChatGPT prompt, `output.txt` source, and `split_cards.py`
  - `card_progress.md` — Progress log; update after generating decks
- `cards/` — Ready‑to‑import Anki decks grouped by source (`articles/`, `infofinland/`, `orientation_guide/`)
- `data/` — Raw source material and crawled content
  - `infofinland/` — Crawler and downloaded HTML under `content/`
  - `orientation/` — Crawler and downloaded HTML under language subfolders
- `third/` — External tooling vendored as git submodules (e.g., `kahoot-generator/`)
- `kahoot/` — Generated Kahoot exports (XLSX; committed)

See also:
- `card_creator/README.md` — Card format and creation workflow
- `card_creator/orientation_guide/README.md` — Orientation Guide workflow details
- `data/infofinland/README.md` — Crawler usage and options
- `data/orientation/README.md` — Crawler usage and options

## Card Format (MCQ)

- Pipe‑delimited rows with exactly 4 options and a single correct flag, e.g.:
  - `Question|Category|2|Opt1|Opt2|Opt3|Opt4||0 1 0 0|2`
- Targeted for the Anki “Multiple Choice Question” add‑on (ID 1566095810).
- Keep language and content per source (e.g., Swedish for InfoFinland and Orientation Guide).
 - Standalone questions: Do not reference the source. Avoid phrases like “enligt kapitlet”, “enligt texten”, “enligt artikeln”, or “i kapitlet/texten” (and English equivalents). Allowed: references to law or named institutions/authorities (e.g., “enligt lag”, “enligt Statistikcentralen/FPA/Migri”).

## Typical Workflows

Orientation Guide (textbook‑derived):
- Paste ChatGPT‑generated cards into `card_creator/orientation_guide/output.txt` and commit it.
- Split into per‑subchapter decks: `poetry run python card_creator/orientation_guide/split_cards.py`
- Verify outputs in `cards/orientation_guide/` (spot‑check with `head`).
- Update `card_creator/card_progress.md` with completed sections.

InfoFinland (crawler‑derived):
- Refresh content: `poetry run python data/infofinland/crawler.py -o data/infofinland/content`
- Confirm `data/infofinland/content/crawl_stats.txt` reflects the new page count.
- Manually review a few saved HTML files for correctness.

Yhteiskuntaorientaatio (crawler‑derived):
- Refresh content: `poetry run python data/orientation/crawler.py -l en -o data/orientation/en`
- Confirm `data/orientation/en/crawl_stats.txt` reflects the new page count.
- Manually review a few saved HTML files for correctness.

## Development

- Smoke‑check Python syntax: `poetry run python -m compileall card_creator data/infofinland data/orientation`
- Optional pre‑commit hooks:
  - `poetry run pre-commit install`
  - `poetry run pre-commit run --all-files`

Dependencies (Poetry‑managed): `requests`, `beautifulsoup4`.

## Contributing

- Keep scripts ASCII‑only unless source content requires accents.
- Filenames should be normalized (underscores, lowercase) to keep deck names stable.
- Preserve raw sources under `data/`; do not overwrite original PDFs or archives.
- Follow short, imperative commit messages and bundle related changes.

Agent policy: Do not commit or push without explicit confirmation. Summarize staged changes and propose a message before committing.

## License

MIT License. See `LICENSE`.
