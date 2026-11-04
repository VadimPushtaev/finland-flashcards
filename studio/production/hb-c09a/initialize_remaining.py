"""Scaffold the rest of exclusively assigned Chapter9 against reviewed records."""
from pathlib import Path
import sys,yaml
sys.path.insert(0,str(Path.cwd()/'studio/tools'));import script
inventory=yaml.safe_load(Path('studio/episodes.yaml').read_text())['episodes']
for row in inventory:
    if row['chapter_id']!='hb-c09':continue
    sid=row['section_id'];ep=Path('studio/episodes')/sid
    if not ep.exists():script.initialize(script.load_context(sid),ep);print(sid,'initialized',flush=True)
