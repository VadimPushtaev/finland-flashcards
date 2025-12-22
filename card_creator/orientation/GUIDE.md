# Citizenship Exam Topic Mapping (Orientation Materials)

This guide maps the exam topic areas (as summarized in `news/all-we-know.md`)
to specific source files in the orientation materials crawl under
`data/orientation/en/`. Use this when selecting sources for question
generation.

Sources:
- Exam topic list: `news/all-we-know.md`
- Orientation crawl overview: `data/orientation/README.md`

## Orientation vs orientation_guide (important)

- `orientation` (this guide): the *website-based* civic orientation materials we scraped under
  `data/orientation/` (yhteiskuntaorientaatio.fi). Output decks belong under `cards/orientation/` (by category).
- `orientation_guide` (legacy): the *single PDF textbook* `data/orientation_guide.pdf` with its own workflow under
  `card_creator/orientation_guide/` and per-subchapter decks under `cards/orientation_guide/`.

These two pipelines are independent; `cards/orientation/` has nothing to do with `cards/orientation_guide/`.

## Scope and source rules

- Use the English learning materials under `data/orientation/en/learning-materials/`
  as the primary question sources.
- Use `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/` as
  section-level overviews to frame question coverage.
- Avoid trainer guides and site meta pages (e.g., `data/orientation/en/kouluttajan-opas.html`,
  `data/orientation/en/about-the-site/`) as direct question sources.

## Orientation learning materials structure (index)

Learning materials categories (entry pages):
- `data/orientation/en/learning-materials/integration.html`
- `data/orientation/en/learning-materials/people-and-culture.html`
- `data/orientation/en/learning-materials/living-in-finland.html`
- `data/orientation/en/learning-materials/work.html`
- `data/orientation/en/learning-materials/education-and-training.html`
- `data/orientation/en/learning-materials/families.html`
- `data/orientation/en/learning-materials/healt-and-wellbeing.html`
- `data/orientation/en/learning-materials/society-and-civic-participation.html`
- `data/orientation/en/learning-materials/laws-and-justice.html`
- `data/orientation/en/learning-materials/finnish-history.html`

Section overviews (orientation material "osio" pages):
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-1-kotoutuminen.html` (integration)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-2-ihmiset-ja-kulttuuri.html` (people and culture)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-3-arki.html` (everyday life)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-4.-tyo.html` (work)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-5-opiskelu-ja-koulutus.html` (education and training)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-6-perheet.html` (families)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-7-terveys-ja-hyvinvointi.html` (health and wellbeing)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-8-yhteiskunta-ja-vaikuttaminen.html` (society and civic participation)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-9-lait-ja-oikeus.html` (laws and justice)
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-10-suomen-historiaa.html` (history)

## Topic-to-source mapping

Each topic below is an exam topic. "Primary sources" should be used for
question generation. "Overview sources" can be used to ensure full
coverage and to identify question angles.

### 1) How Finnish society functions

Primary sources:
- `data/orientation/en/learning-materials/society-and-civic-participation/finlands-system-of-governance.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/democracy.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/elections-in-finland.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/finnish-political-parties.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/ways-of-civic-participation.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/association-activities.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/media.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/business-and-economy.html`
- `data/orientation/en/learning-materials/living-in-finland/dealing-with-authorities.html`
- `data/orientation/en/learning-materials/integration/key-characteristics-of-finnish-society.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-8-yhteiskunta-ja-vaikuttaminen.html`

### 2) Key societal principles

Primary sources:
- `data/orientation/en/learning-materials/people-and-culture/values-of-finnish-society.html`
- `data/orientation/en/learning-materials/people-and-culture/culture-and-social-norms.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/democracy.html`
- `data/orientation/en/learning-materials/laws-and-justice/equality-and-non-discrimination.html`
- `data/orientation/en/learning-materials/integration/key-characteristics-of-finnish-society.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-2-ihmiset-ja-kulttuuri.html`
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-8-yhteiskunta-ja-vaikuttaminen.html`

### 3) Individual rights and obligations

Primary sources:
- `data/orientation/en/learning-materials/laws-and-justice/the-individuals-rights-and-obligations.html`
- `data/orientation/en/learning-materials/laws-and-justice/the-finnish-legal-system.html`
- `data/orientation/en/learning-materials/laws-and-justice/the-legal-process.html`
- `data/orientation/en/learning-materials/laws-and-justice/crimes.html`
- `data/orientation/en/learning-materials/laws-and-justice/equality-and-non-discrimination.html`
- `data/orientation/en/learning-materials/work/laws-and-regulations-at-work.html`
- `data/orientation/en/learning-materials/work/occupational-safety-and-health.html`
- `data/orientation/en/learning-materials/work/issues-at-work.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-9-lait-ja-oikeus.html`
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-4.-tyo.html`

### 4) Values and norms in Finnish society

Primary sources:
- `data/orientation/en/learning-materials/people-and-culture/values-of-finnish-society.html`
- `data/orientation/en/learning-materials/people-and-culture/culture-and-social-norms.html`
- `data/orientation/en/learning-materials/people-and-culture/celebrations-and-traditions.html`
- `data/orientation/en/learning-materials/people-and-culture/religion-religiosity-and-being-non-religious.html`
- `data/orientation/en/learning-materials/people-and-culture/food-culture-and-eating-habits.html`
- `data/orientation/en/learning-materials/people-and-culture/the-finnish-population.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-2-ihmiset-ja-kulttuuri.html`

