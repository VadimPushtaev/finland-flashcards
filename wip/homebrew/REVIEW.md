# Checkpoint 1: proposed Homebrew outline and selection

**Approved:** the user authorized the pilot with “do it, make a commit (I approve)”.
The proposal below is retained as the review record. Current work is at
[checkpoint 2](PILOT_REVIEW.md).

**Decision requested:** review the 12-chapter outline and the inclusion/exclusion
boundaries below before the rights-and-obligations pilot is composed. This is
the first review checkpoint agreed in [PLAN.md](PLAN.md).

The first implementation stage is complete: local extraction, source inventory,
legal scope analysis and source-unit coverage proposal. The standalone chapters
have not yet been written. All content candidates come from the three agreed
sources already in the repository.

## Proposed Swedish reading order

Title: **Samhällskunskap inför medborgarskapsprovet**. Future location:
`data/homebrew/`. Each chapter will be YAML with stable block/sentence IDs;
provenance will be separate.

| ID | Chapter | Principal coverage |
| --- | --- | --- |
| 01 | Finland, befolkningen och språken | Geography, regions, Aland, seasons, population, languages, minorities and indigenous people. |
| 02 | Finlands historia | Swedish/Russian periods, independence, wars, democracy, welfare-state development and international integration. |
| 03 | Kultur, värderingar och traditioner | Values, customs, religion, holidays, food and sauna culture. |
| 04 | Demokrati, förvaltning och påverkan | Parliament, government, president, municipalities/counties, EU/international institutions, elections, parties, participation and media. |
| 05 | Grundläggande rättigheter, jämlikhet och skyldigheter | Fundamental/human rights, equality, minorities, sexual rights, citizenship duties and defence. **Pilot chapter.** |
| 06 | Lagar, rättsväsende och rättsskydd | Constitution, rule of law, good administration, police, prosecution, courts, crimes, punishment, appeals and legal aid. |
| 07 | Arbete, näringsliv och beskattning | Economy, labour market, contracts, unions, working conditions, occupational safety, unemployment, entrepreneurship and tax. |
| 08 | Utbildning och lärande | Education system, compulsory schooling, secondary/higher/adult education, students' rights and support. |
| 09 | Familj, barn och relationer | Family forms, marriage/cohabitation, separation, children, family support, protection against violence, death and inheritance. |
| 10 | Hälsa, social trygghet och åldrande | Welfare institutions, access to care, public/private services, disability, illness support, pensions and older people's care. |
| 11 | Boende, vardag och miljö | Housing rights/duties, household finance, consumer protection, recycling, nature access, traffic, emergencies and public leisure services. |
| 12 | Integration, uppehåll och medborgarskap | Integration institutions, public-authority dealings, language/interpretation, registration, residence/protection and citizenship concepts. |

Detailed topic lists: [outline.yaml](outline.yaml). Legal reasons and exact
archived page references: [LEGAL_SCOPE.md](LEGAL_SCOPE.md).

The enacted provision has broad society-knowledge coverage. The proposal's
supporting discussion specifically mentions housing, healthcare, work, tax,
education, geography, customs, emergencies and traffic. This supports retaining
those subjects while filtering their non-civic details. It does not prove that
every retained fact will appear on the official exam.

## What the proposal removes

- **Whole lesson pages:** emotional phases of moving to a new country and generic
  future-skills/course-reflection coaching.
- **Whole language-practice pages:** online Finnish-course directories, useful
  Finnish phrases and language-course level selection.
- **Non-reading material:** trainer handbooks, website administration, municipal
  service directories, index duplicates, textbook front matter and classroom
  discussion questions.
- **Within otherwise relevant pages:** CV/interview coaching, form-filling,
  booking and application walkthroughs, provider directories, personal diet and
  exercise prescriptions, shopping/relocation advice and unrelated lifestyle tips.
- **Exam logistics:** no registration, fee, score-threshold or exemption chapter.

## What the filtering deliberately preserves

- National holidays and their meanings, useful historical context, minority and
  language rights, religion, family diversity and ordinary civic institutions.
- Useful definitions, examples, qualifications and explanatory context.
- Rights and duties embedded in practical pages. For example, InfoFinland's CV
  page contains consent rules for contacting references and limits on interview
  questions; its job-search tips state that placement is free for workers. These
  are **partial inclusions**, despite their procedural page titles.
- Safety actions, legal remedies and compulsory duties. Emergency instructions
  and the duty to register a change are not removed merely for describing actions.

For overlap, select one main explanation and add useful additional facts.
When quality and accuracy are equal, prefer the orientation website, then the
textbook, then InfoFinland. No further-reading tier or arbitrary word limit.

## Inventory and dispositions

| Source | Units mapped | Include | Partial | Exclude | Duplicate | Source gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Swedish orientation archive | 105 pages | 37 | 31 | 36 | 0 | 1 |
| Swedish InfoFinland archive | 234 pages | 11 | 139 | 74 | 10 | 0 |
| Textbook | 45 substantive subsections + front matter and 9 discussion sections | 18 | 27 | 10 | 0 | 0 |
| **Total** | **394** | **66** | **197** | **120** | **10** | **1** |

These are source-unit decisions, not final paragraph counts. Exact passage
selection and a second omission review follow outline approval. Some partially
included pages may ultimately contribute no text if another source covers all
their useful facts better.

Full dispositions: [COVERAGE.md](COVERAGE.md). Source headings, safeguards and
PDF locations: [coverage.yaml](coverage.yaml). Source-byte inventory:
[source_inventory.yaml](source_inventory.yaml), covering 349 files including
legal evidence and provenance documents.

## Findings that affect composition

1. The archived orientation holidays page is only a shell. Keep the topic and use
   the existing textbook and InfoFinland passages.
2. The textbook's compulsory-education endpoint conflicts with both website
   sources. Use the later source passage, preserving the original PDF.
3. Healthcare administration must reflect the later local account, including the
   Helsinki exception; do not reuse the older institutional description blindly.
4. The website archives contain no image files. Essential visuals must already
   exist in the PDF or another allowed local asset; missing visuals are recorded
   as gaps rather than fetched.

[ISSUES.md](ISSUES.md) records these findings and the source reuse/attribution
information. That metadata stays outside the reading chapters.

## Next stage after review

Build chapter 05 as the pilot, finalize the YAML structure and stable sentence
ranges, and demonstrate exact passage provenance separately. Present the pilot
for the second agreed review before writing the remaining chapters.
