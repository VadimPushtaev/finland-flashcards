"""Rebuild this episode foregrounds, then apply pinned photographic overrides."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SECTION = Path(__file__).resolve().parent.name
sys.path.insert(0, str(ROOT / 'studio/production/hb-c09a'))
from family_art import prepare

if __name__ == '__main__':
    prepare(SECTION)
    subprocess.run([sys.executable,
                    str(ROOT / 'studio/production/hb-c09a/prepare_photo_overrides.py'),
                    SECTION], cwd=ROOT, check=True)
