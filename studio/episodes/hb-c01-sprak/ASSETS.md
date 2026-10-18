# Prepared assets

The editable creative plan is `script.yaml`; exact acquired files, hashes, credits and input text are in `assets.yaml`.

| Asset | Selection and source |
| --- | --- |
| Continuous decorative photograph | https://commons.wikimedia.org/wiki/File:Bilingual_street_sign_of_Hietalahdenkatu_in_Helsinki,_Finland,_2020.jpg — Henry Söderlund; CC BY 2.0; https://creativecommons.org/licenses/by/2.0 |
| Useful foreground | Original stationary typography containing only exact Swedish source substrings; no invented identities, borders or historical photographs |
| Distinct instrumental bed | Evening Fall (Harp) — Kevin MacLeod (incompetech.com); https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100236; CC BY 4.0 |
| Narration | 16 local Supertonic 3/F1 Swedish clips,32 steps,speed 0.95,seed 42,44.1 kHz mono PCM16 |

Music master and prepared lossless stereo bed are separately hashed. Crossfade repetitions, if required by measured duration, are recorded in the music asset creation method. The mix uses the accepted shared +2 dB music adjustment with speech ducking and gentle fades.

Source photo identity/license and composer metadata snapshots are retained in `media-sources.json`. Per-episode downloaded masters restore through `../../runtime/hb-c01-sprak-downloads.yaml`. Recreate source-only graphics and the lossless bed with `studio/runtime/.venv/bin/python studio/episodes/hb-c01-sprak/prepare_assets.py`; this rewrites generated hashes and requires complete-video review again.

Exact source wording and translated display text remain unchanged. TTS-only number/date expansions are recorded in the script. All clips have local ASR diagnostics in `narration-check.json`; targeted corrections are documented in `retake-history.json`. ASR is a diagnostic, not auditory or user approval. Review the final voice and mix together in the complete video.
