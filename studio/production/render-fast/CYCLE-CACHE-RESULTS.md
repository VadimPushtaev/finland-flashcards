# Cycle-cache prototype rejected

The measured candidate is slower and does not preserve all required timing invariants. No production/shared-code/script/canonical-export change was made. The owned ASR supervisor resumed automatically at 05:13:04 UTC, after a bounded single-CPU experiment.

The fixture is an unchanged eight-second actual Hux card/audio excerpt, including its original six-frame picture transition, with a deliberately accelerated two-cycle background for testing. RGB reference/cache comparisons occur before final chroma subsampling. The actual production clock's noninteger period was analyzed in CACHE-ASSESSMENT.md; production-clock visual equivalence remains unproved.

| Measurement | Result |
| --- | --- |
| CPU affinity | one CPU, FFmpeg threads1 |
| Cache | FFV1 lossless RGB, 96 frames, 70 MiB |
| Cache decode versus generated RGB | all 96 frames byte-identical |
| Foreground PNG preparation | 2.882 s, 8 unique PNGs |
| Background-cache creation | 21.224 s |
| Reference H264/AAC encoding | 40.613 s |
| Cached encoding | 54.301 s |
| Encoding throughput ratio | 0.748x |
| Ratio including cache/PNG preparation | 0.518x |
| Output video frame count/PTS | identical, 192 frames at24fps |
| Opaque RGB pixels | failed; up to225/255 difference at the card transition |
| AAC payload/count | failed; 376 versus361 packets, 8.00 versus7.68 seconds |
| Temporary storage | 2,474,485,529 bytes, mostly two uncompressed RGB comparison streams |

The held-PNG path displays the next body card one frame late at the transition. Its static opaque interiors agree after the transition, but that does not satisfy the frame-boundary invariant. Background differences also grow in this accelerated fixture; command-driven interpolation is not established as equivalent. Paired still95 was inspected, but there was no continuous audiovisual playback or production-clock smoothness approval.

The tested FFV1 decode/overlay path provides no useful throughput gain. Faster cache codecs and revised FFmpeg timestamp handling were not tested or adopted; further work would require a new bounded investigation. Existing exports and the running Stöd render retain the current verified renderer.

Evidence: cycle-cache-results.json, cycle-cache.log, cycle-cache-state.json, cycle-asr-pause.json and the temporary fixture files under /tmp/hb-cycle-cache.
