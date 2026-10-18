# Climate and seasons assets

The script is the creative source of truth. The asset register contains exact
checksums and credit/relevance checks. Download the pinned originals with:

```sh
studio/runtime/.venv/bin/python studio/tools/fetch_assets.py studio/runtime/hb-c01-arstider-downloads.yaml
studio/runtime/.venv/bin/python studio/tools/audition.py supertonic --voice F1 --speed .95 --section hb-c01-arstider --all --output studio/media/hb-c01-arstider/narration
studio/runtime/.venv/bin/python studio/episodes/hb-c01-arstider/prepare_assets.py
```

The background is JIP's verified snowy December forest in Vuosaari, Helsinki
(CC BY-SA 4.0), continuously moving across the entire episode. It is decorative,
not evidence for weather elsewhere in Finland. The steady foreground photograph
is Janne Hellsten's Nuuksio autumn colors (CC BY 2.0), illustrating autumn colors
without claiming that this photograph establishes seasonal dates nationally.

Fact cards reproduce only source figures and terms. They are typography rather
than quantitative maps or graphs. The longest bilingual comparison uses 44/36 px
Swedish/Russian fonts; all other body pairs use 48/40 px.

The distinct Kevin MacLeod track Almost in F (official filename and catalog title;
ISRC USUAN1100394) lasts 32m42s and needs no loop. Excerpt, fade and duck beneath
narration with the accepted series music setting (+2 dB). The official catalog
snapshot is music-source.json. Model terms and fixed synthesis settings follow
studio/TTS.md. Raw takes and final mix require whole-video listening review;
automated file checks and transcript diagnostics do not imply user approval.
