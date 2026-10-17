# Studio validation — 2026-10-17

The first video is complete and accepted by the user. Its [review record](episodes/hb-c01-lage/review.md)
distinguishes user acceptance from automated checks.

- 16 script/source tests and 10 asset/render tests pass.
- The script preserves all 14 source sentences and reviewed Russian translations.
- Asset file hashes, narration coverage, duration and headroom checks pass.
- Production downloads match the pinned manifest.
- The final MP4 decodes completely: 3,401 frames, 141.708 seconds, 1080p/24 fps,
  stereo 48 kHz audio, no clipping, and continuous background motion across cards.
- Final relocation preserves the export checksum. Verification writes no temporary
  images into the deliverables folder.

The initial inventory was checked against all 187 Homebrew sections in source order:
86 have reviewed translations and 101 await translation. The first episode is now
`complete`; other episodes remain `unstarted`.

Repeat the focused checks using [SCRIPTING.md](SCRIPTING.md), [ASSETS.md](ASSETS.md)
and [RENDERING.md](RENDERING.md). Automated checks do not certify accent, naturalness
or pronunciation; those belong to complete-video review.
