# Assessment format, version 1

## Five scores

All scores are integers from 0 through 3. They are independent ordinal judgments,
not calibrated probabilities. Do not add weights, a total, or a card-selection
decision at this stage.

| Key | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| `exam_relevance` | No identifiable testable citizenship knowledge; transition or incidental detail | Peripheral/background knowledge | Plausible substantive citizenship-exam topic | Central civic knowledge and a strong question candidate |
| `knowledge_value` | Adds no useful understanding | Minor illustrative detail | Useful for understanding society or navigating everyday life | Foundational concept or major practical right/responsibility |
| `factual_specificity` | No definite factual claim | Broad qualitative claim | Identifiable relationship, role, rule, or condition | Precisely specified name, date, quantity, definition, or bounded rule |
| `question_suitability` | Cannot support a clear defensible answer, even with supplied context | Needs substantial contextual reconstruction or claim separation | Supports a clear question with modest context/rewording | Directly supports a focused question with one defensible correct answer |
| `change_risk` | Stable concept or historical event with a fixed timeframe | Slow-changing structural information | Policy, procedure, or present-day statistic needing periodic checks | Frequently revised amounts, current officeholders, temporary measures, or similarly volatile details |

A historically dated amount need not be volatile; an undated current benefit
amount can be. Assess the actual claim and its timeframe. High exam relevance
can coexist with low confidence: do not invent evidence that the exam asks it.
Lower confidence when scoring is materially uncertain rather than using zero to
mean "unknown." For several claims in one sentence, assess the sentence as a
whole; use the highest material change risk and note a dominant claim or necessary
split in the rationale. Do not silently create new sentence identities.

## Six additional fields

| Field | Type and meaning |
| --- | --- |
| `sentence_id` | Existing segmented Swedish body-sentence ID; no chapter/section-heading IDs |
| `fact_types` | Unique labels from `date`, `number`, `name`, `definition`, `institution`, `right`, `obligation`, `rule`, `procedure`, `exception`, `explanation`; `[]` if none apply |
| `context_sentence_ids` | Unique existing body-sentence IDs needed to interpret the assessed sentence; `[]` if self-contained; never the sentence itself |
| `duplicate_of` | One earlier body-sentence ID conveying the same complete claim, or YAML `null`; never self, reciprocal links, mere topic similarity, or partial overlap |
| `assessment_confidence` | `low`, `medium`, or `high`: confidence in the assessment, especially estimated exam relevance |
| `rationale` | Short nonempty English explanation, usually 1-2 sentences, specific to this source sentence |

Confidence concerns the assessment, not whether the underlying source is true.
Use `high` when the interpretation and relevance judgment are well supported,
`medium` for a reasonable estimate with limited exam-specific evidence, and `low`
for material uncertainty. No confidence level guarantees an exam question.

## Files and source identity

One UTF-8 YAML file per section:
`card_creator/homebrew/assessments/SECTION_ID.yaml`.

The document has exactly `schema_version`, `section_id`, `source_sha256`, and
`assessments`. Each assessment has exactly `sentence_id`, `scores`, `fact_types`,
`context_sentence_ids`, `duplicate_of`, `assessment_confidence`, and `rationale`.
The `scores` mapping contains exactly the five keys above. Do not duplicate the
Swedish text, chapter labels, or source offsets inside assessment records.

`source_sha256` is document metadata, not another scoring field. It uses the
existing `translation/homebrew/tools/workflow.py` helpers:
`fingerprint(source_records(chapter, section))`. This covers the section heading
and all ordered sentence IDs/text. Use the preparation helper to obtain it.
Changes to referenced passages outside that section require human reassessment
of affected context/duplicate links; the section hash does not cover them.

Example shape (illustrative scores, not an approved assessment):

```yaml
schema_version: 1
section_id: hb-c01-lage
source_sha256: "COPY_THE_PREPARED_SECTION_FINGERPRINT"
assessments:
- sentence_id: hb-c01-u0001-s001
  scores:
    exam_relevance: 2
    knowledge_value: 2
    factual_specificity: 1
    question_suitability: 2
    change_risk: 0
  fact_types: [name]
  context_sentence_ids: []
  duplicate_of: null
  assessment_confidence: medium
  rationale: "This introduces Finland's location and landscape, useful geographic knowledge; actual exam coverage is uncertain."
```

Subset requests may produce partial section files. Merge existing records by ID
and retain source order; never claim a full section/chapter is assessed from a
successful subset validation. The validator requires every sentence selected by
its command-line targets and also checks all existing records in touched files.
