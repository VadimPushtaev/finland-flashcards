"""Separate recorded sequential TTS and ASR lanes without duplicating selected takes."""
from pathlib import Path
import json,time,datetime,sys
import narration_queue as q
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
SECTIONS=['hb-c10-pension','hb-c10-aldre','hb-c11-trafik','hb-c11-nodsituationer','hb-c11-brandsakerhet','hb-c10-funktionsnedsattning']
CONTROL=P/'narration-pipeline-control.json'
lane=sys.argv[1];assert lane in['tts','asr'];q.STATUS=P/f'narration-pipeline-{lane}-status.json'
def status(value,**extra):
 r=dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),lane=lane,status=value,threads=2,**extra);q.STATUS.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
def stage_state(sid,stage):
 owner=P if sid.startswith('hb-c10-')else R/'studio/production/hb-c11-safety';return owner/f'{sid}-{stage}-state.json'
def wait_existing(sid,stage,allow_unstarted=False):
 path=stage_state(sid,stage)
 while True:
  state=q.read(path)
  if state.get('status')=='finished'and state.get('returncode')==0 and not state.get('missing_outputs'):q.verify(sid,stage);return
  if state.get('status')=='failed'or state.get('returncode')not in[None,0]:raise RuntimeError('Preserve selected takes;stage failed:'+str(path))
  if not state and not allow_unstarted:raise RuntimeError('Unexpected absent stage:'+str(path))
  status('waiting_for_selected_stage',section_id=sid,stage=stage,supervisor_pid=state.get('supervisor_pid'));time.sleep(30)
q.verify('hb-c10-psykisk','asr')
for sid in SECTIONS:
 control=q.read(CONTROL)
 if control.get('stop_before_next_stage'):status('stopped_before_stage',section_id=sid);raise SystemExit(0)
 if lane=='tts':
  if sid in control.get('externally_owned_tts',[]):status('externally_assigned_tts_skipped',section_id=sid);continue
  state=q.read(stage_state(sid,'tts'))
  if state.get('status')in['running','starting']:wait_existing(sid,'tts')
  else:status('starting_stage',section_id=sid,stage=lane);q.run_stage(sid,lane)
 else:
  wait_existing(sid,'tts',allow_unstarted=True)
  if q.read(stage_state(sid,'asr')).get('status') in ['running','starting']:
   status('waiting_for_owned_or_loaned_asr',section_id=sid);wait_existing(sid,'asr')
  else:status('starting_stage',section_id=sid,stage=lane);q.run_stage(sid,lane)
status('owned_sequence_complete',sections=SECTIONS,external_tts=q.read(CONTROL).get('externally_owned_tts',[]))
