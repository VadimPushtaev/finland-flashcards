# Orientation Guide Flashcard Workflow

This folder contains the workflow and helper script for generating Anki decks from the main orientation guide textbook (`data/orientation_guide.pdf`).

## Steps

1) Generate ChatGPT output
- Use `chatgpt_card_generation_prompt.md` with the relevant chapter text.
- Ensure output is in Swedish and formatted as specified below.

2) Save output
- Paste the full ChatGPT result into `card_creator/orientation_guide/output.txt`.
- Note: `output.txt` is scratch. Do not commit it.

3) Split into decks
- Run: `poetry run python card_creator/orientation_guide/split_cards.py`
- Resulting files appear in `cards/orientation_guide/` (one per subchapter).

## Required format in output.txt

- Subchapter headers must be lines like:
  - `# Subchapter X.Y: Title`
- Each card line must be pipe-delimited with exactly 4 options and a single correct flag:
  - `Question|Category|Type|Opt1|Opt2|Opt3|Opt4||0 1 0 0|2`
- Use ASCII filenames: the splitter normalizes accents, spaces -> underscores, and lowercases.

## Quick checks

- Inspect headers: `rg -n "^# Subchapter" card_creator/orientation_guide/output.txt`
- Preview: `head -n 40 card_creator/orientation_guide/output.txt`
- After splitting:
  - `ls -1 cards/orientation_guide`
  - `head cards/orientation_guide/*.txt`

## Notes

- Commit the generated files under `cards/orientation_guide/` but do not commit `output.txt`.
- Each card must have exactly one correct answer flag (e.g., `0 1 0 0`).
- Keep language Swedish and questions challenging and precise.
