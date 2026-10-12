# Homebrew Russian translation workflow

Permanent instructions and Python tools for translating the Swedish Homebrew book,
section by section. Start with [INSTRUCTIONS.md](INSTRUCTIONS.md) and the
[Russian data schema](../../data/homebrew/TRANSLATION_SCHEMA.md).

This directory is the authoritative workflow, not a disposable work plan. Final
Russian data belongs in `data/homebrew/ru/`. Generated context and temporary drafts
may live under `wip/homebrew/translation/` or outside the repository. Do not commit
context bundles: they duplicate archived material and become stale.

## Prepare a job

From the repository root, use the existing Poetry environment:

```sh
poetry install
poetry run python translation/homebrew/tools/workflow.py prepare hb-c01-lage --output /tmp/hb-c01-lage-context.yaml
```

The output must not already exist. The tool verifies archived source hashes and
fails if required sources are missing. It reads committed Swedish chapter data,
not disposable extraction intermediates. HTML context contains full article
bodies; PDF context includes cited pages and one neighboring page on either side.

Give the executor this task:

> Follow translation/homebrew/INSTRUCTIONS.md for section hb-c01-lage. Read the
> generated context bundle and schema. Produce the section translation and review
> metadata, coordinate shared terminology and the chapter heading, use parallel
> agents when useful, and run validation. Do not modify Swedish originals or UI.

Preparation does not generate translations or call a model service. The executor
performs the linguistic work. Language references may be consulted separately;
the preparation tool makes no network requests.

## Validate and inspect progress

```sh
poetry run python translation/homebrew/tools/workflow.py validate --source-id hb-c01-lage
poetry run python translation/homebrew/tools/workflow.py validate --source-id hb-c01-lage --require-complete
poetry run python translation/homebrew/tools/workflow.py validate
poetry run python -m unittest discover -s translation/homebrew/tests -v
```

Validation reports the status of each available target and the total number of
expected section and chapter-heading targets. An empty collection is explicitly
reported as zero available; it is not a completed book. `--require-complete`
requires available/selected results to be complete, not that the entire book has
been translated. Use an explicit source ID to require a particular result.

A draft may contain unresolved issues, but stored result files must still have
complete structural coverage. Keep partial drafting outside final data until it
can pass structural validation. Section completion also requires its shared
chapter heading to be complete. No human approval is required for each section;
commit and push authorization remain governed by repository policy.

The fixture under `tests/fixtures/` is invented demonstration text, not a
production translation. Tests exercise both its format and failure cases.
