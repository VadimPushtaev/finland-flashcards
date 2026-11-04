"""Append five source-ready batches after the existing two-thread queue.

The current prefix process keeps its source order and selected takes untouched.
This supervisor waits without starting heavy work until that entire prefix has
completed and its narration/ASR hashes pass again. It then reuses the same lane.
"""
from pathlib import Path
import json
import time
import datetime
from narration_queue import run_stage, verify, stopped, read
R = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parent
DEPENDENCY = P / 'narration-queue-supervisor-state.json'
STATUS = P / 'narration-queue-extension-status.json'
PREFIX = ['hb-c10-tillgang', 'hb-c10-lakemedel', 'hb-c11-bibliotek', 'hb-c11-fritid']
APPENDED = ['hb-c10-sjukdom', 'hb-c10-sexuell', 'hb-c10-psykisk', 'hb-c10-pension', 'hb-c10-aldre']


def status(state, **kwargs):
    record = dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  status=state, allocation_threads=2, appended=APPENDED, **kwargs)
    STATUS.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    while read(DEPENDENCY).get('status') != 'finished':
        status('waiting_for_existing_queue', dependency=str(DEPENDENCY.relative_to(R)))
        time.sleep(30)
    if read(DEPENDENCY).get('returncode') != 0:
        raise RuntimeError('Existing queue failed; preserve all takes and do not acquire another lane.')
    if stopped():
        status('stopped_before_extension')
        raise SystemExit(0)
    for section in PREFIX:
        verify(section, 'asr')
    for section in APPENDED:
        for stage in ['tts', 'asr']:
            status('using_existing_lane', section_id=section, stage=stage)
            run_stage(section, stage)
    status('complete')
