"""Bind complete narration diagnostics to exact selected WAVs without claiming listening."""
from pathlib import Path
import json, hashlib, re, difflib
import yaml, numpy as np, soundfile as sf
ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
SID = EP.name

def main():
    script = yaml.safe_load((EP / 'script.yaml').read_text())
    folder = ROOT / 'studio/media' / SID / 'narration'
    metrics = json.loads((folder / 'metrics.json').read_text())
    asr = {x['file']: x for x in json.loads((folder / 'asr.json').read_text())}
    assert [m['sentence_id'] for m in metrics] == [r['sentence_id'] for r in script['sentences']]
    normalize = lambda t: re.sub('[^\\w]+', '', t.casefold())
    checks = []
    flags = []
    for row, m in zip(script['sentences'], metrics):
        p = ROOT / m['path']
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        w, rate = sf.read(p)
        assert sf.info(p).subtype == 'PCM_16'
        assert rate == 44100 and w.ndim == 1 and np.isfinite(w).all() and (0.001 < np.abs(w).max() < 0.999)
        assert abs(len(w) / rate - m['seconds']) < 0.001
        assert m['text'] == (row.get('speech_override') or {}).get('text', row['sv'])
        a = asr[m['path']]
        assert a['sha256'] == sha and a['language'] == 'sv'
        sim = difflib.SequenceMatcher(None, normalize(m['text']), normalize(a['asr_text']), autojunk=False).ratio()
        item = {'sentence_id': row['sentence_id'], 'tts_input': m['text'], 'asr_text': a['asr_text'], 'sha256': sha, 'seconds': len(w) / rate, 'sample_rate': rate, 'peak': float(np.abs(w).max()), 'diagnostic_text_similarity': round(sim, 4), 'listening_status': 'pending'}
        checks.append(item)
        if sim < 0.94 or re.findall('\\d+', m['text']) != re.findall('\\d+', a['asr_text']):
            flags.append(item)
    priorities = {'hb-c05-likabehandling': ['Finnish legal names: yhdenvertaisuuslaki,tasa-arvolaki,työsopimuslaki,tasa-arvosuunnitelma,yhdenvertaisuussuunnitelma.', 'Numbers2015 and30; long protected-characteristics list hb-c05-u0051-s001 and dense bilingual reading comfort.', 'First long sentence hb-c05-u0048-s002: ASR splits finsk lagstiftning and appears to repeat a syllable after nationalitet; uncertain without listening.'], 'hb-c05-rasism': ['Swedish compounds hatbrott,strukturell rasism,mikroaggressioner,minoritetsstress and internaliserad rasism.', 'Archived source hb-c05-u0068-s005 says Egendomen; preserved exactly, without editorial correction in production.'], 'hb-c05-hjalp': ['Finnish authority names: yhdenvertaisuusvaltuutettu,työsuojeluviranomaiset,työsuojeluvaltuutettu,luottamusmies,tasa-arvovaltuutettu.', 'Long Swedish authority compounds diskrimineringsombudsmannen,jämställdhetsombudsmannen,Regionförvaltningsverket.', 'Archived authority names preserved; no claim that production updates the source to current legal/service guidance.']}
    report = {'method': 'Local faster-whisper small Swedish beam5 CPU int8, resume bound to WAV hashes; transcript diagnostic only.', 'integrity': 'Every exact source-order clip is finite mono44100Hz PCM16, nonempty, below full scale, with expected duration, current input and matching ASR hash.', 'listening_status': 'pending', 'priority_review': priorities[SID], 'sentences': checks, 'diagnostic_flags': flags, 'script_source_section_sha256': script['source_section_sha256'], 'translation_file_sha256': script['translation_file_sha256']}
    (EP / 'narration-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    lines = ['# Narration review notes', '', SID, '', 'Automated transcript differences are diagnostics; no listening, accent or pronunciation acceptance is claimed.', '']
    lines += ['- ' + t for t in priorities[SID]]
    lines += ['', '## Flagged transcript comparisons', '']
    for item in flags:
        lines += ['- ' + item['sentence_id'] + ' (similarity ' + str(item['diagnostic_text_similarity']) + '):', '  - Input: ' + item['tts_input'], '  - ASR: ' + item['asr_text']]
    if not flags:
        lines += ['No comparisons crossed the diagnostic threshold; listening is still required.']
    (EP / 'ASR_NOTES.md').write_text('\n'.join(lines) + '\n')
    print(SID, len(checks), 'integrity/source/hash checks;', len(flags), 'diagnostic flags')
if __name__ == '__main__':
    main()
