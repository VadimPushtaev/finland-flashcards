"""Cookie authentication and account-scoped reader mutations."""
import hashlib
import os
import secrets
import time
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictBool
from app.accounts import passwords, username_key
from app.database import database, state

COOKIE = 'homebrew_session'
COOKIE_AGE = 365 * 24 * 3600
DUMMY_HASH = passwords.hash(secrets.token_urlsafe(32))
router = APIRouter()


class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=1024)


class Flag(BaseModel):
    model_config = ConfigDict(extra='forbid')
    saved: StrictBool


class Preferences(BaseModel):
    model_config = ConfigDict(extra='forbid')
    size: Literal[18, 20, 22, 24] | None = None
    serif: StrictBool | None = None
    dark: StrictBool | None = None


class Position(BaseModel):
    model_config = ConfigDict(extra='forbid')
    chapter: str = Field(max_length=64)
    section: str = Field(max_length=64)


def token_hash(token):
    """Store only a digest of bearer secrets."""
    return hashlib.sha256(token.encode()).hexdigest()


def set_cookie(response, token):
    """Refresh the browser cookie without imposing a server session expiry."""
    response.set_cookie(COOKIE, token, max_age=COOKIE_AGE, httponly=True, samesite='lax',
                        secure=os.environ.get('STUDY_SECURE_COOKIES', 'false').lower() == 'true', path='/')


def same_origin(request: Request):
    """Require a non-simple same-origin request for every browser mutation."""
    if request.headers.get('x-study-request') != '1':
        raise HTTPException(403, 'Begäran kunde inte verifieras.')
    origin = request.headers.get('origin')
    expected = (os.environ.get('STUDY_PUBLIC_ORIGIN') or str(request.base_url)).rstrip('/')
    if origin and origin != expected:
        raise HTTPException(403, 'Begäran kunde inte verifieras.')
    if request.headers.get('sec-fetch-site') in ('cross-site', 'same-site'):
        raise HTTPException(403, 'Begäran kunde inte verifieras.')


def session(request: Request, response: Response):
    """Resolve a persistent session; account IDs never come from request bodies."""
    token = request.cookies.get(COOKIE, '')
    if not token or len(token) > 256:
        return None
    with database() as db:
        row = db.execute('SELECT users.id, users.username FROM sessions JOIN users '
                         'ON users.id = sessions.user_id WHERE token_hash = ?', (token_hash(token),)).fetchone()
    if row:
        set_cookie(response, token)
        return dict(row)
    return None


def current_user(request: Request, user=Depends(session)):
    """Reject unauthenticated account reads and writes."""
    if user is None:
        raise HTTPException(401, 'Logga in för att spara.')
    expected = request.headers.get('x-study-user')
    if expected is not None and expected != user['username']:
        raise HTTPException(401, 'Kontot har ändrats. Logga in igen för att spara.')
    return user


@router.get('/api/auth/session')
def get_session(response: Response, user=Depends(session)):
    response.headers['Cache-Control'] = 'no-store'
    return {'user': {'username': user['username']} if user else None}


