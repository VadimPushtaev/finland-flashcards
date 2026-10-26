# Rendering and reviewing a video

Use the isolated Poetry environment described in [ASSETS.md](ASSETS.md).
The renderer consumes exact bilingual text, selected images, narration files,
pauses and credit copy from the episode's `script.yaml`. Episode-specific layout,
font and mix decisions are recorded there. Source media remain unchanged.

From the repository root:

```sh
studio/runtime/.venv/bin/python studio/tools/validate_assets.py hb-c01-lage
studio/runtime/.venv/bin/python studio/tools/render.py hb-c01-lage --stills-only
studio/runtime/.venv/bin/python studio/tools/render.py hb-c01-lage
studio/runtime/.venv/bin/python studio/tools/verify_render.py hb-c01-lage
poetry run python studio/tools/script.py review hb-c01-lage --ready
poetry run python studio/tools/script.py validate hb-c01-lage --ready
```

The renderer uses Pillow, the locally installed Arial fonts on macOS, and the
FFmpeg binary provided by the locked `imageio-ffmpeg` package. It makes a 1080p,
24 fps H.264/AAC MP4, with exact frame-aligned display timing and measured audio
placement. It rejects text overflow and music shorter than the planned video.
Audio normalization retains headroom; music ducks beneath narration and fades
at the beginning and end. Useful foreground images remain still. The selected
darkened, softly blurred photograph fills the background throughout; its fractional crop follows a continuous full-video
timeline, with no sentence-boundary resets. Motion should be visible over 5–10 seconds;
the current episode uses 15% relative zoom with a diagonal pan and immediate linear
progress rather than a near-static eased opening. Empty foreground slots remain transparent. Sentence transitions never dissolve two text pairs together.

Final outputs live in `videos/homebrew/hb-c<chapter>-<subchapter>-<slug>.mp4` with a matching
`<video-stem>.CREDITS.md`. Scratch files (mix master, timeline and review frames)
live in `studio/media/<section>/render/` and can be removed after acceptance.
The verifier writes review images there only when called with `--save-frames`. `render.json` in the episode directory records
the output checksum, settings and timings. `start_seconds` and `end_seconds` in
the script describe narration onset/end; the timeline also records the earlier
text appearance and the hold after speech. Regenerate `SCRIPT.md` after rendering.

Keep `<video-stem>.CREDITS.md` with the MP4 when sharing it. It contains full source links,
licenses, author attribution and adaptation notices in addition to closing cards.

Generated exports and narration stay outside Git. Preserve verified output bytes
and use [SSH media sync](MEDIA_SYNC.md) when a copy is requested. GitHub's file-size
limit does not apply to these files; do not recompress just to fit Git. If a future
render revision changes an export, rerun verification and refresh its production
hashes and review records before syncing it.

Check the exported file decodes end to end, has the expected frame count/duration,
and retains both audio and video streams. Inspect representative frames including
the longest text, numerical facts and credits. Review voice quality and music
balance in the complete video; there is no separate user audio-approval stage.
Record automated checks honestly without claiming an auditory review occurred.

The user reviews the whole video. Keep its status `preview_ready` until they are
happy with the result; commit production metadata only afterward under the repository commit policy.

For a small music-level revision, set `render.music_gain_adjustment_db` in the
episode script. It scales the music alone, preserving narration gain and the
ducking envelope. An audio-only export may copy the existing H.264 stream after
checking that the timeline is unchanged; verify identical video packet checksums
and run the full export validation afterward.

For Chapter 1, keep the shared evergreen palette. Long section headings fit within
the title area; the progress indicator adapts to the sentence count. A sentence
may explicitly record `text_style: {sv_size: 44, ru_size: 36}` when the default
48/40 text does not fit. Sizes below 40/34 are rejected; split an oversized pair
into manually aligned display segments instead of making it illegible.

