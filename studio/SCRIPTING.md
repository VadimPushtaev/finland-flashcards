# Writing an episode script

The shared [directing guide](DIRECTING.md) applies to every episode. The episode's
`script.yaml` is the single editable source for all video-specific creative decisions.
The first complete example is [Finland i Norden](episodes/hb-c01-lage/SCRIPT.md).
It is a proposal for review, not an approved video or a set of finished assets.

## Files and ownership

Use `studio/episodes/<existing-section-id>/` without renumbering the source IDs.

| File | Purpose | How to edit |
| --- | --- | --- |
| `script.yaml` | Exact bilingual text, episode decisions, scenes, visual requests, pauses, and pronunciation | Edit creative fields; preserve source-owned fields |
| `SCRIPT.md` | Readable script for review | Generated; edit YAML and regenerate |
| `sources.yaml` | Used passage provenance, source URLs, and publisher credit/reuse notices | Generated snapshot; review source changes before refreshing |
| `brief.yaml` | Source identity, production status, issues, and revision history | Update status and issues manually |
| `review.md` | Evidence and actual review outcomes | Check only work actually reviewed |
| `assets.yaml` (later) | Acquired files, creators, credits, and asset verification | Add during asset preparation; reference IDs in `asset_requests` |

The brief, inventory, and asset register do not introduce competing creative
decisions. If asset availability changes an illustration or pacing, update the script.
Generated media, voice selection, and rendering tooling belong to later stages.

## Commands

Run from the repository root with the existing root Poetry environment. No extra
dependencies or separate studio environment are required for script work.

```sh
# Scaffold exact bilingual content and source credits. Refuses an existing folder.
poetry run python studio/tools/script.py init hb-c01-lage

# After editing script.yaml, regenerate its readable review copy.
poetry run python studio/tools/script.py review hb-c01-lage --ready

# Read-only check of the script, provenance, and generated review copy.
poetry run python studio/tools/script.py validate hb-c01-lage --ready

# Exercise fidelity failures and overwrite protection.
poetry run python -m unittest discover -s studio/tests -p 'test_*.py' -v
```

The first episode already exists, so use `review` or `validate` on it. For a new
episode, replace the ID in `init`. Initialization validates current section and
chapter-heading translations using the existing translation workflow, including
review and glossary fingerprints. It rejects missing/draft translations and
unsupported source blocks before writing the episode.

The scaffold deliberately leaves creative fields empty. Without `--ready`, a
draft can be exported and checked for source fidelity. With `--ready`, every
sentence needs a scene, visual cue, referenced asset request, and planned pause;
all scenes must be consecutive, and asset requests need explicit fallbacks.
Deferred asset/render choices are allowed, but unresolved script-stage decisions
are not. Passing validation means ready for editorial review, not user approval.

After initialization, set the inventory entry to `script_draft` and record the
episode directory. After editorial completion and passing the ready checks, set
the brief and inventory to `script_ready`, with user review still listed as pending.
The commands never update statuses, approve choices, create media, stage, or commit.

## Content recipe

1. Read the whole subchapter. Group consecutive sentences into a few coherent
   scenes without changing their order or adding spoken transitions.
2. Write episode-wide decisions, including the opening, ending, pacing, visual
   treatment, and any choices deferred to assets or rendering. Follow shared
   direction; explicitly flag a proposed exception rather than silently overriding it.
3. For every sentence, choose a visual cue, reference reusable asset requests,
   select only useful source-based highlights, and plan a reading pause. Reuse
   images across sentences when the topic remains the same.
4. Request specific, verifiable imagery. Describe what the asset must show and a
   truthful fallback. Do not call a generic lake Saimaa or draw invented borders.
5. Record pronunciation risks and optional TTS-only expansions separately. They
   must preserve meaning and remain pending until listened to. Exact Swedish and
   Russian display text is never replaced by the spoken expansion.
6. Review `SCRIPT.md` for clarity, complete coverage, and feasible visuals. Resolve
   script decisions before moving to asset production. Keep all work uncommitted
   until the final video is approved, as specified in the workflow.

Use the source heading for an unspoken bilingual opening. Preserve every body
sentence and list fragment. Do not add narration, invented facts, summaries, or
quiz material. Speech numbers may expand into words, but labels retain source
notation. With no suitable illustration, revise the visual cue, not the content.

## Script format, version 1

The [template](templates/script.yaml) describes the editable shape. This is a
production-planning format, not a promise about a future rendering API.

- Identity, titles, source paths, and source/translation fingerprints are copied
  from the anthology. Sentence IDs and order come from the stored source ranges.
- `episode_decisions` entries have an `id`, `decision`, `status` (`proposed`,
  `deferred`, or `approved`), and `resolve_during` (`script`, `assets`, or `render`).
  Only an actual user decision permits changing a decision to `approved`.
- `scenes` contains ordered `{id, description}` records; each sentence references
  one `scene_id`. A scene groups consecutive sentences, without adding narration.
- `asset_requests` contains `{id, kind, description, fallback}` records. Kinds are
  background, foreground, music, or narration. Sentence `asset_ids` reference
  visual requests; music and narration requests cover the episode as a whole.
- `text_highlights` contains exact Swedish substrings. `pronunciation_notes`
  describe risks. Optional `speech_override` has `text`, `reason`, and
  `review_status` (`pending` or `approved`); it does not change `sv` or `ru`.
- `pause_after_seconds` is a proposed pause, not a measured timeline. Leave
  `audio_path`, `start_seconds`, and `end_seconds` null until audio exists.
- Empty `display_segments` means show the complete sentence pair with line
  wrapping. If a later layout needs segments, add ordered `{sv, ru, start_seconds,
  end_seconds}` pairs and manually review their correspondence. Together they
  must preserve all text in both languages; do not divide translations blindly.

The old two-sentence example under `examples/` is a partial illustration retained
from studio setup, not a complete production script. The validator rejects it;
use the first full episode and current template for new work.

## Source changes and validation limits

Changed source IDs, wording, order, translation bytes, review records, or original
archive hashes cause validation to fail. Do not delete a curated episode and
rerun `init` to silence errors. Review the changes by stable ID, update affected
script records and snapshots deliberately, log the revision in the brief, and
invalidate affected future audio/timing. Regenerate `SCRIPT.md` afterward.

Automated checks establish fidelity, reference integrity, current translation
reviews, original source fingerprints, and consistency of the readable copy.
They cannot approve pronunciation, historical image identity, music balance,
reading comfort, or user preferences. Those remain explicit later review tasks.
