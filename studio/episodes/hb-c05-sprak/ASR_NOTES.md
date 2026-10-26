# Swedish narration diagnostics

All 47 retained clips pass waveform, source-order input, duration and SHA-256 checks. Every selected clip has a current Swedish local-ASR transcript. These checks do not establish listening quality or correct accent.

A specific number discrepancy was corrected: the first take of hb-c05-u0092-s004 was recognized as 500 instead of the source 5 500. The selected separate retake uses the speech-only expansion “fem tusen fem hundra”; its complete transcript recovers 5500 and the rest of the sentence. The original take and both metrics/transcripts remain in retake-5500-history.json and the local retake folder. The other 46 takes were preserved.

Remaining listening priorities include Sámi language names, Sametinget, Romani, word boundaries and inflected endings. Numbers 85%, 5%, 2023, 10 000 and the corrected 5500 are recovered by diagnostics, but still require normal whole-video listening. The source's repeated “rättigheter rättigheter” is deliberately retained, as are all original source words and reviewed Russian text.

listening-priorities.json includes 20 automatic flags (including expected digit/word normalization and numerical passages); these are not 20 confirmed audible defects. No headphone/speaker or whole-video auditory review is claimed.
