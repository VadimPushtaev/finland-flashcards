# Homebrew flashcard practice — implementation specification

> **Status: specification approved? NOT YET.** This document lives in the feature PR that will ultimately deliver the complete practice feature. It is not a separate "planning PR". At present, only this specification is committed. Do not start implementing, merging, or deploying until the owner explicitly approves implementation. Subsequent code commits should use this same PR and branch.

## 1. Product outcome

Add a first-class **Öva / Practice** experience to the existing Homebrew study site. It is independent of the reading/lecture interface; users select **one of the 12 whole chapters**, not the roughly 100+ sections. The site presents randomized multiple-choice flashcards, checks answers automatically, tracks detailed personal statistics, and schedules future reviews with **Py-FSRS**. No daily card limits.

The experience should be simple: open Practice, select a chapter, see "N cards to practice", answer until the queue is exhausted, then optionally request **"Want more?"** to practice future cards early. Avoid complicated "today/tomorrow" distinctions in the main UI.

### Agreed requirements

- Source decks: `cards/homebrew/hb-c01/ALL.txt` through `hb-c12/ALL.txt`; do not combine with subchapter files or duplicate cards.
- Include **every new/unseen card and every currently due card** for the chosen chapter, with randomly shuffled presentation. No daily caps.
- One Swedish question and four choices. Clicking an option immediately checks its correctness and reveals the right choice.
- After the reveal show **Again / Hard / Good / Easy**, with a **suggested grade already selected**, plus one prominent **Next** button. Clicking Next commits the selected grade; the user does not need to rate each answer manually.
- Automatic grade: correct without pre-answer translation = **Good**; correct with pre-answer translation = **Hard**; incorrect, with or without translation = **Again**. The user may override **any** automatic grade, even choose Good after an incorrect click (e.g., an accidental tap). Log both raw correctness and the committed grade separately.
- When card translation data **eventually exists**, tapping any word in the question or any of the four options opens both a Russian word explanation and translation of its full source sentence/text. Using a translation **before** answering affects suggested grading; using it after answering does not. If no card translation exists, the card works as regular text without dead links or fake translations.
- A failed/Again card should return after a few other cards, **even when a standard short learning interval would otherwise delay it**. The intent is to finish a chapter in one sitting without waiting ten minutes. All such retries still go through **Py-FSRS** with their actual timestamp; do not implement FSRS stability/interval equations or keep a second long-term scheduler. If there are no other cards, provide a simple path to retry instead of forcing the user to wait.
- Personal persistent progress and full per-card answer statistics are stored **only in server-side SQLite**. Browser component state may hold the current screen/question, but no browser localStorage/IndexedDB persisted practice progress.
- Desired retention starts at **90% for each account** and is user-editable. New retention applies to subsequent scheduling decisions; do not mass-reschedule the entire existing collection on setting changes.
- **Want more?** is a **one-time, session-local** choice after the normal queue is exhausted: raise the current retrievability selection threshold above the user's saved desired retention, show counts of additional eligible not-yet-due cards and let the user study them early. If the threshold yields none, offer the nearest future reviews by due date as a fallback. Never modify the saved retention preference just to get more cards. These early responses count as **real** Py-FSRS reviews.
- No explanations: neither generate explanations nor add explanation fields/placeholders.
- Preserve existing Kahoot-compatible card format and existing reading functionality.

## 2. Relevant existing architecture

- `study/app/main.py`: FastAPI backend and routes for chapter reader.
- `study/app/auth.py`: cookie sessions, authenticated user lookup, `same_origin` protection for writes.
- `study/app/database.py`: persistent SQLite schema version 1 and existing users/sessions/reading state.
- `study/frontend/src/App.tsx`: React/TypeScript hash navigation and sidebar; Bootstrap layout.
- `study/frontend/src/Translation.tsx`: `TranslationText` and `TranslationPanel`; reuse their UX and data types.
- `study/app/translations.py`: reviewed and source-hash-validated Russian translation pipeline for the reader.
- `cards/homebrew/hb-cNN/ALL.txt`: pipe-separated chapter decks, with prompt, metadata, four options and correct answer flags; source subchapter files must not be parsed in addition.
- `study/Dockerfile` currently copies reader data but not chapter card decks; packaging must be added.
- `study/README.md`, `study/tests/`, `study/frontend/tests/`: document and validate behavior using existing conventions.

