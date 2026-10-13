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
progress, bookmarks and preferences live in SQLite in the persistent Docker volume.

## Study features

- Twelve chapter cards and section navigation, with reading-time estimates.
- Complete original paragraphs and ordered/unordered lists, without rewriting.
- Search across the anthology; results open the original passage in context.
- Paragraph bookmarks, completed sections and resume-reading links.
- Font choice, text size and dark mode; responsive desktop/mobile layouts.
- Optional source locations plus original credits and reuse terms.

Reading, search and translations are public. Saving a bookmark, marking a section
as read, or changing font, text size or theme prompts guests to log in. Login
completes the requested change; cancelling leaves it unapplied. Account state
follows the user across browsers. Old browser-local saves are discarded without
importing them. No third-party account service is used.

## Accounts and persistent storage

Run account commands on the Docker host. Passwords are prompted twice without
being echoed or included in command arguments:

```bash
docker compose exec study python -m app.admin create-user vadim
docker compose exec study python -m app.admin reset-password vadim
```

Usernames are case-insensitive, contain 1–64 characters and cannot contain spaces.
Passwords contain 8–1024 characters and are stored as Argon2 hashes. There is no
registration or password-change web endpoint. Resetting a password revokes every
session for that account; existing study state remains intact.

Login has no server-side expiry. The HttpOnly, SameSite cookie lasts one year and
is renewed on authenticated requests. Browser cookie deletion or browser-imposed
retention limits require login again; logout and host password resets revoke
sessions. Login attempts are limited to ten per client address per five minutes.

SQLite lives at `/var/lib/homebrew-study/study.sqlite3` in the named Docker volume
**finland-flashcards-study-data**. Accounts, hashed sessions and saved state survive
restarts, image rebuilds, container replacement, and ordinary `docker compose down`
followed by `up`. Keep this volume when changing deployments. **`docker compose down -v` deletes the volume and its data.** Schema initialization preserves existing data
and refuses unsupported database versions. Health checks verify database access.

For the later nginx HTTPS deployment, set these in the host `.env`:

```dotenv
STUDY_SECURE_COOKIES=true
STUDY_PUBLIC_ORIGIN=https://fi.pushtaev.ru
# Use the actual nginx peer address/network trusted to supply forwarded headers.
STUDY_PROXY_IPS=127.0.0.1
```

Keep the application port private behind nginx. `STUDY_PUBLIC_ORIGIN` must exactly
match the browser's origin, including a nonstandard port when used. When unset,
origin checks use the request origin seen by the app. Local HTTP uses
`STUDY_SECURE_COOKIES=false`. nginx installation is managed separately.

### Backup and restore

Use SQLite's backup API, which includes committed WAL data; do not copy only the
live database file. Choose a new backup filename each time:

```bash
docker compose exec -T study python -m app.admin backup-db /tmp/study-backup.sqlite3
docker compose cp study:/tmp/study-backup.sqlite3 ./study-backup.sqlite3
chmod 600 study-backup.sqlite3
docker compose exec -T study rm /tmp/study-backup.sqlite3
```

Backups contain private account information and should be stored outside Git.
To restore a trusted backup, stop the service, mount the backup read-only and use
SQLite's backup API to replace the database contents in the same persistent volume:

```bash
docker compose stop study
docker compose run --rm --no-deps --user root -T \
  -v "$PWD/study-backup.sqlite3:/tmp/restore.sqlite3:ro" study python - <<'PYRESTORE'
from contextlib import closing
import os
from pathlib import Path
import sqlite3

target = Path(os.environ["STUDY_DATABASE_PATH"])
with closing(sqlite3.connect("file:/tmp/restore.sqlite3?mode=ro", uri=True)) as source:
    assert source.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert source.execute("PRAGMA user_version").fetchone()[0] == 1
    with closing(sqlite3.connect(target)) as destination:
        source.backup(destination)
# Keep the volume writable by the service's non-root user.
owner = target.parent.stat()
for file in (target, Path(str(target) + "-wal"), Path(str(target) + "-shm")):
    if file.exists():
        os.chown(file, owner.st_uid, owner.st_gid)
        os.chmod(file, 0o600)
PYRESTORE
docker compose up -d
```

Restore replaces account state with the backup snapshot; make a fresh backup first
if existing state needs to be retained.

## Local development

Requires Python 3.12–3.14, Poetry and Node.js 22.12+ (or 24 LTS).
The root project's older Python environment is unaffected. Local development uses
`study/state/study.sqlite3` (ignored by Git), or `STUDY_DATABASE_PATH` when set.
Create local development accounts with `poetry run python -m app.admin create-user NAME`.

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

Browser tests start their own server on port 18745 with a disposable SQLite database
and isolated test accounts; they never modify the Compose volume. Build the frontend
before running them. `STUDY_URL` can override the server for public reading tests,
but account tests require the isolated local server. Tests cover source fidelity,
search, bookmarks, completion/resume, account isolation, login/cancel/revocation,
failed saves, persisted preferences and mobile navigation. Production does not
include browser-test tools.

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
