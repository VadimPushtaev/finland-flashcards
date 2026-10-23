# Förhistoria och medeltid — narration diagnostics

All 24 selected sentences were checked with local faster-whisper-small (Swedish, beam 5, CPU int8, one thread). The retained [narration-check.json](narration-check.json) includes each selected WAV hash, input, duration and diagnostic transcript.

ASR is diagnostic evidence, not proof of spoken accuracy. Complete-video listening for pronunciation and music balance, and user acceptance, remain pending. Displayed Swedish and Russian source text was not changed.

Listening priorities:

- 1323 retake recovered as 1320, tre; date components present but listening is still essential.
- Tavastehus retake recovered as tavaste huslott; spelling and segmentation uncertain.
- Polyteistisk recovered as politisk in original and candidate. Original retained; high-priority listening check.
- Other proper-name/compound ASR spelling differences include Åbo/Borgå, hedniskt, hansaköpmän, påven and korståg.

Retake decisions (full inputs, original/candidate hashes and transcripts are retained in [retake-history.json](retake-history.json)):

- `hb-c02-u0003-s002`: Selected candidate. Original ASR: “Nöteborgsfreden, 1320 avslutade kriget mellan Sverige och Novgorod om häraväldet i området.” Candidate ASR: “Nöteborgsfreden 1320, tre avslutade kriget mellan Sverige och Novgorod om häraväldet i området.”
- `hb-c02-u0006-s002`: Selected candidate. Original ASR: “Två av dem var tavas det hur Slott och Viborg Slott.” Candidate ASR: “Två av dem var tavaste huslott och Viborgs slott.”
- `hb-c02-u0007-s002`: Rejected candidate; original retained. Original ASR: “Det var en politisk religion. Det vill säga människorna trodde på många gudar.” Candidate ASR: “Det var en politisk religion. Det vill säga människorna trodde på många gudar.”

See [review.md](review.md) for export verification and the distinction between visual/automated checks and pending listening.
