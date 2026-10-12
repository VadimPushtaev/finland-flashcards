# Checkpoint 1 validation

Executed on 2026-10-12 with Poetry and Python 3.9.6. These results cover the
inventory/outline stage; learner YAML, sentence offsets and final passage
provenance are not yet implemented or claimed to be validated.

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

Remaining editorial work is explicit: outline review, exact passage selection,
comparison of time-sensitive claims, final deduplication, sentence segmentation,
asset assessment and a second omission audit.
