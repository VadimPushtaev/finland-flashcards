# Selection and output

## Priority scoring

Use `card_creator/homebrew/score_sentences.py`; the assessment skill continues to
store only its independent five ratings and six additional fields.

```text
Score = 9 * exam_relevance
      + 6 * knowledge_value
      + 4 * question_suitability
      + factual_specificity
```

Each input is 0-3, so the score is 0-60. Relative weights are 45%, 30%, 20%, 5%.
Change risk and assessment confidence never subtract points or change tiers.
Question suitability already has its explicit formula weight; there is no second
penalty for it. Flags request review, not automatic exclusion from CORE.

The initial reference cutoffs are CORE >=41, SUPPORTING =40, SKIP <40. On the
213 Chapter 1 assessments these yield 48 / 29 / 136 sentences. These counts are
historical calibration evidence, not quotas or assumptions about current files.

As assessments grow, the default script recalibrates against all structurally
valid, source-current assessed sentences across the collection. It tests integer
cutoff pairs, minimizing the sum of absolute deviations from approximately 21%
CORE and 14% SUPPORTING. Equal scores always stay together. Equally good fits
prefer cutoffs closest to 41/40, then the stricter pair. No per-chapter or
per-subchapter quotas, and no requirement to force exact percentages.

For general calibrated thresholds, CORE is `score >= core_min`, SUPPORTING is
`supporting_min <= score < core_min`, and SKIP is below `supporting_min`.
An explicit `--cutoffs CORE_MIN SUPPORTING_MIN` pins a previous/global pair for
reproduction or a user-specified policy; do not tune it to manufacture cards for
a particular section. `--all-assessed --tiers CORE SUPPORTING SKIP` reports the
entire current assessment population. Default output remains CORE only.

The JSON report includes the formula, cutoffs, global and requested counts,
assessment/source hashes, excluded invalid files, selected sentences, their
original assessment fields, and derived review flags. Calibration counts are
sentence counts, not card counts. One global report must govern the whole run;
do not recalibrate independently for each generated section.

## File layout and provenance

- Deck: `cards/homebrew/CHAPTER_ID/SECTION_ID.txt`.
- Source records: `card_creator/homebrew/card_sources/SECTION_ID.yaml`.
- Selection report: `card_creator/homebrew/selections/RUN_NAME.json`.

Choose a descriptive, unused run name (for example, chapter ID plus date and a
suffix if necessary). Save the complete scoring JSON used for generation; do not
overwrite reports referenced by existing cards. Each deck row uses:

```text
Question|Exact Swedish section title|2|Option1|Option2|Option3|Option4||0 1 0 0|2
```

Use four nonempty, distinct options and exactly one correct binary flag. No
literal pipe characters or line breaks inside fields. The final numeric field
is `2`, not the correct-option index.

The source-record YAML has `schema_version: 1`, `section_id`, and `cards`:

```yaml
schema_version: 1
section_id: hb-c01-lage
cards:
- row_sha256: "SHA256_OF_EXACT_DECK_ROW_WITHOUT_NEWLINE"
  primary_sentence_id: hb-c01-u0002-s001
  source_sentence_ids: [hb-c01-u0002-s001]
  selection_report: card_creator/homebrew/selections/RUN_NAME.json
  score: 45
  priority: CORE
  review_notes: "Source supports Nordic membership; checked the alternatives against the question's exact scope."
```

This is a shape example, not an instruction to generate this card. Hash the exact
UTF-8 row without its newline using SHA-256. Keep one source record per deck row;
the hash is the link, so option reordering or wording edits require a new hash.
Do not put these hashes or source IDs in the learner-visible card text.

The primary sentence must belong to the deck's section, be selected by the saved
report, and carry the same score/priority. `source_sentence_ids` lists the primary
sentence and all additional supporting context IDs; every ID must exist in the
Swedish source. The report's hashes identify the assessments and section text
used; examine actual external context when reviewing those links. Store concise
review notes, including dated primary-source verification when needed.

When merging, preserve existing rows and their source records outside the
requested revision. Previously generated cards may reference older reports;
recalibration alone does not authorize deleting them. Check duplicate claims
across the current Homebrew collection and record reused cards in the completion
summary. Report blocked selected candidates with reasons so a smaller card count
does not silently hide unresolved material.
