# Orientation Learning Materials (Page-Based Cards)

This guide defines the page-based workflow for the civic orientation website
crawl under `data/orientation/en/`. We generate one file of questions per page
in the Learning materials tree. See `card_creator/orientation/PROGRESS.md` for
the full list and progress tracking.

Sources:
- Orientation crawl overview: `data/orientation/README.md`
- Learning materials index: `data/orientation/en/learning-materials.html`
- Progress tracking: `card_creator/orientation/PROGRESS.md`

## Orientation vs orientation_guide (important)

- `orientation` (this guide): the website-based civic orientation materials
  under `data/orientation/`. Output decks belong under `cards/orientation/` and
  are organized by page.
- `orientation_guide` (legacy): the single PDF textbook
  `data/orientation_guide.pdf` with its own workflow under
  `card_creator/orientation_guide/` and per-subchapter decks under
  `cards/orientation_guide/`.

These two pipelines are independent; `cards/orientation/` has nothing to do
with `cards/orientation_guide/`.

## Scope and source rules

- Use the English learning materials under `data/orientation/en/learning-materials/`
  as the primary question sources.
- Use `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/` as
  section-level overviews to frame question coverage.
- Avoid trainer guides and site meta pages (e.g.,
  `data/orientation/en/kouluttajan-opas.html`,
  `data/orientation/en/about-the-site/`) as direct question sources.

## Page-based output (required)

- Every page in the Learning materials tree gets its own output file.
- Do not group pages by exam topic or broad categories.
- Do not hesitate to generate many questions for a single page; more cards are
  better.
- Update `card_creator/orientation/PROGRESS.md` with the question count for
  each page (or mark a page as skipped).

### Output file conventions

- Output location: `cards/orientation/<section>/<page>.txt`.
- `<section>` is the top-level section slug (e.g., `integration`,
  `people-and-culture`, `living-in-finland`).
- `<page>` is the page slug from the URL (lowercase, ASCII, hyphenated).
- For the section landing page itself, use `<section>.txt`.

Examples:
- `data/orientation/en/learning-materials/integration.html` ->
  `cards/orientation/integration/integration.txt`
- `data/orientation/en/learning-materials/integration/what-does-integration-mean.html` ->
  `cards/orientation/integration/what-does-integration-mean.txt`

## Question creation rules

### Card format (required)

Each card must use this pipe-separated format:

```
Question|Category|Type|Option1|Option2|Option3|Option4||CorrectAnswerFlags|Type
```

Field definitions:
- Question: clear, straightforward question text (Swedish only).
- Category: page title from the Learning materials tree (exact match).
- Type: always `2`.
- Option1-4: four answer choices (Swedish only).
- Empty field: always a double pipe `||`.
- CorrectAnswerFlags: binary flags with exactly one `1` (e.g., `0 1 0 0`).
- Type (again): always `2`.

### Core requirements

- Swedish only: all questions and options must be in Swedish.
- Single correct answer only: exactly one correct option per card.
- Exactly four options: no more, no fewer.
- Clear and unambiguous: avoid tricky phrasing or multiple interpretations.
- Challenging difficulty: test understanding, not only trivial recall.
- Factual accuracy: every question must be supported by the source material.
- High-quality distractors: wrong answers must be realistic and non-obvious
  (see "Distractor design" below).
- Simple language: clear, direct Swedish without unnecessary complexity.

### Distractor design (wrong answers must be plausible)

Bad wrong answers make the right answer "pop out" even if the learner doesn't
know the material. Avoid childish, absurd, or obviously off-topic distractors
that can be eliminated without knowing the content.

Goal: a learner who is unsure should have to think. A learner who knows the
material should still be confident which one is correct.

#### Rules of thumb

- Same "kind" of answer: all four options must belong to the same semantic
  category (all are institutions, all are time periods, all are policies, all
  are places, etc.).
- Same specificity: match the granularity of the correct answer. Don't mix
  a precise option ("järnvägar") with a vague one ("samhället förbättrades").
- Same grammar: keep options parallel (same part of speech, number, and form).
- Similar length: avoid one option being much longer/shorter or unusually
  detailed, which makes it feel "more correct".
- Avoid "test-taking hacks": no "alla ovanstående", "inget av ovanstående", or
  options that are just negations ("inte ...") unless every option follows the
  same pattern.
- No jokes, memes, or profanity: distractors must read like serious exam
  answers.
- No "obvious absurdity": avoid options that are clearly impossible or
  unrelated to the topic unless the question explicitly tests that (rare).
- No anachronisms: for historical questions, avoid technology, institutions,
  or terms that did not exist in that era.
- No "tell-tale" markers: avoid "alltid", "aldrig", "bara", "helt", "ingen",
  "alla", or exaggerated wording unless the source itself is absolute.
- Avoid overlapping answers: distractors must be clearly wrong; don't include
  two options that could both be defended as correct.

#### Ways to generate good distractors

Pick distractors that are "near misses" (close enough to be tempting) while
still wrong for this question.

