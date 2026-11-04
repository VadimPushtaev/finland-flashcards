"""Resume missing Chapter 8 source-backed episode scaffolds."""
from pathlib import Path
import sys,yaml,json,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import script
rows=[e for e in script.read(ROOT/'studio/episodes.yaml')['episodes'] if e['chapter_id']=='hb-c08']
for e in rows:
 sid=e['section_id'];ep=ROOT/'studio/episodes'/sid
 if ep.exists():continue
 context=script.load_context(sid);script.initialize(context,ep);print(sid,len(script.read(ep/'script.yaml')['sentences']),flush=True)
