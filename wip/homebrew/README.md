# Homebrew working area

Start with [PILOT_REVIEW.md](PILOT_REVIEW.md), the pending second checkpoint, and
[PILOT.sv.md](PILOT.sv.md) for the Swedish reading copy. The agreed
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

Checkpoint 1 is approved. The standalone Swedish pilot is in `data/homebrew/`.
The original [REVIEW.md](REVIEW.md) remains the record of the approved proposal.
`pilot_selection.yaml` records exact selections and stable text-unit IDs;
`pilot_sentences.yaml` freezes sentence IDs and ranges. See the collection's
[schema](../../data/homebrew/SCHEMA.md) for editing and regeneration rules.

## Reproduce the review artifacts

From the repository root, using its supported Python version and Poetry:

```bash
poetry install --no-root
poetry run python wip/homebrew/tools/extract_sources.py
poetry run python wip/homebrew/tools/build_review.py
poetry run python wip/homebrew/tools/validate_review.py
poetry run python wip/homebrew/tools/build_pilot.py
poetry run python wip/homebrew/tools/validate_pilot.py
poetry run python -m unittest discover -s wip/homebrew/tools -p 'test_*.py' -v
```

Extraction reads only local files. Dependency installation downloads software,
not study material. The tools use BeautifulSoup, pypdf and PyYAML; dependency
versions are managed in the repository's Poetry files.

`extracted/` is ignored by Git because it duplicates about 9 MB of source text.
It is regenerated deterministically and retains source paths/hashes, HTML block
locators and PDF page boundaries. Its block IDs locate fixed source snapshots;
they are not the stable learner-content IDs allocated in the pilot.

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

Checkpoint 1 approved the source-level dispositions. The pilot's exact selections
and omission audit are in `data/homebrew/metadata/05_editorial_review.yaml`;
the broad map is not a claim that other chapters' passage selection is complete.
`validate_review.py` checks the inventory and broad map; `validate_pilot.py` checks
the learner content and re-reads original bytes for passage and sentence fidelity.
