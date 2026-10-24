# Narration diagnostics — vinterfester

Complete selected source-order takes are checked against actual inputs, finite mono 44.1 kHz waveforms, measured durations and checksum-bound Swedish transcripts in [narration-check.json](narration-check.json). Local Supertonic 3 / F1, 32 steps, speed 0.95, seed 42, four ONNX threads; original full-episode stream except explicitly recorded selected comparison.

Winter dates 31 December, 6 January and 14 February recover correctly. A bounded full-sentence USA comparison replaced the ambiguous letter-name expansion (EU,SA) with its exact Swedish meaning Förenta staterna, which ASR identifies as föränta staterna; selected this take, preserving the rest of the sentence. Full comparison and original hash are in [retake-history.json](retake-history.json). Remaining listening priorities: fyrverkeripjäser (4väcker i piäser), the wise-men phrase kom med gåvor (kommer att gå vår), Trettondagen, Fastlagen and fastlagsbullar. These are ASR ambiguities, not confirmed audible errors.

No listening, physical-device review, accent approval or user acceptance is claimed. Review pronunciation, naturalness, pauses and music balance with the complete video; ASR is diagnostic only.
