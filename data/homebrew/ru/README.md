# Russian Homebrew data

Russian sentence translations, contextual vocabulary, shared terminology, and
review metadata for the archived Swedish Homebrew anthology.

Chapter 1 has translations for all 213 sentence records, all eight
section headings, and the chapter heading. Each section received full independent
agent review, including its contextual vocabulary and dictionary meanings.

| Section | Sentence records | Vocabulary records (including heading) | Status |
| --- | ---: | ---: | --- |
| [Finland i Norden](sections/hb-c01-lage.yaml) | 14 | 90 | Complete |
| [Regioner](sections/hb-c01-regioner.yaml) | 54 | 379 | Complete |
| [Natur](sections/hb-c01-natur.yaml) | 8 | 50 | Complete |
| [Årstider och klimat](sections/hb-c01-arstider.yaml) | 53 | 392 | Complete |
| [Befolkning](sections/hb-c01-befolkning.yaml) | 15 | 108 | Complete |
| [Språk](sections/hb-c01-sprak.yaml) | 16 | 117 | Complete |
| [Folkgrupper](sections/hb-c01-folkgrupper.yaml) | 39 | 326 | Complete |
| [Flyttning](sections/hb-c01-flyttning.yaml) | 14 | 134 | Complete |

The completed [chapter heading](headings/hb-c01.yaml) adds three vocabulary
records, bringing the chapter total to **1,599**. The [shared glossary](glossary.yaml)
contains 28 reviewed terminology entries. Later chapters have not been translated.

All eight sections are complete and available after rebuilding the study image.
Two combined climate sentence records were split with user approval, preserving
all Swedish wording: `hb-c01-u0032-s002` became `s008` and `s009` in the same unit;
`hb-c01-u0034-s003` became `s007` and `s008`. The retired IDs are documented in the
[editorial review](../metadata/01_editorial_review.yaml), and the
[climate review](reviews/hb-c01-arstider.yaml) records their resolution.
Per-target translation review records are under `reviews/`.

Follow the [translation workflow](../../../translation/homebrew/README.md) and
[data schema](../TRANSLATION_SCHEMA.md). Preserve the Swedish anthology's
[source credits and reuse terms](../metadata/attribution.yaml) and
[chapter 1 passage provenance](../metadata/01_provenance.yaml). The Russian layer
adds sentence translations and vocabulary explanations; Swedish originals are
unchanged. External language references are recorded in review metadata and do not
supply new factual content. These are translations of archived study materials,
not an official exam textbook or verification of current facts.
