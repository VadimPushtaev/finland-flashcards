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
at the beginning and end. Useful foreground images remain still. A darkened, softly blurred forest photograph
fills the background throughout; its fractional crop follows a continuous full-video
timeline, with no sentence-boundary resets. Motion should be visible over 5–10 seconds;
the current episode uses 15% relative zoom with a diagonal pan and immediate linear
progress rather than a near-static eased opening. Empty foreground slots remain transparent. Sentence transitions never dissolve two text pairs together.

Final outputs live in `videos/homebrew/<section>.mp4` with a matching
`<section>.CREDITS.md`. Scratch files (mix master, timeline and review frames)
live in `studio/media/<section>/render/` and can be removed after acceptance.
The verifier writes review images there only when called with `--save-frames`. `render.json` in the episode directory records
the output checksum, settings and timings. `start_seconds` and `end_seconds` in
the script describe narration onset/end; the timeline also records the earlier
text appearance and the hold after speech. Regenerate `SCRIPT.md` after rendering.

Keep `<section>.CREDITS.md` with the MP4 when sharing it. It contains full source links,
licenses, author attribution and adaptation notices in addition to closing cards.

Check the exported file decodes end to end, has the expected frame count/duration,
and retains both audio and video streams. Inspect representative frames including
the longest text, numerical facts and credits. Review voice quality and music
balance in the complete video; there is no separate user audio-approval stage.
Record automated checks honestly without claiming an auditory review occurred.

The user reviews the whole video. Keep its status `preview_ready` until they are
happy with the result; commit only afterward under the repository commit policy.

For a small music-level revision, set `render.music_gain_adjustment_db` in the
episode script. It scales the music alone, preserving narration gain and the
ducking envelope. An audio-only export may copy the existing H.264 stream after
checking that the timeline is unchanged; verify identical video packet checksums
and run the full export validation afterward.
