# Worked example — partial, not a production episode

For new episodes, use the current [script-authoring workflow](../SCRIPTING.md)
and the complete [Finland i Norden script](../episodes/hb-c01-lage/SCRIPT.md).
The files here retain the minimal illustration from the initial studio setup;
they are not accepted by the production-script validator.

[script.yaml](script.yaml) contains only the first two sentences of
`hb-c01-lage` (Finland i Norden), copied exactly from the Swedish source and
matched to the existing reviewed Russian translations by sentence ID.

The section fingerprint covers the whole section, including its heading; it does
not imply this partial script covers the whole section. `example_only: true`
marks the example explicitly. Audio paths and timings remain unset.

[assets.yaml](assets.yaml) illustrates one requested background shared by both
sentences. No image has been acquired and no reuse terms have been established.
The fallback is a production suggestion, not a completed asset.

This example demonstrates the script-to-asset relationship. Actual episodes must
include every sentence in their section and satisfy the full review checklist.