- Same topic, wrong detail:
  - correct: "Riksdagen"
  - distractors (examples; verify against the source): "Regeringen",
    "Presidenten", "Högsta domstolen"
- Swap within a known set (but keep only one correct):
  - if the correct answer is one branch of government, use other branches,
    not random objects.
- Numbers/dates:
  - use close-by numbers (e.g., 18/20/21 instead of 1/100/1000) and keep the
    same units (years, %, euros).
- Terms that learners confuse:
  - use common misconceptions or similar-looking concepts (e.g., "kommun" vs
    "landskap", "riksdag" vs "regering") as distractors.
- True statements, wrong for the question:
  - a distractor can be factually true in general, but not the answer to this
    specific question (e.g., true for another era, another authority, another
    definition).

#### Distractor patterns by question type

- Definitions ("Vad betyder X?"):
  - use nearby concepts and common confusions (X vs Y), not unrelated words.
- Responsibility ("Vem ansvarar för ...?"):
  - use other realistic authorities at the same level (kommun vs statlig
    myndighet vs region/landskap), but ensure only one fits the described duty.
- Time/era ("När hände ...?"):
  - use nearby years/decades and keep the same format (e.g., four-digit years).
- Process/requirements ("Vilket krav gäller ...?"):
  - use realistic-sounding requirements that are wrong by one key condition
    (wrong age, wrong duration, wrong document).

#### Quick sanity checks for distractors

Before accepting a card, ask:
- Would someone who hasn't read the page be able to eliminate 2-3 options just
  because they are silly or unrelated?
- Do the wrong options look like something that could plausibly appear in the
  same textbook/lesson?
- Are the options comparable (same style, length, and specificity)?
- Is there exactly one best answer given the source wording?

#### Micro-example (structure, not content)

DON'T (one plausible + three nonsense):
- [Question]
  - [Correct option]
  - [Unrelated object]
  - [Impossible event]
  - [Joke/meme]

DO (all four options plausible; only one correct):
- [Question]
  - [Correct option]
  - [Plausible near-miss #1]
  - [Plausible near-miss #2]
  - [Plausible near-miss #3]

### Length limits (Kahoot import)

Kahoot enforces strict length limits, but the exact limits can vary by template
and import path. To stay safe, keep text short:

- Target answer length: <= 70 characters per option.
- Target question length: <= 120 characters.

If an option is a long definition, shorten it to a compact phrasing that
preserves the core meaning.

### Standalone question rules (no source references)

Questions must be standalone. Users do not see the chapter or source.

Forbidden in the question stem (examples of Swedish substrings):
- "enligt"
- "i texten"
- "i kapitlet"
- "i avsnittet"
- "i materialet"
- "i pdf:en"
- "beskrivningen"
- "uppgifterna"
- "informationen"

Allowed exceptions:
- Explicit references to named laws, regulations, or authorities, for example:
  - "enligt arbetstidslagen"
  - "enligt FPA/Migri/Statistikcentralen"
- Avoid vague attributions like "enligt experter" or "enligt uppgifter".

Rewrite rules for source-free questions:
- Replace any "enligt ... / i texten ..." phrasing with a neutral question.
- If the source is time-qualified (e.g., "i dag", "numera"), keep that time cue.
- If the source cites a specific law or authority, include it explicitly.

DON'T (source-bound; Swedish examples):
- Vilken sektor sysselsatter flest i Finland enligt uppgifterna?
- Vad galler for overtid enligt beskrivningen?
- Hur lang bor ett cv vara enligt texten?

DO (standalone; Swedish examples):
- Vilken sektor sysselsatter flest i Finland i dag?
- Vad avses med overtid enligt arbetstidslagen?
- Hur lang bor ett cv vara?

Additional DO / DON'T examples:

DON'T:
- Vad blev den overgripande trenden for arbeten i Finland enligt kapitlet?
- Nar upphor laroplikten enligt kapitlet?
- Vilket mal med utbildningen blev viktigare i borjan av 1900-talet enligt texten?

DO:
- Vad blev den overgripande trenden for arbeten i Finland under 1900-talet?
- Nar upphor laroplikten i Finland?
- Vilket utbildningsmal blev viktigare i borjan av 1900-talet?

### Coverage and organization rules

- Generate a maximum number of cards: convert virtually every fact, date,
  name, concept, and detail into a question.
- "Every fact becomes a card" is the guiding principle; more cards is better.
- Cover all important topics and concepts thoroughly.
- Each output file contains only flashcard lines (no headings or commentary).
- Keep all questions in a file tied to the page named in the Category field.

### Format examples (Swedish)

```
Vilket organ stiftar lagar i Finland?|Finland's system of governance|2|Presidenten|Regeringen|Riksdagen|Hogsta domstolen||0 0 1 0|2
Hur manga platser finns det i Finlands riksdag?|Finland's system of governance|2|150|200|250|300||0 1 0 0|2
```

### Final quality check

- Ensure no forbidden substrings appear in question stems.
- Confirm four options per card and exactly one correct flag.
- Ensure distractors are plausible (same category, no absurd outliers).
- Verify double-pipe separator `||` and trailing `|2` are present.
