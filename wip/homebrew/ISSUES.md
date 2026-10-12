# Source issues and passage-selection requirements

These notes are editorial metadata; none belongs in the reading chapters.

| Issue | Repository evidence | Handling |
| --- | --- | --- |
| Orientation holidays page lacks its lesson | `data/orientation/sv/laromedel/manniskorna-och-kulturen/hogtider-och-traditioner.html` has navigation and a title, but no lesson body. | Record a source gap, not an irrelevant-topic exclusion. Use textbook section 1.5 (printed pp. 15-22) and InfoFinland `information-about-finland/finnish-holidays.html`. |
| Textbook compulsory education is outdated relative to local websites | Textbook printed p. 65 / PDF p. 66 ends compulsory education at 17. Orientation `skolgang-och-studier-i-finland.html`, blocks b0003/b0018, and InfoFinland `the-finnish-education-system.html`, b0034, describe completion of secondary studies or age 18. | Use the newer website passages. Keep the older PDF unchanged and record this substitution in provenance during composition. |
| Organization of healthcare has changed across sources | The textbook's healthcare account predates the website account. Orientation `det-finlandska-forvaltningssystemet.html`, b0052, identifies wellbeing services counties and the Helsinki exception. | Prefer the later institutional explanation and preserve its exception. Check every old municipality/health-service claim before use. |
| Some useful protections are inside procedural pages | InfoFinland `job-application-and-cv.html`, b0055/b0075: reference-contact consent and interview-question limits. `tips-for-job-hunting.html`, b0032: free job placement for workers. | Mark these pages partial, not wholly excluded. Retain relevant protections and remove coaching. Whole mixed paragraphs may remain when needed to preserve wording. |
| Some Swedish pages contain Finnish labels | For example orientation `rattsprocessen.html` includes the duplicate Finnish heading "Syyttäjä päättää, nostetaanko syyte"; some exercise headings are Finnish. | Remove duplicate foreign-language headings and exercises. If substantive content exists only in another language, record a gap rather than translate it in this edition. |
| Source numbers and conditions can be time-sensitive | Textbook metadata records creation/modification on 2019-06-14; website articles and official snapshots have different dates. | Review population counts, officeholders, pension ages, tax/benefit figures, permit/citizenship conditions and healthcare entitlement claims. A newer date alone does not resolve a contradiction. Preserve explicitly dated historical facts. |
| Website images are not stored locally | No PNG/JPEG/SVG/WebP/GIF assets are present under the two website archive directories. HTML references remote/relative image resources. | Do not fetch them. Assess essential PDF visuals after outline approval. Record any essential uncaptured information as a gap. |
| PDF extraction preserves layout artifacts | Pages retain headers/footers, line breaks and some broken words. The TOC page windows deliberately overlap where headings share a page. | Do not quote a whole candidate page window blindly. Isolate the correct heading, verify reading order against the PDF, and log any extraction repairs. |
| Swedish Finlex HTML needs JavaScript hydration | Static extraction of the archived act 552/2026 yields only a title/shell. | Use the Swedish government decision attachment and the published Finnish final act for the legal scope review. Do not call the shell an absent law. |
| Exact passage selection is partial | Chapter 05 now has exact excerpts, stable sentence IDs and a source/block audit. The other chapters still have source-unit eligibility only. | Review the pilot at checkpoint 2, then continue composition. See `data/homebrew/metadata/05_editorial_review.yaml` for its locally resolved conflicts, extradition gap and source-era limitations. |

## Attribution and reuse records

- **InfoFinland:** the local `data/infofinland/content/open-data.html` explicitly
  grants CC BY 4.0 reuse for text, requires attribution, a link and adaptation
  information, and excludes images from that permission. Preserve these notices
  in companion metadata. A future public renderer must carry the accompanying
  attribution information through to its publication packaging.
- **Textbook:** the PDF credits Finlands Flyktinghjälp and its foreword says the
  material can also be used freely by others.
  Preserve the exact notice and credits; do not relabel it as MIT or CC BY.
- **Orientation website:** the local about page identifies Finlands Flyktinghjälp,
  Utbildningsstyrelsen, UF-centret and illustrator Jutta Kivilompolo. The local
  LICENSE defers to publisher terms, and no explicit redistribution license was
  identified in the inspected material. Record that status accurately in
  metadata rather than inventing a license.

All provenance/reuse information remains separate from the reader's chapter text.
