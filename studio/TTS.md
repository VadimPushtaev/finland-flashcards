# Local Swedish narration

Use one female Sweden Swedish voice consistently throughout the series.
Review narration in the complete video; do not introduce a separate user
listening-approval step. Select
for intelligibility and natural delivery before speed of generation. Synthesize
locally; downloading model weights does not authorize cloud synthesis.

## Selection and evidence

The first episode compares Supertonic 3's five female presets and the dedicated
Swedish Piper Alma voice on six actual script sentences: opening, long compound
words, land/sea border, EET/GMT, 338 432 km² and Saimen. OmniVoice is also evaluated
as a larger local candidate. Record the selected voice and exact settings below
in the production default below.

A local speech-recognition transcript is a diagnostic, not proof of correct
speech. In particular, it can normalize numbers, misspell proper names, or infer
words that are unclear in the audio. Accent, pleasantness, identity consistency,
and correct Swedish letter names require listening. Never describe an automated
transcript check as a listening review or a universal quality ranking.

## Production default (2026-10-17)

**Supertonic 3 / F1**, language `sv`, 32 synthesis steps, speed `0.95`, NumPy
seed `42`, 44,100 Hz mono PCM16 WAV. Package `supertonic==1.3.1`; model revision
`aafc6e32416a594460b32413efc49d7fe4ce6d46`. Use local ONNX CPU inference with
four intra-op threads. The first production run uses macOS 15.3.2 on arm64.

This is the studio default, accepted by the user with the first complete video
on 2026-10-17 and selected on observed script fidelity,
fixed voice identity, practical local operation and recorded model terms. It is
not a claim of universally best sound or an independent expert pronunciation review. F1 recovered all three ordinary-prose test sentences in local ASR
apart from punctuation/hyphen normalization. Other Supertonic presets had more
transcript differences in those passages; Alma had substantially more. OmniVoice
ran successfully on Apple MPS, but its trial was too fast for this lesson and
showed no clear transcript advantage; its model also has noncommercial terms.
A slower OmniVoice trial could change the comparison and has not been performed.

Abbreviations and the proper name Saimen were flagged. Number formatting in ASR
is not evidence of exact spoken units. Listen before accepting these takes or
speech overrides. Sweden Swedish accent and a pleasant female delivery remain
listening criteria even when a preset is labeled female and language is Swedish.

Generate the selected voice from the repository root:

```sh
studio/runtime/.venv/bin/python studio/tools/audition.py supertonic \
  --voice F1 --speed .95 --section hb-c01-lage --all \
  --output studio/media/hb-c01-lage/narration
```

The tool supports other episode IDs; use `--all` for production and explicit
`--indices` for that episode's audition passages. Existing files at the output
path are replaced, so choose a new directory when comparing approved takes.
See the first episode's `tts-comparison.json` for historical measured trials and
raw ASR transcripts. Trial WAVs and unused candidate weights were removed after
acceptance; `runtime/audition-downloads.yaml` preserves their pinned downloads. ASR uses local faster-whisper small, Swedish, beam size 5, CPU int8;
model revision `536b0662742c02347bc0e980a01041f333bce120`.

## Sources and licensing

| Candidate | Primary documentation | Relevant constraints |
|---|---|---|
| Supertonic 3 | [Official repository](https://github.com/supertone-oss-archive/supertonic), [model](https://huggingface.co/supertone-oss-archive/supertonic-3) | Swedish supported; female presets F1–F5; local ONNX CPU inference; code MIT, weights OpenRAIL-M. Upstream repository is archived; pin the tested version. |
| Piper Alma | [Voice model card](https://huggingface.co/yeagersthlm/piper-voice-sv-alma), [Piper engine](https://github.com/OHF-Voice/piper1-gpl) | Dedicated sv_SE female voice; model CC BY 4.0, maintained by Daniel Nylander; engine GPL-3.0. |
| OmniVoice | [Official repository](https://github.com/k2-fsa/OmniVoice), [model card](https://huggingface.co/k2-fsa/OmniVoice) | Swedish supported; Apple Silicon inference; code Apache 2.0; model card states CC-BY-NC. Voice design needs a stable reference for consistency. |

Do not infer a model's license from its code license. Preserve downloaded license
files. Supertonic's OpenRAIL-M license includes use restrictions and states that
its licensor claims no rights in generated output; it does not make the weights
public domain. Credit the tool/model in production records even when no output
attribution is required. Respect Alma's model attribution if that voice is used.

## Production procedure

1. Validate the exact Swedish/Russian script and source fingerprints.
2. Supply Swedish text, explicitly set Swedish language, and use the selected
   voice. Expand numbers, symbols or abbreviations only in `speech_override`.
3. Generate one WAV per sentence ID, preserving source order. Do not add pauses,
   music or final loudness processing inside those raw speech clips.
4. Measure duration and peak level; use measured timing when assembling video.
   Start around 120–140 words per minute for ordinary prose. Word counts are
   misleading for spelled-out abbreviations and long Swedish number compounds.
5. Run local transcript diagnostics, then listen to every selected take. Check
   omissions, invented words, sentence endings, Sweden Swedish pronunciation,
   names and numbers. Keep speech overrides pending until listening is complete.
6. Store engine/package versions, model revision, preset, seed, generation
   settings, actual input text, output checksum, sample rate, duration and hardware.
   Preserve the approved WAVs. Re-synthesis requires review again.
7. Set speech/music loudness and ducking during video assembly. Check headphones
   and speakers; do not mistake a quieter raw voice for worse quality.

Use [ASSETS.md](ASSETS.md) for runtime setup, downloads and integrity checks.
The per-video script records selected settings and deviations. This document
owns the shared engine/preset default; avoid separate conflicting voice policies.
