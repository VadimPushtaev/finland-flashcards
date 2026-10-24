# Festmat och drycker — narration diagnostics

All 54 selected source-order F1 clips pass input/settings, sample-rate/duration,
finite waveform/headroom and hash-bound local Swedish ASR checks. Exact Swedish
and reviewed Russian display text is unchanged. No listening/user acceptance is
claimed. `narration-check.json` retains all selected inputs, hashes and transcripts.

Completed-take streaming used one serialized one-thread ASR lane and the existing
CLI. `narration-streaming.json` records the batches. Canonical transcript paths were
mapped only after proving their WAV hashes identical. The inserted coffee passage
`u0156` intentionally remains between `u0129` and `u0130`, matching source order;
no numeric-ID sorting was used for narration or display assembly.

Listen particularly to **memma/pasha**, **risgrynsgröten**, **saftdryck**,
**kålrots-, potatis- och morotslåda**, **lutfisk av torkad fisk**,
**runebergstårtor/fastlagsbullar**, **vispgrädde**, **blinier/bovetemjöl**,
**surmjölk** and **Alko-butikerna**. ASR produced spellings/word boundaries such as
mämma/pascha, riskrynsgröten, saftryck, torkgårdfisk, Runebergstortor,
vispräde, Sormjölk and alkohotbutikerna. It also omitted “är” in the egg-painting
sentence. These are diagnostic uncertainties rather than confirmed audible errors.
Some differences (gjord av/jordav, kaffe/café, bokstaven s/bokstavens) can be
spelling/segmentation rather than a change in speech.

There are no numeric facts requiring number-expansion comparisons. No retakes
were generated without a demonstrated correction strategy. Review accent,
naturalness, food/brand names and music balance with the complete video; automated
transcription cannot approve them, and no physical-device check occurred.
