# Samhällskunskap inför medborgarskapsprovet

Swedish source-based study anthology. The current edition contains chapter 05
as a pilot awaiting review, not the complete twelve-chapter collection.

- [Manifest](manifest.yaml): collection identity, chapter order and metadata paths.
- [Swedish pilot](sv/chapters/05_rattigheter_jamlikhet_och_skyldigheter.yaml).
- [Readable review copy](../../wip/homebrew/PILOT.sv.md).
- [Content schema](SCHEMA.md).
- [Source fingerprints](metadata/sources.yaml), [passage provenance](metadata/05_provenance.yaml)
  and [attribution](metadata/attribution.yaml).
- [Editorial decisions, remaining gaps and snapshot limitations](metadata/05_editorial_review.yaml).
- [Checkpoint 2 review](../../wip/homebrew/PILOT_REVIEW.md) and
  [work progress](../../wip/homebrew/PROGRESS.md).

Only archived repository material is used. This edition preserves the sources'
wording and source-era statements; it does not certify that every statement is
current law or that the eventual official exam is completely covered. Preserve
the accompanying attribution and editorial metadata when distributing or
rendering this collection. Source texts retain their original reuse terms.

Reader-facing chapter files contain Swedish text and English schema keys.
English work notes, provenance and licensing information are kept separately.

Rebuild and validate with Poetry from the repository root:

```bash
poetry run python wip/homebrew/tools/extract_sources.py  # if intermediates are absent
poetry run python wip/homebrew/tools/build_pilot.py
poetry run python wip/homebrew/tools/validate_pilot.py
poetry run python -m unittest discover -s wip/homebrew/tools -p 'test_*.py' -v
```

The editorial inputs are `wip/homebrew/pilot_selection.yaml` and
`wip/homebrew/pilot_sentences.yaml`. Do not hand-edit generated chapter text.
