# Homebrew Video Studio

Production workspace for one calm, bilingual video per Homebrew subchapter.
Swedish narration reads the source verbatim; Swedish and Russian sentences
appear together. This initial studio contains plans and templates, not a renderer.

Start with [directing](DIRECTING.md), then follow the [workflow](WORKFLOW.md).
The [decision log](DECISIONS.md) separates agreed direction from audition defaults
and future technical choices. The [episode inventory](episodes.yaml) lists every
section in source order, with translation readiness separate from production status.

## Preparing an episode

1. Select an inventory entry with ready translations.
2. Copy the [brief](templates/brief.yaml), [script](templates/script.yaml),
   [asset register](templates/assets.yaml), and [review checklist](templates/review.md)
   into `episodes/<section-id>/` when production begins.
3. Populate the script from the source sentence IDs and reviewed translations.
   See the [worked example](examples/README.md) for an explicitly partial illustration.
4. Follow the four workflow stages and update the inventory after each milestone.

YAML records are editable planning interfaces, versioned as `schema_version: 1`;
they are not yet an executable renderer API. Paths inside YAML are repository-root
relative. Null values mean unset, never approved or completed. Template angle-bracket
values are placeholders. Keep generated audio, downloaded images, and rendered video
outside Git until a media storage policy is chosen.

## Source of truth

Use the [Homebrew manifest](../data/homebrew/manifest.yaml),
[Swedish schema](../data/homebrew/SCHEMA.md), and
[translation schema](../data/homebrew/TRANSLATION_SCHEMA.md).
Preserve source IDs, wording, order, provenance, and attribution. Production notes
belong here; do not edit the anthology to accommodate a visual or TTS limitation.

The initial inventory has 187 episodes: 86 with reviewed Russian translations
(chapters 1–6), and 101 awaiting translation (chapters 7–12). None has entered
production. See [validation](VALIDATION.md) for the snapshot checks.
