# Chapter 12 conservative reassessment proposal

**Adopted 2026-11-21:** the user subsequently chose the Chapter 12 >=45 CORE
cutoff and these proposed assessments were applied. The charts, snapshots and
comparison below document the earlier proposal stage using the old >=41 cutoff.
Current study tiers are recorded separately in
`../hb-c01-c12-2026-11-21-study-priorities.json`.

Reviewed all **603 sentences in 20 sections**, including list fragments, using
`assess-homebrew-sentences` and the existing five independent 0-3 scales.
This records the **proposal stage**, dated 2026-11-21. At that stage the canonical
assessments and cards were unchanged; adoption is recorded above. The Swedish
source, historical selection reports and other chapters' assessments remain unchanged.

## Interpretation of the rubric

- Relevance 3 is reserved for central civic knowledge: fundamental rights,
  basic citizenship/status distinctions, and central institutional responsibilities.
  A useful immigration procedure does not automatically receive relevance 3.
- Knowledge value 3 requires a foundational concept or major practical right
  or responsibility. Specialised service navigation generally receives 2;
  major safeguards for vulnerable people can still receive 3.
- Question suitability and specificity are assessed separately from importance.
  Some clear but less important definitions gain suitability while losing
  relevance. Broad or incomplete conditions lose specificity or suitability.
- Change risk remains a maintenance signal. It does not lower the weighted score.
  This review assesses the archived text and does not update or certify current law.
- No target distribution, quota, new score scale, or new cutoff was used.
  Relevance is an informed study judgment, not measured exam coverage.

344 records have at least one changed score; 98 additional records have only
rationale, confidence or metadata changes; 161 records are reused unchanged after
review. Weighted totals decrease for 285 sentences, increase for 46, and remain
the same for 272. Some score changes affect risk only, which is not weighted.
Both relevance and knowledge value are 3 in **36** proposed records, versus **180**
before. Context links were corrected, one incomplete duplicate match was removed,
and one equivalent repeated advice sentence was linked to its earlier occurrence.

## Comparison with the existing scoring stage

Only after the assessments were completed, the separate comparison script applied
the unchanged repository formula:

`9 * exam_relevance + 6 * knowledge_value + 4 * question_suitability + factual_specificity`

For this historical comparison, CORE is >=41, SUPPORTING is 40, and SKIP is <40.
All 603 sentences are counted, including repeated claims and fragments.

| Threshold | Sentences before | Sentences proposed | Existing cards before | Existing cards proposed |
| --- | ---: | ---: | ---: | ---: |
| >=41 | 206 | 197 | 103 | 92 |
| >=45 | 182 | 149 | 90 | 72 |
| >=50 | 180 | 52 | 90 | 27 |
| >=60 | 27 | 7 | 21 | 5 |

The card comparison rescores the primary sentences of the **same 103 existing
cards**. It is not a count of newly generated questions or a decision to remove
cards. Existing questions can combine and qualify several source sentences;
their primary-sentence scores remain a proxy, not a new assessment of each
question's full wording.

The 62 existing cards previously tied at 56 now have this distribution:

| Proposed score | 32 | 35 | 36 | 40 | 41 | 45 | 46 | 47 | 54 | 55 | 56 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cards | 1 | 1 | 2 | 1 | 12 | 9 | 6 | 21 | 1 | 4 | 4 |

For example, identifying the reception allowance's payer falls to 32, the
population-data authority's role to 45, and asylum interpretation safeguards to
47. The national-language rights claim remains at 56. Ties remain because the
rubric uses a small number of ordinal categories; no artificial precision was
added to break every tie.

## Review artifacts

- `homebrew-ch12-scores-before-after.png`: four histograms; all sentences above,
  existing cards below. Orange follows the original group of 62 cards.
- `sentence-comparison.csv`: all 603 source texts, five before/proposed scores,
  totals, tiers, rationales, confidence, context, duplicates and linked card IDs.
- `existing-card-comparison.csv`: all 103 questions and answers, primary sentence
  IDs and texts, before/proposed totals and rationales.
- `assessments/`: complete proposed per-section assessment YAML in the skill schema.
- `before/`: byte-preserved canonical assessment snapshot.
- `changes.tsv`: individually authored rating/confidence/rationale overrides.
  Despite the filename, fields use `|`; the five digits are relevance, value,
  suitability, specificity, risk, in that order.
- `metadata-overrides.yaml`: explicit context, duplicate and fact-type corrections.
- `assessment-audit.json`: coverage, counts and before/proposed file fingerprints.
- `before-selection.json`, `proposed-selection.json`, `comparison.json`: derived
  scoring data, exact distributions and verified card provenance fingerprints.

## Reproduction and validation

From the repository root, set `proposal` to this directory, then run:

```bash
poetry run python "$proposal/build_assessments.py"
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py validate hb-c12 --data-dir "$proposal/assessments"
poetry run python "$proposal/compare_scores.py"
poetry run python "$proposal/plot_comparison.py"
```

The plotting step needs Matplotlib and NumPy. For this review they were used from
the isolated `/tmp/homebrew-card-plot-deps` directory through `PYTHONPATH`; project
dependencies were not changed. `build_assessments.py` rebuilds the proposal from
the saved `before/` snapshot, verifies its recorded hashes and never replaces it
with today's canonical scores. `compare_scores.py` explicitly uses the old 41/40
cutoffs rather than today's chapter policy. Neither script changes canonical data.

Validation passed for all **603 requested sentences in 20 section files**.
All 103 canonical cards matched their provenance through the exact exported-row
SHA-256, and their recorded baseline scores matched the original assessments.
Schema validation checks references and source freshness; it does not establish
the correctness of subjective relevance judgments. Low-confidence and volatile
claims retain review flags in the derived reports.
