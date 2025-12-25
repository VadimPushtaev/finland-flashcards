# Translations

This directory contains translated versions of selected source materials under
`data/`.

Rules:
- Never edit or overwrite the original files in `data/`.
- Keep translations as close to the original structure and formatting as
  possible (including HTML structure and images where present).
- Preserve original provenance: keep the original source URL metadata (e.g.
  `<meta name="source" ...>` in HTML) unchanged.

Currently tracked:
- `translations/ru/orientation/`: translations of the civic orientation website
  crawl under `data/orientation/`.

We currently translate only to Russian (under `translations/ru/`), but we may
add more languages in the future.

## Conventions

Each translation area folder (e.g., `translations/ru/orientation/`) contains:
- `GUIDE.md`: how to translate that source.
- `PROGRESS.md`: what has been translated (or skipped) and current status.
