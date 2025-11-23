# ChatGPT Card Conversion Prompt (Danish Originals)

Use this prompt when uploading **both** `data/danish/all_questions.pdf` and `data/danish/all_answers.pdf` to ChatGPT. The goal is to copy **every single question from every exam** contained in the combined PDFs into the Anki Multiple Choice Question plugin format **without translating or rewriting anything**, and to output one continuous list of cards (no exam headings). We will translate/adapt later, so every question and option must stay exactly as printed in the PDFs.

---

I need you to convert the attached Danish citizenship exam PDFs into Anki flashcards for the **Anki Multiple Choice Question plugin**. Create one card per question, using the original Danish wording for both questions and options.

## Inputs
- `all_questions.pdf`: Contains **all exams** back-to-back. Each exam usually has 45 questions (numbered 1–45) and its own header/date. You must process every exam in the file, not just the first one.
- `all_answers.pdf`: Combined answer key that maps each question number to the correct option letter for **every** exam in `all_questions.pdf`.

## Card Format

Each card uses this pipe-separated format:

```
Question|Category|Type|Option1|Option2|Option3|Option4||CorrectAnswerFlags|Type
```

Field rules:
- **Question**: Question text copied verbatim (no translation or paraphrasing).
- **Category**: Use `Indfødsretsprøven` for every card (no exam labels needed).
- **Type**: Always `2`.
- **Option1-4**: Answer options in the exact order shown in `all_questions.pdf`.
- **Empty field**: Double pipe `||`.
- **CorrectAnswerFlags**: Binary flags for the correct option (e.g., `0 1 0 0` if Option2 is correct).
- **Type (again)**: Always `2`.

## Requirements
1. **Verbatim text only**: Copy the Danish question text exactly as printed. Do not translate, summarize, or rephrase. You may drop only the leading question number (e.g., remove `12.`); keep all other wording, punctuation, and casing untouched.
2. **Original options**: Copy each option exactly as printed, preserving spelling and accents. Remove only the option label (`A)`, `B)`, etc.) so the option text is clean; keep the option order exactly as shown.
3. **Correct answer mapping**: Use `all_answers.pdf` to set a single `1` in `CorrectAnswerFlags` that matches the correct option letter for each question. All other positions must be `0`.
4. **One-to-one coverage for EVERY exam in the combined PDF**:
   - Detect each new exam (question numbering typically resets to 1–45 and the PDF header/date changes).
   - Produce one flashcard per question for **every exam**; do not drop or add questions.
   - Keep card order exactly as in `all_questions.pdf` across all exams (single continuous list).
   - Continue until there are **no more questions in the PDF**. Do not stop after the first exam.
5. **No extra commentary or headings**: Output only the flashcard lines. No exam headings, explanations, summaries, or notes.

## Output Instructions
1. Output only flashcard lines, one per question, in the exact format above (no headings).
2. Maintain the original question order across the entire `all_questions.pdf` (all exams back-to-back).
3. Ensure every line contains **exactly** two consecutive pipes `||` before the `CorrectAnswerFlags`.
4. Self-check totals: the total number of cards must equal the total number of questions in `all_questions.pdf` (sum of all exams; typically 45 per exam). Confirm that you have processed every exam in the file before stopping.

## Example (illustrative only)

If the PDF shows:
```
12. Hvad er Danmarks hovedstad?
A) København
B) Aarhus
C) Odense
D) Aalborg
Correct answer (from answer key): A
```

Then output:
```
# Danish Citizenship Exam — Original Questions
Hvad er Danmarks hovedstad?|Indfødsretsprøven|2|København|Aarhus|Odense|Aalborg||1 0 0 0|2
```

Please convert all questions now, keeping Danish text exactly as in the PDFs.
