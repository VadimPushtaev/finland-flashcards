---
name: generate-homebrew-cards
description: Create Swedish Homebrew multiple-choice cards for Anki and Kahoot in finland-flashcards. Complete missing sentence assessments first, select CORE study-priority material by default, and preserve source traceability. Use for Homebrew card creation or revision.
---

# Generate Homebrew cards

Work in the current finland-flashcards checkout. Generate cards for requested
chapters, subchapters, sentence IDs, or unambiguously identified passages.
**Unless the user explicitly specifies otherwise, create only CORE cards.**
CORE denotes study priority, not guaranteed exam coverage.

## Check assessments before creating cards

Resolve the scope through `data/homebrew/manifest.yaml` and the Swedish chapters.
Use existing sentence IDs and source order, including list fragments; headings
provide context but are not assessed sentences. Inspect existing Homebrew decks
and their source records to decide what to add or revise.

Before drafting any cards, validate assessments for every requested sentence:

```sh
poetry run python .agents/skills/assess-homebrew-sentences/scripts/assessments.py validate hb-c01
```

If assessments are absent, incomplete, invalid, or stale, invoke
`$assess-homebrew-sentences`: read
`.agents/skills/assess-homebrew-sentences/SKILL.md` and follow it for the missing
or affected requested sentences. Assessment is an authorized prerequisite of
card creation; continue into generation after it passes. Preserve current
assessments and unrequested work. Do not manufacture default scores or merely
refresh a source hash. Respect that skill's handling of partially stale files;
report genuinely blocked targets and continue unaffected ones.

## Select study priorities

Read [references/selection-and-output.md](references/selection-and-output.md)
for the formula, chapter cutoffs, and source-record format. Assess only the
requested material needed for generation, reusing current assessments. Score the
requested scope once after its assessments are ready:

```sh
poetry run python card_creator/homebrew/score_sentences.py hb-c01 > /tmp/hb-c01-card-selection.json
```

Use the explicit policy in `data/homebrew/study-priorities.yaml`: CORE starts
at the chapter cutoff, EXTENDED starts at 41 below CORE, SUPPORTING is 40, and
SKIP is below 40. Chapter cutoffs are 41 for 1-4, 45 for 5 and 12, 50 for 6 and
8-10, and 60 for 7 and 11. The weighted formula is unchanged. Never recalibrate
cutoffs or expand assessment scope to fit percentages; change policy only on
explicit user instruction. CORE denotes the essential study set, EXTENDED
optional material. The web app currently exposes CORE only.

The default report includes requested CORE candidates only, plus requested-scope
counts for all four tiers. It reads assessments for the requested sections;
missing requested assessments are errors. Use that one report throughout the run.
Read related passages and existing cards for context and duplicate checks without
assessing or reclassifying unrelated material. Use `--all-assessed` only when the
user asks for a collection-wide report, with the same chapter policy.

Only when explicitly requested, include additional tiers, for example:

```sh
poetry run python card_creator/homebrew/score_sentences.py hb-c01 --tiers CORE EXTENDED > /tmp/hb-c01-expanded-selection.json
```

Do not add EXTENDED/SUPPORTING/SKIP questions to fill a quota or compensate for an empty
CORE selection. Supporting sentences may supply context for a CORE question
without becoming independent questions. Review flags do not reduce priority.

## Write and review cards

Read [references/card-writing.md](references/card-writing.md), copied and adapted
from the Orientation guide. Apply its Swedish-only, four-option, single-answer,
standalone-question, distractor, and Kahoot requirements. For general export
conventions consult `card_creator/README.md`. The legacy instruction to maximize
cards from every fact does not apply to Homebrew: cover the selected claims.

Read each candidate in its full section context, including the assessment's
`context_sentence_ids`, `duplicate_of`, rationale, and review flags. Questions
must be supported by the Swedish source and retain material qualifications.
Use one focused learning point per card; several sentences may support one card,
and several materially different points may justify multiple cards. A CORE
sentence containing incidental details is not permission to test each detail.

Resolve changeable facts and low-confidence judgments before publishing a card.
Use current primary sources when a current fact requires verification; record
the source and check date in review notes. A historical framing must have a
source-supported date. If an answer cannot be established honestly, keep the
candidate's priority and report it as blocked rather than lowering its score.
Low question suitability calls for better wording or context, not an extra
priority penalty.

Check existing Homebrew cards and duplicate links. Reuse an existing equivalent
question instead of creating a paraphrase of the same learning point. Do not
drop a candidate solely because `duplicate_of` is set: first establish that a
card covers that claim, or create one in the requested scope. Referenced context
outside the scope does not authorize creating independent cards for it.

## Save and verify

Edit canonical `data/homebrew/cards/CHAPTER_ID.yaml`, preserving permanent card
and option IDs; do not edit generated TXT directly. Set `study_priority` explicitly
to CORE (or EXTENDED only when authorized). Use the exact Swedish section title as
Category. Run `make combine-homebrew` to render section TXT and chapter aggregates.
Maintain source records in `card_creator/homebrew/card_sources/SECTION_ID.yaml`
and a saved selection report as described in the output reference. After updating
provenance, run `poetry run python card_creator/homebrew/sync_priorities.py --check`
to verify study tiers against current primary-sentence scores and policy. Keep unrelated
cards/records intact; replace a card only when revising that same learning point.
If no cards qualify, report that result and do not create an empty placeholder.

Validate every changed deck, including its exact category:

```sh
poetry run python card_creator/homebrew/validate_cards.py cards/homebrew/hb-c01/hb-c01-lage.txt --category 'Finland i Norden'
```

Enforce **120 characters per question and 70 per answer**, including spaces.
Rewrite overly long wording without dropping necessary conditions; never truncate
it mechanically. Check source links, selected tiers, and the correctness and
plausibility of all four answers separately: format validation cannot establish
those properties.

After generating cards, exercise the existing exporter on Homebrew decks:

```sh
poetry run python card_creator/kahoot/export.py --cards-dir cards/homebrew
```

Its default output preserves the `homebrew/` paths under `kahoot/`. If dependencies
or the submodule are unavailable, report the export limitation; do not claim a
successful Kahoot check. Update Homebrew entries in `card_creator/card_progress.md`
with actual card counts and any blocked candidates, distinct from assessment
counts. Report cards created/reused, covered source scope, tier counts and
thresholds, verification results, and blockers. Generation alone does not request
a commit or push; when requested, follow repository policy and run `make`.
