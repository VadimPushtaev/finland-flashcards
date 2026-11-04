"""Initialize owned Chapter 9 scripts against reviewed source snapshots."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'studio/tools'))
import script
for slug in ['familjeformer','kon','samlevnad','aktenskap','makar']:
    sid='hb-c09-'+slug; ep=Path('studio/episodes')/sid
    if not ep.exists():
        script.initialize(script.load_context(sid),ep)
        print(sid,'initialized',flush=True)
