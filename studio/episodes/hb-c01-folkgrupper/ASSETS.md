# Prepared assets

The editable creative plan is `script.yaml`; exact acquired files, checksums, credits and narration inputs are in `assets.yaml`.

| Asset | Selection and primary source |
| --- | --- |
| Continuous decorative photograph | Turku Cathedral and Aura River, Markus Koljonen (Dilaudid); https://commons.wikimedia.org/wiki/File:Turku_Cathedral_and_Aura_River.jpg; CC BY-SA 3.0 |
| Useful foreground |13 original text cards containing exact Swedish source substrings, including dates, names and population figures |
| Distinct instrumental bed | Meditation Impromptu 01, Kevin MacLeod; https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100163; CC BY 4.0 |
| Narration |39 local Supertonic 3/F1 Swedish clips,32 steps,speed 0.95,seed 42,44.1 kHz mono PCM16 |

The city/river photograph provides decorative context. It is not presented as a portrait of any community or as an image of a historical migration event. The photo adaptation retains CC BY-SA 3.0 terms. No invented geographic borders or anonymous ethnic portraits are used.

The original music master and prepared lossless stereo bed are separately hashed. The 7:21 video uses two explicit 4-second equal-power repetitions of the selected calm piano track. The renderer applies the accepted +2 dB music adjustment, ducking under narration, a 2-second fade-in and 3-second fade-out.

Photo and composer evidence snapshots are retained in `media-sources.json`. Restore downloaded masters with `studio/runtime/hb-c01-folkgrupper-downloads.yaml`, then run `studio/runtime/.venv/bin/python studio/episodes/hb-c01-folkgrupper/prepare_assets.py` to regenerate typography and the lossless bed. The helper verifies pinned masters first and does not require ignored research metadata files.

All 39 selected clips have local ASR diagnostics in `narration-check.json`; see `ASR_NOTES.md` and `retake-history.json` for the targeted 1991 correction and remaining recognition ambiguities. No auditory or user approval is claimed. Review pronunciation and the mix together in the complete video.
