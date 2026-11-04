"""Resume owned narration in small retained chunks under the host supervisor.

The control file is read between chunks. Existing selected takes are fingerprinted
and retained byte for byte. Every new chunk has its own metrics and seed scope.
"""
from datetime import datetime,timezone
from pathlib import Path
import fcntl,hashlib,json,math,os,shutil,subprocess,time
import numpy as np
import soundfile as sf
import yaml
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
CONTROL=P/'tts-control.json';STATE=P/'durable-tts-progress.json'
def write(path,value):
    tmp=path.with_suffix('.writing');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def file_info(path):
    data,rate=sf.read(path,dtype='float32');assert data.ndim==1 and rate==44100 and np.isfinite(data).all();peak=float(np.abs(data).max());assert .001<peak<.999
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),seconds=len(data)/rate,sample_rate=rate,peak=peak)
def run(command,log,state):
    with log.open('a') as stream:
        process=subprocess.Popen(command,cwd=R,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
        state.update(pid=process.pid,command=command,log=str(log.relative_to(R)),started=time.time());write(STATE,state)
        while process.poll() is None:
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                state['heartbeat']=time.time();write(STATE,state);print(state['section_id'],state['stage'],'running for',round(time.time()-state['started']),'seconds',flush=True)
        if process.returncode:
            state.update(status='failed',returncode=process.returncode);write(STATE,state);raise RuntimeError('Owned job failed; retained takes preserved. See '+str(log))
def retained(sid,script):
    folder=R/'studio/media'/sid/'narration';folder.mkdir(parents=True,exist_ok=True);path=folder/'metrics.json';records=json.loads(path.read_text()) if path.exists() else [];source={r['sentence_id']:r for r in script['sentences']};seen=set()
    for m in records:
        assert m['sentence_id'] in source and m['sentence_id'] not in seen;seen.add(m['sentence_id']);row=source[m['sentence_id']]
        assert m['text']==(row.get('speech_override') or {}).get('text',row['sv']);facts=file_info(R/m['path']);assert abs(facts['seconds']-m['seconds'])<.001
        m.setdefault('sha256',facts['sha256']);m.setdefault('generation_run','Initial complete source-order invocation, NumPy seed 42; retained before durable resumption.')
    return folder,records
with (P/'durable-tts.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state=dict(owner='chapter09a',status='running',controller_pid=os.getpid(),episodes={})
    while True:
        control=json.loads(CONTROL.read_text())
        if control.get('pause'):
            state.update(status='paused_at_checkpoint',pid=None);write(STATE,state);print('Owned narration queue paused at a safe checkpoint.',flush=True);break
        chosen=None
        for sid in control['order']:
            script_path=R/'studio/episodes'/sid/'script.yaml';script=yaml.safe_load(script_path.read_text());folder,records=retained(sid,script)
            if len(records)==len(script['sentences']):state['episodes'][sid]=dict(status='complete',clips=len(records));continue
            if not script['episode_decisions'] or not (script_path.parent/'visual-plan.json').exists():
                state['episodes'][sid]=dict(status='waiting_for_editorial_plan',retained_clips=len(records));continue
            chosen=sid,script,folder,records;break
        if chosen is None:
            waiting=[k for k,v in state['episodes'].items() if v['status']!='complete']
            state.update(status='waiting_for_editorial_plan' if waiting else 'complete',pid=None);write(STATE,state)
            if not waiting:write(P/'tts-completed.json',state)
            print('Owned narration queue checkpoint:',state['status'],flush=True);break
        sid,script,folder,records=chosen;ep=R/'studio/episodes'/sid;state.update(section_id=sid,status='running')
        if state['episodes'].get(sid,{}).get('validated') is not True:
            for operation in ['review','validate']:
                state['stage']='source_'+operation;run([str(R/'.venv/bin/python'),str(R/'studio/tools/script.py'),operation,sid,'--ready'],P/(sid+'-durable-source.log'),state)
            state['episodes'][sid]=dict(validated=True,status='synthesizing',retained_clips=len(records))
        fingerprints={m['sentence_id']:file_info(R/m['path']) for m in records};preservation=ep/'narration-preservation.json'
        if not preservation.exists():write(preservation,dict(reason='Retain all complete selected takes before resuming only missing source sentences.',clips=fingerprints))
        existing={m['sentence_id'] for m in records};missing=[i for i,r in enumerate(script['sentences']) if r['sentence_id'] not in existing];indices=missing[:control.get('chunk_size',8)]
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');chunk=folder.parent/('narration-resume-'+stamp);state['stage']='tts_chunk';state['indices']=indices
        command=[str(R/'studio/runtime/.venv/bin/python'),str(R/'studio/tools/audition.py'),'supertonic','--voice','F1','--speed','.95','--threads',str(control.get('threads',2)),'--section',sid,'--indices',','.join(map(str,indices)),'--output',str(chunk)]
        run(command,P/(sid+'-durable-tts.log'),state);new=json.loads((chunk/'metrics.json').read_text());assert [m['sentence_id'] for m in new]==[script['sentences'][i]['sentence_id'] for i in indices]
        for m in new:
            original=R/m['path'];facts=file_info(original);target=folder/original.name
            if target.exists():
                orphan=folder.parent/'narration-incomplete-orphans';orphan.mkdir(exist_ok=True);backup=orphan/(stamp+'-'+target.name);target.rename(backup)
            shutil.copy2(original,target);assert hashlib.sha256(target.read_bytes()).hexdigest()==facts['sha256'];m['path']=str(target.relative_to(R));m['sha256']=facts['sha256'];m['generation_run']='Durable resume chunk '+stamp+'; NumPy seed 42 at chunk start, ordered source indices '+','.join(map(str,indices))+'.';m['retained_chunk_metrics']=str((chunk/'metrics.json').relative_to(R));records.append(m)
        by_id={m['sentence_id']:m for m in records};ordered=[by_id[r['sentence_id']] for r in script['sentences'] if r['sentence_id'] in by_id]
        for sentence_id,facts in fingerprints.items():assert file_info(R/by_id[sentence_id]['path'])['sha256']==facts['sha256'],'An existing selected take changed'
        write(folder/'metrics.json',ordered);state['episodes'][sid].update(status='complete' if len(ordered)==len(script['sentences']) else 'synthesizing',retained_clips=len(ordered));write(STATE,state)
        print(sid,'retained',len(ordered),'of',len(script['sentences']),'complete clips.',flush=True)
