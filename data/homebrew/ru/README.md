# Russian Homebrew data

Russian sentence translations, contextual vocabulary, shared terminology, and
review metadata for the archived Swedish Homebrew anthology.

The current scope is chapters 1–6: 86 sections, 2,618 sentence records,
86 section headings, and six chapter headings. Chapters 7–12 are deferred.
Every completed target has a full review of its sentence translations,
contextual vocabulary and dictionary meanings. Chapters 1–5 use independent
agent review; chapter 6 records a separate full author review as `self_review`.

| Chapter | Sections | Sentence records | Vocabulary records, including headings | Status |
| --- | ---: | ---: | ---: | --- |
| 1. Finland, befolkningen och språken | 8 | 213 | 1,599 | Complete |
| 2. Finlands historia | 13 | 321 | 2,554 | Complete |
| 3. Kultur, värderingar och traditioner | 21 | 520 | 3,919 | Complete |
| 4. Demokrati, förvaltning och påverkan | 15 | 753 | 5,537 | Complete |
| 5. Grundläggande rättigheter, jämlikhet och skyldigheter | 15 | 469 | 3,570 | Complete |
| 6. Lagar, rättsväsende och rättsskydd | 14 | 342 | 2,509 | Complete |
| **Total** | **86** | **2,618** | **19,688** | **Complete** |

The [shared glossary](glossary.yaml) contains 177 reviewed terminology entries.
Reviewed sections become available after rebuilding the study image.
All 92 expected translation targets (sections and chapter headings) are complete;
the remaining 101 sections in chapters 7–12 have no Russian translations yet.
Two combined climate sentence records were split with user approval, preserving
all Swedish wording: `hb-c01-u0032-s002` became `s008` and `s009` in the same unit;
`hb-c01-u0034-s003` became `s007` and `s008`. The retired IDs are documented in the
[editorial review](../metadata/01_editorial_review.yaml), and the
[climate review](reviews/hb-c01-arstider.yaml) records their resolution.
Per-target translation review records are under `reviews/`.

Follow the [translation workflow](../../../translation/homebrew/README.md) and
[data schema](../TRANSLATION_SCHEMA.md). Preserve the Swedish anthology's
[source credits and reuse terms](../metadata/attribution.yaml) and
[per-chapter passage provenance](../metadata/). The Russian layer
adds sentence translations and vocabulary explanations; Swedish originals are
unchanged. External language references are recorded in review metadata and do not
supply new factual content. These are translations of archived study materials,
not an official exam textbook or verification of current facts.
