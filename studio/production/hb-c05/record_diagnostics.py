"""Bind retained sentence diagnostics and listening priorities to selected media."""
from pathlib import Path
import difflib, hashlib, json, re, sys
import yaml
ROOT = Path(__file__).resolve().parents[3]

def normalized(t):
    t = t.lower()
    for a, b in [('tolv', '12'), ('tjugo', '20'), ('arton', '18'), ('noll', '0'), ('ett', '1'), ('tjugofyra', '24'), ('fyra', '4'), ('sjutton', '17'), ('fyrtio', '40')]:
        t = re.sub('\\b' + a + '\\b', b, t)
    return re.findall('\\w+', t)

def main(sid):
    ep = ROOT / 'studio/episodes' / sid
    media = ROOT / 'studio/media' / sid
    s = yaml.safe_load((ep / 'script.yaml').read_text())
    metrics = json.loads((media / 'narration/metrics.json').read_text())
    transcripts = {Path(r['file']).stem: r for r in json.loads((media / 'narration/asr.json').read_text())}
    rows = []
    flags = []
    assert [m['sentence_id'] for m in metrics] == [r['sentence_id'] for r in s['sentences']]
    for row, m in zip(s['sentences'], metrics):
        a = transcripts[row['sentence_id']]
        path = ROOT / m['path']
        assert a['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert m['text'] == (row.get('speech_override') or {}).get('text', row['sv'])
        expected = normalized(m['text'])
        observed = normalized(a['asr_text'])
        matcher = difflib.SequenceMatcher(a=expected, b=observed)
        diff = [{'input': ' '.join(expected[i:j]), 'asr': ' '.join(observed[k:l])} for op, i, j, k, l in matcher.get_opcodes() if op != 'equal']
        r = dict(sentence_id=row['sentence_id'], tts_input=m['text'], asr_text=a['asr_text'], sha256=a['sha256'], seconds=m['seconds'], sample_rate=m['sample_rate'], peak=m['peak'], token_similarity=matcher.ratio(), transcript_differences=diff, listening_status='pending')
        rows.append(r)
        if diff or re.search('\\d|Valvira|asevelvollisuus', m['text']):
            flags.append(dict(sentence_id=row['sentence_id'], start_seconds=row.get('start_seconds'), end_seconds=row.get('end_seconds'), intended_wording=m['text'], asr_text=a['asr_text'], transcript_differences=diff, status='ASR uncertainty or source number/name; not a confirmed audible error'))
    (ep / 'narration-check.json').write_text(json.dumps(dict(method='Local faster-whisper small, sv, beam 5, int8 CPU; recorded job thread allocation. ASR is diagnostic only.', integrity='Every retained mono 44,100 Hz WAV is checked against selected metrics, source-order input and diagnostic hash.', sentences=rows, listening_status='pending'), ensure_ascii=False, indent=2) + '\n')
    render = ep / 'render.json'
    export = json.loads(render.read_text()) if render.exists() else {}
    (ep / 'listening-priorities.json').write_text(json.dumps(dict(export_sha256=export.get('sha256'), unresolved=flags, resolved_audible_issues=[], listening_status='No auditory review performed; transcript diagnostics do not establish accent, pronunciation or mix quality.'), ensure_ascii=False, indent=2) + '\n')
    print(sid, len(rows), 'checked;', len(flags), 'listening priorities')
if __name__ == '__main__':
    for sid in sys.argv[1:]:
        main(sid)
