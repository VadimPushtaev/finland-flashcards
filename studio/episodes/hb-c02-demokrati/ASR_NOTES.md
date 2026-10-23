# Narration diagnostic notes

These are automated transcript comparisons, not auditory approval.

One targeted batch corrected the clearly flagged numbers, preserving every displayed source sentence:

- 1919: initial ASR 1999; full-value speech expansion now transcribes 1919.
- 1918: initial ASR 1990; full-value expansion now gives `1900-arton`. This captures arton but remains a hybrid spelling. Check this year in whole-video review.
- 1917 in the working-hours sentence: initial ASR contained an extra `90 år`; selected full-value expansion reads `1.917`, with no extra number.
- 1930-talet: initial ASR 1960-talet; explicit spoken decade now reads 1930-talet.

The remaining original 1917 and 1930 references were recognized correctly. Entire candidate sentences were compared with the source before adoption; other wording remained represented. Minor recognition differences include inflections and compounds such as extremhögern, arbetarrevolution and inbördeskriget. Those spellings alone do not establish pronunciation errors.

Current inputs, transcripts, waveform measurements and SHA-256 hashes are in narration-check.json. The single comparison and effective CPU affinity are recorded in retake-history.json. No further speculative variants were generated.
