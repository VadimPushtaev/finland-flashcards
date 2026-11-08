"""Authenticated FSRS scheduling and personal review history for Homebrew cards."""
from datetime import datetime, timezone
import os
from pathlib import Path
import yaml

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from fsrs import Card, Rating, Scheduler

from app.auth import current_user, same_origin
from app.database import database
from app.flashcards import CHAPTER_IDS, load_chapter
from app.translations import reviewed_records

router = APIRouter()
GRADE_NAMES = {1: 'Again', 2: 'Hard', 3: 'Good', 4: 'Easy'}


def utc_now():
    return datetime.now(timezone.utc)


def scheduler_for(retention):
    return Scheduler(desired_retention=retention, enable_fuzzing=False)


def retention_for(db, user_id):
    row = db.execute('SELECT desired_retention FROM practice_preferences WHERE user_id=?',
                     (user_id,)).fetchone()
    return row['desired_retention'] if row else 0.90


def deck(chapter_id):
    if chapter_id not in CHAPTER_IDS:
        raise HTTPException(404, 'Kapitlet finns inte.')
    try:
        return load_chapter(chapter_id)
    except (OSError, ValueError) as error:
        raise HTTPException(503, f'Kortleken kunde inte läsas: {error}') from error


def current_rows(db, user_id, chapter_id):
    return {row['card_id']: row for row in db.execute(
        'SELECT card_id, fsrs_json, due_at FROM practice_cards WHERE user_id=? AND chapter_id=?',
        (user_id, chapter_id))}


def exposed(card):
    return {key: value for key, value in card.items() if key != 'correct_option'}


def due_cards(db, user_id, chapter_id, now):
    saved = current_rows(db, user_id, chapter_id)
    return [exposed(card) for card in deck(chapter_id)
            if card['id'] not in saved or datetime.fromisoformat(saved[card['id']]['due_at']) <= now]


