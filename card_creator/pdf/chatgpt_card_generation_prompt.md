# ChatGPT Card Generation Prompt

Use this prompt when uploading a PDF file to ChatGPT to generate flashcards.

---

**CHAPTER: [INSERT CHAPTER NUMBER]**

I need you to create Anki flashcards from the chapter specified above in the attached PDF file. The flashcards are for the **Anki Multiple Choice Question plugin** and must follow this exact format.

**🚨 CRITICAL: ALL flashcards must be written in SWEDISH ONLY. Questions and all answer options must be in Swedish. 🚨**

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
1. **SWEDISH LANGUAGE ONLY**: ALL questions and answer options MUST be written in Swedish (Svenska). This is mandatory.
2. **Single correct answer only**: Exactly one correct answer per question (one `1` in CorrectAnswerFlags)
3. **Exactly four options**: Each question must have exactly 4 answer choices
4. **Clear and unambiguous**: Questions should be straightforward and not confusing
5. **Challenging difficulty**: All questions must be challenging and test deep knowledge and understanding (not basic facts)
6. **Factual accuracy**: Base all questions on the actual content from the PDF
7. **Plausible distractors**: Wrong answers should be plausible but clearly incorrect
8. **Simple language**: Use clear, direct Swedish language

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

