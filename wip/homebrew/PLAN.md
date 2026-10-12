# Homebrew: Swedish citizenship-exam preparation material

## Purpose and agreed approach

Create a standalone Swedish collection titled **Samhällskunskap inför
medborgarskapsprovet**, under
`data/homebrew/`.

Build a new thematic anthology from exactly three existing content sources:
the orientation textbook PDF, Swedish civic orientation website archive, and
Swedish InfoFinland archive. Preserve substantive wording. Allow filtering,
rearrangement, new headings, formatting cleanup and documented extraction repairs.

Use archived exam legislation and official guidance to determine relevance.
Include material tied to the exam's scope and retain useful context. Exclude
irrelevant topics and procedural detail. No further-reading tier, translations,
practice questions or exam-administration chapter.

Reader-facing content must stand alone: no source annotations, exclusion notices
or explanations of how it was created. Keep those in separate English metadata
and work documents. Reader-facing text and titles are Swedish; schema keys and
work documents are English.

## Deliverables and content interface

Working area: `wip/homebrew/` contains this plan, progress, inventory, legal scope
analysis, coverage/exclusion decisions, unresolved issues, tools and reviewable
extracted text.

Final collection: `data/homebrew/` contains a collection manifest, YAML chapters
under `sv/chapters/`, separate metadata and any essential locally available
assets. Metadata records sources, hashes, attribution/reuse notices, passage
provenance, repairs and editorial decisions.

- Chapters and sections have stable IDs, Swedish titles and explicit ordering.
- Blocks support paragraphs, ordered/unordered lists, factual tables and images
  with available captions.
- Each paragraph, list item or table cell retains its complete text, with stable
  sentence IDs and zero-based Unicode code-point ranges into that exact text.
  End offsets are exclusive; surrounding whitespace is outside sentence ranges.
- IDs survive reordering and are not derived from positions or text hashes.
- Headings have stable IDs. Word tokenization and translations are deferred.
- Separate provenance maps text units to source file, file hash, heading/page
  location and exact extracted passage.
- A future renderer consumes this structure; building a website is out of scope.

## Execution sequence

### 1. Save the plan and freeze the source inventory

Record local source files and hashes without modifying the originals. Inspect
the Swedish textbook and actual website article bodies. Remove navigation,
scripts and repeated furniture during extraction, distinguishing them from real
headings and prose. Use Poetry for tools and dependencies. No crawling or
external factual supplementation.

Record source dates and reuse terms where present, including the archived
InfoFinland CC BY 4.0 notice. Do not assume source content uses the repo MIT license.

### 2. Establish scope and propose the anthology

Read the archived enacted law's exam-content provision. Use legislative
explanations and official guidance as supporting evidence, distinguishing drafts
from enacted requirements. Map coverage for society's functioning, rights and
obligations, central legislation, fundamental/human rights, equality and gender
equality, Finnish history/culture and other supported central civic knowledge.

Assess every substantive source chapter/article as included, partially included,
excluded or duplicated; record reasons and destination chapters. Include
education, work, health, pensions, housing and other topics where a connection to
exam scope is defensible. Omit trainer instructions, local directories, website
administration and detailed application procedures while retaining civic facts
embedded in those sections.

Propose a new Swedish outline from this analysis rather than copying one source.

**Review checkpoint 1:** present the outline, coverage map and exclusions, with
examples for consequential choices. Wait for user review before composing chapters.

### 3. Produce and review a representative pilot

Use rights and obligations as the pilot. Choose suitable passages, preferring
the orientation website, then textbook, then InfoFinland when accuracy and
suitability are equal. Other sources contribute additional facts or nuance.

Preserve substantive wording. Log repairs to PDF line breaks, extraction
artifacts and demonstrably broken hyphenation. Preserve needed qualifications,
lists, tables and examples. Resolve dangling references by keeping context or
selecting another passage. Resolve factual conflicts using repository evidence;
keep unresolved claims outside reader text and record coverage gaps. Add no
factual prose from memory or outside sources.

Finalize the YAML schema and demonstrate sentence segmentation, provenance and
separate metadata. Manually inspect Swedish abbreviations, dates and fragments.

**Review checkpoint 2:** present readable pilot text and its YAML representation.
Wait for review before producing the remaining chapters.

### 4. Complete the collection

Proceed chapter by chapter using the approved structure and pilot conventions.
Keep progress records. Use essential visuals only when already available locally;
website image links are not local assets. Extract useful PDF visuals where
feasible; retain captions and metadata. Record essential unavailable visuals as
gaps. No optional-reading tier or arbitrary length limit.

### 5. Validate and perform a final omission review

Review coverage against legal scope and the complete source inventory. Revisit
exclusions for civic knowledge hidden in otherwise irrelevant material. Deliver
content, metadata, validation results and unresolved issues; do not claim full
exam coverage where archived evidence leaves uncertainty.

## Validation and acceptance

Automated checks verify valid YAML/block structures, unique stable IDs, manifest
references, sentence ranges (including Swedish characters, punctuation,
abbreviations and multiline text), provenance for all substantive units/assets,
agreement with source passages after permitted normalization/logged repairs,
absence of metadata/boilerplate in reading text, local assets and valid tables/lists.

Focused tests cover HTML body extraction, representative PDF extraction,
sentence offsets, provenance mismatches and invalid structures. Editorial review
requires coverage or an explicit gap for each legal topic, a disposition for
every substantive source section, useful rather than repetitive overlap and
reasoned exclusions that do not remove relevant knowledge.

## Constraints

- Use fixed repository snapshots and record their dates without presenting them
  as verification of current facts.
- New headings are editorial; substantive learning passages come from the three
  agreed sources.
- Preserve original sources and existing flashcards.
- Pause for outline and pilot reviews; proceed through later chapters with
  progress updates.
- Do not commit or push without explicit user approval. Before any commit,
  follow the repository's make/ALL.txt and staged-change review requirements.
