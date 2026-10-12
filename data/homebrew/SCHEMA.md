# Homebrew content schema, version 1

The executable shape validator is
[`validate_chapter`](../../wip/homebrew/tools/validate_pilot.py).
Unknown keys are rejected in reader content. YAML strings are Unicode; offsets
count Unicode code points (Python string indices), not UTF-8 bytes or UTF-16 code
units. JavaScript consumers must convert to code points before slicing.

## Collection and chapter

`manifest.yaml` has `schema_version`, `id`, `language`, `title`, `status`,
`chapters` and `metadata`. Chapter entries contain stable `id`, numeric `order`
and collection-relative `path`. Metadata paths also resolve relative to the
collection. Only existing chapter files are listed: the pilot's order is 5,
even while chapters 1–4 and 6–12 are absent.

A chapter has `schema_version: 1`, `id`, `language: sv`, `title` and an ordered
`sections` array. Each section has `id`, `title` and an ordered `blocks` array.
Section and chapter IDs also identify their headings. Titles are editorial
Swedish headings, not source quotations. Headings have no sentence segmentation.

## Text units and typed blocks

A text unit contains `id`, complete `text` and a nonempty `sentences` array.
Each sentence has `id`, `start` and `end`; `start` is inclusive and `end` exclusive.
Sentence ranges cover every non-whitespace character in order, without overlap.
Whitespace between sentences is excluded. A list fragment or table cell without
terminal punctuation still receives a segment. Empty text units are not valid.

| Block `type` | Required fields beyond `id` and `type` |
| --- | --- |
| `paragraph` | `text`, `sentences` (the block is also a text unit) |
| `list` | Boolean `ordered`; nonempty `items` of text units |
| `table` | Integer `header_rows`; nonempty rectangular `rows`, each a list of text-unit cells |
| `image` | Collection-relative `path` under `assets/`; nonempty Swedish `alt`; optional `caption` text unit |

Lists are flat; nested source lists must be represented explicitly without
dropping their context before that content can be admitted. Tables require
nonempty cell text; no merged cells are supported in version 1. An image must
exist locally. A figure caption keeps its original wording and provenance.

The pilot exercises paragraphs and unordered lists. Ordered lists, table shapes,
and local-image restrictions have fixture tests. The current source builder and
readable-copy renderer support paragraphs and lists only. Before adding a real
table or image, implement source-cell/asset provenance and rendering, and extend
the integration validator; it currently rejects pilot assets deliberately.

## Identity and editing

IDs match `hb-[a-z0-9-]+` and are globally unique within a chapter, including
sentences, sections, list items and cells. The pilot allocates `hb-c05-uNNNN`
identities once in the committed selection file. Their numeric suffixes are
allocation labels, not display positions. Reordering changes array order only.
Never renumber existing content to close gaps or reuse a retired identity.

`pilot_sentences.yaml` freezes each text unit's UTF-8 SHA-256 and its sentence
IDs/ranges. A normal build reads these entries unchanged and refuses missing
entries or changed text. `--initialize-sentences` proposes entries for newly
allocated units; it never updates existing entries. Review every new boundary.
The suggestions protect common Swedish abbreviations, initials, decimals and
closing quotes, but are not a universal language parser.

When changing a text unit, explicitly review and migrate its registry entry:
retain IDs for unchanged sentences, allocate new IDs for new sentences, and
adjust offsets. Record the edit in editorial metadata. The whole-unit identity
is preserved when editing the same logical paragraph. Word tokenization and
translations are deferred.

## Provenance and editorial metadata

Each substantive text unit has exactly one record in `05_provenance.yaml`:
original repository path and SHA-256, source block and original-DOM CSS selector
or PDF/printed page, source character range, exact extracted passage,
normalization, repairs and selection reason. HTML ranges index the
whitespace-normalized source block; PDF ranges index raw pypdf page text. These
source ranges are separate from learner sentence ranges.

The pilot permits only whitespace normalization, with an empty word-repair log.
Two selections retain a complete sentence from a longer source block. A third
keeps the entry/non-expulsion clauses of a list item while excluding its separate
extradition clause. Other units retain complete paragraphs/list items. Source typos are preserved and
listed in editorial metadata. Substantive factual rewriting is not supported.

Every source has a fingerprint and an attribution-group reference in
`metadata/sources.yaml`. `metadata/attribution.yaml` keeps credits, source links,
reuse notices and change statements. `05_editorial_review.yaml` records topic
coverage, source/block decisions, locally resolved conflicts, gaps, visuals and
snapshot-sensitive claims. These records do not appear in learner text.
