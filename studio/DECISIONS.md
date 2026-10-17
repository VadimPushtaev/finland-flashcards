# Decision log

## Settled — 2026-10-17

| Decision | Rationale |
| --- | --- |
| One episode per Homebrew section, using its stable ID | Matches the requested subchapter scope and existing bilingual records. |
| Documentation and templates first | Establish the studio before producing episodes or implementing tooling. |
| Verbatim Swedish body narration | Preserve the selected source faithfully, including list fragments. |
| Swedish and Russian on screen together | Support simultaneous listening and comprehension. |
| Calm documentary, 16:9 at 1080p | Provide space for two languages and relevant supporting imagery. |
| Local female TTS in Sweden Swedish | The user changed the accent requirement to simplify local TTS selection; this supersedes the earlier Finland Swedish preference. |
| Gentle instrumental background music | Maintain the requested calm atmosphere while keeping speech clear. |
| Asset limitations change visuals only | Preserve the verbatim-reading commitment. |
| One shared directing guide for every video | `DIRECTING.md` governs the series; all video-specific decisions live in the episode script. Supporting records hold status, provenance, and review evidence. |
| One commit after the final video is approved | Keep intermediate work uncommitted. Commit the related documentation, script, and production changes together only after the user is happy with the final video and approves the commit. This replaces the earlier per-step commit plan. |

## Provisional defaults

Start voice auditions at 120–140 words per minute and about one second between
sentences. Use longer pauses between topic blocks. Begin composition previews with
5% safe margins, Swedish above Russian, muted colors, and restrained image motion.
Use an unspoken bilingual section title and source-based names/dates as optional
highlights. Final timing, layout, and mix depend on listening and readability review.

## First video accepted — 2026-10-17

The user accepted the complete first video, including the selected Supertonic 3/F1
voice, bilingual Arial layout, foreground illustrations, continuous forest motion
and music mix. The local Pillow/FFmpeg renderer exports H.264/AAC at 1080p/24 fps.
See [TTS.md](TTS.md), [RENDERING.md](RENDERING.md) and the episode script for settings.
There is no standalone audio approval gate. Automated checks and user acceptance
are recorded separately in the [episode review](episodes/hb-c01-lage/review.md).

Final videos and sidecar credits belong in `videos/homebrew/`, outside `studio/`.
Commit one accepted export and its approved sentence WAVs with the production
records and tools. Remove old exports and temporary audition/review files.
Retain pinned manifests for reproducible sources and optional comparison models.
Chapters 7–12 still require translation and review before production.

## Continuous decorative background

Following user review, decorative landscape photography fills the entire background
throughout each video. Useful foreground imagery keeps its dedicated area; leave
that area open when no illustration helps. Background motion uses one continuous
subpixel path across sentences; foreground images stay steady. Shared direction
and the first episode script now record this treatment.

## Visible background motion

User review found the initial 3.4% full-episode zoom imperceptible. The shared
direction now calls for motion that can be noticed over a normal 5–10 second
viewing interval. The first episode uses 15% relative zoom and a diagonal pan,
with linear progress from the opening and no sentence resets. Foreground images
and text stay fixed. Existing source assets are reused.

## Chapter colors and subchapter backgrounds

Each chapter has a distinct, consistent color palette across its videos. Every
subchapter gets a new topic-related background photograph, held continuously
through its own video. Chapter palette assignments belong in the shared directing
guide; episode scripts record the selected background and application of the palette.

## Distinct music per subchapter

Each subchapter gets its own music track, recorded in its script and asset register.
The first subchapter retains Light Thought var 1. After user review, its music bed
is raised by 2 dB (one small step), preserving narration gain, ducking and fades.
