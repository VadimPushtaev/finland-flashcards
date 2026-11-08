"""Load canonical Homebrew YAML cards with explicit, content-independent IDs."""
import os
import re
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import yaml

CARDS_DIR = Path(os.environ.get(
    'HOMEBREW_CARDS_DIR', Path(__file__).resolve().parents[2] / 'data/homebrew/cards'))
CHAPTER_IDS = tuple(f'hb-c{i:02d}' for i in range(1, 13))
ID_PATTERN = re.compile(r'^hb-c\d{2}-[a-z0-9-]+-\d{4}$')


def parse_chapter(chapter_id: str, content: str) -> tuple[dict, ...]:
    """Validate canonical chapter data; never infer card IDs from text."""
    if chapter_id not in CHAPTER_IDS:
        raise ValueError(f'Unknown chapter: {chapter_id}')
    document = yaml.safe_load(content)
    if (not isinstance(document, dict) or document.get('schema_version') != 1
            or document.get('chapter_id') != chapter_id
            or document.get('language') != 'sv'
            or not isinstance(document.get('cards'), list)):
        raise ValueError(f'{chapter_id}: invalid canonical YAML document')
    cards = {}
    for number, record in enumerate(document['cards'], 1):
        if not isinstance(record, dict):
            raise ValueError(f'{chapter_id}:{number}: invalid card record')
        identity, section = record.get('id'), record.get('section_id')
        if (not isinstance(identity, str) or not ID_PATTERN.fullmatch(identity)
                or not identity.startswith(chapter_id + '-')
                or not isinstance(section, str) or not identity.startswith(section + '-')):
            raise ValueError(f'{chapter_id}:{number}: invalid stable card ID')
        question, category = record.get('question'), record.get('category')
        if (not isinstance(question, str) or not question.strip()
                or not isinstance(category, str) or not category.strip()):
            raise ValueError(f'{chapter_id}:{number}: missing question/category')
        choices = record.get('options')
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError(f'{chapter_id}:{number}: exactly four options required')
        if any(not isinstance(choice, dict) for choice in choices):
            raise ValueError(f'{chapter_id}:{number}: invalid option')
        ids = [choice.get('id') for choice in choices]
        options = [choice.get('text') for choice in choices]
        if (ids != ['a0', 'a1', 'a2', 'a3']
                or any(not isinstance(text, str) or not text.strip() for text in options)
                or len({text.casefold() for text in options}) != 4
                or record.get('correct_option_id') not in ids):
            raise ValueError(f'{chapter_id}:{number}: invalid choices/correct answer')
        if identity in cards:
            raise ValueError(f'{chapter_id}:{number}: duplicate stable ID {identity}')
        cards[identity] = {
            'id': identity, 'chapter_id': chapter_id, 'section_id': section,
            'question': question, 'topic': category, 'options': options,
            'correct_option': ids.index(record['correct_option_id'])
        }
    if not cards:
        raise ValueError(f'{chapter_id}: empty deck')
    return tuple(cards.values())


@lru_cache(maxsize=12)
def load_chapter(chapter_id: str) -> tuple[dict, ...]:
    if chapter_id not in CHAPTER_IDS:
        raise ValueError(f'Unknown chapter: {chapter_id}')
    return parse_chapter(chapter_id, (CARDS_DIR / f'{chapter_id}.yaml').read_text(encoding='utf-8'))


def install_practice_catalog(app, library):
    """Expose public questions without revealing their answers until checked."""
    router = APIRouter()

    def deck(chapter_id: str):
        if chapter_id not in CHAPTER_IDS:
            raise HTTPException(404, 'Kapitlet finns inte.')
        try:
            return load_chapter(chapter_id)
        except (OSError, ValueError, yaml.YAMLError) as exc:
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
