"""Run browser checks against a disposable database, never the Compose volume."""
import os
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import uvicorn

if __name__ == '__main__':
    path = Path(os.environ['STUDY_DATABASE_PATH'])
    if not path.parent.name.startswith('homebrew-e2e-'):
        raise RuntimeError('Browser tests require an isolated homebrew-e2e- directory.')
    os.environ['STUDY_LOGIN_LIMIT'] = '10000'
    os.environ['STUDY_SECURE_COOKIES'] = 'false'
    os.environ['STUDY_PUBLIC_ORIGIN'] = 'http://127.0.0.1:18745'
    try:
        uvicorn.run('app.main:app', host='127.0.0.1', port=18745)
    finally:
        shutil.rmtree(path.parent, ignore_errors=True)
