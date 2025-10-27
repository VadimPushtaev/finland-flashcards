# Repository Guidelines

## Project Structure & Module Organization
- `card_creator/` holds tooling and prompts for flashcard creation; keep scripts alongside their domain (e.g., `orientation_guide/` for textbook-derived workflows) and document progress in `card_creator/card_progress.md`.
- `card_creator/orientation_guide/split_cards.py` converts the aggregated `output.txt` into per-subchapter decks under `cards/orientation_guide/`. The `output.txt` file is committed and serves as the source-of-truth for card generation.
- `cards/` stores ready-to-import Anki decks grouped by source (`articles/`, `infofinland/`, `orientation_guide/`); match filenames to chapter numbers plus a slug (e.g., `1.2_rights_and_obligations.txt`).
- `data/` archives the raw material consumed by agents; keep crawled InfoFinland HTML within `data/infofinland/content/` and PDFs or source bundles in the language-specific subdirectories.

## Build, Test, and Development Commands
Use Poetry for dependency management and to run scripts.
```bash
# First-time setup
poetry install

# Split the latest orientation guide-derived cards into chapter files
poetry run python card_creator/orientation_guide/split_cards.py

# Refresh Swedish InfoFinland articles
poetry run python data/infofinland/crawler.py -o data/infofinland/content

# Smoke-check Python syntax before committing
poetry run python -m compileall card_creator data/infofinland

# (optional) Install and run pre-commit hooks locally
poetry run pre-commit install
poetry run pre-commit run --all-files
```
Poetry-managed deps: `requests`, `beautifulsoup4`. No separate requirements.txt is used.

## Coding Style & Naming Conventions
- Python uses 4-space indentation, docstrings for modules/classes, and `snake_case` for functions, variables, and filenames.
- Keep scripts ASCII-only unless the source content demands accents; rely on `clean_filename` patterns that normalize titles.
- Flashcard rows must remain pipe-delimited with exactly four options and a single correct flag (`0 1 0 0` format).
- Place ad-hoc notebooks or prompts under a clearly named subfolder (e.g., `card_creator/research/`) to avoid polluting production paths.

## Testing Guidelines
- Verify regenerated decks by spot-checking formatting (`head cards/orientation_guide/*.txt`) and ensuring every line contains a double pipe separator.
- After running the crawler, confirm `data/infofinland/content/crawl_stats.txt` reflects the new page count and manually review a sample HTML file.
- When editing generators, re-run `split_cards.py` and diff the produced files to detect unintended reorderings before pushing.

## Commit & Pull Request Guidelines
- Follow the existing history: short (≤72 char), imperative subject lines such as `Add Chapter 1 flashcards`.
- Bundle related changes per commit (crawler tweaks vs. card updates) and mention affected directories in the body when clarification helps reviewers.
- Pull requests should outline the data sources touched, highlight any manual curation, and include screenshots or sample card excerpts when UX changes are introduced.

### Agent Commit Policy (IMPORTANT)
- Do not commit or push changes without explicit user confirmation.
- Before committing, summarize staged changes, propose a commit message, and wait for approval.
- Apply patches and run validations freely, but pause at the commit/push step until the user confirms.

## Data & Content Management
- Record newly processed sections in `card_progress.md` so collaborators avoid duplicating effort.
- Preserve original source archives in `data/` and note provenance; never overwrite raw PDFs—add dated versions if updates are required.
- For sensitive or rate-limited sources, document authentication steps in a separate credential handoff, not in the repository.
