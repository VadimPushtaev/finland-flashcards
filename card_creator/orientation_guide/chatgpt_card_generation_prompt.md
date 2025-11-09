# ChatGPT Card Generation Prompt

Use this prompt when uploading a PDF file to ChatGPT to generate flashcards.

---

**CHAPTER: [INSERT CHAPTER NUMBER]**

I need you to create Anki flashcards from the chapter specified above in the attached PDF file. The flashcards are for the **Anki Multiple Choice Question plugin** and must follow this exact format.

**🚨 CRITICAL: ALL flashcards must be written in SWEDISH ONLY. Questions and all answer options must be in Swedish. Instructions below are in English for clarity. 🚨**

## Card Format

Each card must use this pipe-separated format:

```
Question|Category|Type|Option1|Option2|Option3|Option4||CorrectAnswerFlags|Type
```

### Field Definitions:
- **Question**: The question text (clear and straightforward)
- **Category**: Subject/topic (e.g., Geography, History, Culture, Politics, Economy, Education, Society, etc.)
- **Type**: Always use `2`
- **Option1-4**: Four answer choices
- **Empty field**: Double pipe `||` (required)
- **CorrectAnswerFlags**: Binary flags indicating correct answer (e.g., `0 1 0 0` means Option2 is correct)
- **Type**: Type identifier again (always `2`)

### Format Examples (in Swedish):

```
Vad är huvudstaden i Frankrike?|Geografi|2|Berlin|Madrid|Paris|Rom||0 0 1 0|2
Hur mycket är 2 + 2?|Matematik|2|3|4|5|6||0 1 0 0|2
Vad är vattens kemiska formel?|Vetenskap|2|CO2|H2O|O2|NaCl||0 1 0 0|2
Vem skrev "Romeo och Julia"?|Litteratur|2|Charles Dickens|William Shakespeare|Leo Tolstoy|Mark Twain||0 1 0 0|2
```

## Requirements

**CRITICAL REQUIREMENTS:**
1. SWEDISH LANGUAGE ONLY: ALL questions and answer options must be written in Swedish. This is mandatory.
2. Single correct answer only: Exactly one correct answer per question (one `1` in CorrectAnswerFlags).
3. Exactly four options: Each question must have exactly 4 answer choices.
4. Clear and unambiguous: Questions should be straightforward and not confusing.
5. Challenging difficulty: Questions should test understanding, not just trivial facts.
6. Factual accuracy: Base every question strictly on the chapter’s content.
7. Plausible distractors: Wrong answers should be plausible but clearly incorrect.
8. Simple language: Use clear, direct Swedish.
9. Standalone questions (no source references): We are creating cards using the textbook, not for the textbook. Users don’t see the chapter. Never reference the source.
   - Forbidden in the question stem: Swedish phrases like “enligt …”, “enligt kapitlet/texten/beskrivningen/uppgifterna/informationen”, and any “i texten/kapitlet/avsnittet/materialet/pdf:en”, “som beskrivs/nämns ovan”, “baserat på texten”.
   - Write questions generically instead (e.g., “Vad …?”, “Vilken …?”, “När …?”) with no source marker.
   - Allowed exceptions: explicit references to a named law, regulation, or authority (e.g., “enligt arbetstidslagen”, “enligt FPA/Migri/Statistikcentralen”). Avoid vague attributions like “enligt experter/uppgifter”.

### Rewrite rules for source‑free questions (important)
- Replace any “enligt …/i texten …” phrasing with a neutral, general question.
- If the fact is time‑qualified in the chapter (e.g., “i dag”, “numera”), keep the time cue in the question (“Vilken sektor sysselsätter flest i Finland i dag?”).
- If the chapter cites a specific law or authority, include it explicitly (“Vad avses med övertid enligt arbetstidslagen?”).

DON’T (source‑bound; Swedish examples):
- Vilken sektor sysselsätter flest i Finland enligt uppgifterna?
- Vad gäller för övertid enligt beskrivningen?
- Hur lång bör ett cv vara enligt texten?

DO (standalone; Swedish examples):
- Vilken sektor sysselsätter flest i Finland i dag?
- Vad avses med övertid enligt arbetstidslagen?
- Hur lång bör ett cv vara?

### DO / DON’T examples (Swedish)

DON’T:
- Vad blev den övergripande trenden för arbeten i Finland enligt kapitlet?
- När upphör läroplikten enligt kapitlet?
- Vilket mål med utbildningen blev viktigare i början av 1900‑talet enligt texten?

DO:
- Vad blev den övergripande trenden för arbeten i Finland under 1900‑talet?
- När upphör läroplikten i Finland?
- Vilket utbildningsmål blev viktigare i början av 1900‑talet?

## Output Instructions

1. Read the specified chapter from the attached PDF carefully
2. Identify all subchapters within the chapter
3. **Generate MAXIMUM number of flashcards**: Convert virtually every fact, date, name, concept, and detail into a question. We need abundance of questions.
4. **Every fact should become a card**: If there's a fact in the text, create a question about it. More cards is better.
5. Cover all important topics and concepts from the chapter thoroughly
6. **Organize output by subchapters**: Group flashcards by subchapter with a clear heading for each subchapter
7. For each subchapter, output the flashcard lines in the specified format
8. Use subchapter headings in this format: `# Subchapter X.Y: [Subchapter Title]`
9. After each subchapter heading, output ONLY the flashcard lines (no explanations or additional text)
10. Each flashcard line should be complete and properly formatted
11. Use appropriate categories based on the content (e.g., History, Politics, Geography, Culture, Economy, Education, Society, Law, etc.)
12. Do not mention the source (chapter/text/article) anywhere in questions or options.
13. Final quality check: Ensure the output contains none of these Swedish substrings in questions: “enligt”, “i texten”, “i kapitlet”, “i avsnittet”, “i materialet”, “i pdf:en”, “beskrivningen”, “uppgifterna”, “informationen”. If any occur, rewrite the question to be fully standalone.

## Example Output Format (in Swedish):

```
# Subchapter 3.1: Det politiska systemet

Vilket organ stiftar lagar i Finland?|Politik|2|Presidenten|Regeringen|Riksdagen|Högsta domstolen||0 0 1 0|2
Hur många platser finns det i Finlands riksdag?|Politik|2|150|200|250|300||0 1 0 0|2

# Subchapter 3.2: Ekonomi och valuta

Vad är Finlands officiella valuta?|Ekonomi|2|Svensk krona|Euro|Finsk mark|Norsk krona||0 1 0 0|2
När införde Finland euron?|Ekonomi|2|1995|1999|2002|2005||0 0 1 0|2

# Subchapter 3.3: Historiska händelser

När blev Finland självständigt?|Historia|2|1905|1917|1920|1939||0 1 0 0|2
Från vilket land blev Finland självständigt?|Historia|2|Sverige|Ryssland|Danmark|Norge||0 1 0 0|2
```

Please generate the flashcards now from the specified chapter of the attached PDF, organized by subchapters as shown above.

**REMEMBER:
- Write everything in SWEDISH (Svenska) - questions, answers, and all content must be in Swedish!
- Create as MANY cards as possible - convert every fact, detail, date, and concept into a question. Abundance is key!**
