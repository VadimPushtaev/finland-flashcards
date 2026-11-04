# Card Creation Progress Tracker

This document tracks which data sources have been converted into flashcards.

<!-- remaining-video-progress -->
Homebrew videos (2026-11-03): all **88 remaining subchapters in chapters 8–12** now have verified local previews, covering **3,730 exact Swedish/Russian body pairs** and **11:45:12** of video. Foreground pictures cover every narrated body pair; conservative within-episode visual diversity is **93.4%**. All five chapter audits and exported-card visual reviews passed. Whole-video listening, physical-device playback and user acceptance remain pending. See the [video index](../videos/homebrew/README.md) and [production completion record](../studio/production/remaining/completion.json). Flashcard selection and deck counts are unchanged by video production.

<!-- /remaining-video-progress -->

Homebrew preparation material: all twelve chapters have been curated as a
Swedish source-based reading collection in `data/homebrew/`. Track its source
selections and next steps in
[`wip/homebrew/PROGRESS.md`](../wip/homebrew/PROGRESS.md).

Homebrew sentence assessments: chapter 1, **Finland, befolkningen och språken**
(`hb-c01`), has all 213 body sentences across eight subchapters assessed for future
card selection in [`homebrew/assessments/`](homebrew/assessments/). The first 14
assessments in `hb-c01-lage` were retained; the remaining 199 were added across
`hb-c01-regioner`, `hb-c01-natur`, `hb-c01-arstider`, `hb-c01-befolkning`,
`hb-c01-sprak`, `hb-c01-folkgrupper`, and `hb-c01-flyttning`.

Homebrew cards (2026-10-31): chapter 1 now has **44 CORE cards in eight decks**,
covering all 48 selected CORE sentences. Related claims share a card where
appropriate. No existing Homebrew cards were reused and no selected candidates
remain blocked. CORE denotes study priority, not guaranteed exam coverage.

The [saved selection report](homebrew/selections/hb-c01-2026-10-31-core.json)
used the whole assessed collection at that generation (213 sentences): **CORE >=41:
48; SUPPORTING =40: 29; SKIP <40: 136**. Only CORE material was used for independent
questions. Assessments remain separate from these derived priorities.

| Subchapter | CORE sentences covered | Cards |
| --- | ---: | ---: |
| Finland i Norden | 8 | 6 |
| Landskap, regioner och städer | 9 | 8 |
| Natur och friluftsliv | 1 | 1 |
| Klimat och årstider | 2 | 2 |
| Befolkning och urbanisering | 4 | 4 |
| Nationalspråk och andra språk | 10 | 9 |
| Folkgrupper och urfolk | 9 | 9 |
| Ut- och invandring | 5 | 5 |
| **Total** | **48** | **44** |

Outputs: [Anki decks](../cards/homebrew/hb-c01/),
[card source records](homebrew/card_sources/), and
[eight Kahoot workbooks](../kahoot/homebrew/hb-c01/).
Reviewed Swedish source context and all answer choices; retained the 2023 frame
for population/language figures and recorded dated primary-source checks for
flagged claims in the source records. Validation passed for every deck's format,
exact category, source links, row hashes, and selected CORE primary sentences.
All questions/answers fit the 120/70-character limits (actual maxima: 99/62).
Reopened every exported workbook and checked all 44 questions, options,
20-second time limits, and correct-answer indices against the decks.

Homebrew chapter 2 (2026-10-31), **Finlands historia** (`hb-c02`): all **321 body
sentences across 13 subchapters** were individually assessed, with no existing
Chapter 2 assessments to reuse. Generated **57 new CORE cards in 12 subchapter
decks**, covering the 79 selected sentences. Related claims share cards, including
repeated school-reform and EU-accession passages; no previously generated cards
needed reuse. No selected candidate remains blocked.

The [Chapter 2 selection report](homebrew/selections/hb-c02-2026-10-31-core.json)
calibrates once against all 534 current assessments in 21 sections. Its thresholds
are **CORE >=46, SUPPORTING 42-45, SKIP <42**. Chapter 2 has **79 CORE, 44 SUPPORTING,
198 SKIP** sentences; the whole assessed collection has 87 / 64 / 383 respectively.
Equal scores stay together and no subchapter quotas were applied. Chapter 1's
existing cards retain their original selection report and were not reselected.

| Chapter 2 subchapter | Selected CORE sentences | New cards |
| --- | ---: | ---: |
| Förhistoria och medeltid | 0 | 0 |
| Svenskt styre, reformation och upplysning | 2 | 2 |
| Autonomin och industrialiseringen | 3 | 3 |
| Nationell identitet och demokratisering | 5 | 5 |
| Självständigheten och inbördeskriget | 2 | 2 |
| Republik och demokrati mellan krigen | 7 | 5 |
| Vinterkriget, fortsättningskriget och Lapplandskriget | 11 | 8 |
| Återuppbyggnad och kalla kriget | 7 | 5 |
| Välfärdsstatens framväxt | 15 | 10 |
| Utbildning för hela befolkningen | 4 | 2 |
| Från jordbruk till industri och informationssamhälle | 3 | 1 |
| Finland i EU och Nato | 12 | 9 |
| Ett föränderligt samhälle | 8 | 5 |
| **Total** | **79** | **57** |

