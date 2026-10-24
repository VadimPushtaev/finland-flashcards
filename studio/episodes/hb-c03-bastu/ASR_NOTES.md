# Bastukultur — narration diagnostics

All 27 selected source-order F1 clips pass input, sample-rate, duration, finite
waveform, headroom and SHA-256 checks. Exact Swedish/Russian display text, including
all source glossary fragments, remains intact. No listening or user acceptance is
claimed. `narration-check.json` retains every selected input and bound transcript.

Finnish key terms need particular listening attention:

| Source term | Original Swedish ASR | One comparison | Selection |
|---|---|---|---|
| kiuas | Tjuas | ki-uas → Ki, oas | Original; inconclusive |
| löyly | Löjlig | löy-ly → Löjli | Original; inconclusive |
| vihta | vita | Not resynthesized | Original; listening priority |
| lauteet | Laotiet | Not resynthesized | Original; listening priority |

Each comparison used the complete source sentence and unchanged local F1 settings,
with only a speech-only syllable hyphen. `retake-history.json` preserves the exact
candidate/original inputs, metrics, hashes and complete transcripts. Neither target
was clearly recovered; closer spelling cannot establish correct pronunciation, so
originals were retained and no further variants generated. The retained
`audition_finnish.py` helper reproduces the bounded candidate procedure; candidate
WAVs remain ignored scratch rather than additional selected takes.

Also check **immateriella kulturarv**, **höghus**, **bastuugn**, **bastuaggregat**,
**blandbastu**, and the opening **bastu**. Swedish ASR split or changed these
compounds; it rendered immateriella as “i materiella” and höghus as “höra hus”.
Other small differences such as baddräkt/badräkt or finskt ord/finstord may be
spelling normalization. This episode has no numeric facts requiring date retakes.

Review the complete video for pronunciation, naturalness and music balance.
Automated transcription cannot approve Finnish pronunciation or Sweden Swedish
accent, and no auditory/physical-device review has occurred.
