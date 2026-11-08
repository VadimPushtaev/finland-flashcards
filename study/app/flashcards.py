"""Read Homebrew multiple-choice chapter decks without changing source files."""
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

CARDS_DIR = Path(os.environ.get(
    'HOMEBREW_CARDS_DIR', Path(__file__).resolve().parents[2] / 'cards/homebrew'))
CHAPTER_IDS = tuple(f'hb-c{i:02d}' for i in range(1, 13))


def parse_chapter(chapter_id: str, content: str) -> tuple[dict, ...]:
    """Parse one chapter ALL.txt; stable content IDs deliberately reset on edits."""
    if chapter_id not in CHAPTER_IDS:
        raise ValueError(f'Unknown chapter: {chapter_id}')
    cards = {}
    for number, line in enumerate(content.splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split('|')
        if len(fields) != 10:
            raise ValueError(f'{chapter_id}:{number}: expected 10 pipe-separated fields')
        question, topic = fields[0].strip(), fields[1].strip()
        options = [part.strip() for part in fields[3:7]]
        flags = fields[8].split()
        if (not question or not topic or any(not option for option in options)
                or len(flags) != 4 or flags.count('1') != 1
                or any(flag not in ('0', '1') for flag in flags)):
            raise ValueError(f'{chapter_id}:{number}: invalid question, choices or answer flags')
        correct_option = flags.index('1')
        identity = [chapter_id, question, options, correct_option]
        card_id = hashlib.sha256(json.dumps(
            identity, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
        card = {'id': card_id, 'chapter_id': chapter_id, 'question': question,
                'topic': topic, 'options': options, 'correct_option': correct_option}
        # Identical lines represent one logical card, even if repeated in the source.
        if card_id in cards and cards[card_id] != card:
            raise ValueError(f'{chapter_id}:{number}: card ID collision')
        cards[card_id] = card
    if not cards:
        raise ValueError(f'{chapter_id}: empty deck')
    return tuple(cards.values())


@lru_cache(maxsize=12)
def load_chapter(chapter_id: str) -> tuple[dict, ...]:
    if chapter_id not in CHAPTER_IDS:
        raise ValueError(f'Unknown chapter: {chapter_id}')
    return parse_chapter(chapter_id, (CARDS_DIR / chapter_id / 'ALL.txt').read_text(encoding='utf-8'))


def install_practice_catalog(app, library):
    """Expose read-only questions and stateless server-side answer verification."""
    router = APIRouter()

    def deck(chapter_id: str):
        if chapter_id not in CHAPTER_IDS:
            raise HTTPException(404, 'Kapitlet finns inte.')
        try:
            return load_chapter(chapter_id)
        except (OSError, ValueError) as exc:
            raise HTTPException(503, f'Kortleken kunde inte läsas: {exc}') from exc

    @router.get('/api/practice/chapters')
    def chapters():
        _, library_chapters, _ = library()
        return {'chapters': [
            {'id': chapter_id, 'order': number, 'title': library_chapters[chapter_id]['title'],
             'total': len(deck(chapter_id))}
            for number, chapter_id in enumerate(CHAPTER_IDS, 1)]}

    @router.get('/api/practice/chapters/{chapter_id}/cards')
    def cards(chapter_id: str):
        return {'chapter_id': chapter_id, 'cards': [
            {key: value for key, value in card.items() if key != 'correct_option'}
            for card in deck(chapter_id)]}

    class Answer(BaseModel):
        option: int = Field(ge=0, le=3)

    @router.post('/api/practice/chapters/{chapter_id}/cards/{card_id}/check')
    def check(chapter_id: str, card_id: str, body: Answer):
        card = next((card for card in deck(chapter_id) if card['id'] == card_id), None)
        if card is None:
            raise HTTPException(404, 'Frågan finns inte.')
        return {'correct': body.option == card['correct_option'],
                'correct_option': card['correct_option']}

    app.include_router(router)
