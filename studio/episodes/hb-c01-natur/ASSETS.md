# Natur och friluftsliv — prepared assets

All acquired files, checksums and terms are in `assets.yaml`; sources are pinned in `studio/runtime/hb-c01-natur-downloads.yaml`. Shared model weights use `studio/runtime/downloads.yaml`.

- Distinct verified decorative photograph throughout; optional source-only useful foreground graphics or verified photographs.
- Music: Garden Music, Kevin MacLeod, CC BY4.0; exact edit/loop plan in script.
- Narration: 8 locally generated Supertonic 3 F1 Swedish sentence WAVs, 32 steps, speed 0.95, seed 42. Exact inputs and measured settings retained.
- Rebuild source text cards: `studio/runtime/.venv/bin/python studio/episodes/hb-c01-natur/graphics.py`.

Whole-video user review remains pending; automated diagnostics do not constitute listening or approval.

To regenerate the music excerpt without re-encoding, use the FFmpeg binary supplied by the pinned `imageio-ffmpeg` runtime with `-i studio/media/hb-c01-natur/sources/music.mp3 -t 180 -c copy studio/media/hb-c01-natur/sources/music-excerpt.mp3`. The original master is pinned separately. The final video uses only the measured timeline length with fades and ducking.
