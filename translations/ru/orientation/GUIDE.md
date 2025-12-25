# Orientation HTML Translation Guide

We translate selected HTML pages from the civic orientation website crawl under
`data/orientation/` into Russian while keeping the HTML as close to the
original as possible (including images and layout markup).

## Goals

- Output should be a "drop-in" translated copy of the source HTML.
- Preserve the original HTML structure, attributes, and ordering.
- Translate only the human-readable text content.
- Keep images and other media embedded (do not delete `<img>`, `<picture>`,
  `<figure>`, `<iframe>`, etc.).
- Always remove the site navigation menu blocks ("MENU") from the HTML.

## What to translate

Translate:
- Headings, paragraphs, list items, table text.
- Button/link visible text.
- Figure captions (when they contain meaningful text).
- Short UI labels inside the content area, if present.

Do not translate:
- URLs in `href`/`src`/`srcset`.
- HTML tag names, class names, ids, `data-*` attributes.
- File paths and references (keep the same relative/absolute URLs).
- Proper names of organisations when they are names (use Russian exonyms only
  if they are standard and unambiguous).

## Output location and naming

For a source file under `data/orientation/en/...`, create a translated file
under:

`translations/ru/orientation/...` (same relative path after `en/`).

Examples:
- `data/orientation/en/learning-materials.html` ->
  `translations/ru/orientation/learning-materials.html`
- `data/orientation/en/learning-materials/finnish-history/main-periods-of-finnish-history-2-independent-finland.html` ->
  `translations/ru/orientation/learning-materials/finnish-history/main-periods-of-finnish-history-2-independent-finland.html`

## Translation workflow (per page)

1. Pick a page from `translations/ru/orientation/PROGRESS.md`.
2. Copy the source HTML from `data/orientation/en/...` to the corresponding
   `translations/ru/orientation/...` path.
3. Remove the site navigation menu blocks ("MENU"):
   - Delete the top header menu container: `<div class="kt-c-site-main-menu-container ..."> ... </div>`.
   - Delete the side menu portlet block: `<div class="... portlet-navigation" ...SiteNavigationMenuPortlet...> ... </div>`.
4. Translate the visible text in-place:
   - Keep whitespace and line breaks reasonably close to the original.
   - Keep punctuation, numbers, years, and named entities accurate.
5. Preserve media:
   - Do not remove images or iframes.
   - Keep `src`, `srcset`, and `href` attributes unchanged.
6. Basic sanity check:
   - The resulting file should still be valid HTML.
   - No accidental removal of `||`-like separators is relevant here; just make
     sure tags remain balanced and the page renders.
7. Update `translations/ru/orientation/PROGRESS.md`:
   - Mark the page as translated (`yes`) or skipped (`yes`).
   - Optionally add notes (e.g., "image captions kept", "table translated").

## Fidelity rules (important)

- Do not simplify the HTML (except removing the "MENU" blocks described above).
- Do not "rewrite" content into a different structure.
- If the original contains English key terms that are defined (e.g., "Welfare
  state:"), translate the definition text but keep the concept faithful.
- If the page contains embedded "Discussion questions" or "Tasks" blocks, keep
  them and translate their visible text too (unless the page is explicitly
  skipped in progress).
