# Studio validation

## Chapter 1 — 2026-10-17

All eight Chapter 1 videos have been rendered and technically verified. The first
video was previously accepted; the seven new videos await whole-video user review.
No separate audio-approval stage was introduced and no user acceptance is invented.

- 17 script/source tests and 14 asset/render tests pass.
- The chapter inventory matches all eight canonical sections in source order.
- All 213 exact Swedish/Russian sentence pairs are preserved, with selected local
  Supertonic 3/F1 narration, measured timing and complete timeline coverage.
- Each subchapter uses a distinct verified photograph and distinct music source.
- Asset checksums, narration inputs/settings and final export hashes are checked.
- Full exports decode at 1920×1080/24 fps with stereo 48 kHz audio; no clipping or
  sentence-boundary background jumps are detected. Opening motion is measured.
- Each new export's decoded audio matches its current mix master after retakes.
- Representative exported frames and reduced-size previews were inspected.

[Chapter audit](hb-c01-audit.json) records per-video coverage, duration and export
checksums. Each episode's review.md, narration-check.json and render-check.json
distinguish automated diagnostics from whole-video user acceptance. ASR does not
certify accent, naturalness or every pronunciation, and no physical-device
listening check is claimed by the assistant.

Repeat the checks using [SCRIPTING.md](SCRIPTING.md), [ASSETS.md](ASSETS.md) and
[RENDERING.md](RENDERING.md). Other chapters were outside this checkpoint.

## Chapter 2 — 2026-10-24

All thirteen Chapter 2 previews are rendered and technically verified, totaling
3822.083 seconds (1:03:42). All remain `preview_ready`; user acceptance and listening
review are pending. Production is committed at the user's request.

- 17 script/source tests and 16 asset/render tests pass.
- All 321 exact Swedish/Russian sentence pairs appear once, in source order.
- Selected local Supertonic 3/F1 narration retains measured timing, generation
  settings, input text, hashes, diagnostics and bounded retake comparisons.
- Thirteen distinct photographs and thirteen distinct music sources have recorded
  provenance, licenses and checksums. Chapter 2 uses its own slate palette.
- Full exports decode at 1920×1080/24 fps with stereo 48 kHz audio; mix matching,
  waveform peaks, opening motion and sentence-boundary continuity pass.
- Producers and independent agents inspected exported long passages, numbers,
  credits and reduced-size previews. No auditory or physical-device review is claimed.

The [chapter audit](hb-c02-audit.json) records coverage, durations, media uniqueness
and actual export hashes. The [listening-review checklist](hb-c02-review.md) collects
unresolved dates, names and compounds with timestamps and links to detailed notes.
ASR diagnostics cannot establish pronunciation or whole-video acceptance.

## Chapter 3 — 2026-10-24

All twenty-one previews are rendered and technically verified, totaling
5629.833 seconds (1:33:50). All remain `preview_ready`; listening review and
user acceptance are pending. The user authorized committing and pushing previews.

- All 520 Swedish/Russian sentence pairs retain exact source wording, IDs and order.
  Current source/translation fingerprints and provenance snapshots validate.
- Selected local Supertonic 3/F1 narration retains inputs, generation settings,
  measured timing, selected WAV hashes, diagnostics and bounded retake comparisons.
  The fourteen required local model files match pinned checksums.
- Twenty-one distinct photos and twenty-one distinct instrumental music sources
  retain provenance, licenses, adaptation notices and checksums.
- Full exports decode at 1920×1080/24 fps with stereo 48 kHz audio. Current mix
  matching, waveform peaks, opening motion and scene-boundary continuity pass.
- Producers and independent agents inspected exported long passages, dates,
  credits and reduced-size previews. No auditory or physical-device review is claimed.
- Prepared music stems have zero subtype-rail samples. Pre-PCM headroom guards
  corrected decoded MP3/crossfade overshoot, preserving raw masters and accepted
  mixer RMS normalization/+2 dB. The checksum-bound music report records each bed.
- New episode preparation helpers and repository card/crawler tooling pass Python
  syntax checks; the required `make` combined-deck/Kahoot rebuild passes.

[Chapter audit](hb-c03-audit.json), [music headroom](hb-c03-music-headroom.json),
and [listening review](hb-c03-review.md) distinguish automated evidence from user
acceptance. Unresolved ASR phrase/number diagnostics remain explicit review items.
