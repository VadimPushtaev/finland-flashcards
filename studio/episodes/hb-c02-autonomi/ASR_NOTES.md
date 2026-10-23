# Autonomin och industrialiseringen — narration diagnostics

All 28 selected sentences were checked with local faster-whisper-small (Swedish, beam 5, CPU int8, one thread). The retained [narration-check.json](narration-check.json) includes each selected WAV hash, input, duration and diagnostic transcript.

ASR is diagnostic evidence, not proof of spoken accuracy. Complete-video listening for pronunciation and music balance, and user acceptance, remain pending. Displayed Swedish and Russian source text was not changed.

Listening priorities:

- Opening1809 retake recovers entire sentence and date correctly in ASR; selected, pending listening.
- 1860 and1880 remain ambiguously segmented in ASR; targeted candidates added adjacent words and were rejected, originals retained.
- Lutherska tron, kejsaren, pappersindustrin and other compounds have diagnostic spelling/segmentation differences; review audibly.

Retake decisions (full inputs, original/candidate hashes and transcripts are retained in [retake-history.json](retake-history.json)):

- `hb-c02-u0022-s001`: Rejected candidate; original retained. Original ASR: “Arton 160 Finland inför en egen valuta, Mark.” Candidate ASR: “Arton 160 och Finland inför en egen valuta, Mark.”
- `hb-c02-u0024-s003`: Rejected candidate; original retained. Original ASR: “I Finland tog industrialiseringen fart först på arton 180-talet när pappesindustrin utvecklades.” Candidate ASR: “I Finland tog industrialiseringen fart först, först på 1880-talet, när pappes industrin utvecklades.”
- `hb-c02-u0019-s001`: Selected candidate. Original ASR: “Finland blev en del av det ryska riket år 1800, då Sverige förlorade ett krig som det föredemot Ryssland.” Candidate ASR: “Finland blev en del av det ryska riket år 1809, då Sverige förlorade ett krig som det förde mot Ryssland.”

See [review.md](review.md) for export verification and the distinction between visual/automated checks and pending listening.
