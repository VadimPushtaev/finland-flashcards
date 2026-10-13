# Homebrew validation

## Completed Swedish collection

Executed locally on 2026-10-12 with Poetry and Python 3.9.6. All twelve chapters
are complete: 187 sections, 2,597 sourced text units and 7,150 sentence ranges.
The [final review](FINAL_REVIEW.md) gives chapter counts and remaining source gaps.

On 2026-10-13, two combined climate sentence records were split with user approval.
Chapter 1 source validation passed with 59 unchanged text units and 213 sentence
ranges; the collection now contains 7,152 sentence ranges. The original wording
and all unaffected sentence IDs were preserved.

| Check | Result |
| --- | --- |
| Original source inventory | PASS: 349 frozen files, 16,368 HTML blocks, 394 coverage units and 135 textbook pages. |
| Exact passage fidelity | PASS: original HTML selectors/PDF ranges and hashes re-read for every selected unit. |
| Structure and identity | PASS: all chapter schemas, global IDs, complete sentence ranges, registries and generated reading copies. |
| Source/topic audits | PASS: every mapped source unit accounted for; all outline topics have destinations or explicit gaps. |
| Manifest and attribution | PASS: local references, source union, attribution records and archived notice hashes. |
| Regression tests | PASS: all 16 tests; collection rebuild tests repeated after the final elder-care addition. |
| Python syntax | PASS: Homebrew tools, card_creator, InfoFinland and orientation scripts compile. |
| Existing flashcards | PASS: combined deck rebuilt before each commit; cards/ALL.txt remains unchanged. |
| Whitespace | PASS: git diff --check. |

The full collection validator passed after the family review. The final addition
of one elder-care paragraph was then separately source-validated (chapter 10:
265 units, 685 sentence ranges); the completed collection totals above include it.
That paragraph uses an explicit source-range cut to remove only a stray leading
`J` from `JOm`, with the cleanup recorded in its selection and editorial audit.

Independent editorial reviews restored benefit and parenthood qualifications,
resolved cross-chapter sick-pay wording, corrected a misleading violence typo by
selecting another literal definition, and removed an unsupported guardian cap.
The pilot correction preserves surviving sentence IDs and records the retired ID.
Two unpublished abbreviation boundaries were corrected. Duplicate diagnostics
identified nine exact cross-chapter repetitions of at least twelve words; these
provide local context. Full electoral eligibility lists intentionally repeat in
the municipal and welfare-election sections.

Rendered textbook pages 6, 22, 65, 78 and 124 were visually checked, supplementing
the pilot checks on pages 114 and 115. Selected passages do not depend on an
unavailable visual. No external study material or image assets were fetched.
Current legal accuracy and an eventual official question bank are not certified;
the source-specific gaps and snapshot limitations remain in the metadata.

The syntax check used `PYTHONPYCACHEPREFIX=/private/tmp/homebrew-pycache` because
the platform's default bytecode-cache location is outside the writable sandbox.

## Pilot validation (checkpoint 2, historical record)

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
At that checkpoint, review was pending and the remaining eleven chapters were
not yet validated. The user subsequently approved the pilot and completion;
the current collection results are recorded above.

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
