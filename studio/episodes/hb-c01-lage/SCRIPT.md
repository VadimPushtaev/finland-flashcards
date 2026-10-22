# Finland i Norden

Финляндия в регионе Северных стран

> Generated from script.yaml. Edit YAML, then run the review command.

Status: source-validated script; see assets.yaml for acquired files and review.md for approval status.

Shared direction: [DIRECTING.md](../../DIRECTING.md). Section: `hb-c01-lage`.

14 sentences; 134 Swedish words. Final timeline timestamps are assigned during assembly from measured audio and planned pauses.

## Episode decisions

- **opening** (approved; script): Show the exact bilingual heading for 3 seconds over the same full-frame forest background used throughout the video. Begin continuous background motion immediately; no narration on title.
- **story_structure** (approved; script): Move from landscape and shape to the Nordic region, then neighboring countries, two factual highlights, and finally Lake Saimaa. Keep every source sentence in its original order; add no spoken introduction, transition, or summary.
- **text_and_layout** (approved; script): Follow the shared directing guide: Swedish above Russian on a stable readable panel, imagery in a separate area. Show each complete sentence pair together with automatic line wrapping. No sentence segmentation is planned for this short episode; if fitting fails during layout review, record exact bilingual display segments here.
- **pace** (approved; script): Start narration trials at 120–140 words per minute. Show each pair about 0.25 seconds before its speech; use the planned pauses below, with longer holds at topic boundaries. Measure actual audio later; do not infer final duration from word count or shorten text to fit.
- **visual_motion** (approved; script): Use the Kuivaketvele forest/lake photo throughout. Make its motion perceptible within 5–10 seconds: continuous diagonal pan from normalized crop position (0.15, 0.15) to (0.85, 0.85), with zoom 1.06 to 1.219 (15% relative increase) across the full episode. Use linear progress and fractional bicubic sampling so motion starts immediately without sentence resets. Keep foreground images and text fixed.
- **voice_selection** (approved; assets): Use the shared Supertonic 3 F1 female voice with Swedish language sv, 32 synthesis steps, speed 0.95, seed 42 and 44.1 kHz mono PCM WAV. Select one clip per source sentence. The user accepted this voice in the complete video. Local transcript diagnostics remain available for future pronunciation review.
- **music_selection** (approved; assets): Keep Light Thought var 1 by Kevin MacLeod for this first subchapter, under CC BY 4.0; reserve a different track for every other subchapter. Raise music alone by 2 dB relative to v3, a small single-step increase requested after review. Retain narration level, music ducking, fades and timing. Record the official filename and differing embedded ID3 title in assets.yaml.
- **foreground_selection** (approved; script): Use generated Natural Earth 5.1.2 maps: nordic_map for sentences 4–5; neighbors_all for sentence 6, then neighbors_russia, neighbors_norway, neighbors_sweden and neighbors_estonia for the matching sentences. Reuse neighbors_estonia for the no-land-border sentence. Use finland_outline for shape and numerical facts. No flags or portraits.
- **closing** (approved; script): Hold the steady Saimaa foreground photo through the last sentence and pause, then show two 15-second credit cards over the continuing forest background with a dark translucent backing. Include full CREDITS.md alongside the video.
- **exceptions** (approved; script): No exceptions to the shared directing guide are proposed. Missing illustrations change the visual treatment only; retain all Swedish and Russian text.
- **render_layout** (approved; render): Keep the 1920×1080 24 fps bilingual split layout and typography. Add a stable translucent evergreen backing behind the text. Leave the useful-image area open for the first two sentences; show maps thereafter and the verified Saimaa photograph at the end. Background is always visible, darkened 42%, blurred 2.5 px, and continuously zoomed from 1.06 to 1.219 (15% relative increase), with a visible diagonal pan from crop position (0.15, 0.15) to (0.85, 0.85), across the complete timeline using linear progress and fractional sampling. All foreground images remain still. Narration, pauses, music and credit durations remain as in the first render. Music-only revision: +2 dB relative to v3; preserve the rendered visuals and narration.
- **russian_audio_track** (proposed; assets): Replace the Russian audio track using the reviewed Russian sentences and local Silero v5_6_ru Baya voice with explicit stress hints. Expand EET/GMT into their Russian meanings in speech. Preserve the accepted video and its scene boundaries. Use the original music bed, fades and levels with ducking aligned to Russian speech. Record pronunciation expansions and per-sentence timing in russian-narration.yaml and russian-narration.json. The selected takes fit without tempo adjustment. Supersede the previous Russian track at the user's request.

## Asset requests

Production requirements; see assets.yaml for acquired files and review status.

