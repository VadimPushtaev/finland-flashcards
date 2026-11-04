"""Refresh the worker-owned resumable status and verified-preview handoff index."""
from pathlib import Path
import datetime
import json
import yaml
R = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parent
path = P / 'worker-checkpoint.json'
old = json.loads(path.read_text())
transferred = ['hb-c11-trafik', 'hb-c11-nodsituationer']
owned = [sid for sid in old['exclusive_episodes'] if sid not in transferred]
rows = []
for sid in owned:
    episode = R / 'studio/episodes' / sid
    media = R / 'studio/media' / sid
    brief = yaml.load((episode / 'brief.yaml').read_text(), Loader=yaml.CSafeLoader)
    script = yaml.load((episode / 'script.yaml').read_text(), Loader=yaml.CSafeLoader)
    metrics = media / 'narration/metrics.json'
    handoff = episode / 'production-handoff.json'
    row = dict(section_id=sid, brief_status=brief['production_status'],
               sentences=len(script['sentences']), has_picture_plan=(episode / 'picture-plan.json').exists(),
               has_assets=(episode / 'assets.yaml').exists(), has_render=(episode / 'render.json').exists(),
               selected_clips=len(json.loads(metrics.read_text())) if metrics.exists() else 0,
               retained_wav_files=len(list((media/'narration').glob('hb-*.wav'))))
    if handoff.exists():
        result = json.loads(handoff.read_text())
        row.update(output=result['output'], output_sha256=result['sha256'], seconds=result['seconds'],
                   measured_picture_fraction=result['actual_body_picture_fraction'],
                   distinct_pictures=result['distinct_pictures'], user_acceptance=result['user_acceptance'])
    rows.append(row)
states = []
for directory in [P, R / 'studio/production/hb-c11-safety']:
    for file in directory.glob('*-state.json'):
        state = json.loads(file.read_text())
        if state.get('section_id') in owned and state.get('status') == 'running' and state.get('supervisor_pid'):
            states.append(dict(section_id=state['section_id'], stage=state['stage'],
                               supervisor_pid=state['supervisor_pid'], child_pid=state.get('pid'),
                               heartbeat_at=state.get('heartbeat_at'), state=str(file.relative_to(R)),
                               log=state.get('log')))
result = dict(owner='/root/chapter10', updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              exclusive_episodes=owned, episodes=rows, recorded_running_jobs=states,
              transferred_episodes=transferred,
              transfer_proof='studio/production/hb-c10/traffic-emergency-transfer-checkpoint.json',
              allocation_threads=0, narration_queue_supervisor=250454, narration_asr_pipeline_supervisor=250457,
              narration_complete=True,
              tts_release='studio/production/hb-c10/all-owned-tts-release.json',
              asr_release='studio/production/hb-c10/all-owned-asr-release.json',
              narration_tts_pipeline_state='studio/production/hb-c10/narration-pipeline-tts-state.json',
              narration_asr_pipeline_state='studio/production/hb-c10/narration-pipeline-asr-state.json',
              narration_pipeline_control='studio/production/hb-c10/narration-pipeline-control.json',
              narration_queue_chain='studio/production/hb-c10/narration-queue-chain.json',
              retired_serial_extension_state='studio/production/hb-c10/narration-queue-extension-state.json',
              retired_serial_final_supervisor=155767,
              retired_serial_final_state='studio/production/hb-c10/narration-queue-final-state.json',
              narration_queue_status='studio/production/hb-c10/narration-pipeline-tts-status.json',
              narration_asr_status='studio/production/hb-c10/narration-pipeline-asr-status.json',
              donor_narration_release='studio/production/hb-c10/donor-narration-release.json',
              donor_narration_job='studio/production/hb-c10/donor-narration-job.json',
              narration_queue_control='studio/production/hb-c10/narration-queue-control.json',
              external_encoder_coordination='Root assigns exact successor streams; obey current remaining/resource-budget.json.',
              assigned_successors=['studio/production/hb-c10/pension-successors-state.json',
                                   'studio/production/hb-c10/aldre-successors-state.json'],
              whole_video_listening=False, user_acceptance=False)
temporary = path.with_suffix('.tmp')
temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
temporary.replace(path)
print('Checkpoint:', len(rows), 'owned episodes;', sum(r['brief_status'] == 'preview_ready' for r in rows),
      'verified previews;', len(states), 'recorded running stages.')
