---
name: assess-homebrew-sentences
description: Assess requested Swedish Homebrew sentences for future flashcard selection in finland-flashcards. Save five 0-3 scores plus fact types, context and duplicate references, confidence, and rationale. Use for sentence assessment, not card generation or translation.
---

# Assess Homebrew sentences

Write a separate assessment layer for the requested sentences in the current
finland-flashcards checkout. This is the selection-preparation stage: preserve
the Swedish source and assess it without generating cards or choosing a final
card cutoff. Store results in
`card_creator/homebrew/assessments/SECTION_ID.yaml`.

## Resolve the request and read context

Read [references/assessment-format.md](references/assessment-format.md) for the
five scoring scales and exact output format. Consult `data/homebrew/SCHEMA.md`
for the source structure and `data/homebrew/manifest.yaml` for current chapters.

Resolve chapter numbers/titles, section IDs, sentence IDs, and quoted passages
to existing source IDs. For a range, use source array order, not numeric ID
suffixes: IDs are allocation labels. Ask about an ambiguous quotation or range
only when the available context cannot resolve it. A chapter/section request
covers every segmented body sentence, including list fragments. Headings supply
context but do not receive assessment records.

Use the bundled helper from the repository root, after resolving the targets:

```sh
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py prepare hb-c01-lage > /tmp/hb-c01-lage-assessment-context.yaml
# Multiple targets, including individual sentences, are supported:
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py prepare hb-c01-u0001-s001 hb-c01-u0002-s001
```

Preparation is read-only. It supplies selected IDs, exact text, full parent
sections, and source fingerprints; it does not assign scores. Read the whole
parent section and relevant neighboring sections/chapter context. Preserve
qualifiers, negation, dates, and the meaning of list fragments. The original
Swedish is authoritative; Russian translations may help interpretation.

## Assess the selected sentences

Apply the rubric consistently across the requested scope. Assess each sentence
individually after reading its context; do not assign identical scores by chapter
or score solely from keywords, numbers, length, or sentence position.

Exam relevance is an informed estimate, not a probability or a claim about actual
exam questions. The anthology's presence alone does not establish official exam
coverage. If available official exam guidance is used, identify the supporting
document in the rationale; verify any external claim before relying on it.
Routine assessment of archived text does not require updating its facts.

Keep factual specificity separate from importance. A precise incidental date may
be a poor card, while understanding an institution's role may be valuable.
Question suitability is about a clear, defensible answer; record missing context
rather than simplifying away qualifications or inventing distractors. High
change risk identifies maintenance work, not information to discard automatically.
Do not calculate an overall score or invent selection thresholds.

Identify necessary context and duplicate claims in the parent chapter and
obvious related passages elsewhere. Same topic is insufficient for duplication:
the claim and its scope/conditions must match. A partial overlap in a sentence
with several claims is not a full duplicate. Use an earlier source sentence as
the duplicate representative; references may point outside the requested scope
without creating assessments for those sentences. An empty duplicate reference
means none identified in the inspected context, not proof of global uniqueness.

Write brief English rationales grounded in each sentence. Explain the main
reason for its exam-relevance/knowledge-value scores and any material uncertainty,
context dependency, or volatility. Use conservative assessment confidence when
exam relevance or the source meaning is uncertain. Do not equate confidence in a
date with confidence that it will be tested.

## Save, validate, and report

Merge records by `sentence_id` into the relevant per-section YAML files, in
source order. Include low-scoring requested sentences; absence must not mean
"unimportant." Preserve unrequested records. Reuse existing current assessments
unless revisions are requested; report how many were reused and newly assessed.
Partial section files are valid, but all requested IDs must be covered.

Use the preparation output's `source_sha256`. If an existing file has a different
fingerprint, inspect the source change before reusing any scores. Do not merely
replace the hash. When the request covers only part of a stale file, leave that
file untouched, report the additional reassessment needed, and continue unaffected
targets; keep requested draft work in `/tmp` until it can be merged honestly.

```sh
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py validate hb-c01-lage
# Validate a partial request against its actual sentence IDs:
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py validate hb-c01-u0001-s001 hb-c01-u0002-s001
```

Validation checks schema, source freshness, scores, references, ordering, and
requested coverage. It does not establish judgment quality: review the scores
and rationales against the text, especially uncertain assessments and duplicate
links. Report the scope/count assessed, output paths, validation result, and
consequential uncertainties. Commit/push only when requested; then follow the
repository's commit checks, including `make`.
