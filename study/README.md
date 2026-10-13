# Homebrew study website

A Swedish reader for the twelve chapters in `data/homebrew/`. FastAPI serves the
original chapter text and a React frontend styled with Bootstrap 5. Node.js/Vite
build the frontend; Poetry manages the separate Python application environment.

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build -d
```

Open **http://localhost:18743**. The port deliberately differs from typical
development ports. It is bound to localhost. To choose another port:

```bash
STUDY_PORT=19471 docker compose up --build -d
```

```bash
docker compose logs -f study
docker compose down
```

The image uses Node.js 24 for the frontend build and Python 3.12 for runtime.
Both dependency lockfiles pin the build inputs. The application reads a copy
of `data/homebrew/`; rebuild the image after updating that collection.

## Hetzner deployment

The public reader is at **http://fi.pushtaev.ru:18743** on `ssh hetzner`.
Its files live in `/opt/finland-flashcards`, using Compose project
`finland-flashcards`. The server `.env` sets `STUDY_BIND=0.0.0.0` and
`STUDY_PORT=18743`; local Compose runs still bind to localhost by default.

To update from the current local checkout (including uncommitted files), run
from the repository root:

```bash
rsync -azR --exclude=node_modules --exclude=dist --exclude=__pycache__ \
  --exclude='*.pyc' --exclude=.venv --exclude=test-results \
  --exclude=playwright-report \
  compose.yaml .dockerignore study/ data/homebrew/ \
  hetzner:/opt/finland-flashcards/
ssh hetzner 'cd /opt/finland-flashcards && docker compose -p finland-flashcards up --build -d --wait --wait-timeout 120'
```

Operational commands:

```bash
ssh hetzner 'cd /opt/finland-flashcards && docker compose -p finland-flashcards ps'
ssh hetzner 'cd /opt/finland-flashcards && docker compose -p finland-flashcards logs --tail=100 study'
ssh hetzner 'cd /opt/finland-flashcards && docker compose -p finland-flashcards down'
curl --fail http://fi.pushtaev.ru:18743/api/health
```

The service restarts automatically after a reboot. Content and reviewed
translations are baked into the image, so updates require a rebuild. Reading
progress stays in each browser and is specific to the public URL.

## Study features

- Twelve chapter cards and section navigation, with reading-time estimates.
- Complete original paragraphs and ordered/unordered lists, without rewriting.
- Search across the anthology; results open the original passage in context.
- Paragraph bookmarks, completed sections and resume-reading links.
- Font choice, text size and dark mode; responsive desktop/mobile layouts.
- Optional source locations plus original credits and reuse terms.

Progress and bookmarks live in browser local storage, using the collection's
stable IDs. They persist through container rebuilds but are specific to the
browser and origin/port. Clearing browser storage removes them. No account or
database is required. Study data is not sent to a third-party service.

## Local development

Requires Python 3.12–3.14, Poetry and Node.js 22.12+ (or 24 LTS).
The root project's older Python environment is unaffected.

```bash
cd study
poetry install --no-root
poetry run uvicorn app.main:app --reload --port 18743
```

In another terminal:

```bash
cd study/frontend
npm ci
npm run dev
```

Open **http://localhost:18744** for Vite with hot reload. `/api` requests proxy
to the Python backend on port 18743. For a production-style local preview, run
`npm run build` and open the Python server on port 18743 instead.

## Verification

```bash
cd study
poetry run python -m unittest discover -s tests -v
cd frontend
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests expect the Compose app to be running on port 18743. Override
`STUDY_URL` to test another deployment. Tests cover exact source fidelity,
Swedish search/pagination, bookmarks, completion/resume, persisted preferences
and mobile navigation. Production does not include browser-test tools.

The browser suite covers 320, 375, 390 and 430 pixel phone widths, an 844×390
landscape phone, a 768 pixel tablet and a desktop. It checks the overview,
search, bookmarks, expanded source credits, large reading text and access to
the chapter menu on short screens.

## Russian reading support

Open the first section, **Finland i Norden**, and select a Swedish word to see its
contextual Russian meaning and the full sentence translation. The dictionary
entry and Swedish original are expandable in the same panel. Selecting a function
word without a vocabulary record still shows the sentence translation.

The focused reader keeps chapter/section selectors behind **Innehåll** and the
main navigation behind the menu button. Desktop and landscape phones place the
translation beside the reader; portrait phones place it below. Both panes scroll
independently, and closing the translation restores the full reading area.
Keyboard users can select words with Enter/Space and close with Escape.

Only reviewed translations are displayed. Chapter 1 has Russian data for all eight
sections and its chapter heading. All eight sections are complete.
Draft and untranslated sections remain readable in Swedish with an availability
message. The API at
`/api/chapters/{chapter_id}/sections/{section_id}/translation` verifies source,
result and used-glossary fingerprints before returning records, including exact
Swedish sentence text and Unicode code-point vocabulary spans. Missing, draft or
stale translations return `available: false`; unknown section IDs return 404.
Rebuild the Docker image after adding reviewed translation files.

Browser tests cover translation selection, discontinuous expressions, Unicode
spans, keyboard focus, unavailable/error states, non-overlapping panes, orientation
changes, large text, and retained bookmarks/navigation across seven viewport sizes.
