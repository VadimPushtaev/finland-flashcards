"""Run the actual source/translation/heading/credit/readable-script checks after metadata-only corrections."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;sys.path.insert(0,str(R));from studio.tools import script
owned=json.loads((P/'worker-checkpoint.json').read_text())['exclusive_episodes'];results=[]
for sid in owned:
 e=R/'studio/episodes'/sid;context=script.load_context(sid);data=script.read(e/'script.yaml');script.validate(data,context,ready=True);script.require(script.read(e/'sources.yaml')==script.source_snapshot(context),'Stale source-credit snapshot:'+sid);rendered=script.review_markdown(data,context);(e/'SCRIPT.md').write_text(rendered,encoding='utf-8');script.require((e/'SCRIPT.md').read_text(encoding='utf-8')==rendered,'Readable script mismatch:'+sid);results.append(dict(section_id=sid,ready_source_validation='passed',exact_pairs=len(data['sentences'])));print('PASS',sid,len(data['sentences']),flush=True)
(P/'adaptation-note-source-validation.json').write_text(json.dumps(results,indent=2)+'\n')
