"""Resolve ordered video filenames while preserving stable source IDs."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def export_stem(section_id, root=ROOT):
    """Include the inventory's subchapter position in the exported filename."""
    inventory = yaml.safe_load((root / 'studio/episodes.yaml').read_text())
    episode = next(e for e in inventory['episodes'] if e['section_id'] == section_id)
    chapter = episode['chapter_id']
    slug = section_id.removeprefix(chapter + '-')
    return f"{chapter}-{episode['section_order']:02d}-{slug}"