Card generation and the original card rows remain **read-only** for this feature. No Kahoot conversion changes.

## 3. Card catalog, stable IDs, and updates

1. Implement a small read-only backend loader for all twelve chapter-level `ALL.txt` files; package these assets in the runtime image. Do not load the project-wide `cards/ALL.txt`.
2. Validate the exact source field layout, four options, and exactly one correct-answer flag. Fail clearly on malformed files, missing chapter decks, or inconsistent rows; add parser fixtures using real example lines.
3. The unit of selection is a whole chapter. Expose total, unseen and available-to-review counts without leaking other users' state.
4. **Keep identity deliberately simple:** hash canonical chapter ID and relevant card contents, not source line number. If wording, options, or correctness changes, the card becomes new and **its prior schedule/statistics need not migrate**. This is accepted by the owner. Handle identical duplicate rows deterministically (e.g., deduplicate identical content or distinguish occurrences consistently) and test the policy. Historical events for old identities may remain in the DB but need not map to the new card.
5. Do not introduce an explicit persistent ID registry or complicated content-matching/migration system.
6. Server is authoritative for answer validation; frontend should not receive correctness before submission. The question/choice rendering can be randomized if the submitted choice mapping is consistent.
7. Leave a future-compatible attachment point for translations per question and option, using canonical text identity and stale-data checking. Do **not** generate translations now or modify the source card format.

## 4. FSRS scheduling: use the package, keep queues simple

1. Depend on a pinned compatible version of **`fsrs` / Py-FSRS** in `study/pyproject.toml` and `study/poetry.lock`. Use its public scheduling/retrievability APIs and serialized card state; do **not** reimplement FSRS mathematics.
2. Store per-user/per-card FSRS state and its next due timestamp. New cards have no review history and are always included in a normal chapter session.
3. Regular selection = union of **all unseen cards + all cards whose schedule is due now**, shuffled into one queue. No daily caps or artificial "today" boundary for the core user experience.
4. **Short-session retries:** an Again/failure makes the card reappear after a small number of other queued questions where possible. For the explicit one-sitting UX, permit these retries before Py-FSRS's normal minute-scale learning due time; use the package's normal review operation with the true review time and record the attempt. This is a queue policy (selection), **not** a new formula for scheduling memory. Test Py-FSRS behavior for immediate/early repeat operations and adjust the implementation to stay within supported API semantics; do not synthesize fake elapsed time.
5. Prevent infinite forced retries: define a sane session-exit path and make retry count visible when relevant. Do not silently discard failed-card history. Once a card is answered successfully (or user explicitly ends the session), stop repeatedly forcing it in the same sitting; its next normal due is owned by FSRS.
6. Suggested automatic grades follow the three-way mapping in §1. Four explicit buttons override them, and the **committed** grade drives FSRS scheduling. Keep answer correctness, pre-answer translation use, suggested grade, and chosen grade as **independent** fields.
7. Changing the saved desired retention affects subsequent scheduler operations. It does not automatically rewrite all previous due dates. The separate "Want more?" selection cutoff never persists into account settings.
8. Use real UTC timestamps and trusted server time; no client-supplied grading/correctness truth. Don't create a review just by showing a card or selecting an option; update FSRS and history when **Next** commits.

### An important design constraint

The source-of-truth for long-term memory scheduling is Py-FSRS. We do not create another due-date algorithm. In-session shuffle/priority/retry is presentation logic. The final implementation must test and document how Py-FSRS handles learning/relearning reviews committed earlier than its recommended timestamp. Do not treat an early repeat as if 10 minutes elapsed.

## 5. Full per-user statistics and per-card history

