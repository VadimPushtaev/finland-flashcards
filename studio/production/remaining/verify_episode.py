"""Run complete technical checks for a prepared root-owned export.

This records preview readiness only. Actual exported-frame review, listening,
physical-device playback and user acceptance remain separately recorded work.
"""
from pathlib import Path
import json
import subprocess
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]


def main(section):
    runtime='studio/runtime/.venv/bin/python'
    source='.venv/bin/python'
    commands=[
        [source,'studio/production/remaining/audio_diagnostics.py',section],
        [runtime,'studio/tools/validate_assets.py',section],
        [runtime,'studio/tools/verify_render.py',section,'--save-frames'],
        [source,'studio/tools/script.py','review',section,'--ready'],
        [source,'studio/tools/script.py','validate',section,'--ready'],
        [source,'studio/tools/picture_coverage.py',section,'--require-target'],
        [source,'studio/production/remaining/picture_diversity.py',section],
    ]
    for command in commands:
        print('Checking:', ' '.join(command),flush=True)
        subprocess.run(command,cwd=ROOT,check=True)
    episode=ROOT/'studio/episodes'/section
    report=json.loads((episode/'render.json').read_text())
    check=json.loads((episode/'render-check.json').read_text())
    coverage=json.loads((episode/'picture-coverage.json').read_text())
    diversity=json.loads((episode/'picture-diversity.json').read_text())
    if not report['sha256']==check['sha256']==coverage['export_sha256']==diversity['export_sha256']:
        raise ValueError('Technical reports do not bind the same canonical export')
    script=yaml.safe_load((episode/'script.yaml').read_text())
    asr_path=ROOT/'studio/media'/section/'narration/asr.json'
    asr=json.loads(asr_path.read_text())
    if len(asr)!=len(script['sentences']):
        raise ValueError('Every retained narration clip requires a current diagnostic record')
    assets=yaml.safe_load((episode/'assets.yaml').read_text())
    narration=next(a for a in assets['assets'] if a['asset_id']=='narration')
    hashes={record['file']:record['sha256'] for record in asr}
    if any(hashes.get(entry['path'])!=entry['sha256'] for entry in narration['files']):
        raise ValueError('ASR diagnostics do not match current selected WAV hashes')
    brief=yaml.safe_load((episode/'brief.yaml').read_text())
    brief.update(production_status='preview_ready',output_path=report['output'],issues=[
        'Actual exported-frame review must be reconciled separately; see review.md and peer reports.',
        'Whole-video listening,physical-device playback and user acceptance pending; diagnostic transcript differences are not pronunciation approval.'])
    (episode/'brief.yaml').write_text(yaml.safe_dump(brief,allow_unicode=True,sort_keys=False,width=100))
    handoff=dict(section_id=section,production_status='preview_ready',output=report['output'],
        sha256=report['sha256'],seconds=report['seconds'],source_sentences=len(script['sentences']),
        source_section_sha256=script['source_section_sha256'],translation_file_sha256=script['translation_file_sha256'],
        picture_fraction=coverage['picture_fraction'],distinct_picture_sources=diversity['distinct_picture_sources'],
        technical_checks='Asset integrity,current diagnostic hashes,full decode,current mix,motion,exact bilingual source/timing,and measured picture coverage passed.',
        actual_exported_frame_review='Separate producer/peer evidence required',whole_video_listening=False,
        physical_device_playback=False,user_acceptance=False)
    (episode/'production-handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(handoff,ensure_ascii=False),flush=True)


if __name__=='__main__':main(sys.argv[1])
