"""Record hash-bound local transcript diagnostics without claiming a listening review."""
from pathlib import Path
import json,hashlib,difflib,re
import yaml
ROOT=Path(__file__).resolve().parents[3]
def main(section):
 ep=ROOT/'studio/episodes'/section;media=ROOT/'studio/media'/section
 d=yaml.safe_load((ep/'script.yaml').read_text());metrics=json.loads((media/'narration/metrics.json').read_text());asr={Path(r['file']).stem:r for r in json.loads((media/'narration/asr.json').read_text())};records=[]
 normalize=lambda s:re.sub(r'[^\w]+','',s.lower())
 for row,m in zip(d['sentences'],metrics):
  a=asr[row['sentence_id']];checksum=hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest()
  if checksum!=a['sha256']:raise ValueError('Stale ASR '+row['sentence_id'])
  records.append({'sentence_id':row['sentence_id'],'tts_input':m['text'],'asr_text':a['asr_text'],'sha256':checksum,'seconds':m['seconds'],'sample_rate':m['sample_rate'],'peak':m['peak'],'diagnostic_text_similarity':round(difflib.SequenceMatcher(None,normalize(m['text']),normalize(a['asr_text'])).ratio(),4),'listening_status':'pending'})
 report={'method':'Local faster-whisper small, Swedish, beam5, CPU int8; each transcript bound to the retained WAV SHA256. Diagnostic only.','integrity':'Complete ordered synthesis metrics; selected WAV hashes and source inputs checked against script/assets by normal validators.','listening_status':'pending','priority_review':['Legal compounds and any Finnish terms; source years and list fragments. Automated transcript differences do not establish pronunciation or listening quality.'],'sentences':records}
 (ep/'narration-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(ep/'generation-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
 print(section,'diagnostics',len(records),'low_similarity',[(r['sentence_id'],r['diagnostic_text_similarity']) for r in records if r['diagnostic_text_similarity']<.85])
if __name__=='__main__':
 import sys;main(sys.argv[1])
