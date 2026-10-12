# Homebrew validation

## Pilot validation (checkpoint 2)

Executed with Poetry and Python 3.9.6. The pilot consists of 15 sections,
194 text units, 470 sentence ranges and 18 source files. Checks:

- Re-read original HTML selectors and PDF pages; all selected text matches after
  whitespace normalization only. Validate every frozen source hash and exact
  source range, not merely cached extraction text.
- Validate YAML shape, unique IDs, sentence range completeness/non-overlap,
  Unicode code points, local paths, manifest/provenance references, attribution
  records and all eight chapter topics.
- Verify the readable Swedish copy is generated from the same chapter content.
- Check 18 planned source units and four supplements in the editorial audit.
- Run all 14 extraction, coverage and pilot regression tests. They cover actual
  source tampering, wording changes, lost sentence coverage, stable identity
  after reordering, decimal/abbreviation/quote handling and invalid structures.
- Compile Python tooling and rebuild `cards/ALL.txt`; the deck is unchanged.

Editorial checks: reviewed sentence boundaries and source context, including the
prescription referent; visually verified PDF pages 114/115; retained complete
lists and qualifications. No PDF illustration is required for these paragraphs.

Limits: source fidelity does not prove legal accuracy or currency. One
extradition gap, source typos and source-era authority/service claims are
recorded in the pilot metadata. Table/image shape tests use fixtures; actual
table/image extraction and asset provenance remain work for later chapters.
Checkpoint 2 is pending; the remaining eleven chapters are not validated content.

## Checkpoint 1 validation (historical record)

Executed on 2026-10-12 with Poetry and Python 3.9.6. These results cover the
inventory/outline stage; learner YAML, sentence offsets and final passage
provenance were not yet implemented or claimed to be validated at that checkpoint.

| Check | Result |
| --- | --- |
| Source fingerprints | PASS: 349 source files match their recorded SHA-256 hashes and sizes. |
| HTML inventory completeness | PASS: every local Swedish orientation and InfoFinland HTML file is accounted for. |
| Extraction fidelity | PASS: all 16,368 extracted HTML blocks occur in the whitespace-normalized source text. |
| Textbook extraction | PASS: all 135 PDF pages yield text; all 45 substantive TOC subsections are mapped. |
| Coverage completeness | PASS: 394 unique source units, valid dispositions and destinations, no unsupported outline chapters. |
| Legal topic coverage | PASS: all six scope keys have chapter support; the known missing holiday page is recorded as a gap. |
| Regression tests | PASS: 6 tests covering article/glossary/activity extraction, nested list/table preservation, original DOM locators, Swedish text/PDF pages, the exact legal quote and rejection of incomplete coverage. |
| Python syntax | PASS: compileall for the new tools, card_creator, data/infofinland and data/orientation. |
| Poetry lock consistency | PASS: poetry check --lock; only existing legacy-metadata deprecation warnings. |
| Tracked diff whitespace | PASS: git diff --check. |

Reproduction commands are in [README.md](README.md). The validators are local
and do not contact the source websites. No original source files were changed.

At that checkpoint, remaining editorial work was: outline review, exact passage selection,
comparison of time-sensitive claims, final deduplication, sentence segmentation,
asset assessment and a second omission audit.
