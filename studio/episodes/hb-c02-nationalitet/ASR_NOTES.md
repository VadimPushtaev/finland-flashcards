# Nationell identitet och demokratisering — narration diagnostics

All 23 selected sentences were checked with local faster-whisper-small (Swedish, beam 5, CPU int8, one thread). The retained [narration-check.json](narration-check.json) includes each selected WAV hash, input, duration and diagnostic transcript.

ASR is diagnostic evidence, not proof of spoken accuracy. Complete-video listening for pronunciation and music balance, and user acceptance, remain pending. Displayed Swedish and Russian source text was not changed.

Listening priorities:

- Both1907 passages use selected full-value retakes; ASR now recovers1907 and adjacent24/19 without new changes. Listening remains pending.
- Other dates1906,1860s and1900s recovered correctly in initial diagnostics.
- Nationalitetsidén, svenskheten and some Finnish/Swedish language compounds show orthographic/inflection differences; complete-video listening remains required.

Retake decisions (full inputs, original/candidate hashes and transcripts are retained in [retake-history.json](retake-history.json)):

- `hb-c02-u0031-s002`: Selected candidate. Original ASR: “År 1970 hölls det första riksdagsvalet där alla finländare över 24 år fick rösta.” Candidate ASR: “År 1907 hölls det första riksdagsvalet där alla finländare över 24 år fick rösta.”
- `hb-c02-u0032-s003`: Selected candidate. Original ASR: “I valet år 1920 valdes 19 kvinnor in i Finlands riksdag.” Candidate ASR: “I valet år 1907 valdes 19 kvinnor in i Finlands riksdag.”

See [review.md](review.md) for export verification and the distinction between visual/automated checks and pending listening.
