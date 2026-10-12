# Homebrew working area

Start with [REVIEW.md](REVIEW.md), the first review checkpoint. The agreed
[plan](PLAN.md) governs the work; [PROGRESS.md](PROGRESS.md) records its state.

- [LEGAL_SCOPE.md](LEGAL_SCOPE.md): local law and official guidance, with exact
  page references and the distinction between enacted scope and interpretation.
- [outline.yaml](outline.yaml): proposed Swedish chapter order and topics.
- [COVERAGE.md](COVERAGE.md): readable disposition for every source unit.
- [coverage.yaml](coverage.yaml): the same map with source headings, safeguards
  and PDF candidate-page locators.
- [selection_rules.yaml](selection_rules.yaml): editable editorial rules used to
  generate the coverage proposal.
- [source_inventory.yaml](source_inventory.yaml): hashes of every source file
  used in the review.
- [ISSUES.md](ISSUES.md): conflicts, missing content and source-reuse records.
- [VALIDATION.md](VALIDATION.md): checks completed for this review stage.

No learner chapters are authored before checkpoint 1. The eventual standalone
Swedish material belongs in `data/homebrew/`, not in this working area.

## Reproduce the review artifacts

From the repository root, using its supported Python version and Poetry:

```bash
poetry install --no-root
poetry run python wip/homebrew/tools/extract_sources.py
poetry run python wip/homebrew/tools/build_review.py
poetry run python wip/homebrew/tools/validate_review.py
poetry run python -m unittest discover -s wip/homebrew/tools -p 'test_*.py' -v
```

Extraction reads only local files. Dependency installation downloads software,
not study material. The tools use BeautifulSoup, pypdf and PyYAML; dependency
versions are managed in the repository's Poetry files.

`extracted/` is ignored by Git because it duplicates about 9 MB of source text.
It is regenerated deterministically and retains source paths/hashes, HTML block
locators and PDF page boundaries. Its block IDs locate fixed source snapshots;
they are not the stable learner-content IDs to be introduced in the pilot.

On this sandboxed machine, Poetry's default cache was not writable. The commands
were run with `POETRY_CACHE_DIR=/private/tmp/homebrew-poetry-cache`,
`POETRY_VIRTUALENVS_PATH=/private/tmp/homebrew-poetry-envs` and
`VIRTUALENV_APP_DATA=/private/tmp/homebrew-virtualenv-data`, using system Python
3.9.6. These are temporary execution settings, not repository configuration.

## Review granularity

`include` means retain substantive coverage subject to common omissions;
`partial` identifies substantive cuts within a source; `exclude` removes the
source unit; `duplicate` routes index-level material to detailed articles;
`gap` identifies missing source content that remains relevant.

Every disposition remains proposed until checkpoint 1 is reviewed. Exact
paragraph selection, deduplication, repair logs and learner YAML/sentence-range
validation are deliberately later stages. The current validator checks source
fingerprints, extraction fidelity and coverage-map completeness.
