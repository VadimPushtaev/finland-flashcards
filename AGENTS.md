# Repository Guidelines

## Project Structure & Module Organization
- `card_creator/` holds tooling and prompts for flashcard creation; keep scripts alongside their domain (e.g., `pdf/` for PDF-derived workflows) and document progress in `card_creator/card_progress.md`.
- `card_creator/pdf/split_cards.py` converts the aggregated `output.txt` into per-subchapter decks under `cards/pdf/`; treat `output.txt` as scratch space that should not be committed.
- `cards/` stores ready-to-import Anki decks grouped by source (`articles/`, `infofinland/`, `pdf/`); match filenames to chapter numbers plus a slug (e.g., `1.2_rights_and_obligations.txt`).
- `data/` archives the raw material consumed by agents; keep crawled InfoFinland HTML within `data/infofinland/content/` and PDFs or source bundles in the language-specific subdirectories.

## Build, Test, and Development Commands
```bash
python3 card_creator/pdf/split_cards.py       # Split the latest PDF-derived cards into chapter files
python3 data/infofinland/crawler.py -o data/infofinland/content  # Refresh Swedish InfoFinland articles
python3 -m compileall card_creator data/infofinland              # Smoke-check Python syntax before committing
```
Install Python deps (`requests`, `beautifulsoup4`) in your virtualenv before running crawlers.

## Coding Style & Naming Conventions
- Python uses 4-space indentation, docstrings for modules/classes, and `snake_case` for functions, variables, and filenames.
- Keep scripts ASCII-only unless the source content demands accents; rely on `clean_filename` patterns that normalize titles.
- Flashcard rows must remain pipe-delimited with exactly four options and a single correct flag (`0 1 0 0` format).
- Place ad-hoc notebooks or prompts under a clearly named subfolder (e.g., `card_creator/research/`) to avoid polluting production paths.

## Testing Guidelines
- Verify regenerated decks by spot-checking formatting (`head cards/pdf/*.txt`) and ensuring every line contains a double pipe separator.
- After running the crawler, confirm `data/infofinland/content/crawl_stats.txt` reflects the new page count and manually review a sample HTML file.
- When editing generators, re-run `split_cards.py` and diff the produced files to detect unintended reorderings before pushing.

## Commit & Pull Request Guidelines
- Follow the existing history: short (≤72 char), imperative subject lines such as `Add Chapter 1 flashcards`.
- Bundle related changes per commit (crawler tweaks vs. card updates) and mention affected directories in the body when clarification helps reviewers.
- Pull requests should outline the data sources touched, highlight any manual curation, and include screenshots or sample card excerpts when UX changes are introduced.

## Data & Content Management
- Record newly processed sections in `card_progress.md` so collaborators avoid duplicating effort.
- Preserve original source archives in `data/` and note provenance; never overwrite raw PDFs—add dated versions if updates are required.
- For sensitive or rate-limited sources, document authentication steps in a separate credential handoff, not in the repository.
