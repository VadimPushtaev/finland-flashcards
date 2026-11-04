"""Validate every planned Chapter 8 episode against current reviewed bilingual source records."""
from pathlib import Path
import datetime,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'studio/tools'));import script
rows=[]
for ep in sorted((ROOT/'studio/episodes').glob('hb-c08-*')):
 context=script.load_context(ep.name);d=script.read(ep/'script.yaml');script.validate(d,context,ready=True);assert script.read(ep/'sources.yaml')==script.source_snapshot(context);(ep/'SCRIPT.md').write_text(script.review_markdown(d,context));rows.append(dict(section_id=ep.name,sentences=len(d['sentences']),source_section_sha256=d['source_section_sha256'],translation_file_sha256=d['translation_file_sha256'],script_sha256=script.file_hash(ep/'script.yaml'),status='source_and_translation_ready',user_acceptance=False));print(ep.name,'PASS',len(d['sentences']),flush=True)
(ROOT/'studio/production/hb-c08/source-check.json').write_text(json.dumps(dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),episodes=rows,total_sentences=sum(r['sentences'] for r in rows)),ensure_ascii=False,indent=2)+'\n')