The prehistory subchapter has no qualifying CORE candidates and no empty deck.
The selected-sentence counts above belong to their original sections; shared
learning points may be covered by a card in another Chapter 2 subchapter.

Outputs: [Chapter 2 decks and combined ALL.txt](../cards/homebrew/hb-c02/),
[source records](homebrew/card_sources/), and
[12 Kahoot workbooks](../kahoot/homebrew/hb-c02/).
Reviewed all questions and alternatives against their context. Dated primary-source
checks in the records resolve election wording, historical insurance coverage,
EU law, euro cash versus currency adoption, NATO assistance, and demographic
framing. In particular, the early accident-insurance card does not repeat the
source's implication that occupational diseases were covered by the 1895 law;
government legislative history dates that extension to 1925. The demographic
question tests a conditional financing relationship rather than asserting an
uninterrupted present-day decline in working-age numbers.

Validation passed for all 321 assessments, all 57 card rows and their exact
categories, source links, selected primary sentences, row hashes, and coverage of
all 79 CORE candidates. Questions/answers have maximum lengths of 101/67 characters
within the 120/70 limits. All 12 exported workbooks were reopened and their 57
questions, four options, time limits and correct-answer indices matched the decks.
The combined chapter deck has 57 rows in anthology order and passes
`make check-homebrew`; generated combined files are excluded from card counts.

Homebrew chapter 3 (2026-11-01, fixed-cutoff revision), **Kultur, värderingar och
traditioner** (`hb-c03`): reused all **520 current sentence assessments across
21 subchapters**. The permanent **CORE >=41, SUPPORTING =40, SKIP <40** policy
selects **145 CORE, 63 SUPPORTING and 312 SKIP** sentences. No assessment scores
were changed and no unrelated material was assessed or reclassified.

The [fixed-cutoff selection report](homebrew/selections/hb-c03-2026-11-01-fixed-core.json)
contains only the requested Chapter 3 assessments and scores. It selects 67 more
CORE sentences than the earlier report. Generation added **51 new cards**, revised
**one existing Christmas-date question**, and kept **60 original cards and source
records unchanged**. Chapter 3 now has **112 cards in all 21 subchapter decks**.
Together with the existing Chapter 2 independence-date card, these cover all
**145 selected CORE sentences**. No selected candidates remain blocked.
CORE denotes study priority, not guaranteed exam coverage.

| Chapter 3 subchapter | Selected CORE sentences | Added cards | Total cards |
| --- | ---: | ---: | ---: |
| Värderingar och olikheter | 10 | 2 | 9 |
| Tillit, jämlikhet och självständighet | 6 | 3 | 4 |
| Seder, personligt utrymme och samtal | 7 | 6 | 6 |
| Hälsningar, punktlighet och besök | 13 | 6 | 7 |
| Religioner och religionslöshet | 20 | 6 | 16 |
| Religion i vardagen och högtiderna | 15 | 2 | 9 |
| Högtider och flaggdagar | 2 | 1 | 1 |
| Nyår, trettondag och vintertraditioner | 3 | 2 | 3 |
| Påsk och Kristi himmelsfärdsdag | 2 | 0 | 2 |
| Valborg, första maj och morsdag | 3 | 0 | 3 |
| Midsommar | 4 | 0 | 2 |
| Alla helgons dag och farsdag | 4 | 1 | 3 |
| Självständighetsdagen och julen | 4 | 0 | 1 |
| Runeberg, kvinnodagen och Minna Canths dag (19 mars) | 7 | 1 | 6 |
| Årets andra traditioner | 4 | 4 | 4 |
| Fester genom livet | 10 | 5 | 8 |
| Matkultur och matvanor | 6 | 3 | 6 |
| Vardagsmat och måltider | 8 | 3 | 7 |
| Festmat och drycker | 5 | 1 | 4 |
| Bastukultur | 7 | 2 | 6 |
| Kulturliv | 5 | 3 | 5 |
| **Total** | **145** | **51** | **112** |

Of the 67 newly eligible sentences, 64 are covered by the new questions (several
related claims share a card). Two reuse questions already teaching those claims:
`hb-c03-u0058-s002` is covered by the school Christmas-celebration question in
`hb-c03-religiositet`, and `hb-c03-u0153-s001` by the bonfire-tradition question in
`hb-c03-midsommar`. Bonfire location is incidental to that learning point and was
not turned into a second question. The Christmas-date question was expanded to
cover `hb-c03-u0082-s005` (usual gift-giving on Christmas Eve), retaining its date
choices and answer position. Existing references to ordinary queues and to
livsåskådningskunskap were supporting context in older cards; new questions now
explicitly teach those newly eligible learning points rather than counting an
incidental source reference as sufficient coverage.

Cross-section coverage includes the liberty and education-access claims in
`hb-c03-tillit` covered by cards in `hb-c03-varderingar`, privacy in `hb-c03-seder`
covered by the privacy question in `hb-c03-tillit`, and personal belief despite
limited participation in `hb-c03-religiositet` covered by the affiliation-and-belief
question in `hb-c03-religion`. The two definitions of secularization share one
existing card. The existing Chapter 2 question
"Vilket datum förklarade sig Finland självständigt?" in
[`hb-c02-sjalvstandighet.txt`](../cards/homebrew/hb-c02/hb-c02-sjalvstandighet.txt)
continues to cover `hb-c03-u0081-s001` and `hb-c03-u0081-s002`; its row hash remains
`0f27b0515c8259aec00bedee3b4b76a906c30f6ff062a0c8f1a13486eb3243f2`.
No duplicate independence-date card was added.

