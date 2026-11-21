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

The explicit user policy is `data/homebrew/study-priorities.yaml`:

| Chapters | CORE minimum |
| --- | ---: |
| 1-4 | 41 |
| 5, 12 | 45 |
| 6, 8-10 | 50 |
| 7, 11 | 60 |

EXTENDED covers scores >=41 below the chapter CORE cutoff; SUPPORTING remains
40 and SKIP remains <40. Use the same policy on every run. Equal scores within
a chapter have equal tiers. Change cutoffs only on explicit user instruction,
never to fit quotas. The default study/generation tier is CORE.

Assess only requested sentences needed for the generation task. Reuse current
assessments and complete missing or stale requested assessments under the
assessment skill. Related source context and existing cards may be inspected for
interpretation and duplicate checks without assessing unrelated sentences.

The default script reads assessments for requested sections and scores only
requested sentence IDs. `--all-assessed` explicitly requests a collection-wide
report using the same chapter policy; it never initiates additional assessment.
`--cutoffs CORE_MIN SUPPORTING_MIN` exists for reproducing older reports or an
explicitly requested legacy comparison; it bypasses EXTENDED and the current
chapter policy. Do not use it during normal generation. Change chapter cutoffs
through the policy file only when the user requests it.

The JSON report includes the formula, chapter cutoffs, requested counts,
assessment/source hashes, selected sentences, their original assessment fields,
and derived review flags. Its legacy `calibration` object uses mode
`chapter_cutoffs` and scope `requested` by default; the counts describe that scope,
not all chapters. Only `--all-assessed` loads the full assessed collection and
reports invalid files excluded from that explicit report. Counts are sentence
counts, not card counts. Save one report for the requested run and use it
throughout generation.

## File layout and provenance

- Canonical cards: `data/homebrew/cards/CHAPTER_ID.yaml`, with permanent IDs and
  `study_priority: CORE` or `EXTENDED`.
- Derived deck: `cards/homebrew/CHAPTER_ID/SECTION_ID.txt`; render with `make combine-homebrew`.
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
changing selection policy does not authorize regenerating or deleting them.
Revise existing cards only within a requested generation or revision scope. Check duplicate claims
across the current Homebrew collection and record reused cards in the completion
summary. Report blocked selected candidates with reasons so a smaller card count
does not silently hide unresolved material.

## Updating study priority without regenerating questions

Use `card_creator/homebrew/sync_priorities.py` after an authorized assessment or
cutoff change. It matches canonical cards to primary sources via exact exported
row hashes and updates only `study_priority`; `--check` is read-only. Keep card
IDs, questions, answers, translations and historical generation records intact.
Existing cards below current CORE remain EXTENDED study cards, including cards
whose reassessed primary is now SUPPORTING or SKIP. That retention rule does not
change sentence eligibility for new generation. Current study metadata and old
source-record generation priorities may therefore differ intentionally. The
2026-11-21 policy application audit is in
`card_creator/homebrew/reviews/hb-c01-c12-2026-11-21-study-priorities.json`.
