# Production workflow

Keep work across all stages uncommitted. Once the user approves the final video,
prepare one commit containing the related scripts, credits and production metadata,
following the repository's staged-summary and commit-approval policy. Do not commit individual stages.
Generated video/audio remain ignored and are retained locally; use
[SSH media sync](MEDIA_SYNC.md) when the user requests a remote copy.

## 1. Direction

Use `DIRECTING.md` as the single shared direction for the entire series. Maintain
series-wide decisions in that guide and their rationale in the decision log.
Once the shared principles are agreed, proceed to an episode's script. Voice,
layout, and music trials belong to asset preparation and do not require rendering
a sample video before writing the script.

## 2. Script

Follow [Writing an episode script](SCRIPTING.md). Initialize the source-backed
files in `episodes/<section-id>/` with `studio/tools/script.py init`. Resolve the chapter from the
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

Record all video-specific decisions in the script: episode-wide choices in
`episode_decisions`, and sentence-specific choices alongside each sentence.
Include visual cues, source-based text highlights, and separate pronunciation
notes. Record proposed exceptions to shared direction explicitly for review;
do not silently override the guide. Leave audio timing unset until synthesis.
Script completion requires every
sentence exactly once in source order, matching Russian records, source references,
and a feasible visual treatment. The worked example is partial and cannot satisfy
this completion criterion. Generate `SCRIPT.md` from the editable `script.yaml`
and run `validate --ready` before handing the script over for review. Passing the
checks does not imply user approval or completed assets.

## 3. Assets

Resolve each asset request; record its source or creation method, creator, reuse
terms, credits, local path, and relevance verification. Keep music in the same
register. Record an explicit fallback when an optional foreground image is dropped.
Record asset-driven changes to video-specific decisions in the script while
preserving narration and translation. The asset register holds supporting file,
source, and credit details rather than a separate set of directing decisions.

Audition the local voice and check bilingual layout and music balance as needed.
Record episode-specific choices in the script and review evidence in the checklist.
Promote a choice to the shared directing guide only when it is adopted series-wide.

Generate local narration using the selected voice. Listen for mispronounced names,
dates, abbreviations, missing words, and abrupt delivery. Record any TTS-only
pronunciation adjustments, regenerate affected speech, and measure final durations.
Assets are ready when narration files pass integrity/source checks, required visuals
and music are resolved, and reuse/credit information is available. Carry unresolved
pronunciation diagnostics into complete-video review; do not require a separate
user listening-approval step.

## 4. Render and review

Build timing from finalized audio. Align both text languages and any long-sentence
display segments, then add visuals, source-based highlights, music, and credits.
Render a preview and complete the review checklist. Correct failures before export.
An episode is complete only when the finished export has been watched and heard,
its output location is recorded, and its checklist is complete.

Use the local Pillow/FFmpeg renderer and verification procedure in [RENDERING.md](RENDERING.md).

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
