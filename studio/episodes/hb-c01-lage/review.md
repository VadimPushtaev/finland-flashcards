# Finland i Norden — final review

Status: complete. The user accepted the complete video on 2026-10-17 and requested
cleanup and a single commit. Acceptance covers the final audiovisual result;
no separate listening approval stage was introduced.

- [Canonical video](../../../videos/homebrew/hb-c01-01-lage.mp4)
- [Accompanying credits](../../../videos/homebrew/hb-c01-01-lage.CREDITS.md)
- [Export settings, checksum and timeline](render.json)
- [Full decode verification](render-check.json)

The export contains all 14 exact Swedish/Russian sentence pairs, in source order,
with local Supertonic 3/F1 narration. It is 1920×1080 at 24 fps, 3,401 frames,
141.708 seconds, with stereo 48 kHz audio. Source/translation validation and asset
checksum checks pass. The entire video decodes; narration stays inside its text
intervals and audio does not clip. Representative frames and a reduced-size
preview were inspected during production; no physical-device listening test is
claimed by the assistant.

The accepted design uses continuous forest pan/zoom, steady useful foreground
maps and a Saimaa photo, bilingual text, chapter colors and source-based highlights.
The final music revision raises music alone by 2 dB while preserving the previous
video stream, narration gain, fades and ducking. The final file was relocated
without re-encoding; its recorded checksum is unchanged.

Speech-only expansions for EET/GMT and the area figure are recorded in the script.
Historical local-ASR flags remain in narration-check.json and tts-comparison.json;
they are diagnostic evidence, not confirmed pronunciation errors or expert review.

Superseded exports, trial audio and render intermediates were removed. Approved
narration takes are retained in Git. Source downloads and generated maps remain
local caches, with pinned download manifests and production tools for restoration.

## Russian alternate audio — revised 2026-10-20

The user rejected the first Russian track's pronunciation and authorized replacing
it. The [replacement Russian track](../../../videos/homebrew/hb-c01-01-lage.ru.m4a)
uses Silero v5_6_ru / Baya with explicit Russian stress hints. All 14 takes fit the
accepted scene boundaries without speeding up or truncation. EET/GMT are spoken
as their Russian meanings. The original video and Swedish audio are unchanged.

The original music is remixed with ducking aligned to the new Russian speech.
See [configuration](russian-narration.yaml), [timings/checksums](russian-narration.json),
[voice comparison](russian-voice-comparison.json), and
[local ASR diagnostics](russian-narration-check.json). Listening review of this
replacement is pending; automated transcripts do not establish pronunciation quality.
