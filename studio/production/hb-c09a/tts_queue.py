"""Resumable owned narration queue: retain completed runs and log exact PIDs."""
import subprocess,json,os,time
from pathlib import Path
R=Path.cwd();P=R/'studio/production/hb-c09a';state={};out=P/'tts-state.json'
for slug in ['samlevnad','makar','aktenskap','familjeformer','kon','forandring']:
    sid='hb-c09-'+slug;media=R/'studio/media'/sid/'narration';metrics=media/'metrics.json'
    if metrics.exists():
        d=json.loads(metrics.read_text());import yaml
        expected=yaml.safe_load((R/'studio/episodes'/sid/'script.yaml').read_text())['sentences']
        if len(d)==len(expected):state[sid]={'stage':'tts_done','retained':True,'clips':len(d)};out.write_text(json.dumps(state,indent=2));continue
        raise RuntimeError('Partial retained narration requires explicit resume merging: '+sid)
    for cmd in [['.venv/bin/python','studio/tools/script.py','review',sid,'--ready'],['.venv/bin/python','studio/tools/script.py','validate',sid,'--ready'],['studio/runtime/.venv/bin/python','studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--section',sid,'--all','--threads','2','--output',str(media.relative_to(R))]]:
        stage='tts' if 'audition.py' in cmd[1] else cmd[2]
        with (P/(sid+'-'+stage+'.log')).open('a') as log:
            proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            state[sid]={'stage':stage,'pid':proc.pid,'controller_pid':os.getpid(),'started':time.time(),'command':cmd};out.write_text(json.dumps(state,indent=2));print(sid,stage,proc.pid,flush=True)
            while proc.poll() is None:
                try:proc.wait(timeout=35)
                except subprocess.TimeoutExpired:print(sid,stage,'still running',round(time.time()-state[sid]['started']),'seconds',flush=True)
            rc=proc.returncode
        if rc:state[sid].update(stage=stage+'_failed',returncode=rc);out.write_text(json.dumps(state,indent=2));raise SystemExit(rc)
    state[sid]={'stage':'tts_done','clips':len(json.loads(metrics.read_text()))};out.write_text(json.dumps(state,indent=2))
