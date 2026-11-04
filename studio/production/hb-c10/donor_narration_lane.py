"""Use a released two-thread donor lane for one bounded comparison,then four untouched TTS batches."""
from pathlib import Path
import json,subprocess,time,datetime
import narration_queue as q
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;q.STATUS=P/'donor-narration-status.json'
release=q.read(P/'donor-narration-release.json');assert release.get('status')=='released'and release.get('coordinator_authorized'), 'Wait for exact coordinator donor-lane release.'
def run_job(config):
 j=q.read(P/config);state=R/j['state'];s=q.read(state)
 if s.get('status')not in['running','finished']:
  assert not s.get('returncode'),'Prior targeted failure requires missing-only recovery.'
  subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/job.py','start',str((P/config).relative_to(R))],cwd=R,check=True)
 while True:
  s=q.read(state)
  if s.get('status')=='finished'and s.get('returncode')==0 and not s.get('missing_outputs'):return
  if s.get('status')=='failed'or s.get('returncode')not in[None,0]:raise RuntimeError('Preserve targeted takes;job failed:'+str(state))
  print(json.dumps(dict(stage=j['stage'],status=s.get('status'),supervisor=s.get('supervisor_pid'),updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat())),flush=True);time.sleep(30)
run_job('mental-112-tts-job.json');run_job('mental-112-asr-job.json');subprocess.run([str(R/'.venv/bin/python'),'studio/production/hb-c10/select_mental_112.py'],cwd=R,check=True)
if q.read(R/'studio/episodes/hb-c10-psykisk/emergency112-comparison.json').get('selected'):
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/job.py','start','studio/production/hb-c10/mental-preflight-job.json'],cwd=R,check=True)
for section in['hb-c11-trafik','hb-c11-nodsituationer','hb-c11-brandsakerhet','hb-c10-funktionsnedsattning']:q.run_stage(section,'tts')
print('Released donor TTS lane complete;all selected takes preserved,ASR handled by recorded independent lane.',flush=True)
