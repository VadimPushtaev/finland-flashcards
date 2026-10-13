# Russian translation schema, version 1

The permanent workflow is [translation/homebrew](../../translation/homebrew/README.md).
Swedish schema version 1 remains unchanged. Russian output is an additive layer
consumed by the study reader after review and fingerprint validation. YAML is
UTF-8, with English keys and Russian meanings.
Unknown fields in result, vocabulary, glossary, and review records are rejected.

## Files and identity

Under `data/homebrew/ru/`:

- `sections/<section-id>.yaml`: one section heading followed by its sentences in
  source order, including every list item fragment.
- `headings/<chapter-id>.yaml`: one chapter-heading record, shared by its sections.
- `reviews/<source-id>.yaml`: review metadata for either target type.
- `glossary.yaml`: approved shared terminology, initially empty.

A section cannot be complete before its chapter heading is complete. Absent files
mean not started. Structurally valid results can be draft or complete; partial
working drafts belong outside final data. Do not create an empty production
translation to represent a job that has not started.

## Result

Required fields:

```yaml
schema_version: 1
language: ru
source_id: hb-c01-lage
source_sha256: <fingerprint of ordered source records>
records:
  - source_id: <existing heading or sentence ID>
    ru: <one translated sentence, heading, or fragment>
    vocabulary:
      - spans:
          - start: 0
            end: 7
            text: <exact Swedish substring>
        lemma: <Swedish dictionary form>
        pos: NOUN
        context_ru: <meaning here>
        general_ru: <short dictionary meaning>
        glossary_id: <optional approved entry ID>
        terminology_note: <optional explanation of a contextual departure>
```

The example above is a shape description, not valid translated data. See the
[invented executable fixture](../../translation/homebrew/tests/fixtures/example.yaml)
for complete sample text, including a discontinuous expression.

Offsets are zero-based Unicode code points, end-exclusive, relative to the exact
sentence or heading. Each span includes its exact surface text and excludes
surrounding whitespace. Multiple spans belong to one expression and must be
ordered and disjoint. Different annotations cannot overlap. An intervening word
can have its own annotation. Sort vocabulary records by their first span's start.
Written compounds use a single span; do not split components.

POS codes use Universal Dependencies spellings: `NOUN`, `PROPN`, `VERB`, `ADJ`,
`ADV`, `PRON`, `DET`, `ADP`, `AUX`, `CCONJ`, `SCONJ`, `NUM`, `PART`, `INTJ`, `X`.
An expression takes its overall functional POS. Allowed codes do not imply that
standalone function words or numbers should be annotated.

`source_sha256` hashes UTF-8 JSON of the ordered `(ID, exact text)` pairs, using
`ensure_ascii=False` and separators `(',', ':')`. The context tool supplies it.
Heading fingerprints are supplied separately. Chapter reordering alone does not
invalidate an otherwise unchanged section; changes inside its record sequence do.

## Glossary

```yaml
schema_version: 1
entries:
  - id: <stable descriptive ID>
    lemma: <Swedish lemma>
    pos: NOUN
    sense: <brief English sense discriminator>
    ru: <approved general Russian meaning>
    note: <English decision note, possibly empty>
```

IDs and case-insensitive `(lemma, POS, sense)` combinations must be unique.
Referenced annotations must match the entry's lemma, POS and `ru` as their
`general_ru`. Contextual meanings remain sentence-specific. A terminology note
requires a glossary reference. New senses get new entries; do not overwrite an
existing sense to resolve a conflict. The coordinator approves merges after review.

## Review and progress

Required fields:

```yaml
schema_version: 1
source_id: <same target ID>
result_sha256: <canonical result hash>
glossary_sha256: <canonical used-entry hash>
status: draft
review_mode: pending
reviewer: ''
checks:
  fidelity: false
  one_to_one: false
  natural_russian: false
  vocabulary: false
  terminology: false
  headings: false
issues: []
references: []
```

`review_mode` is `pending`, `independent`, or `self_review`. Record an actual
reviewer/agent identifier or role; self-review explicitly records the independence
limitation. `complete` requires all six checks true, a nonempty reviewer, a
non-pending review mode, and no unresolved blocking issues.

Each issue requires `source_id` (a record in this target), Boolean `blocking`,
Boolean `resolved`, and a nonempty English `note` describing the issue/resolution.
Each reference requires nonempty `location` (URL or repository path) and `purpose`.
References substantiate linguistic decisions, not new textbook facts.

Review hashes use SHA-256 of UTF-8 JSON with `ensure_ascii=False`, `sort_keys=True`,
and separators `(',', ':')`. `result_sha256` hashes the full parsed result mapping.
`glossary_sha256` hashes a list of only referenced entries, ordered by glossary ID;
no references means the hash of `[]`. YAML reformatting does not invalidate review.
The public Python helpers `digest` and `glossary_entries` in `tools/workflow.py`
can be used to calculate these values; tests demonstrate the exact algorithm.
Fingerprints are freshness checks, not evidence that language review occurred.

Validation reports available target statuses and the total expected target count.
It validates available output, not whole-book completion. Missing requested files,
orphan reviews, unknown IDs, stale hashes and malformed structures are failures.
Language quality, true sentence correspondence, unreferenced terminology drift,
and vocabulary coverage require the full review described in the instructions.
