# Narration diagnostics — Religion i vardagen och högtiderna

All 38 selected source-order WAVs have matching inputs, measured durations,
finite mono 44.1 kHz waveforms, headroom and checksum-bound Swedish transcripts in
[narration-check.json](narration-check.json). Local Supertonic 3 / F1, 32 steps,
speed 0.95, seed 42, four ONNX threads; one full original source-order stream, with one
explicitly selected targeted comparison documented in [retake-history.json](retake-history.json).

## Bounded phrase comparison

- u0058-s001: original **daghem firas** collapsed to ASR **dag M4s**. A speech-only
  comma after **daghem** recovered **dagäm firas** and the remainder of the sentence,
  restoring the verb boundary. Selected this candidate; the daycare word's spelling
  and the new pause still need listening. Exact source display remains unchanged.
- u0061-s005: source gender-neutral **hen** was transcribed **henne**. One candidate
  with a comma after **hen** still returned **henne** and additionally collapsed the
  final phrase. Rejected it and retained the original. No more variants were made.

## Listening priorities

Prioritize **hen/henne** (u0061-s005), **daghem firas** (u0058-s001), and the
compounds **livsåskådningskunskap/åskådningsämne** in the school passages
(u0063 and u0066). ASR separated these as *livs- och skådningskunskap* or
*och skådningssämne*. Other diagnostic spellings include **lutherska**, **andlighet**,
**själavandring**, **festtraditioner** and **seder**. These do not establish an
actual audible error; full transcripts and original/candidate hashes are retained.

No listening, physical-device check, accent approval, or user acceptance is claimed.
Review pronunciation, naturalness, pauses and music balance with the complete video.
Automated integrity/transcription checks are not whole-video acceptance.
