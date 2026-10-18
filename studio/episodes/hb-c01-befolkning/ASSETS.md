# Population and urbanisation assets

The script is the creative source of truth. The asset register contains exact
checksums and credit/relevance checks. Download the pinned originals with:

```sh
studio/runtime/.venv/bin/python studio/tools/fetch_assets.py studio/runtime/hb-c01-befolkning-downloads.yaml
studio/runtime/.venv/bin/python studio/tools/audition.py supertonic --voice F1 --speed .95 --section hb-c01-befolkning --all --output studio/media/hb-c01-befolkning/narration
studio/runtime/.venv/bin/python studio/episodes/hb-c01-befolkning/prepare_assets.py
```

The background is DIMMIS's verified Helsinki panorama from Olympiastadion tower
(CC BY-SA 3.0), continuously moving across the whole episode. It illustrates a
Finnish city without pretending to depict a statistical population distribution,
the 1950s, or every urban community. Open foreground space is intentional when
there is no useful factual illustration.

Fact cards repeat source figures with their dates: 2023 / 5,6 miljoner,
2020 / 73 procent, 1950-talet. These are simple typography, without invented chart
proportions or silently updated statistics. All bilingual body pairs use 48/40 px
Swedish/Russian fonts.

The distinct Kevin MacLeod track Dreams Become Real (ISRC USUAN1500027)
lasts 6m50s and needs no loop. Excerpt, fade and duck beneath narration with the
accepted series music setting (+2 dB). The official catalog snapshot is
music-source.json. Model terms and fixed synthesis settings follow studio/TTS.md.
Raw takes and final mix require whole-video listening review; automated file
checks and transcript diagnostics do not imply user approval.

The initial percentage take was rejected by transcript diagnostics (70 instead of
73). A targeted fresh-seed take using the speech-only expansion “sjuttio tre” now
recovers 73 percent. The replacement WAV, its generation record and the preserved
full source-order metrics are recorded in narration-revisions.json and assets.yaml.
The exact on-screen source remains unchanged. Whole-video user listening review
is still pending.
