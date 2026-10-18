# Landskap, regioner och städer — prepared assets

All acquired files, checksums and terms are in `assets.yaml`; sources are pinned in `studio/runtime/hb-c01-regioner-downloads.yaml`. Shared model weights use `studio/runtime/downloads.yaml`.

- Distinct verified decorative photograph throughout; optional source-only useful foreground graphics or verified photographs.
- Music: Floating Cities, Kevin MacLeod, CC BY 4.0; exact edit/loop plan in script.
- Narration: 54 locally generated Supertonic 3 F1 Swedish sentence WAVs, 32 steps, speed 0.95, seed 42. Exact inputs and measured settings retained.
- Rebuild source text cards: `studio/runtime/.venv/bin/python studio/episodes/hb-c01-regioner/graphics.py`.

Whole-video user review remains pending; automated diagnostics do not constitute listening or approval.

Rebuild the five city-pointer maps with `MPLCONFIGDIR=/private/tmp/studio-matplotlib studio/runtime/.venv/bin/python studio/episodes/hb-c01-regioner/maps.py`. Restore the default country geometry with the shared download manifest, then the episode's pinned populated-place dataset. The maps use actual city points and a Finland outline; they introduce no regional boundaries.

The final narration set contains two selected targeted candidates (sentences 33 and 35), generated in a fresh seed-42 stream with the same shared engine/voice/settings. Sentence 33 changes punctuation only in a separate speech override; sentence 35 preserves the original input unchanged. Full source-order metrics, selected WAV hashes, complete ASR transcripts and retake history are retained. This is diagnostic evidence, not listening approval.
