# Production review — hb-c04-partier

Producer: /root/c04_civic, 2026-10-26.
Preview/export: `videos/homebrew/hb-c04-11-partier.mp4`.

- [x] Exact Swedish source order and reviewed Russian body and heading records validated against current source snapshots.
- [x] Every selected narration clip has current input and waveform hashes, finite unclipped waveform checks and hash-bound Swedish ASR diagnostics; selected and rejected targeted retakes remain documented.
- [x] All bilingual layouts fit. Actual exported title, every unique foreground treatment, longest bilingual pair and every attribution card were visually inspected, including reduced phone-size images.
- [x] Relevant licensed foreground pictures cover 88.8% of measured narrated-body display duration (71/81 pairs). Decorative backgrounds and text cards do not count.
- [x] Full video/audio decode, exact sentence/timeline coverage, continuous background motion and encoded-audio/current-mix comparison passed.
- [x] Source, foreground pictures, distinct background, music and voice credits are registered and reproduced in the canonical CREDITS.md sidecar.
- [x] Current output hash and preview_ready milestone recorded.
- [x] Independent compressed-export source, credits, audio identity and actual-frame comparison passed by /root/c04_elections; see independent-export-review.json.
- [ ] Complete narration and whole video heard end to end.
- [ ] Music balance checked on headphones and ordinary speakers.
- [ ] Actual physical phone-device preview reviewed.
- [ ] User final-video acceptance received.

Export SHA-256: `687137c4a875f253fe590f0b66f53a94a8657afc17f7be491b843dede13fd4c8`.

No auditory, physical-device or user-acceptance review is claimed. ASR differences are listening diagnostics, not confirmed audible errors. See ASR_NOTES.md, narration-check.json and listening-priorities.json. Encoded audio correlation establishes file integrity, not perceived sound quality. Pictures preserve their full aspect ratios; historical photographs and portraits retain dated source context in provenance.

Distribution compression revision: libx264 preset slow, CRF 22, 3 encoder threads, streamcopy AAC and +faststart. Size changed from 102.351 MiB to 89.172 MiB, below the 100 MiB limit. Frame count, dimensions, frame rate and exact AAC packet payloads/timestamps match the retained original. Same-timestamp original/new frame comparisons were inspected; no material text, portrait, image or credit legibility regression found.

Superseded original SHA-256: `17e3be9f0d24c9c257fa3045507c5786dc3f54aa5fb351546ca39bf9c09463d0`. Original MP4 is retained at `studio/media/hb-c04-partier/render/pre-commit-original.mp4`; previous review evidence is explicitly marked superseded in the adjacent `pre-compression-review` folder. Current export SHA-256 is `687137c4a875f253fe590f0b66f53a94a8657afc17f7be491b843dede13fd4c8`. Exact reproducible FFmpeg arguments, pinned binary/version and stream comparisons are recorded in `render.json` under `distribution_compression`. Current comparison evidence is in `studio/media/hb-c04-partier/render/distribution-comparison/`.

The final AAC packet's container duration metadata normalized from 784 to 768 ticks at 48 kHz (0.333333 ms). Every AAC payload and PTS/DTS remains identical; decoded PCM sample count and samples are bit-identical in both producer and independent checks. This bounded metadata normalization was explicitly authorized and does not represent missing decoded audio.
