# Background-cycle cache: bounded feasibility assessment

This is a prototype proposal only. No production code, episode script, media asset or canonical export is changed.

For a finished episode with `F` frames at 24 fps and `motion_cycles = F / (24*140)`, the existing sinusoidal motion phase at frame `f` is `2*pi*f*F / (3360*(F-1))`. A 3360-frame integer cache loop sampled at phases `2*pi*j/3360` therefore lags the analytic phase by almost one frame at the end. Simply rounding the period would change the current background trajectory.

A useful identity is `q = f*F/(F-1) = f + f/(F-1)`. Except for the final endpoint, the correct continuous cache phase lies between cached frame `f mod 3360` and `(f+1) mod 3360`, with interpolation fraction `f/(F-1)`. Thus a background-only linear blend between two loop streams offset by one frame can preserve the analytic phase without dropping or duplicating card/audio/timeline frames. Linear interpolation of sampled raster frames will not be byte-identical to a new continuous Pillow crop. This difference must be measured, especially at the wrap boundary. The source is already blurred 2.5 pixels, so the production one-frame positional increment is small; no equivalence has been established yet.

The installed FFmpeg `blend` filter exposes runtime `all_opacity` control. A bounded test may use frame-specific commands at `(f-0.5)/24` to apply opacity before target frame `f`, then validate every output frame against the reference. This avoids a per-pixel expression interpreter. If runtime commands or exact card holds do not behave as required, stop the test rather than change the production clock.

The candidate foreground input is run-length-held original RGBA PNG cards, plus the original six Pillow-blended transition PNGs. Concat/fps timestamps must be checked frame-by-frame; neither card frames nor transitions may shift. All opaque foreground pixels must match the reference before video encoding. RGB compositing must avoid implicit chroma subsampling before this comparison. The final existing AAC mix input and frame count must remain unchanged; AAC packet payloads, decoded duration, frame order and opaque pixels must be compared explicitly.

A gain of at least 1.5x appears plausible for a long episode such as Stöd (~9.8 cycles), because one background cycle's generation/encoding can be amortized while foreground holds avoid Python's per-frame crop/composite path. This is an unmeasured hypothesis. Unique episode backgrounds prevent reuse across episodes, and short episodes may fail to amortize cache creation.

Potential temporary storage: a 140-second uncompressed RGB cache is ~20.9 GB; a measured lossless codec should be substantially smaller, but its actual size and decode/encode cost remain to be measured. Static RGBA cards and six-frame transition variants must be stored once, not expanded as a full uncompressed foreground timeline.

Coordinator constraints: launch only after Högskolor review and Stöd launch; cap investigation/prototype at about 20 minutes, use at most one CPU in the existing ASR allocation after a safe immutable-snapshot boundary, resume ASR afterward, and retain the production maximum of two encoders. A short accelerated two-cycle fixture is sufficient for initial behavior/performance evidence; production-clock pixel probes remain necessary to assess interpolation error.
