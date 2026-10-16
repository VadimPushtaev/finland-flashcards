# Production workflow

## 1. Direction

Read the directing guide and decision log. Before the first production episode,
complete a local voice audition, a bilingual layout preview, and a speech/music
mix sample. Record settings and review outcomes in the decision log. Direction
is ready when these samples support clear speech and readable text in the agreed style.

## 2. Script

Copy the templates into `episodes/<section-id>/`. Resolve the chapter from the
Homebrew manifest and the section by its stable ID. Read paragraph sentences and
list-item sentences in array order, slicing text with the stored Unicode offsets.
Reuse the existing sentence IDs; never derive ordering from their numeric suffixes.
Stop and document any unsupported source block instead of silently omitting it.

Copy each Russian record by sentence ID. Verify the section and chapter-heading
translations have complete reviews and current fingerprints. A missing, draft,
or stale translation keeps translation readiness pending; do not invent a silent
fallback. Translation work follows the existing Homebrew translation workflow.

Store the section fingerprint using the algorithm in the translation schema:
SHA-256 of UTF-8 JSON of ordered `(ID, exact text)` pairs, including the heading,
with `ensure_ascii=False` and separators `(',', ':')`. Also record the SHA-256
of the exact translation-file bytes. These identify the script's source snapshot.

Populate visual cues, source-based text highlights, and separate pronunciation
notes. Leave audio timing unset until synthesis. Script completion requires every
sentence exactly once in source order, matching Russian records, source references,
and a feasible visual treatment. The worked example is partial and cannot satisfy
this completion criterion.

## 3. Assets

Resolve each asset request; record its source or creation method, creator, reuse
terms, credits, local path, and relevance verification. Keep music in the same
register. Record an explicit fallback when an optional foreground image is dropped.
Revise visual directions as necessary while preserving narration and translation.

Generate local narration using the selected voice. Listen for mispronounced names,
dates, abbreviations, missing words, and abrupt delivery. Record any TTS-only
pronunciation adjustments, regenerate affected speech, and measure final durations.
Assets are ready when speech is checked, required visuals and music are resolved,
and all reuse and credit information is available.

## 4. Render and review

Build timing from finalized audio. Align both text languages and any long-sentence
display segments, then add visuals, source-based highlights, music, and credits.
Render a preview and complete the review checklist. Correct failures before export.
An episode is complete only when the finished export has been watched and heard,
its output location is recorded, and its checklist is complete.

Rendering technology and export encoding will be selected in the later tooling task.

## Tracking and revisions

Inventory `production_status` progresses through `unstarted`, `script_draft`,
`script_ready`, `assets_ready`, `preview_ready`, and `complete`. Record blockers
in `issues`; do not overwrite the last achieved milestone with a translation status.
`translation_readiness` is `ready` or `pending`, with a reason in `issues` when pending.
Only set `episode_path` once a real episode directory exists.

Before resuming production, compare source and translation fingerprints. Review
changed IDs, text, and order; update the script snapshot deliberately and invalidate
affected audio, text timing, and renders. Return production status to the last still
valid milestone. Retain unaffected records and record the revision in the brief.
Never renumber source IDs or edit the anthology to fix a production problem.
