# Studio validation — 2026-10-17

The documentation-only studio was checked against the current local Homebrew
manifest and translation files using Poetry with the repository's locked runtime
dependencies in a temporary Python 3.9 environment. No dependencies were added.

- Inventory matches all 187 section IDs exactly once and in manifest/section order.
- All source paths resolve; all production states are `unstarted` with no episode path.
- 86 sections have Russian translations and complete section/chapter-heading reviews;
  the other 101 await translation. Available source fingerprints and review result
  hashes match, all review checks are true, and no unresolved blocking issue is recorded.
- All studio YAML parses successfully.
- The two example sentences match exact Swedish source slices and Russian records;
  referenced asset IDs resolve and audio timing remains unset.
- Studio documentation links resolve and `git diff --check` passes.

These checks validate records and documentation, not voice quality, visual layout,
music balance, media rights, or rendered output. Those require the future production
samples and episode reviews described in the workflow. No video has been produced.

To repeat the content checks, parse the manifest and inventory, compare their ordered
section IDs, inspect the referenced source/translation files, and apply the fingerprint
algorithms in the linked Homebrew translation schema. Compare example strings directly
to source sentence slices and Russian records by ID. Recheck links after editing docs.
