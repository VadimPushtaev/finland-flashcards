"""Compare native Russian presets on the first episode's difficult sentences."""
import argparse
import json
from pathlib import Path
import time

import soundfile as sf
import yaml

from russian_narration import ROOT, checksum, load_model, speech_text, synthesize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--voices', nargs='+', default=['xenia', 'kseniya', 'baya'])
    args = parser.parse_args()
    episode = ROOT / 'studio/episodes' / args.section
    config = yaml.safe_load((episode / 'russian-narration.yaml').read_text())
    rows = yaml.safe_load((episode / 'script.yaml').read_text())['sentences']
    render = json.loads((episode / 'render.json').read_text())
    timeline = {item['sentence_id']: item for item in render['timeline'] if item['kind'] == 'sentence'}
    model = load_model(config)
    selected = [rows[i] for i in [0, 2, 5, 11, 12, 13]]
    for voice in args.voices:
        folder = ROOT / 'studio/media' / args.section / 'russian-auditions' / voice
        folder.mkdir(parents=True, exist_ok=True)
        records = []
        for row in selected:
            text = speech_text(row, config)
            start = time.monotonic()
            audio = synthesize(model, text, config, voice)
            path = folder / (row['sentence_id'] + '.wav')
            sf.write(path, audio, config['sample_rate'], subtype='PCM_16')
            item = timeline[row['sentence_id']]
            budget = (item['start_frame'] + item['frames']) / render['fps'] - config['scene_end_margin_seconds'] - item['speech_start_seconds']
            record = dict(sentence_id=row['sentence_id'], text=text, voice=voice,
                          path=str(path.relative_to(ROOT)), sha256=checksum(path),
                          seconds=len(audio) / config['sample_rate'], scene_budget_seconds=budget,
                          generation_seconds=time.monotonic()-start)
            records.append(record)
            print(json.dumps(record, ensure_ascii=False), flush=True)
        (folder / 'metrics.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
