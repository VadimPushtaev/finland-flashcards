# Blurred-background resampler comparison

Bounded read-only run:2026-11-03 03:30–03:41 UTC. Five actual Chapter8/12 background sources, each already darkened42% and blurred2.5pixels. No production file, source audio, shared renderer or current/completed export changed.

The inspected side-by-side stills showed no perceptible loss of background quality or bilingual readability with bilinear. It is reasonable to retain/use explicit bilinear for these already blurred decorative backgrounds in future exports. This is not a recommendation to change sharp foreground photographs or global unblurred-image defaults.

## Measured tradeoff

Four alternating12frame compositor batches per sampler/source, same cached RGB/alpha card, same floating-point pan/zoom extent. CPU time is more stable than wall time under concurrent production load.

|Source|Bilinear compositor fps|Bicubic compositor fps|Bilinear CPU saving|Encoded bilinear fps|Encoded bicubic fps|Raw max channel error|
|---|---:|---:|---:|---:|---:|---:|
|hb-c08-utveckling|12.83|9.69|29.2%|6.37|5.34|2|
|hb-c08-smabarn|11.90|7.90|24.1%|5.28|6.29|2|
|hb-c08-hogskolor|12.82|12.18|20.0%|7.07|5.59|3|
|hb-c12-sprak|14.23|12.56|25.1%|6.87|6.10|3|
|hb-c12-e-tjanster|15.40|13.83|21.3%|8.27|6.58|2|

Bilinear used20–29%less compositor CPU per frame across allfive sources. Encoded wall-time improved in four samples and reversed for kindergarten under changing shared host load; do not infer a guaranteed whole-batch speedup from these short timings. All ten H264 samples used one x264 thread,fast/CRF20,1920×1080,24fps,96frames(4seconds),and completely decoded. The diagnostic temporal-patch computation adds small common per-frame cost,so absolute encode fps is not a direct production-throughput forecast.

## Pixel and motion evidence

At seven full-motion positions per source, raw exposed-background mean absolute error ranged0.022–0.101channel levels out of255 averaged across positions; worst single-position mean0.159. Raw maximum error was2–3/255;99th-percentile exposed-background error never exceeded1/255. At worst only two of6.22million frame channel values exceeded a difference of2. Every fully opaque glyph/photo/diagram pixel was byte-identical before encoding. Antialiased card geometry and source typography did not move.

Both kernels retain identical continuous fractional crop coordinates and exact frame clock. No integer-crop quantization was introduced; the same continuous fractional trajectory is retained. Exposed-strip temporal standard deviations were similar(approximately0.010–0.020 versus0.010–0.019channel levels/frame); these measurements support continuity but do not replace playback-level expert perception review.

Independently encoded samples have larger differences due to H264 decisions: mean exposed-background errors0.68–1.07/255,opaque-content errors0.11–1.01/255,despite identical opaque input pixels. Therefore the encoded outputs are not byte-identical. Earlier RGB/mask compositor optimization was separately byte-identical,including audio; this sampling change is a distinct small visual tradeoff.

The firstthree sources use their actual completed export frame clocks; pre-export Chapter12 sources use a documented140second reference cycle for the short encode. Original/comparison styles and source hashes are recorded in per-source JSON.

## Review and artifacts

Actually inspected:five paired native-scale background/header detail strips and the full bilingual street-sign card comparison. No visible sharpness,color,layout or reading difference was found in these stills. Short sequences were fully decoded and temporally measured; no whole-video listening or expert playback-level motion approval is claimed.

Prototype images/videos: `/tmp/hb-resampler-comparison/`. Main visual contacts: `background-contact.png` and `full-card-contact.png`. Per-source data and complete source/command settings: `studio/production/render-fast/resampler-results/`. Reproduction: `studio/runtime/.venv/bin/python studio/production/render-fast/resampler_compare.py`.

Peak benchmark Python RSS292.3MiB. One-thread FFmpeg peaks341–421MiB; this is approximately the same frame/card/encoder footprint for both choices and not a measured memory optimization.

Coordinator found79/88scripts already explicitbilinear. Any remaining prepared-setting decision belongs to coordinator; no shared-code change is required or proposed here.
