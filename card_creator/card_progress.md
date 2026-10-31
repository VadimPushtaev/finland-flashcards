# Card Creation Progress Tracker

This document tracks which data sources have been converted into flashcards.

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
uses the whole assessed collection (currently these 213 sentences): **CORE >=41:
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
