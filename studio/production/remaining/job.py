"""Start or supervise an exact local production job, retaining PID/log/status.

Launch `start CONFIG.json` from an unsandboxed approved local command so the
supervisor can survive the transient tool session. Commands are argument lists,
never shell strings. A per-job lock rejects duplicate supervisors. This runner
does not retry, synthesize over existing takes, or promote production milestones.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix('.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(path)


def wait_for_startup(process, state_path):
    """Publish a launch only after its exact supervisor has written atomic state."""
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            state = json.loads(state_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}
        if state.get('supervisor_pid') == process.pid:
            return
        if process.poll() is not None:
            raise SystemExit('Supervisor exited before publishing matching state; inspect job log')
        time.sleep(.05)
    raise SystemExit('Supervisor startup state is delayed; inspect exact PID/log before any retry')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['start','run'])
    parser.add_argument('config', type=Path)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text())
    state_path = ROOT/config['state']
    log_path = ROOT/config['log']
    for path in (state_path,log_path):
        if not path.resolve().is_relative_to(ROOT/'studio/production'):
            parser.error('Keep job state and logs inside studio/production')
        path.parent.mkdir(parents=True,exist_ok=True)
    command = config['command']
    if not isinstance(command,list) or not command or not all(isinstance(x,str) for x in command):
        parser.error('Command must be a nonempty argument list')
    if args.action=='start':
        with log_path.open('a') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'run',str(config_path)],
                cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                start_new_session=True,close_fds=True)
        wait_for_startup(process, state_path)
        print(json.dumps(dict(supervisor_pid=process.pid,config=str(config_path),log=str(log_path))))
        return
    with state_path.with_suffix('.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('An existing supervisor already owns this exact job')
        for path in config.get('refuse_existing_outputs',[]):
            if (ROOT/path).exists():
                raise SystemExit('Retain existing output and prepare an explicit resume plan: '+path)
        state=dict(section_id=config['section_id'],stage=config['stage'],status='running',
                   supervisor_pid=os.getpid(),command=command,started_at=now(),log=config['log'])
        with log_path.open('a') as log:
            child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,
                                   stderr=subprocess.STDOUT,close_fds=True)
            state['pid']=child.pid
            save(state_path,state)
            while True:
                try:
                    result=child.wait(timeout=30)
                    break
                except subprocess.TimeoutExpired:
                    state['heartbeat_at']=now()
                    save(state_path,state)
                    print(f'{now()} {config["section_id"]} {config["stage"]}: PID {child.pid} running',flush=True)
            missing=[path for path in config.get('expected_outputs',[]) if not (ROOT/path).is_file()]
            state.update(returncode=result,finished_at=now(),missing_outputs=missing,
                         status='finished' if result==0 and not missing else 'failed')
            save(state_path,state)
            print(json.dumps(state),flush=True)
            if state['status']=='failed':
                raise SystemExit(result or 1)


if __name__=='__main__':
    main()