- **forest_lake** (background): Verified Finnish forest/lake photograph used as a continuous decorative full-frame background throughout the episode, softly blurred and darkened beneath stable text and useful foreground imagery. Fallback: Use another verified Finnish forest/lake image; if no suitable photo is available, use an explicitly illustrative landscape without naming a real location.
- **finland_outline** (foreground): Accurate north-up Finland outline for the north–south shape, time-zone, and area scenes. Use reusable geographic data and maintain recognizable proportions. Fallback: Use a sourced map of Finland. For numerical facts alone, retain the exact text highlight on a quiet background if the outline cannot be obtained.
- **nordic_map** (foreground): Accurate north-up map showing Finland, Sweden, Norway, Denmark, and Iceland. Include Iceland visibly; use an explicitly marked inset if needed. Swedish labels come from the source sentences. Fallback: Create a simple map from reusable geographic data. If unavailable, use a clean text arrangement of the named countries without implying geographic positions.
- **neighbors_map** (foreground): Accurate closer map with Finland, Russia, Norway, Sweden, Estonia, and the Gulf of Finland. Keep the Finland–Estonia water gap visible; provide variants that emphasize one named country at a time. Fallback: Use an attributed existing regional map with readable labels. If neither is available, use exact country-name text cards; never invent borders or a land connection to Estonia.
- **saimaa_view** (background): A photograph verified as Lake Saimaa, with creator, source, and reuse terms. Label it with the Swedish name Saimen. Fallback: Use an accurately located map of Lake Saimaa. If neither photo nor map is available, show only the source name on a neutral background; never label a generic lake as Saimaa.
- **music_bed** (music): One gentle instrumental bed for the whole episode, with suitable reuse terms or an original score. Exact selection follows the script’s music decision. Fallback: Create or choose another suitable instrumental bed; do not silently remove the required music.
- **narration** (narration): Fourteen separately identified local Swedish TTS clips, using one selected female voice and checked speech-only expansions. Fallback: If a candidate voice is unsuitable, audition another local female Sweden Swedish voice; keep the selection pending rather than using remote synthesis.

## Sentence script

### landscape

Sentences 1–3: establish forests and lakes, then show Finland’s north–south shape.

#### 01 · hb-c01-u0001-s001

**SV:** Finland är ett land i norra Europa där största delen av ytan täcks av skogar och sjöar.

**RU:** Финляндия — страна на севере Европы, большую часть территории которой занимают леса и озёра.

**Visual:** Leave the useful-image area open to the full-frame forest/lake background. Keep the bilingual text panel fixed; background motion continues across sentence boundaries.

**Assets:** forest_lake

**Highlights:** None.

**Pause after:** 1.3 seconds (planned).

#### 02 · hb-c01-u0001-s002

**SV:** Finland är ganska stort till ytan, men glest befolkat.

**RU:** Финляндия довольно велика по площади, но малонаселена.

**Visual:** Leave the useful-image area open to the full-frame forest/lake background. Keep the bilingual text panel fixed; background motion continues across sentence boundaries.

**Assets:** forest_lake

**Highlights:** None.

**Pause after:** 1.3 seconds (planned).

#### 03 · hb-c01-u0001-s003

**SV:** Finland är också långt i nord-sydlig riktning, vilket innebär att naturförhållandena varierar mycket i olika delar av landet.

**RU:** Финляндия также имеет большую протяжённость с севера на юг, а это означает, что природные условия в разных частях страны сильно различаются.

**Visual:** Show a north-up Finland outline and trace its north–south extent gently. Do not add climate zones or invented distances.

**Assets:** finland_outline

**Highlights:** nord-sydlig

**Pause after:** 2.0 seconds (planned).

**Pronunciation:** Check nord-sydlig and naturförhållandena in the chosen voice.

### nordic_region

Sentences 4–5: locate Finland within the Nordic region and show the other named countries.

#### 04 · hb-c01-u0002-s001

**SV:** Finland ligger i Nordeuropa och hör till Norden.

**RU:** Финляндия расположена в Северной Европе и относится к Северным странам.

**Visual:** Show the Nordic map and emphasize Finland; keep enough regional context to locate it.

**Assets:** nordic_map

**Highlights:** Finland, Norden

**Pause after:** 1.3 seconds (planned).

#### 05 · hb-c01-u0002-s002

**SV:** De övriga nordiska länderna är Sverige, Norge, Danmark och Island.

**RU:** Остальные Северные страны — Швеция, Норвегия, Дания и Исландия.

**Visual:** Keep the same map and highlight Sweden, Norway, Denmark, and Iceland together; all four labels remain visible for the sentence.

**Assets:** nordic_map

**Highlights:** Sverige, Norge, Danmark, Island

**Pause after:** 2.0 seconds (planned).

**Pronunciation:** Check the Swedish country names; do not substitute English or Finnish names.

### neighbors

Sentences 6–11: keep a stable closer map while emphasizing each neighboring country and the sea gap to Estonia.

#### 06 · hb-c01-u0003-s001

**SV:** Finlands grannländer är Ryssland, Norge, Sverige och Estland.

**RU:** Соседние с Финляндией страны — Россия, Норвегия, Швеция и Эстония.

**Visual:** Move to the closer map showing all four neighboring countries; Estonia appears across water, not joined by land.

**Assets:** neighbors_map

**Highlights:** Ryssland, Norge, Sverige, Estland

**Pause after:** 1.3 seconds (planned).

**Pronunciation:** Check the Swedish country names; do not substitute English or Finnish names.

#### 07 · hb-c01-u0003-s002

**SV:** Finland har en lång gemensam landgräns med Ryssland i öster.

