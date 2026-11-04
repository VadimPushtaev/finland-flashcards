"""One bounded exact-input comparison for a repeated-phrase ASR diagnostic."""
from pathlib import Path
import json
import os
import signal
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
PID=109292
OUT='studio/media/hb-c11-agarbostad/retake-repeated-phrase'

def main():
    command=Path(f'/proc/{PID}/cmdline').read_bytes().replace(b'\0',b' ')
    assert b'remaining/asr_controller.py' in command
    deadline=time.monotonic()+1200
    while True:
        os.kill(PID,signal.SIGSTOP)
        children=Path(f'/proc/{PID}/task/{PID}/children').read_text().strip()
        if not children:
            break
        os.kill(PID,signal.SIGCONT)
        assert time.monotonic()<deadline,'No idle diagnostic allocation became available'
        time.sleep(15)
    try:
        assert not (ROOT/OUT).exists(),'Preserve existing comparisons'
        subprocess.run(['studio/runtime/.venv/bin/python','studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--threads','1','--section','hb-c11-agarbostad','--indices','4','--output',OUT],cwd=ROOT,check=True,timeout=600)
        subprocess.run(['studio/runtime/.venv/bin/python','studio/tools/check_audio.py',OUT,'--language','sv','--pattern','hb-*.wav','--threads','1'],cwd=ROOT,check=True,timeout=240)
        print('Bounded comparison complete; original selected take unchanged',flush=True)
    finally:
        os.kill(PID,signal.SIGCONT)

if __name__=='__main__':main()
