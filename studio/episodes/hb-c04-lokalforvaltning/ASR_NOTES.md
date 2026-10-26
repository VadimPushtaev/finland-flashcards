# Pronunciation diagnostics — Kommuner och välfärdsområden

All 27 selected clips pass waveform and source-input checks, with hash-bound local Swedish ASR in [narration-check.json](narration-check.json). ASR is diagnostic, not listening approval.

Two same-text candidates were compared, with complete initial/candidate evidence in [retake-review.json](retake-review.json). The committee sentence `hb-c04-u0057-s001` now uses the candidate: the transcript recovers utser and a single near-matching Kommunfullmäktige compound instead of the initial multiword mismatch. The remaining Kommon/Kommun vowel spelling requires listening. The basservice candidate did not clearly recover the word, so its initial take remains selected and is a listening priority.

Other priorities: Också versus Och så, å andra sidan, the small conjunction in Var och en, småbarnspedagogiken, utses, Nämnderna and utsetts. Compound splitting and spelling differences can originate in ASR. Both source figures, 21 wellbeing counties and approximately 300 municipalities, are recovered correctly.

Initial takes used four ONNX threads; the selected targeted retake used two. Exact Swedish and reviewed Russian display text remain unchanged. Whole-video listening, mix balance and user acceptance remain pending.
