# Vardagsmat och måltider — narration diagnostics

All 29 selected source-order F1 clips pass waveform/input/settings and hash-bound
local ASR checks. Exact Swedish/Russian text remains unchanged; clock abbreviations
and numerals have separate meaning-preserving Swedish speech expansions.
`narration-check.json` retains all inputs, transcript differences and selected hashes.

The complete clock sentences recover the intended values:

- `hb-c03-u0118-s002`: 10.30 till 12, matching source 10.30–12.
- `hb-c03-u0118-s005`: 17 eller arton, matching source 17 eller 18.
- `hb-c03-u0118-s006`: 20, matching source 20.

No numerical retake was indicated. These diagnostics do not certify pronunciation.
Check **ugnslax**, **köttfärssås**, **gryt- och gröträtter**, **lunchrätt/lunchrasten**,
**kranvattnet**, **te till frukost**, and **restaurang**. ASR produced spellings such
as ugenslax, köttfärsås, lungschrätt/Lundkrasten, kramvattnet, TT-frukost and
restauranger. Some are compound/word-boundary normalization; others remain uncertain.
No resynthesis was attempted without a demonstrated correction strategy.

Whole-video listening, accent/naturalness, music balance and physical-device checks
remain pending. No auditory or user acceptance is claimed.