### 5) Key legislation

Primary sources:
- `data/orientation/en/learning-materials/laws-and-justice/the-finnish-legal-system.html`
- `data/orientation/en/learning-materials/laws-and-justice/the-legal-process.html`
- `data/orientation/en/learning-materials/laws-and-justice/crimes.html`
- `data/orientation/en/learning-materials/laws-and-justice/residence-permits-and-citizenship.html`
- `data/orientation/en/learning-materials/laws-and-justice/equality-and-non-discrimination.html`
- `data/orientation/en/learning-materials/work/laws-and-regulations-at-work.html`
- `data/orientation/en/learning-materials/work/occupational-safety-and-health.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-9-lait-ja-oikeus.html`
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-4.-tyo.html`

### 6) Fundamental and human rights

Primary sources:
- `data/orientation/en/learning-materials/laws-and-justice/the-individuals-rights-and-obligations.html`
- `data/orientation/en/learning-materials/laws-and-justice/equality-and-non-discrimination.html`
- `data/orientation/en/learning-materials/laws-and-justice/the-finnish-legal-system.html`
- `data/orientation/en/learning-materials/society-and-civic-participation/democracy.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-9-lait-ja-oikeus.html`

### 7) Equality and gender equality

Primary sources:
- `data/orientation/en/learning-materials/laws-and-justice/equality-and-non-discrimination.html`
- `data/orientation/en/learning-materials/families/equality-and-gender-norms-in-families-and-society.html`
- `data/orientation/en/learning-materials/families/different-types-of-families.html`
- `data/orientation/en/learning-materials/families/marriage-and-common-law-relationships.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-6-perheet.html`
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-9-lait-ja-oikeus.html`

### 8) Finnish culture

Primary sources:
- `data/orientation/en/learning-materials/people-and-culture/culture-and-social-norms.html`
- `data/orientation/en/learning-materials/people-and-culture/celebrations-and-traditions.html`
- `data/orientation/en/learning-materials/people-and-culture/food-culture-and-eating-habits.html`
- `data/orientation/en/learning-materials/people-and-culture/religion-religiosity-and-being-non-religious.html`
- `data/orientation/en/learning-materials/people-and-culture/the-finnish-population.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-2-ihmiset-ja-kulttuuri.html`

### 9) Finnish history

Primary sources:
- `data/orientation/en/learning-materials/finnish-history.html`
- `data/orientation/en/learning-materials/finnish-history/main-periods-of-finnish-history-1-finland-as-a-part-of-sweden-and-russia.html`
- `data/orientation/en/learning-materials/finnish-history/main-periods-of-finnish-history-2-independent-finland.html`

Overview sources:
- `data/orientation/en/yhteiskuntaorientaation-oppimateriaali/osio-10-suomen-historiaa.html`

## Question creation rules

### Card format (required)

Each card must use this pipe-separated format:

```
Question|Category|Type|Option1|Option2|Option3|Option4||CorrectAnswerFlags|Type
```

Field definitions:
- Question: clear, straightforward question text (Swedish only).
- Category: subject/topic (e.g., History, Culture, Politics, Economy, Education, Society, Law).
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
- Plausible distractors: wrong answers should be realistic but clearly incorrect.
- Simple language: clear, direct Swedish without unnecessary complexity.

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
- Vilken sektor sysselsätter flest i Finland enligt uppgifterna?
- Vad gäller för övertid enligt beskrivningen?
- Hur lång bör ett cv vara enligt texten?

DO (standalone; Swedish examples):
- Vilken sektor sysselsätter flest i Finland i dag?
- Vad avses med övertid enligt arbetstidslagen?
- Hur lång bör ett cv vara?

Additional DO / DON'T examples:

DON'T:
- Vad blev den övergripande trenden för arbeten i Finland enligt kapitlet?
- När upphör läroplikten enligt kapitlet?
- Vilket mål med utbildningen blev viktigare i början av 1900-talet enligt texten?

DO:
- Vad blev den övergripande trenden för arbeten i Finland under 1900-talet?
- När upphör läroplikten i Finland?
- Vilket utbildningsmål blev viktigare i början av 1900-talet?

### Coverage and organization rules

- Generate a maximum number of cards: convert virtually every fact, date,
  name, concept, and detail into a question.
- "Every fact becomes a card" is the guiding principle; more cards is better.
- Cover all important topics and concepts thoroughly.
- Organize output by subchapters with headings:
  - `# Subchapter X.Y: [Subchapter Title]`
- After each subchapter heading, include only the flashcard lines
  (no extra commentary).
- Use appropriate categories based on the content (e.g., History, Politics,
  Geography, Culture, Economy, Education, Society, Law).
- Each category maps to an output folder under `cards/orientation/` using a
  lowercase name, for example:
  - `History` -> `cards/orientation/history/`
  - `Politics` -> `cards/orientation/politics/`

### Format examples (Swedish)

```
Vilket organ stiftar lagar i Finland?|Politik|2|Presidenten|Regeringen|Riksdagen|Högsta domstolen||0 0 1 0|2
Hur många platser finns det i Finlands riksdag?|Politik|2|150|200|250|300||0 1 0 0|2
```

### Final quality check

- Ensure no forbidden substrings appear in question stems.
- Confirm four options per card and exactly one correct flag.
- Verify double-pipe separator `||` and trailing `|2` are present.