The [original Chapter 3 report](homebrew/selections/hb-c03-2026-11-01-core.json)
is retained as historical provenance for the unchanged cards: the first pass
selected 78 sentences at a moving cutoff of 45 and created 61 cards in 18 decks.
Those former cutoffs and collection-wide counts are not the current policy.
New and revised rows reference the fixed-cutoff report; retained rows keep their
original report and hashes.

Outputs: [Chapter 3 decks and combined ALL.txt](../cards/homebrew/hb-c03/),
[sentence assessments](homebrew/assessments/),
[card source records](homebrew/card_sources/), and
[21 Kahoot workbooks](../kahoot/homebrew/hb-c03/).
Reviewed full source context and all four options for each new/revised question.
Dated primary-source checks in the source records resolve registration and school
religion, baptism costs, prayer during work breaks, school holidays, confirmation,
Prometheus camps, daycare meals, drinking water, alcohol retail, pool-sauna rules,
National Museum access and music enrollment/admission. Cards qualify cultural
customs as common rather than compulsory or uniform. The ceremony-cost question
uses the verified free church-baptism case without promising all ceremony-related
services are free. Tap-water wording concerns normal public-network supply and
retains local warnings; daycare wording concerns a usual full day; swimwear rules
are qualified by venue. The National Museum card tests its cultural-history role
without promising current admission while its building is closed. Music-course
access retains enrollment conditions, and the entrance-test question is conditional
because some music schools admit students without a test.

The earlier reviews of constitutional equality, religious freedom, clergy, church
tax and diaconal access remain in the retained records. Minority instruction keeps
legal conditions; religious teaching is distinguished from observance. Higher
education eligibility means the right to apply, not automatic admission. Hunting
wording allows hunting rights or permission. School-meal wording remains limited
to basic education. Alcohol questions do not import exact age or strength limits
absent from the anthology. Church-membership comparisons retain their 2023 frame.

Validation passed for all 520 reused assessments, all 112 card rows and exact
categories, current assessment/source hashes, selected primary sentences, source
references and row hashes. Coverage checks account for all 145 CORE sentences,
including the reused Chapter 2 card. All 60 unchanged original rows and their
provenance were compared against the pre-revision snapshot. Maximum question and
answer lengths are **99/69** characters, within 120/70 limits. The 112 correct
answers are balanced **28/28/28/28** across the four positions. All 21 exported
workbooks were reopened and their questions, options, 20-second limits and correct
answer indices matched the decks. All 14 card/export/combiner tests passed. The
combined chapter deck contains 112 rows in source order and the freshness check
passed for all three chapters with cards.

Homebrew chapter 4 replacement generation (2026-11-03), **Demokrati, förvaltning
och påverkan** (`hb-c04`): deleted all **239 earlier chapter questions** and
generated **75 new CORE cards in 13 subchapters**, as explicitly requested.
Reused all **753 current sentence assessments without changing any assessment
file**. The fixed **CORE >=41, SUPPORTING =40, SKIP <40** cutoffs still select
**110 CORE (14.6%), 69 SUPPORTING and 574 SKIP** sentences.

The new cards cover **105 selected sentences**; **four unchanged equivalent
questions in Chapters 2 and 3 cover the remaining five**, for coverage of all
110 CORE sentences. Repeated legislative powers, election cycles, municipal and
EU representation, and expression rights share questions. Broad sentences listing
several institutions, branches, freedoms or voting conditions can be covered
jointly by several focused questions. There are **no blocked CORE candidates**.

| Chapter 4 subchapter | Replacement cards |
| --- | ---: |
| Demokrati och folkstyre | 4 |
| Grundlagen och maktfördelningen | 4 |
| Riksdagens uppgifter | 6 |
| Regeringen och parlamentarismen | 7 |
| Republikens president | 4 |
| Kommuner och välfärdsområden | 10 |
| EU och internationellt samarbete | 8 |
| Val, valhemlighet och proportionellt valsätt | 12 |
| Rösträtt och valbarhet | 9 |
| Politiska partier och ideologier | 2 |
| Partierna i riksdagsvalet 2023 | 0 |
| Medborgarengagemang och påverkan | 4 |
| Föreningar och frivilligverksamhet | 2 |
| Medier, pressfrihet och publicistiskt ansvar | 3 |
| Källkritik och mediekunnighet | 0 |
| **Total** | **75** |

The two sections without CORE candidates have no deck, source-map placeholder or
Kahoot workbook; their old outputs were removed. The other 13 decks and source
maps were replaced in full. No earlier Chapter 4 row was retained. The combined
[chapter ALL.txt](../cards/homebrew/hb-c04/ALL.txt) now contains 75 rows in anthology
order. See the [generation selection](homebrew/selections/hb-c04-2026-11-03-core-redo.json)
and [coverage and verification review](homebrew/reviews/hb-c04-2026-11-03-core-redo.json).

Reviewed Swedish context and all four options for every card. Dated primary-source
checks resolve current institutional responsibilities, voting conditions,
demonstration notification, association and expression rights, privacy,
initiatives, political discrimination, same-sex marriage and Yle's public-service
identity. Questions preserve age/citizenship/residence qualifications, the
mainland scope of proportional parliamentary elections, approximate seat
proportionality, citizenship from birth rather than birthplace, and notification
rather than permission for demonstrations. Incidental numerical and procedural
details do not become extra questions merely because their sentence is CORE.

