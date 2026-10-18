# Preparing episode assets

Follow shared [direction](DIRECTING.md), then the episode's `script.yaml`.
Keep visual and audio choices in that script. `assets.yaml` records the actual
files, checksums, provenance, credits and review state. Do not advance to rendering
until the files exist and integrity checks pass. Review outstanding pronunciation
questions in the complete video; no separate user audio approval is required.

## Runtime and files

Use Poetry in `studio/runtime` for the isolated Python 3.13 media environment.
The root Poetry environment remains responsible for source/script validation.

```sh
cd studio/runtime
POETRY_VIRTUALENVS_IN_PROJECT=true poetry env use python3.13
POETRY_VIRTUALENVS_IN_PROJECT=true poetry install
cd ../..
studio/runtime/.venv/bin/python studio/tools/fetch_assets.py studio/runtime/downloads.yaml
studio/runtime/.venv/bin/python studio/tools/maps.py
```

`studio/media/` is ignored except for explicitly retained selected narration
WAVs and metrics. Commit those takes with the final video in `videos/homebrew/`,
the lockfile, download manifests, asset register and generation tools. Seeds do
not guarantee identical waveforms across hardware or runtime changes. Chapter 1
selected narration and metrics are retained by explicit ignore exceptions; review
status remains in each episode's review record. Add equivalent exceptions for
future chapters when their selected takes are committed.
Unused comparison models can be restored with `runtime/audition-downloads.yaml`;
the default manifest contains production assets and the local ASR model. Generated-file checksums identify the reviewed takes; never
silently rewrite them after approval. Downloaded files must match their SHA-256.

- `media/models/`: pinned local TTS/ASR weights and voice styles.
- `media/sources/`: unchanged photographs, geographic data and music masters.
- `media/<section>/maps/`: generated SVG and PNG map variants.
- `media/<section>/auditions/`: comparative voice trials and diagnostic transcripts.
- `media/<section>/narration/`: one selected WAV per source sentence and metrics.

Keep synthesis inputs in script speech overrides, separate from on-screen text.
Keep sentence timing unset until the renderer assembles the measured clips,
planned pauses and title/credits holds. A narration preview is audio only and
is not an approved final mix.

## Checks

```sh
studio/runtime/.venv/bin/python studio/tools/fetch_assets.py studio/runtime/downloads.yaml --verify
studio/runtime/.venv/bin/python studio/tools/validate_assets.py hb-c01-lage
poetry run python studio/tools/script.py validate hb-c01-lage --ready
```

Inspect map geometry and label placement. Verify photo locations against their
source records. Verify every requested asset and every narration sentence has a
file. Check WAV duration, finite samples, headroom and exact file checksums.
Local ASR helps flag missing or changed words, but cannot approve an accent,
voice quality or pronunciation. Listen to the selected narration before accepting
speech overrides; review the final music balance during the rendering stage.

Preserve source credits and license URLs. Cropped/adapted CC BY-SA photographs
retain their applicable share-alike notice. Model licensing and generated-output
terms are recorded separately; do not label all studio media with one license.
