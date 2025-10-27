# Orientation Guide Flashcard Workflow

This folder contains the workflow and helper script for generating Anki decks from the main orientation guide textbook (`data/orientation_guide.pdf`).

## Workflow

**For User**
- Copy the prompt from `card_creator/orientation_guide/chatgpt_card_generation_prompt.md` into ChatGPT and provide the relevant chapter text.
- Ensure ChatGPT’s output is in Swedish and follows the required format below.
- Paste the full ChatGPT result into `card_creator/orientation_guide/output.txt` and commit it.
- Then ask the project AI to continue with the AI steps below.

**For AI**
- Validate `output.txt` formatting (headers and card rows).
- Split into per-subchapter decks: `poetry run python card_creator/orientation_guide/split_cards.py`.
- Verify generated files in `cards/orientation_guide/` and spot-check formatting.

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

- Commit `card_creator/orientation_guide/output.txt` and the generated files under `cards/orientation_guide/`.
- Each card must have exactly one correct answer flag (e.g., `0 1 0 0`).
- Keep language Swedish and questions challenging and precise.