@router.post('/api/auth/login', dependencies=[Depends(same_origin)])
def login(body: Credentials, request: Request, response: Response):
    now = int(time.time())
    # Use the direct peer, not untrusted arbitrary X-Forwarded-For values.
    address = request.client.host if request.client else 'unknown'
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM login_attempts WHERE attempted_at < ?', (now - 300,))
        count = db.execute('SELECT count(*) FROM login_attempts WHERE address = ?', (address,)).fetchone()[0]
        if count >= int(os.environ.get('STUDY_LOGIN_LIMIT', '10')):
            raise HTTPException(429, 'För många försök. Vänta fem minuter och försök igen.', headers={'Retry-After': '300'})
        db.execute('INSERT INTO login_attempts VALUES (?, ?)', (address, now))
    try:
        name = username_key(body.username)
    except ValueError:
        name = ''
    with database() as db:
        user = db.execute('SELECT * FROM users WHERE username = ?', (name,)).fetchone()
    valid = passwords.verify(body.password, user['password_hash'] if user else DUMMY_HASH)
    if not user or not valid:
        raise HTTPException(401, 'Fel användarnamn eller lösenord.')
    token = secrets.token_urlsafe(32)
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        # A concurrent password reset cannot issue a session for the old password.
        fresh = db.execute('SELECT password_hash FROM users WHERE id = ?', (user['id'],)).fetchone()
        if not fresh or fresh['password_hash'] != user['password_hash']:
            raise HTTPException(401, 'Fel användarnamn eller lösenord.')
        db.execute('DELETE FROM sessions WHERE token_hash = ?', (token_hash(request.cookies.get(COOKIE, '')),))
        db.execute('INSERT INTO sessions VALUES (?, ?, ?)', (token_hash(token), user['id'], now))
    set_cookie(response, token)
    response.headers['Cache-Control'] = 'no-store'
    return {'user': {'username': user['username']}}


@router.post('/api/auth/logout', dependencies=[Depends(same_origin)])
def logout(request: Request, response: Response):
    with database() as db:
        db.execute('DELETE FROM sessions WHERE token_hash = ?', (token_hash(request.cookies.get(COOKIE, '')),))
    response.delete_cookie(COOKIE, path='/')
    response.headers['Cache-Control'] = 'no-store'
    return {'ok': True}


@router.get('/api/state')
def get_state(response: Response, user=Depends(current_user)):
    response.headers['Cache-Control'] = 'no-store'
    with database() as db:
        return state(db, user['id'])


def install_routes(app, get_chapter, get_passage):
    """Bind anthology validation without introducing circular imports."""
    @router.put('/api/state/bookmarks/{unit_id}', dependencies=[Depends(same_origin)])
    def bookmark(unit_id: str, body: Flag, user=Depends(current_user)):
        if body.saved:
            get_passage(unit_id)
        with database() as db:
            if body.saved:
                db.execute('INSERT OR IGNORE INTO bookmarks VALUES (?, ?)', (user['id'], unit_id))
            else:
                db.execute('DELETE FROM bookmarks WHERE user_id = ? AND unit_id = ?', (user['id'], unit_id))
        return {'saved': body.saved}

    @router.put('/api/state/completed/{section_id}', dependencies=[Depends(same_origin)])
    def completion(section_id: str, body: Flag, user=Depends(current_user)):
        chapter = get_chapter(section_id[:6])
        if not any(s['id'] == section_id for s in chapter['sections']):
            raise HTTPException(404, 'Avsnittet finns inte.')
        with database() as db:
            if body.saved:
                db.execute('INSERT OR IGNORE INTO completed VALUES (?, ?)', (user['id'], section_id))
            else:
                db.execute('DELETE FROM completed WHERE user_id = ? AND section_id = ?', (user['id'], section_id))
        return {'saved': body.saved}

    @router.patch('/api/state/preferences', dependencies=[Depends(same_origin)])
    def preferences(body: Preferences, user=Depends(current_user)):
        patch = body.model_dump(exclude_unset=True)
        if not patch or any(v is None for v in patch.values()):
            raise HTTPException(422, 'Ogiltiga läsinställningar.')
        with database() as db:
            columns = ', '.join(f'{key} = ?' for key in patch)
            db.execute(f'UPDATE settings SET {columns} WHERE user_id = ?', (*patch.values(), user['id']))
        return patch

    @router.patch('/api/state/position', dependencies=[Depends(same_origin)])
    def position(body: Position, user=Depends(current_user)):
        chapter = get_chapter(body.chapter)
        if not any(s['id'] == body.section for s in chapter['sections']):
            raise HTTPException(404, 'Avsnittet finns inte.')
        with database() as db:
            db.execute('UPDATE settings SET last_chapter = ?, last_section = ? WHERE user_id = ?',
                       (body.chapter, body.section, user['id']))
        return body.model_dump()

    app.include_router(router)