def install_practice_routes(app, library):
    @router.get('/api/practice/overview')
    def overview(user=Depends(current_user)):
        _, chapters, _ = library()
        now = utc_now()
        with database() as db:
            values = []
            for number, chapter_id in enumerate(CHAPTER_IDS, 1):
                all_cards = deck(chapter_id)
                saved = current_rows(db, user['id'], chapter_id)
                due = sum(1 for card in all_cards if card['id'] in saved
                          and datetime.fromisoformat(saved[card['id']]['due_at']) <= now)
                values.append({'id': chapter_id, 'order': number, 'title': chapters[chapter_id]['title'],
                               'total': len(all_cards), 'new': len(all_cards) - sum(c['id'] in saved for c in all_cards),
                               'due': due})
            return {'chapters': values, 'desired_retention': retention_for(db, user['id'])}

    @router.get('/api/practice/chapters/{chapter_id}/queue')
    def queue(chapter_id: str, user=Depends(current_user)):
        with database() as db:
            return {'chapter_id': chapter_id, 'cards': due_cards(db, user['id'], chapter_id, utc_now())}

    @router.get('/api/practice/settings')
    def settings(user=Depends(current_user)):
        with database() as db:
            return {'desired_retention': retention_for(db, user['id'])}

    class Preferences(BaseModel):
        desired_retention: float = Field(ge=0.70, le=0.99)

    @router.patch('/api/practice/settings', dependencies=[Depends(same_origin)])
    def set_settings(body: Preferences, user=Depends(current_user)):
        with database() as db:
            db.execute('INSERT INTO practice_preferences (user_id, desired_retention) VALUES (?, ?) '
                       'ON CONFLICT(user_id) DO UPDATE SET desired_retention=excluded.desired_retention',
                       (user['id'], body.desired_retention))
        return body.model_dump()

    class Review(BaseModel):
        event_id: str = Field(min_length=8, max_length=128, pattern=r'^[a-zA-Z0-9_-]+$')
        card_id: str = Field(min_length=8, max_length=128)
        option: int = Field(ge=0, le=3)
        grade: int = Field(ge=1, le=4)
        translation_used: bool = False
        kind: str = Field(default='normal', pattern=r'^(normal|retry|extra)$')

    @router.post('/api/practice/chapters/{chapter_id}/review',
                 dependencies=[Depends(same_origin)])
    def review(chapter_id: str, body: Review, user=Depends(current_user)):
        card = next((item for item in deck(chapter_id) if item['id'] == body.card_id), None)
        if not card:
            raise HTTPException(404, 'Frågan finns inte.')
        correct = body.option == card['correct_option']
        suggested = 3 if correct and not body.translation_used else 2 if correct else 1
        now = utc_now()
        with database() as db:
            db.execute('BEGIN IMMEDIATE')
            earlier = db.execute('SELECT user_id, card_id, due_at FROM practice_events WHERE event_id=?',
                                 (body.event_id,)).fetchone()
            if earlier:
                if earlier['user_id'] != user['id'] or earlier['card_id'] != body.card_id:
                    raise HTTPException(409, 'Review key already in use.')
                return {'saved': True, 'duplicate': True, 'due_at': earlier['due_at']}
            existing = db.execute('SELECT fsrs_json FROM practice_cards WHERE user_id=? AND card_id=?',
                                  (user['id'], body.card_id)).fetchone()
            memory = Card.from_json(existing['fsrs_json']) if existing else Card()
            fsrs = scheduler_for(retention_for(db, user['id']))
            memory, log = fsrs.review_card(memory, Rating(body.grade), review_datetime=now)
            due = memory.due.isoformat()
            db.execute('INSERT INTO practice_cards (user_id, card_id, chapter_id, fsrs_json, due_at) '
                       'VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id, card_id) DO UPDATE SET '
                       'chapter_id=excluded.chapter_id, fsrs_json=excluded.fsrs_json, due_at=excluded.due_at',
                       (user['id'], body.card_id, chapter_id, memory.to_json(), due))
            db.execute('INSERT INTO practice_events '
                       '(event_id, user_id, card_id, chapter_id, reviewed_at, option, correct_option, correct, '
                       'translation_used, suggested_grade, final_grade, kind, due_at, fsrs_log) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (body.event_id, user['id'], body.card_id, chapter_id, now.isoformat(),
                        body.option, card['correct_option'], int(correct), int(body.translation_used),
                        suggested, body.grade, body.kind, due, log.to_json()))
        return {'saved': True, 'duplicate': False, 'correct': correct, 'suggested_grade': suggested,
                'grade': body.grade, 'due_at': due}

    class Extra(BaseModel):
        threshold: float = Field(ge=0.70, le=0.99)
        excluded_ids: list[str] = Field(default_factory=list, max_length=2000)

    @router.post('/api/practice/chapters/{chapter_id}/extra',
                 dependencies=[Depends(same_origin)])
    def extra(chapter_id: str, body: Extra, user=Depends(current_user)):
        now = utc_now()
        excluded = set(body.excluded_ids)
        with database() as db:
            saved = current_rows(db, user['id'], chapter_id)
            fsrs = scheduler_for(retention_for(db, user['id']))
            future = [(card, saved[card['id']]) for card in deck(chapter_id)
                      if card['id'] in saved and card['id'] not in excluded
                      and datetime.fromisoformat(saved[card['id']]['due_at']) > now]
            candidates = [card for card, row in future
                          if fsrs.get_card_retrievability(Card.from_json(row['fsrs_json']),
                                                         current_datetime=now) <= body.threshold]
            # Prefer cards not used this session; when all were just studied,
            # still offer the nearest scheduled reviews as an explicit fallback.
            nearest = sorted(future, key=lambda pair: pair[1]['due_at'])
            if not nearest and not candidates:
                nearest = sorted(
                    ((card, saved[card['id']]) for card in deck(chapter_id)
                     if card['id'] in saved and datetime.fromisoformat(saved[card['id']]['due_at']) > now),
                    key=lambda pair: pair[1]['due_at'])
            fallback = [card for card, _ in nearest[:10]] if not candidates else []
            return {'cards': [exposed(card) for card in candidates],
                    'fallback': [exposed(card) for card in fallback],
                    'count': len(candidates), 'fallback_count': len(fallback)}

    @router.get('/api/practice/chapters/{chapter_id}/cards/{card_id}/translation')
    def card_translation(chapter_id: str, card_id: str):
        """Serve only reviewed, source-matched card translations when present."""
        card = next((item for item in deck(chapter_id) if item['id'] == card_id), None)
        if card is None:
            raise HTTPException(404, 'Frågan finns inte.')
        unavailable = {'available': False, 'language': 'ru', 'records': {}}
        source = {card_id + ':q': card['question']}
        source.update({card_id + ':a' + str(index): answer
                       for index, answer in enumerate(card['options'])})
        data = Path(os.environ.get('HOMEBREW_DATA_DIR',
                    Path(__file__).resolve().parents[2] / 'data/homebrew'))
        base = data / 'ru'
        def read(path):
            return yaml.safe_load(path.read_text(encoding='utf-8'))
        try:
            terms = {entry['id']: entry for entry in read(base / 'glossary.yaml')['entries']}
            records = reviewed_records(base, card_id, 'cards', source, terms, read)
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError):
            return unavailable
        return ({'available': True, 'language': 'ru', 'records': records}
                if records is not None else unavailable)

    @router.get('/api/practice/cards/{card_id}/stats')
    def stats(card_id: str, user=Depends(current_user)):
        with database() as db:
            events = [dict(row) for row in db.execute(
                'SELECT reviewed_at, chapter_id, option, correct_option, correct, translation_used, '
                'suggested_grade, final_grade, kind, due_at FROM practice_events '
                'WHERE user_id=? AND card_id=? ORDER BY reviewed_at DESC, rowid DESC',
                (user['id'], card_id))]
        return {'card_id': card_id, 'total': len(events),
                'correct': sum(e['correct'] for e in events),
                'incorrect': sum(not e['correct'] for e in events),
                'with_translation': sum(e['translation_used'] for e in events),
                'grades': {GRADE_NAMES[i]: sum(e['final_grade'] == i for e in events)
                           for i in GRADE_NAMES},
                'breakdown': {
                    f'{"correct" if correct else "incorrect"}_{"translated" if translated else "unassisted"}':
                        sum(e['correct'] == correct and e['translation_used'] == translated for e in events)
                    for correct in (0, 1) for translated in (0, 1)},
                'events': events}

    app.include_router(router)
