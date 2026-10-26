# Production review — hb-c04-paverkan

Producer: /root/c04_civic, 2026-10-26.
Preview/export: `videos/homebrew/hb-c04-12-paverkan.mp4`.

- [x] Exact Swedish source order and reviewed Russian body and heading records validated against current source snapshots.
- [x] Every selected narration clip has current input and waveform hashes, finite unclipped waveform checks and hash-bound Swedish ASR diagnostics; selected and rejected targeted retakes remain documented.
- [x] All bilingual layouts fit. Actual exported title, every unique foreground treatment, longest bilingual pair and every attribution card were visually inspected, including reduced phone-size images.
- [x] Relevant licensed foreground pictures cover 72.7% of measured narrated-body display duration (65/89 pairs). Decorative backgrounds and text cards do not count.
- [x] Full video/audio decode, exact sentence/timeline coverage, continuous background motion and encoded-audio/current-mix comparison passed.
- [x] Source, foreground pictures, distinct background, music and voice credits are registered and reproduced in the canonical CREDITS.md sidecar.
- [x] Current output hash and preview_ready milestone recorded.
- [x] Independent compressed-export source, credits, audio identity and actual-frame comparison passed by /root/c04_elections; see independent-export-review.json.
- [ ] Complete narration and whole video heard end to end.
- [ ] Music balance checked on headphones and ordinary speakers.
- [ ] Actual physical phone-device preview reviewed.
- [ ] User final-video acceptance received.

Export SHA-256: `9e3ab2b677385c6c168a96cb87d14460be8ea9fa7d3a2ce560627adc9ae927fe`.

No auditory, physical-device or user-acceptance review is claimed. ASR differences are listening diagnostics, not confirmed audible errors. See ASR_NOTES.md, narration-check.json and listening-priorities.json. Encoded audio correlation establishes file integrity, not perceived sound quality. Pictures preserve their full aspect ratios; historical photographs and portraits retain dated source context in provenance.

Distribution compression revision: libx264 preset slow, CRF 24, 3 encoder threads, streamcopy AAC and +faststart. Size changed from 127.131 MiB to 92.074 MiB, below the 100 MiB limit. Frame count, dimensions, frame rate and exact AAC packet payloads/timestamps match the retained original. Same-timestamp original/new frame comparisons were inspected; no material text, portrait, image or credit legibility regression found.

Superseded original SHA-256: `d32c733e832780c81e7b0af81635217bf2e08eb9a77359e4b4d827fb65d734b4`. Original MP4 is retained at `studio/media/hb-c04-paverkan/render/pre-commit-original.mp4`; previous review evidence is explicitly marked superseded in the adjacent `pre-compression-review` folder. Current export SHA-256 is `9e3ab2b677385c6c168a96cb87d14460be8ea9fa7d3a2ce560627adc9ae927fe`. Exact reproducible FFmpeg arguments, pinned binary/version and stream comparisons are recorded in `render.json` under `distribution_compression`. Current comparison evidence is in `studio/media/hb-c04-paverkan/render/distribution-comparison/`.

Coordinator pre-commit cleanup: removed one trailing space after `Public domain` in both matching credits sidecars. A byte comparison confirmed this was the only change; source, assets, on-screen credits and video remain unchanged.
