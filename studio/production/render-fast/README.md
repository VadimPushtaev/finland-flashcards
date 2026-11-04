# Renderer throughput investigation

Read-only prototype run 2026-11-03 01:56–02:09 UTC against the accepted Hux export, SHA256 `14050ad974a610a3e650b2698e0f8e56e337aec55b4b79b6cfefb2d2e3416630`. No shared renderer, canonical export, source narration, model or dependency changed. Prototype videos/stills are under `/tmp/hb-render-fast`.

The useful candidate retains the current Pillow floating-coordinate background resize and caches the active overlay's RGB pixels and alpha channel. Paste that pair onto the resized RGB background. This removes the RGBA conversion, general alpha-composite and RGB conversion for every frame. See `recommendation.py`; the coordinator owns integration and shared tests.

## Measurements

1920×1080, exactly24fps, identical x264 fast/CRF20, one encoder/filter thread; other durable production jobs were running. These are measured samples rather than guaranteed whole-batch speedups.

| Method | Sample | Throughput | Python peak MiB | FFmpeg peak MiB |
|---|---:|---:|---:|---:|
| Current Pillow RGBA path |240frames,global1000–1239|8.34fps|212.3|329.9|
| Same sampler, cached RGB/mask paste |same240frames|12.16fps|215.6|338.6|
| FFmpeg zoompan1× |120frames|12.16fps|178.3|567.3|
| FFmpeg zoompan2× |120frames|9.47fps|226.1|613.7|
| FFmpeg zoompan4× |120frames|5.67fps|372.0|745.0|
| FFmpeg continuous perspective |120frames|6.72fps|178.1|579.5|
| Pillow half-size background |120frames|9.13fps|179.3|409.2|

The paired240frame encoded files from current and RGB-paste paths are byte-identical, SHA256 `c925575804a7660e3ac1124e9ba5757135554dec3082b81109a0a0c61c54a164`. Elapsed28.775s versus19.735s:45.8%higher throughput. Alternating eight24frame CPU-only batches measured median10.85 versus16.52fps (+52.2%). Single120frame timings were affected by simultaneous fidelity-analysis CPU load; retain raw results rather than using them for the recommendation.

## Fidelity and timing evidence

* Eleven positions spanning Hux's full continuous pan/zoom cycle: RGB-paste versus original maximum pixel/channel error0.
* All12Hux title/body/credits cards plus all42six-frame foreground transitions:54comparisons, maximum error0 in every pixel/channel.
*250000random RGB/RGBA pixels, all alpha values: maximum compositing error0.
* Five-second120frame fixtures with the unchanged source mix/AAC settings: entire MP4 byte-identical (`066430174c15e203cfe4348eec322181a76b034d9b836aa40840bb120b3ec57d`);235AAC packets, identical packet payload hash `c1b3f199a96b11626d8bab907bcb4a62021b8455a424268f52d21782e7fedffe`. Both decode239616audio samples at48000Hz including codec padding. This tests pipeline equivalence; it does not claim whole-video listening.
* Exact frame clock, extent, resampler, palette, card/text pixels and continuous background trajectory remain unchanged in the RGB-paste method. Foreground transition construction is unchanged.

The FFmpeg1× method had much larger temporal background-change variance: decoded exposed-background patch std0.327 versus0.097 for current. Supersampling4× reduced it to0.099 but removed the speed advantage. Decoded background MAE versus original was0.845/0.737/0.677channel levels out of255 at1×/2×/4×, p99around4–5levels. Both background interpolation and independent lossy encoding contribute. These variants fail the combined throughput/smoothness goal. Two actual exported baseline/4× frames were visually inspected: readable, correct panels, no apparent still-frame color issue. No playback-level perceptual approval is claimed.

Cache only the active card RGB+alpha pair (about7.9MiB), rather than duplicating all cached cards in long episodes. For the six transition frames, prepare the temporary transition overlay in the existing manner and use its RGB/alpha pair; this is a small boundary cost. Test display-segment boundaries and both bilinear/bicubic modes during integration. Resume production after this bounded investigation.
