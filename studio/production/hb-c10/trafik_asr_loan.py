from pathlib import Path
import narration_queue as q
q.STATUS=Path('studio/production/hb-c10/trafik-asr-loan-status.json')
q.run_stage('hb-c11-trafik','asr')