This is a required feature, **not only instrumentation**. For **every committed answer**, persist an append-only event with at least:

- authenticated user ID, card ID and chapter ID;
- UTC time and whether this was ordinary practice, a short-session retry or extra practice;
- selected answer/choice and actual correct answer (or stable identifiers), **correct/incorrect**;
- translation used **before** answer (boolean; optionally track which text surface was opened);
- system-suggested FSRS grade and **user-selected final grade**, plus whether the user manually overrode it;
- FSRS scheduling outcome (due timestamp and any library state needed to audit/replay responsibly).

Per-card statistics must be **viewable in the UI**, scoped to the signed-in account. At minimum show total attempts, correct/incorrect totals, attempts **with vs without pre-answer translation**, a breakdown that crosses correctness with translation use, counts for each **Again / Hard / Good / Easy** committed grade, and chronological attempt history. Show suggested versus overridden grade where relevant. Prefer clear totals rather than a complex analytics dashboard. Historical logs must not be overwritten when a card is reviewed again.

The user explicitly accepts resetting the current card's visible progress if **its content hash changes**; no sophisticated mapping of prior card history is required.

## 6. "Want more?" extra-practice behavior

After the selected chapter's ordinary new/due queue and short retries are finished:

1. Show simple completion status and **Want more? / Jag vill öva mer**.
2. Open a **temporary**, session-only threshold slider from the user's saved desired retention up to a supported high value (for example 0.99), with a live count from server-side eligibility logic.
3. With Py-FSRS, calculate current retrievability for studied but **not yet due** chapter cards; select those at or below the temporary cutoff, excluding cards already completed in this sitting unless explicitly eligible as a failed-card retry. Higher cutoff may include more candidates; never claim it must.
4. **Fallback:** if the threshold yields no eligible extra cards, offer some cards with the **nearest upcoming due timestamps** regardless of their current retrievability, with a transparent label such as "Next scheduled cards" and a count. This makes optional extra practice possible without falsifying FSRS probabilities. Do not mix the two strategies invisibly.
5. Clicking start creates a temporary extra queue. Changing the slider alone has no persistence side effects, and the user's stored desired retention **remains unchanged**.
6. Each extra attempt is graded and committed through the **same Py-FSRS scheduler** as ordinary practice, using actual time, and added to the same personal statistics.
7. When there are genuinely no learned cards available (e.g., everything is new or already practiced in the session), present an honest empty state; no fabricated extra cards. Repeated "Want more" use must not create an unbounded same-card loop by default.

## 7. UI / interaction contract

1. Add a separate **Practice** main navigation item alongside overview/saved texts. Chapter cards list **12 top-level chapters**, total cards and cards currently ready to study. Avoid forcing the user to understand study-day or learning-step terminology.
2. Authenticated practice only; guests may discover the feature but must log in before answering/saving.
3. In a chapter, randomly present questions, four selectable options, immediate correctness feedback and correct-answer highlighting. After an answer, show proposed selected grade, four explicit grade buttons, and **Next**. No explanation panel.
4. **No accidental review on option click:** grade selection and Next are the commit point. Avoid double submissions/duplicate logs. A refresh before Next must not create an FSRS event. Make app usable on desktop and mobile; allow clear session exit.
5. Show per-user retention setting in an understandable place; its saved value and the temporary Want more slider are distinct.
6. Add a simple **per-card statistics view** accessible during practice (e.g., a Details/History affordance after answering) and/or from the chapter. Include all breakdowns in §5, including translation-versus-correctness and four grade counts.
7. Reuse the reader's translation UX, but only if **reviewed, source-matched card-specific translations** are present. The initial rollout has none, so question and choices remain plain Swedish text; do not show fake translations or broken word links. Future translator work must cover both prompts and each option and show whole-sentence translations.
8. Track translation usage before selecting an answer; translating after answering is permitted but does not change the suggested grade or the committed correctness record.
9. Use Swedish UI language consistent with the site, existing themes, accessibility semantics, focus management, keyboard controls and responsive layout. Handle network errors and progress saving errors clearly.