All **14 existing card/export/combiner tests passed**. Validated all 75 actual
deck rows and source records, including exact categories, 120/70 character limits,
source ordering, CORE primaries, scores, row hashes and current selection/source
fingerprints. Maximum question/answer lengths are **110/66** characters. Correct
positions are balanced **19/19/19/18**. All **13 real Kahoot workbooks** were
reopened and their questions, options, 20-second limits and correct answers matched
the decks. Combined-deck freshness checks passed for all four chapters with cards.
Hash comparison confirmed **631 unrequested files**, including all 15 Chapter 4
assessment files, unchanged. No commit or push was requested for this replacement.

Homebrew chapter 4 strict reassessment (2026-11-03), **Demokrati, förvaltning och
påverkan** (`hb-c04`): reviewed all **753 body sentences in 15 subchapters** again
at the user's request. Current assessments yield **110 CORE (14.6%), 69 SUPPORTING
and 574 SKIP**, below the requested chapter-specific ceiling of 15% (at most 112
sentences). The permanent formula and cutoffs remain **CORE >=41, SUPPORTING =40,
SKIP <40**. No other chapter was assessed or recalibrated.

The first full strict pass yielded 114 CORE sentences. A second review of
borderline concepts treated government-programme and majority-government
terminology as secondary, and direct-democracy examples and the broad purpose of
parties as supporting context. Central institutions, major rights and essential
voting rules retain priority; general advice, examples, party profiles and
association administration usually do not. Checklist questions remain source
guidance prompts rather than factual answers supplied by the text. Exam relevance
is an editorial estimate, not verified exam coverage. Risk and confidence remain
independent review flags.

See the [current fixed-cutoff selection](homebrew/selections/hb-c04-2026-11-03-strict-reassessment.json)
and [reassessment review](homebrew/reviews/hb-c04-2026-11-03-strict-reassessment.json).
Validation passed for all 753 requested sentences, including schema, source
freshness, ordering and references. Hash checks confirmed **664 unrequested files**
unchanged. All 753 assessments were individually reviewed; none was reused without
review.

At this assessment stage, the 239 existing cards and Kahoot exports were preserved;
the replacement generation above subsequently removed and regenerated them. Their
original selection describes the earlier generation below. Its exact
assessment files are preserved in the
[historical assessment archive](homebrew/reviews/hb-c04-2026-11-03-before-reassessment/)
so their recorded hashes remain auditable. The older generation validation is
historical and does not imply those cards use the current assessment selections.

Homebrew chapter 4 initial generation (2026-11-03), **Demokrati, förvaltning och påverkan** (`hb-c04`):
individually assessed all **753 body sentences in 15 subchapters**; there were no
existing Chapter 4 assessments or decks to reuse. All unrequested source,
assessment and card files remain unchanged. The permanent **CORE >=41,
SUPPORTING =40, SKIP <40** thresholds yield **403 CORE, 127 SUPPORTING and
223 SKIP** sentences. No collection-wide recalibration or percentage quota was used.

The [saved selection](homebrew/selections/hb-c04-2026-11-03-core.json) records the
requested scope, original five ratings and source/assessment fingerprints.
Generated **239 new CORE cards across all 15 subchapters** and reused **four
existing cards**. Related claims and genuine repetitions share questions rather
than becoming paraphrase duplicates. These cover **401 selected CORE sentences**:
397 through the new cards and four through existing cards. **Two CORE candidates
remain blocked** for source correction; neither was silently dropped or demoted.
CORE is a study priority, not a promise of exam coverage.

| Chapter 4 subchapter | Selected CORE sentences | New cards |
| --- | ---: | ---: |
| Demokrati och folkstyre | 31 | 17 |
| Grundlagen och maktfördelningen | 7 | 5 |
| Riksdagens uppgifter | 20 | 12 |
| Regeringen och parlamentarismen | 24 | 12 |
| Republikens president | 8 | 7 |
| Kommuner och välfärdsområden | 22 | 16 |
| EU och internationellt samarbete | 32 | 22 |
| Val, valhemlighet och proportionellt valsätt | 44 | 28 |
| Rösträtt och valbarhet | 51 | 28 |
| Politiska partier och ideologier | 20 | 15 |
| Partierna i riksdagsvalet 2023 | 9 | 8 |
| Medborgarengagemang och påverkan | 38 | 22 |
| Föreningar och frivilligverksamhet | 20 | 15 |
| Medier, pressfrihet och publicistiskt ansvar | 45 | 18 |
| Källkritik och mediekunnighet | 32 | 14 |
| **Total** | **403** | **239** |

The [coverage and review record](homebrew/reviews/hb-c04-2026-11-03-core.json)
links every covered CORE ID to actual deck-row hashes and records reused rows and
blocked sentences. Reused cards are:

- `hb-c04-u0014-s004`: Chapter 3's constitutional equality question,
  "Vad innebär likhet inför lagen i Finland?"
- `hb-c04-u0031-s004`: Chapter 2's binding EU-law question,
  "Hur påverkar EU-medlemskapet Finlands lagstiftning?"