**RU:** На востоке у Финляндии протяжённая общая сухопутная граница с Россией.

**Visual:** Emphasize Russia east of Finland and their land boundary, using verified map geometry.

**Assets:** neighbors_map

**Highlights:** Ryssland

**Pause after:** 1.3 seconds (planned).

#### 08 · hb-c01-u0003-s003

**SV:** I norr delar Finland gräns med Norge.

**RU:** На севере у Финляндии общая граница с Норвегией.

**Visual:** Emphasize Norway and the northern land boundary. Keep the map in the same orientation.

**Assets:** neighbors_map

**Highlights:** Norge

**Pause after:** 1.3 seconds (planned).

#### 09 · hb-c01-u0003-s004

**SV:** I väster har Finland en gemensam land- och sjögräns med Sverige.

**RU:** На западе у Финляндии общая сухопутная и морская граница со Швецией.

**Visual:** Emphasize Sweden to the west, with both land and sea context. Do not draw an invented maritime boundary.

**Assets:** neighbors_map

**Highlights:** Sverige

**Pause after:** 1.3 seconds (planned).

**Pronunciation:** Check the suspended compound land- och sjögräns; the written form stays unchanged.

#### 10 · hb-c01-u0003-s005

**SV:** I söder på andra sidan Finska viken ligger Estland.

**RU:** На юге, по другую сторону Финского залива, расположена Эстония.

**Visual:** Emphasize Estonia south across the Gulf of Finland. Label the gulf with its Swedish source name.

**Assets:** neighbors_map

**Highlights:** Finska viken, Estland

**Pause after:** 1.3 seconds (planned).

#### 11 · hb-c01-u0003-s006

**SV:** Finland har ingen gemensam landgräns med Estland.

**RU:** У Финляндии нет общей сухопутной границы с Эстонией.

**Visual:** Keep the water gap between Finland and Estonia prominent. Avoid any connecting line that could suggest a land border.

**Assets:** neighbors_map

**Highlights:** Estland

**Pause after:** 2.0 seconds (planned).

### key_facts

Sentences 12–13: use the Finland outline as a quiet setting for the exact time-zone and area labels.

#### 12 · hb-c01-u0004-s001

**SV:** Finlands tidszon är den östeuropeiska tiden EET (GMT +2).

**RU:** Часовой пояс Финляндии — восточноевропейское время EET (GMT +2).

**Visual:** Use the Finland outline with the exact source label EET (GMT +2). Do not add a live clock or imply that the archived label is the current seasonal UTC offset.

**Assets:** finland_outline

**Highlights:** EET, GMT +2

**Pause after:** 1.3 seconds (planned).

**Pronunciation:** Audition the spaced letters: some engines need phoneme instructions instead. The displayed source retains EET (GMT +2).

**Proposed TTS input (approved):** Finlands tidszon är den östeuropeiska tiden. E, E, T. G, M, T plus två.

**Reason:** Spell abbreviations with Swedish letter names and pronounce the plus sign and digit. Added punctuation separates letters after the first audition flagged merged/missing abbreviation letters. Displayed text remains unchanged; listening review required.

#### 13 · hb-c01-u0006-s001

**SV:** Finlands areal är 338 432 km².

**RU:** Площадь Финляндии составляет 338 432 км².

**Visual:** Retain the outline and show the exact area figure prominently, including the square-kilometre unit.

**Assets:** finland_outline

**Highlights:** 338 432 km²

**Pause after:** 2.0 seconds (planned).

**Pronunciation:** Check the full number and kvadratkilometer by listening before approving the override.

**Proposed TTS input (approved):** Finlands areal är trehundratrettioåtta tusen fyrahundratrettiotvå kvadratkilometer.

**Reason:** Read the source figure 338 432 and its km² unit aloud; this is pronunciation expansion, not a new factual statement.

### saimaa

Sentence 14: finish on a verified view of Lake Saimaa with the Swedish name Saimen.

#### 14 · hb-c01-u0007-s001

**SV:** Den största sjön heter Saimen.

**RU:** Самое большое озеро называется Сайма.

**Visual:** Show the verified Saimaa photograph steadily in the useful-image area, labeled Saimen, over the continuous decorative forest background. Hold through the final pause.

**Assets:** saimaa_view

**Highlights:** Saimen

**Pause after:** 2.0 seconds (planned).

**Pronunciation:** Check Saimen, the Swedish name used in the source; do not replace the narration with Saimaa.

## Source credits

Exact passage provenance and publisher notices: [sources.yaml](sources.yaml).

- [Yhteiskuntaorientaatio - Finlands läge och olika områden](https://yhteiskuntaorientaatio.fi/sv/laromedel/integration/finlands-lage-och-olika-omraden): Finlands Flyktinghjälp; Utbildningsstyrelsen; UF-centret. Publisher terms; explicit redistribution license not identified in local archive.
- [Grundläggande information om Finland](https://www.infofinland.fi/sv/information-about-finland/key-facts-about-finland): InfoFinland.fi. CC BY 4.0.

Swedish wording and existing Russian translations are preserved. Presentation,
visual cues, and proposed speech-only expansions are added for this video.
