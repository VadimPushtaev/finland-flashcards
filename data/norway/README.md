# Norwegian citizenship study source archive

Source: [Samfunnskunnskap.no](https://samfunnskunnskap.no/en/index.html), the
learning resource that [HK-dir identifies as preparation material for the
citizenship and social studies tests](https://prove.hkdir.no/en/resources/samfunnskunnskap-no).

The requested scope is **English only**. This archive is separate from the
Finnish Homebrew anthology; no Norwegian material has been added to its cards.

## Saved edition: 2026-11-19

- 71 English HTML pages: the course index, 13 topic overviews and 57 lessons.
- 20,830 reading-text words; 5,434 discussion words; 14,575 exercise-text words.
- 21 linked PDF supplements inventoried, not downloaded.
- All discovered English course links resolved locally, with no download failures.

Homebrew's Swedish chapter body text contains 96,533 words using the same
whitespace-token counting convention: approximately **4.63 times** the Norwegian
English reading text. This comparison excludes Norway's discussion prompts,
quizzes, teacher notes and embedded materials. Details and source hashes are in
`snapshots/2026-11-19/comparison.json`.

## Snapshot layout

Each dated directory under `snapshots/` contains:

- `raw/en/`: original response bytes for the English index, topic overviews and
  lessons. These preserve embedded scripts and the teacher notes present on
  English pages, including Norwegian-language notes.
- `manifest.json`: source/final URLs, UTC retrieval timestamps, HTTP metadata,
  sizes and SHA-256 checksums.
- `extracted/en/`: derived JSON with reading passages, discussion prompts,
  exercise text and teacher notes kept separate; source links and iframe URLs
  are also retained.
- `reading/en/`: plain-text reading copies with their titles and source URLs.
- `index.json`: page titles, URLs, page types and word counts.
- `supplements.json`: linked PDF URLs and referring pages. These are an
  inventory, not downloaded files; the English course links Norwegian teacher
  supplements as well.
- `progress.json` and `summary.json`: progress, failures, totals and whether
  traversal of the English HTML course completed.

This is a source-text archive, **not a self-contained offline website**. Images,
audio, video, embedded interactive charts, external sites, and PDFs are not
mirrored. Quizzes' original HTML/scripts are preserved, but the extracted
exercise text is not a validated question/answer dataset. A complete HTML
traversal does not imply that all multimedia or teacher supplements were saved.

## Download or resume

From the repository root:

```bash
poetry run python data/norway/download.py \
  --snapshot data/norway/snapshots/2026-11-19 --delay 2
```

Requests are serial, use a persistent session, wait at least two seconds
between request starts, and have bounded retries/backoff. Each successful
response is checkpointed immediately. Running the same command resumes a
snapshot, verifies hashes and skips already downloaded pages. Failed URLs are
reported rather than silently omitted. English course discovery is restricted
to same-site `/en/*.html` links in page content; search and other languages are
excluded. The traversal has a 200-page limit.

For a fresh edition, use a new dated directory rather than overwriting the
existing snapshot. To rebuild derived JSON and check the saved course without
network access:

```bash
poetry run python data/norway/download.py \
  --snapshot data/norway/snapshots/2026-11-19 --offline
```

## Word-count method

Counts use whitespace-separated tokens in visible text. Reading counts come
from course text containers (`.bt-tekst`) after removing teacher content;
lesson introduction titles, navigation, discussion panes, exercise panes and
video panes are excluded. Topic overview prose is included. Reading text can
contain instructional questions that are part of the prose. Discussion and
exercise counts are reported separately, not treated as additional textbook
prose. Embedded iframe/PDF/video content is outside these counts.

Teacher-note counts include the languages present on the English pages and
should not be used as an English-only corpus total. Swedish-versus-English
word counts are approximate measures of volume, not semantic coverage scores.

## Attribution and reuse

The source's rights remain with its rights holders; this repository's code
license does not apply to the archived content. The site's
[rights notice](https://samfunnskunnskap.no/rettigheter.html) identifies
Cappelen Damm AS as administering rights. The
[translation credits](https://samfunnskunnskap.no/oversettelser.html) credit
Allegro språktjenester for English. Preserve attribution and source metadata
when working with this archive. Downloading does not establish a redistribution
or adaptation license.

The site's `robots.txt` returned HTTP 404 during the initial connection check
on 2026-11-19. No access controls were bypassed.
