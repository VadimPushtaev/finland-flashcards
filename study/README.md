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