- `hb-c04-u0061-s001`: Chapter 2's EU-accession-year question (1995).
- `hb-c04-u0065-s001`: Chapter 2's NATO-accession-year question (2023).

The two accession assessments also identify their earlier Chapter 2 sentence
representatives. Reused decks and source records were preserved byte for byte.

Blocked CORE candidates, both score **42**:

- **`hb-c04-u0031-s003`** says Finnish and EU law cannot conflict. This absolute
  formulation cannot be taught as a factual guarantee: legal conflicts can arise,
  and the applicable EU-law primacy rules address them. The source does not state
  a precise primacy rule from which to build an honest source-based question.
  The separate, supported obligation to respect EU law is covered by the reused
  Chapter 2 question. Checked 2026-11-03 against
  [EUR-Lex's explanation of primacy](https://eur-lex.europa.eu/EN/legal-content/glossary/primacy-of-eu-law-precedence-supremacy.html).
- **`hb-c04-u0246-s004`** limits advertising-identification rules to content
  produced in Finland. KKV explicitly states that marketing directed to Finnish
  consumers is covered regardless of where the content was made. The supported
  principle that commercial content must be recognizable has its own card; the
  opposite jurisdiction assertion remains blocked. Checked 2026-11-03 against
  [KKV's influencer-marketing guidance, section 1.3](https://www.kkv.fi/sv/konsumentarenden/information-och-anvisningar-till-foretag/konsumentombudsmannens-riktlinjer/influerarmarknadsforing-i-sociala-medier/).

Dated primary-source checks are stored in the source records. Important wording
qualifications include free parliamentary mandates, presidential confirmation
rather than an absolute veto, government confidence rather than a second
ministerial appointment, EU co-legislation rather than every EU decision,
municipal versus county duties, Helsinki/Åland exceptions, lawful voting
assistance, one-country EU voting, nationality/residence/register cutoffs,
statutory candidacy exclusions, and the single-member Åland constituency.
Municipal counts and undated demographic voting trends were not added as extra
questions. Dated EU/NATO/MEP figures keep their actual historical or term frame.

Initiatives distinguish proposals from binding decisions. Citizen initiative
wording does not claim one person can formally launch an initiative alone;
current guidance requires at least five responsible voting-age Finnish citizens.
EU initiatives retain national signature minima as well as the million/seven-state
threshold. A municipal youth council may be an equivalent participation group.
Demonstrations require notification rather than political permission, with the
ordinary 24-hour rule and statutory exceptions. Association cards distinguish
legal personality from officers' own liability, membership authority from board
management, and chair domicile exceptions from the source's overbroad vice-chair
claim. Unemployment guidance is framed as seeking case-specific advice, not a
universal prior-permission requirement for volunteering.

Media cards preserve editorial independence, distinguish ONM ethics from court
punishments, protect privacy without exempting all public figures, and do not
portray Yle taxation as an unrestricted all-persons rule. Media literacy covers
independent corroboration, evidence, motives, dates and misleading image/video
context; realistic synthetic content is possible without claiming every fake is
undetectable. Each question and all four choices were reviewed for a single
supported answer; three redundant draft questions were merged into focused cards.

Outputs: [subchapter decks and combined ALL.txt](../cards/homebrew/hb-c04/),
[assessments](homebrew/assessments/), [source records](homebrew/card_sources/), and
[15 Kahoot workbooks](../kahoot/homebrew/hb-c04/). Validation passed for all
753 assessments and all 239 cards, including exact Swedish categories, source
links, current fingerprints, selected CORE primaries, source-order and row hashes.
All 403 selected sentences have an explicit covered/reused/blocked disposition.
Maximum question/answer lengths are **109/70** characters, within 120/70 limits.
Correct positions are distributed **60/60/60/59** and shuffled in source order.
All 15 actual workbooks were reopened: every question, four choices, 20-second
limit and answer index matched its TXT row. All **14 card/export/combiner tests**
passed. Combined Chapter 4 has 239 rows in anthology order; freshness checks passed
for all four chapters with cards. Hash comparison confirmed **582 unrelated files**
unchanged. Generation did not request a commit or push.

Homebrew chapter 5 (2026-11-04), **Grundläggande rättigheter, jämlikhet och
skyldigheter** (`hb-c05`): individually assessed all **469 body sentences in 15
subchapters**. No Chapter 5 assessments or decks existed to reuse. With the fixed
**CORE >=41, SUPPORTING =40, SKIP <40** thresholds, the requested scope contains
**164 CORE, 36 SUPPORTING and 269 SKIP** sentences. No percentage quota or
collection-wide recalibration was used. Exam relevance remains an editorial
estimate, not a claim of guaranteed exam coverage.

Generated **79 new CORE cards across all 15 subchapters** and reused **14 unchanged
equivalent questions from Chapters 1–4**. Together these cover **162 selected CORE
sentences**; two source claims remain blocked for correction. New cards link to
135 selected sentences and reused cards to 28, with one sentence jointly covered
by both. Lists of rights can be covered jointly by focused questions; source
sentence counts are distinct from card counts.

| Chapter 5 subchapter | New cards |
| --- | ---: |
| Grundläggande och mänskliga rättigheter | 3 |
| Grundläggande friheter och rättigheter | 12 |
| Jämställdhet mellan könen | 8 |
| Likabehandling och diskriminering | 3 |
| Rasism och hatbrott | 2 |
| Hjälp vid diskriminering | 1 |
| Språkliga minoriteter och urfolk | 5 |
| Rättigheter för personer med funktionsnedsättning | 4 |
| Barns rättigheter | 8 |
| Religionsfrihet och barnets religion | 2 |
| Sexuella rättigheter och kroppslig integritet | 11 |
| Självbestämmande och reproduktiv hälsa | 3 |
| Individens skyldigheter | 5 |
| Rättigheter och skyldigheter som följer av medborgarskap | 8 |
| Försvarsplikt, beväringstjänst och civiltjänst | 4 |
| **Total** | **79** |

The [saved selection](homebrew/selections/hb-c05-2026-11-04-core.json) preserves
all assessment fields and source/assessment fingerprints. The
[coverage and verification review](homebrew/reviews/hb-c05-2026-11-04-core.json)
identifies every new or reused question and both blocked candidates:

- **`hb-c05-u0076-s001`** names Regionförvaltningsverket as a current supervisory
  contact. The former agencies ceased operating on 1 January 2026. The source
  needs a current authority reference before this specific claim can be taught.
- **`hb-c05-u0198-s001`** gives a conscription age range of 18–60. The current
  statutory upper limit is 65, subject to transitional rules. The archived range
  has no historical date permitting a faithful dated question. General defence
  and service obligations are covered separately; this range is not taught.

Both retain their CORE scores. Swedish source text and unrequested assessments
were preserved. Repeated equality, religion, expression, privacy, assembly,
association, same-sex marriage, national-language and Åland claims reuse existing
questions. Consent examples, bodily autonomy, child voice, care duties and
capacity-based access to abortion and contraception are consolidated. The EU
citizenship sentence supports two materially different new questions: electoral
participation and access to work.

Primary-source checks dated 2026-11-04 preserve current qualifications on lawful
movement, public-document secrecy, social-service eligibility, indirect
discrimination, pregnancy and parenthood, reasonable accommodation, child consent
to religious affiliation, minors' capacity and privacy, sexual-offence thresholds,
genital-mutilation safeguards, abortion on request, witness privileges and
conscription. Forced marriage is not described as requiring a separately named
criminal offence. Government proposal HE 129/2026 is used for its description of
current equality law, not as evidence that proposed amendments are enacted.

Validated all 469 assessments and 79 actual cards/source records, including exact
categories, selected CORE primaries, scores, source/selection fingerprints,
source order, distinct answer choices and row hashes. Maximum question/answer
lengths are **115/70** characters; correct positions are balanced **20/20/20/19**.
All **15 real Kahoot workbooks** were reopened and their questions, options,
20-second limits and correct answers matched the TXT decks. All **14 existing
card/export/combiner tests passed**. The combined
[chapter ALL.txt](../cards/homebrew/hb-c05/ALL.txt) contains 79 rows in anthology
order. Hash comparison confirmed **700 unrequested files unchanged**, and the
15 new assessment files stayed unchanged after selection. Generation did not
request a commit or push.

## 1. Main Textbook (PRIMARY SOURCE)

**Source:** `data/orientation_guide.pdf`

This is the main source material. Create a **separate card file for each subchapter**.

**Target location:** `cards/orientation_guide/`

### Chapter 1 — Finland och den finska kulturen

- [x] Finlands geografi och klimat → `cards/orientation_guide/1.1_finlands_geografi_och_klimat.txt`
- [x] Finlands befolkning → `cards/orientation_guide/1.2_finlands_befolkning.txt`
- [x] Hurudana är finländarna? → `cards/orientation_guide/1.3_hurudana_ar_finlandarna.txt`
- [x] Huvuddragen i Finlands historia → `cards/orientation_guide/1.4_huvuddragen_i_finlands_historia.txt`
- [x] Finländsk kultur: kalender, fester och traditioner → `cards/orientation_guide/1.5_finlandsk_kultur_kalender_fester_och_traditioner.txt`

### Chapter 2 — Det finländska samhället

 - [x] Det finländska samhällets olika sektorer → `cards/orientation_guide/2.1_det_finlandska_samhallets_olika_sektorer.txt`
 - [x] Välfärdsstatens utveckling i Finland → `cards/orientation_guide/2.2_valfardssamhallets_utveckling_i_finland.txt`
 - [x] Finlands förvaltning → `cards/orientation_guide/2.3_finlands_forvaltning.txt`
 - [x] Finlands näringsliv och ekonomiska system → `cards/orientation_guide/2.4_finlands_naringsliv_och_ekonomiska_system.txt`

### Chapter 3 — Att flytta till och bo i Finland

- [x] Uppehållstillstånd och finskt medborgarskap → `cards/orientation_guide/3.1_uppehallstillstand_och_finskt_medborgarskap.txt`
- [x] Praktiska saker som är bra att känna till → `cards/orientation_guide/3.2_praktiska_saker_som_ar_bra_att_kanna_till.txt`
- [x] Grundläggande fakta om boende → `cards/orientation_guide/3.3_grundlaggande_fakta_om_boende.txt`
- [x] Integration i det nya hemlandet → `cards/orientation_guide/3.4_integration_i_det_nya_hemlandet.txt`

### Chapter 4 — Familjeliv och barn

- [x] Finländska familjer förr och nu → `cards/orientation_guide/4.1_finlandska_familjer_forr_och_nu.txt`
- [x] Äktenskap och samboende → `cards/orientation_guide/4.2_aktenskap_och_samboende.txt`
- [x] Många slag av familjer → `cards/orientation_guide/4.3_manga_slag_av_familjer.txt`
- [x] Barnets omvårdnad och tjänster för barnfamiljer → `cards/orientation_guide/4.4_barnets_omvardnad_och_tjanster_for_barnfamiljer.txt`
- [x] Stöd för familjer i problemsituationer → `cards/orientation_guide/4.5_stod_for_familjer_i_problemsituationer.txt`
- [x] Andra hälsovårds- och socialtjänster → `cards/orientation_guide/4.6_andra_halsovards-_och_socialtjanster.txt`
- [x] När familjen flyttar till Finland → `cards/orientation_guide/4.7_nar_familjen_flyttar_till_finland.txt`

### Chapter 5 — Utbildning

 - [x] Det finländska utbildningssystemets utveckling → `cards/orientation_guide/5.1_det_finlandska_utbildningssystemets_utveckling.txt`
 - [x] Det finländska utbildningssystemet i dag → `cards/orientation_guide/5.2_det_finlandska_utbildningssystemet_i_dag.txt`
 - [x] Finansieringen av studier → `cards/orientation_guide/5.3_finansieringen_av_studier.txt`

### Chapter 6 — Arbete och försörjning i Finland

 - [x] Arbetsmarknaden → `cards/orientation_guide/6.1_arbetsmarknaden.txt`
 - [x] Att hitta arbete → `cards/orientation_guide/6.2_att_hitta_arbete.txt`
 - [x] Lön och beskattning → `cards/orientation_guide/6.3_lon_och_beskattning.txt`
 - [x] Arbetslöshet → `cards/orientation_guide/6.4_arbetsloshet.txt`
 - [x] Företagande och yrkesutövande → `cards/orientation_guide/6.5_foretagande_och_yrkesutovande.txt`

### Chapter 7 — Hälsa och åldrande i Finland

 - [x] Hälsa och sjukdom → `cards/orientation_guide/7.1_halsa_och_sjukdom.txt`
 - [x] Hälsovårdstjänster i Finland → `cards/orientation_guide/7.2_halsovardstjanster_i_finland.txt`
 - [x] Äldre människors hälsa och välbefinnande → `cards/orientation_guide/7.3_aldre_manniskors_halsa_och_valbefinnande.txt`
 - [x] Olika pensioner → `cards/orientation_guide/7.4_olika_pensioner.txt`
 - [x] Vårdtjänster för äldre → `cards/orientation_guide/7.5_vardtjanster_for_aldre.txt`
 - [x] Död och begravning → `cards/orientation_guide/7.6_dod_och_begravning.txt`
 - [x] Arv → `cards/orientation_guide/7.7_arv.txt`

### Chapter 8 — Lagar och rättskipande verksamhet i Finland

 - [x] Finlands rättssystem → `cards/orientation_guide/8.1_finlands_rattssystem.txt`
 - [x] Ett jämlikt och jämställt samhälle → `cards/orientation_guide/8.2_ett_jamlikt_och_jamstallt_samhalle.txt`
 - [x] Individens rättigheter och skyldigheter → `cards/orientation_guide/8.3_individens_rattigheter_och_skyldigheter_i_finland.txt`
 - [x] Brott → `cards/orientation_guide/8.4_brott.txt`
 - [x] Rättsprocessen och rättshjälp → `cards/orientation_guide/8.5_rattsprocessen_och_rattshjalp.txt`

### Chapter 9 — Politik och påverkande i Finland

- [x] Vad är demokrati? → `cards/orientation_guide/9.1_vad_ar_demokrati.txt`
- [x] Demokratins utveckling i Finland → `cards/orientation_guide/9.2_demokratins_utveckling_i_finland.txt`
- [x] Val i Finland → `cards/orientation_guide/9.3_val_i_finland.txt`
- [x] Finlands politiska partier → `cards/orientation_guide/9.4_finlands_politiska_partier.txt`
- [x] Medborgarpåverkan → `cards/orientation_guide/9.5_medborgarpaverkan.txt`

**Total:** 9 chapters, 45 subchapters

---

## 2. Danish Citizenship Exams (TRANSLATION & LOCALIZATION)

**Source:** `data/danish/`

Create one-to-one translations of each Danish citizenship exam, but **localized for Finland** (adapt Danish-specific content to Finnish context).

**Raw dump:** `card_creator/danish/all_cards.txt` contains the verbatim multiple-choice lines copied from the combined exam PDFs (`data/danish/all_questions.pdf` + `data/danish/all_answers.pdf`), with no translation or rewriting.

**Target location:** `cards/danish_adapted/`

### Exam Sets

- [ ] 2020-06 - `indfoedsretsproeven-2020-06.pdf` + answer key
- [ ] 2020-11 - `indfoedsretsproeven-2020-11.pdf` + answer key
- [ ] 2021-06 - `indfoedsretsproeven-2021-06.pdf` + answer key
- [ ] 2021-11 - `indfoedsretsproeven-2021-11.pdf` + answer key
- [ ] 2022-06 - `indfoedsretsproeven-2022-06.pdf` + answer key
- [ ] 2022-11 - `indfoedsretsproeven-2022-11.pdf` + answer key
- [ ] 2023-05 - `indfoedsretsproeven-2023-05.pdf` + answer key
- [ ] 2023-11 - `indfoedsretsproeven-2023-11.pdf` + answer key
- [ ] 2024-05 - `indfoedsretsproeven-2024-05.pdf` + answer key
- [ ] 2024-11 - `indfoedsretsproeven-2024-11.pdf` + answer key
- [ ] 2025-05 - `indfoedsretsproeven-2025-05.pdf` + answer key

**Total:** 11 exam sets × ~40 questions each ≈ 440 cards

---

## 3. InfoFinland Content (CATEGORY-BASED)

**Source:** `data/infofinland/content/`

Create cards organized by categories. One file per category.

**Target location:** `cards/infofinland/`

### Categories (To Be Defined)

Define categories based on InfoFinland structure, then create one card file for each:

- [ ] **Education System** (`education/`)
  - File: `cards/infofinland/education.txt`

- [ ] **Family & Children** (`family/`)
  - File: `cards/infofinland/family.txt`

- [ ] **Finnish & Swedish Language** (`finnish-and-swedish/`)
  - File: `cards/infofinland/languages.txt`

- [ ] **Health & Healthcare** (`health/`)
  - File: `cards/infofinland/health.txt`

- [ ] **Housing** (`housing/`)
  - File: `cards/infofinland/housing.txt`

- [ ] **Information About Finland** (`information-about-finland/`)
  - File: `cards/infofinland/finland_info.txt`

- [ ] **Leisure & Culture** (`leisure/`)
  - File: `cards/infofinland/leisure.txt`

- [ ] **Moving to Finland** (`moving-to-finland/`)
  - File: `cards/infofinland/moving.txt`

- [ ] **Settling in Finland** (`settling-in-finland/`)
  - File: `cards/infofinland/settling.txt`

- [ ] **Work & Enterprise** (`work-and-enterprise/`)
  - File: `cards/infofinland/work.txt`

### City-Specific Content

- [ ] **Helsinki** (`helsinki/`)
  - File: `cards/infofinland/helsinki.txt`

- [ ] **Espoo** (`espoo/`)
  - File: `cards/infofinland/espoo.txt`

- [ ] **Vantaa** (`vantaa/`)
  - File: `cards/infofinland/vantaa.txt`

- [ ] **Kauniainen** (`kauniainen/`)
  - File: `cards/infofinland/kauniainen.txt`

- [ ] **Vaasa** (`vaasa/`)
  - File: `cards/infofinland/vaasa.txt`

---

## 4. Articles

**Source:** `data/articles/`

Create one card file for each article.

**Target location:** `cards/articles/`

### Article Files

- [ ] **Fattigdomens historia i Finland**
  - Source: `Fattigdomens historia i Finland.pdf`
  - File: `cards/articles/poverty_history_finland.txt`

- [ ] **Miraklet i Norden**
  - Source: `Miraklet i Norden.odt`
  - File: `cards/articles/nordic_miracle.txt`

- [ ] **Samhället vi lever i** (Poverty History & Welfare Society)
  - Source: `Samhället vi lever i Fattigdomens historia och välfärdssamhällets framväxt och ord och frågor TILL FILMEN.docx`
  - File: `cards/articles/welfare_society.txt`

---

## 5. Orientation Website (Scraped)

**Source:** `data/orientation/` (yhteiskuntaorientaatio.fi crawl)

Create cards based on the scraped website materials, organized by topic/category
(see `card_creator/orientation/GUIDE.md`).

**Target location:** `cards/orientation/`

### Topics

- [x] **Finnish history** → `cards/orientation/history/9_finnish_history.txt`

---

## Summary Statistics

### Total Progress

- **Main Textbook:** 45/45 subchapters (100%)
- **Danish Exams:** 0/11 exam sets (~0/440 cards)
- **InfoFinland:** 0/15 categories
- **Articles:** 0/3 articles
- **Orientation Website:** 1/9 topics (11.1%)

### Overall Completion: 55.4%

**Grand Total: 46/83 content sections completed**

---

## Notes

- All cards should be **challenging** and test deep knowledge
- Danish questions must be **adapted to Finnish context**, not just translated
- InfoFinland categories may be adjusted based on content depth
- Priority should be given to the main textbook as the primary source

---

## Tools and Workflow

### Orientation Guide Workflow

**Created files:**
- `card_creator/orientation_guide/chatgpt_card_generation_prompt.md` - Prompt template for ChatGPT to generate flashcards from the textbook
- `card_creator/orientation_guide/split_cards.py` - Python script to split ChatGPT's output into individual card files
- `card_creator/orientation_guide/output.txt` - Paste ChatGPT output here (commit this file)
- `card_creator/orientation_guide/README.md` - Step-by-step usage instructions

**Workflow (User vs AI):**
- User:
  1. Extract text for the desired subchapter(s) from `data/orientation_guide.pdf`.
  2. Use `chatgpt_card_generation_prompt.md` with ChatGPT to generate Swedish MCQ cards.
  3. Paste the full result into `card_creator/orientation_guide/output.txt` and commit it.
- AI:
  4. Split into per-subchapter files: `poetry run python card_creator/orientation_guide/split_cards.py`.
  5. Review `cards/orientation_guide/*.txt` (formatting, double pipes, one correct flag).
  6. Commit the updated files under `cards/orientation_guide/`.
