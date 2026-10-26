# Homebrew Video Studio

Production workspace for one calm, bilingual video per Homebrew subchapter.
Swedish narration reads the source verbatim; Swedish and Russian sentences
appear together. The studio contains shared direction, episode scripts, asset tools, and a local renderer.

Start with [directing](DIRECTING.md), then follow the [workflow](WORKFLOW.md).
The directing guide is shared by every video; all video-specific decisions belong
in the episode's script. Briefs, asset registers, and review records support the
script with status, provenance, and validation evidence.
The [decision log](DECISIONS.md) separates agreed direction from audition defaults
and future technical choices. The [episode inventory](episodes.yaml) lists every
section in source order, with translation readiness separate from production status.

## Preparing an episode

1. Select an inventory entry with ready translations.
2. Follow [Writing an episode script](SCRIPTING.md) to initialize the episode from
   exact source sentences and reviewed translations using the root Poetry tools.
3. Edit `script.yaml` and generate `SCRIPT.md` for review. The first complete
   accepted episode script is [Finland i Norden](episodes/hb-c01-lage/SCRIPT.md).
4. Follow the four workflow stages and update the inventory after each milestone.

YAML records are editable production interfaces, versioned as `schema_version: 1`.
Paths inside YAML are repository-root relative. Null values mean unset.

Finished videos and their credits live in [`videos/homebrew/`](../videos/homebrew/),
outside the studio. Keep one canonical `hb-c<chapter>-<subchapter>-<slug>.mp4` per accepted episode.
Use two digits for chapter and subchapter numbers, for example
`hb-c01-03-natur.mp4`. Subchapter order comes from `episodes.yaml`; internal
episode directories and source IDs keep their stable original names.
Keep exports and selected narration WAVs locally and sync them over SSH using
[the media sync tool](MEDIA_SYNC.md). Commit scripts, manifests, credits, generation
metrics, tools, tests and production records; generated video/audio stay ignored. Downloaded media/models, generated maps and temporary render files stay
ignored; pinned download manifests and tools restore them. Remove superseded
exports and audition audio after acceptance, retaining comparison evidence.

## Source of truth

Use the [Homebrew manifest](../data/homebrew/manifest.yaml),
[Swedish schema](../data/homebrew/SCHEMA.md), and
[translation schema](../data/homebrew/TRANSLATION_SCHEMA.md).
Preserve source IDs, wording, order, provenance, and attribution. Production notes
belong here; do not edit the anthology to accommodate a visual or TTS limitation.

The inventory contains 187 episodes: 86 have reviewed Russian translations
(chapters 1–6), and 101 await translation (chapters 7–12). The first video,
[Finland i Norden](../videos/homebrew/hb-c01-01-lage.mp4), is complete and accepted.
All eight Chapter 1 videos are now rendered; the seven new exports are ready for
whole-video user review. See the [video index](../videos/homebrew/README.md) and
[chapter audit](hb-c01-audit.json) for coverage and verification evidence.

All thirteen Chapter 2 videos are also rendered and technically verified, covering
321 exact Swedish/Russian sentence pairs in 1:03:42. They are locally retained previews
awaiting whole-video user review. See the [Chapter 2 audit](hb-c02-audit.json) and
[listening-review checklist](hb-c02-review.md), including unresolved pronunciation
diagnostics. The video index links every export and its accompanying credits.

All twenty-one Chapter 3 videos are rendered and technically verified, covering
520 exact Swedish/Russian sentence pairs in 1:33:50. They are locally retained previews
awaiting whole-video user review. See the [Chapter 3 audit](hb-c03-audit.json),
[music-bed check](hb-c03-music-headroom.json), and
[listening-review checklist](hb-c03-review.md). The video index links all exports
and their credits.

All fifteen Chapter 4 videos are rendered and technically verified, covering
753 exact Swedish/Russian sentence pairs in 2:16:36. Every preview
has relevant foreground pictures for at least 50% of body display time.
See the [Chapter 4 audit](hb-c04-audit.json),
[export picture checks](hb-c04-visual-review.json),
[music-bed check](hb-c04-music-headroom.json), and
[listening-review checklist](hb-c04-review.md). These are locally retained previews;
whole-video listening and user acceptance remain pending.

All fifteen Chapter 5 videos are rendered and technically verified, covering
469 exact Swedish/Russian sentence pairs in 1:31:57. Every preview meets
the 50% foreground-picture target. See the [chapter audit](hb-c05-audit.json),
[export review records](hb-c05-visual-review.json), and
[listening-review checklist](hb-c05-review.md). Whole-video listening and user
acceptance remain pending; exports stay local and uncommitted.

Asset production: [ASSETS.md](ASSETS.md). Shared local voice policy and model
comparison: [TTS.md](TTS.md). Use the isolated Poetry runtime in `runtime/` for
media tools; keep the root environment for script/source validation.

Rendering and full-video review: [RENDERING.md](RENDERING.md).
