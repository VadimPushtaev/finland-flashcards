"""Acquire explicitly selected root media, pin masters and draw planned pictures."""
from pathlib import Path
import subprocess
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]


def main(sections):
    queue=yaml.safe_load((ROOT/'studio/production/remaining/queue.yaml').read_text())['episodes']
    for section in sections:
        if next(r['owner'] for r in queue if r['section_id']==section)!='root':
            raise ValueError('Not root-owned: '+section)
        for command in [
            ['.venv/bin/python','studio/episodes/'+section+'/download_sources.py'],
            ['.venv/bin/python','studio/production/remaining/pin_foregrounds.py',section],
            ['studio/runtime/.venv/bin/python','studio/production/remaining/pictures.py',section],
        ]:
            print('Preparing:', ' '.join(command),flush=True)
            subprocess.run(command,cwd=ROOT,check=True)


if __name__=='__main__':main(sys.argv[1:])