## 8. Storage, authentication and operational simplicity

- Persist everything important in **SQLite on the server**: settings, FSRS states and statistics; no browser-persisted progress. Ephemeral React UI state is fine.
- Reuse the existing account/session system; the server derives the user from session cookies. Use `current_user` and `same_origin` for mutations; enforce user isolation and prevent stale responses following account switch.
- Use a **minimal additive SQLite schema change** to accommodate practice data while preserving existing accounts and reading tables. Avoid unnecessary migration frameworks and elaborate legacy-data migration tooling. Existing user data must not be intentionally erased; any manual handling of old database files before deployment can be coordinated separately.
- Transactions and an idempotency token or equivalent unique event ID must stop double-clicks and network retries from recording the same answer twice. Do not build a complex session orchestration platform or persist large queues in the browser.
- Back up the current SQLite DB before deploying schema changes. No automatic migration of historic Anki data.
- Do not deploy, merge or alter production as part of simply implementing this PR.

## 9. Implementation stages (after explicit approval)

1. **Catalog and tests:** parse chapter ALL.txt files, deterministic hash IDs, source validation, Docker asset packaging, chapter/card API.
2. **Scheduling and storage:** pin Py-FSRS, implement small additive schema update, authenticated per-user settings, FSRS state, immutable review history, atomic commit/Next, basic statistics aggregation.
3. **Practice UI:** chapter picker, random queue with all new and due, automatic checking, grade override + Next, FSRS learning retry queue, simple end-of-session state.
4. **Extra practice:** session-local retrievability cutoff, preview counts, nearest-due fallback, early reviews through Py-FSRS without changing desired retention.
5. **Statistics and translation integration points:** visible card history/counts and missing-translation-safe presentation, reuse existing translation components; **no translation data generation**.
6. **Verification and docs:** test, review, polish, update study README; keep PR in draft until reviewed.

### Test matrix

- Input: all 12 decks, bad rows/correctness flags, duplicate rows, hash/order stability, changed-text reset, packaged runtime paths.
- FSRS: first reviews, Again/Hard/Good/Easy, ordinary due, learning/relearning early repeats with real timestamps, retention changes only affecting future decisions, optional early reviews, deterministic clock fixtures.
- Grading/history: correct and wrong with/without translation; after-answer translation not counted; manual Good after incorrect; suggested/final grade divergences; history breakdown math, append-only audit; no record before Next; Next idempotency.
- Queue: mixed new/due randomized without caps; failure comes back after other cards, session finish behavior, short/single-card cases and bounded retry; no accidental stale cross-account review.
- Extra practice: threshold count accuracy, higher cutoff, empty threshold fallback to nearest future cards, no permanent settings change, early FSRS updates, no repeated endless loop.
- Access/storage: account isolation with existing users, no client-supplied user IDs, CSRF/same-origin, concurrent Next, persist through server restart, minimal schema upgrade preserving reader state.
- UI: choice feedback, four ratings, Next, statistics view, chapter count, responsive layout, keyboard/screen readers, signed-out flow, no translation and mocked future translation, existing reader regression tests.
- Run `study` Python unit tests, frontend build and Playwright suite; update `study/README.md`.

## 10. Deliberately deferred

1. **Card translation generation:** later create a dedicated skill/workflow to generate, review and version Russian word and complete-source-text translations for every question and every option, using the reader's source-fingerprint principles. Do not generate now.
2. **Anki import:** later bring prior user review history into the new SQLite schema with a separate approved import plan. Do not build or perform now.
3. **Kahoot:** retain source compatibility; do not alter Kahoot export tools.
4. **Explanations:** no explanation data or UI in this scope.

## 11. Commit and review policy

This is an **implementation PR**, not a PR whose deliverable is the plan alone. Its **first amended commit** contains just this file in `wip/`, as a reviewable specification. Implementation will be committed to the **same branch and PR** only after the user explicitly says to begin. No application code, card data, dependencies, database, or deployment assets are modified at the planning stage.
