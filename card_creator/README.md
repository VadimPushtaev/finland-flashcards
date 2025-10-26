# Card Creator

This directory contains scripts, prompts, and tools for creating Anki flashcards from the source material in `data/`.

## Purpose

The goal is to transform the educational content from `data/` (PDF files, HTML content, etc.) into multiple-choice question flashcards that will be stored in the `cards/` directory.

## Card Format

Cards are created for the **[Anki Multiple Choice Question plugin](https://ankiweb.net/shared/info/1566095810)**.

### Format Specification

Each card follows this pipe-separated format:

```
Question|Category|Type|Option1|Option2|Option3|Option4||CorrectAnswerFlags|Type
```

**Fields:**
- `Question`: The question text
- `Category`: Subject/topic (e.g., Geography, History, Culture, etc.)
- `Type`: Card type identifier (typically `2`)
- `Option1-4`: Four answer choices
- Empty field: Double pipe `||`
- `CorrectAnswerFlags`: Binary flags indicating correct answer (e.g., `0 1 0 0` means Option2 is correct)
- `Type`: Type identifier again (typically `2`)

### Examples

```
What is the capital of France?|Geography|2|Berlin|Madrid|Paris|Rome||0 0 1 0|2
2 + 2 = ?|Math|2|3|4|5|6||0 1 0 0|2
Water's chemical formula is…|Science|2|CO2|H2O|O2|NaCl||0 1 0 0|2
Largest planet in our solar system?|Astronomy|2|Earth|Jupiter|Mars|Venus||0 1 0 0|2
HTML stands for…|Technology|2|Hyperlinks and Text Markup Language|HyperText Markup Language|Home Tool Markup Language|-||0 1 0 0|2
The process by which plants make food is called…|Biology|2|Photosynthesis|Fermentation|Respiration|Evaporation||1 0 0 0|2
The fastest land animal is…|Animals|2|Cheetah|Lion|Horse|Gazelle||1 0 0 0|2
Who wrote "Romeo and Juliet"?|Literature|2|Charles Dickens|William Shakespeare|Leo Tolstoy|Mark Twain||0 1 0 0|2
Which gas do humans breathe in to stay alive?|Science|2|Oxygen|Carbon Dioxide|Nitrogen|Hydrogen||1 0 0 0|2
What is the square root of 64?|Math|2|6|7|8|9||0 0 1 0|2
```

## Card Requirements

- **Single answer only**: Exactly one correct answer per question
- **Four options**: Each question must have exactly 4 answer choices
- **Clear and unambiguous**: Questions should be straightforward
- **Challenging difficulty**: All questions are expected to be challenging and test deep knowledge

## Source Material

Content in `data/` includes:

### Finnish Citizenship Content
- InfoFinland HTML content (comprehensive information about Finland)
- Finnish history and society materials
- Various citizenship test preparation materials

### Danish Citizenship Content
- Danish citizenship test questions and answers (`data/danish/`)
- Test papers from 2020-2025
- Answer keys and study materials

These materials can serve as:
1. Direct source for questions (especially Danish materials which already contain Q&A)
2. Reference material for creating new questions
3. Templates for question structure and difficulty

## Workflow

1. **Extract content** from source materials in `data/`
2. **Generate questions** based on the content
3. **Format cards** according to the specification above
4. **Save cards** to the `cards/` directory
5. **Update progress** in `card_progress.md`
6. **Import to Anki** using the Multiple Choice Question plugin

## Progress Tracking

See `card_progress.md` for detailed tracking of which data sources have been converted to cards.

## Notes

- Keep questions factual and based on source material
- Ensure distractors (wrong answers) are plausible but clearly incorrect
- Maintain challenging difficulty level - questions should test deep understanding and knowledge
- Use clear, simple language