A short music track may be extended only when the episode explicitly records
`render.music_loop_crossfade_seconds` (for example, 4). The mixer then repeats
that same track with overlapping fades; include the loop adaptation in the script
and credits. Keep the accepted +2 dB music setting. Per-episode
`render.adaptation_notes` supplies the sidecar's adaptation notices. Text source
credits support archived books with a local notice and no external URL.

Long videos may set `background_style.motion_cycles` to the complete video
duration divided by approximately 140 seconds. This uses a continuous sine path
across the recorded pan/zoom range, starting at its midpoint while moving, with
gentle reversals. Leave it unset for the original linear motion.

For parallel production, `check_audio.py --threads 1 --resume <narration-folder>`
transcribes available clips without repeating unchanged work. Reuse is keyed by
the WAV checksum, so regenerated takes are checked again. Record diagnostic flags
in the episode; ASR does not stand in for listening or whole-video acceptance.

For the foreground-picture target, register picture assets as `kind: foreground`
with `visual_type: photograph`, `map`, `flag`, `illustration` or `diagram`, on the
asset or individual file. Plain text cards use `text_card` or remain unclassified.
After stills, run `poetry run python studio/tools/picture_coverage.py SECTION
--planned --require-target`; after the final render and script review, omit
`--planned` to bind the report to the export and current script/assets. The tool
excludes titles, credits, typography and copies of the background, and measures
whole sentence-display intervals. Visual review must still confirm relevance.
Document any genuine shortfall under `DIRECTING.md`; do not relabel text cards.
For a chapter meeting the target throughout, add `--require-pictures` to the
chapter audit to check current coverage reports as well as the video checks.

After every episode in a chapter has a verified export, run
`poetry run python studio/tools/audit_chapter.py hb-c01`. This checks inventory
coverage against the source chapter, exact bilingual scripts, retained audio
inputs/settings, distinct background/music sources, checksums, timeline coverage,
and decode evidence bound to the canonical export.

A sentence may set `render_caption: false` when a useful foreground card already
shows its source labels or a long highlight list would overflow the footer.
The Swedish text still highlights those exact words in the main bilingual panel.

When the mix master is present, export verification also compares decoded audio
against it, recording waveform correlation and relative RMS error. This confirms
the encoded video contains the current mix after targeted narration retakes.
Keep the check report even when scratch mix files are removed after acceptance.

Export names include the two-digit subchapter number from `episodes.yaml`,
for example `hb-c01-03-natur.mp4` and `hb-c01-03-natur.CREDITS.md`.
The shared output-name resolver is used by both rendering and chapter auditing;
source IDs and internal episode paths retain their stable identifiers.

## Portable fonts and chapter palettes

`render.palette` may override `background`, `text`, `secondary`, `highlight`, and
`separator`; omitted values preserve the Chapter 1 defaults. The colors apply to
background tint, panels, text, separators and progress marks. `render.font_files`
records `regular` and `bold` font paths (repository-relative or absolute).
Chapter 2 production on Linux uses Liberation Sans with Swedish/Cyrillic coverage.
Without explicit paths, the renderer uses macOS Arial when present, otherwise
Linux Liberation Sans. Record the actual font choice in the episode script.
Helpers importing the renderer should call `configure_style(script)` before
creating frames so episode settings are applied.

The background uses a bicubic resize over a floating-point crop box. This keeps
the same continuous crop path while avoiding Pillow's slower general-purpose
transform. The output remains 1920×1080 at 24fps. Verify exported motion and
scene-boundary continuity after changing the sampler, just as for other renders.

For already softened decorative backgrounds, an episode may explicitly set
`render.background_style.resampling: bilinear`. Text and foreground graphics
retain their existing rendering. On the Chapter 2 reference background, this
reduced resize time from 0.108s to 0.068s/frame under concurrent load, with a mean
pixel difference of 0.071/255 and a maximum of 2/255 versus bicubic. This is an
optional recorded production setting; bicubic remains the default. Both methods
use the same floating-point crop path and require exported motion checks.
