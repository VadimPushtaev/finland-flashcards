"""Record completion only after all requested current previews and audits pass."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import yaml
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    progress=json.loads((BASE/'progress.json').read_text());evidence=json.loads((BASE/'batch-export-evidence.json').read_text());diversity=json.loads((BASE/'batch-visible-diversity.json').read_text());pictures=json.loads((BASE/'batch-picture-identity-audit.json').read_text())
    assert progress['verified_previews']==progress['requested_episodes']==88
    assert evidence['verified_preview_briefs']==88 and not evidence['pending'] and not evidence['review_evidence_problems']
    assert diversity['assessed_episodes']==88 and diversity['assessed_body_pairs']==3730 and not diversity['missing']
    assert pictures['episodes']==88 and pictures['pictured_body_pairs']==3730 and pictures['distinct_background_sources']==pictures['distinct_music_sources']==88
    assert not pictures['duplicate_sentence_ids'] and not pictures['reused_background_sources'] and not pictures['reused_music_sources'] and not pictures['same_episode_background_foreground_collisions']
    queue=yaml.safe_load((BASE/'queue.yaml').read_text())['episodes'];wanted={r['section_id']for r in queue};assert len(queue)==len(wanted)==88
    def indexed(rows):
        result={r['section_id']:r for r in rows};assert len(rows)==len(result)==88 and set(result)==wanted
        return result
    current=indexed(progress['outputs']);ledger=indexed(evidence['episodes']);picture_rows=indexed(pictures['episodes_current_inputs']);diversity_rows=indexed(diversity['episodes'])
    inventory={r['section_id']:r for r in yaml.safe_load((ROOT/'studio/episodes.yaml').read_text())['episodes']}
    for row in queue:
        section=row['section_id'];ep=ROOT/'studio/episodes'/section;entry=ledger[section];output=current[section]
        assert output['chapter_id']==inventory[section]['chapter_id'] and inventory[section]['production_status']=='preview_ready'
        assert entry['export_sha256']==output['sha256'] and entry['output']==output['output']
        assert entry['sentences']==output['sentences']==picture_rows[section]['sentences']==diversity_rows[section]['sentences']
        for field,name in [('script_sha256','script.yaml'),('assets_sha256','assets.yaml'),('credits_sha256','CREDITS.md')]:assert entry[field]==sha(ep/name)
        render=json.loads((ep/'render.json').read_text());check=json.loads((ep/'render-check.json').read_text());coverage=json.loads((ep/'picture-coverage.json').read_text())
        assert render['sha256']==check['sha256']==coverage['export_sha256']==output['sha256'] and render['output']==output['output']
        assert (ROOT/output['output']).with_suffix('.CREDITS.md').read_bytes()==(ep/'CREDITS.md').read_bytes()
        assert entry['current_actual_export_reviews']
        for review in entry['current_actual_export_reviews']:
            path=ROOT/review['path'];assert sha(path)==review['sha256'];assert json.loads(path.read_text())['export_sha256']==output['sha256']
    auditrefs=[]
    for chapter in range(8,13):
        path=ROOT/'studio'/f'hb-c{chapter:02d}-audit.json';audit=json.loads(path.read_text());expected={k for k,v in current.items()if v['chapter_id']==f'hb-c{chapter:02d}'};assert len(expected)==len(audit['results']) and expected=={r['section_id']for r in audit['results']}
        for row in audit['results']:assert current[row['section_id']]['sha256']==row['sha256']
        auditrefs.append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),episodes=audit['episodes'],sentences=audit['sentences']))
    assert sum(r['sentences']for r in auditrefs)==3730
    for row in pictures['episodes_current_inputs']:
        ep=ROOT/'studio/episodes'/row['section_id'];assert sha(ep/'script.yaml')==row['script_sha256']and sha(ep/'assets.yaml')==row['assets_sha256']
    for row in diversity['episodes']:
        ep=ROOT/'studio/episodes'/row['section_id'];assert sha(ep/'script.yaml')==row['script_sha256']and sha(ep/'assets.yaml')==row['assets_sha256']
    seconds=round(progress['verified_seconds']);duration=f'{seconds//3600}:{seconds//60%60:02d}:{seconds%60:02d}';fraction=diversity['within_episode_diversity_fraction'];date=datetime.now(timezone.utc).date().isoformat()
    summary=(f'## Chapters 8–12 production batch\n\nAll **88 remaining subchapter videos** are available as local previews: **{duration}** total, covering **3,730 exact Swedish/Russian body pairs**. Every narrated body pair has a relevant foreground picture. Conservative review counts **{fraction:.1%} distinct visible compositions within episodes**, ignoring filenames, labels, colour and small layout changes. Verified source photographs and original source-based diagrams are used; relevant recurring compositions and cross-episode photo reuse are recorded honestly. Each episode has its own background source and music track.\n\nAll five chapter audits, current source/audio/asset checks, full decode, timing, audio-to-mix comparison, motion, credits and actual exported-card visual reviews passed. Whole-video listening, physical-device playback and user acceptance remain pending; status stays `preview_ready`.\n\nSee the [current export evidence](../../studio/production/remaining/batch-export-evidence.json), [picture integrity audit](../../studio/production/remaining/batch-picture-identity-audit.json), and [conservative diversity report](../../studio/production/remaining/batch-visible-diversity.json). Videos and matching credits are linked by chapter below.\n\n')
    index=ROOT/'videos/homebrew/README.md';text=index.read_text();text=re.sub(r'(?s)<!-- remaining-batch-summary -->.*?<!-- /remaining-batch-summary -->\n*','',text);position=text.index('## Chapter 8 —');text=text[:position]+'<!-- remaining-batch-summary -->\n'+summary+'<!-- /remaining-batch-summary -->\n\n'+text[position:];index.write_text(text)
    tracker=ROOT/'card_creator/card_progress.md';text=tracker.read_text();note=(f'Homebrew videos ({date}): all **88 remaining subchapters in chapters 8–12** now have verified local previews, covering **3,730 exact Swedish/Russian body pairs** and **{duration}** of video. Foreground pictures cover every narrated body pair; conservative within-episode visual diversity is **{fraction:.1%}**. All five chapter audits and exported-card visual reviews passed. Whole-video listening, physical-device playback and user acceptance remain pending. See the [video index](../videos/homebrew/README.md) and [production completion record](../studio/production/remaining/completion.json). Flashcard selection and deck counts are unchanged by video production.\n\n');text=re.sub(r'(?s)<!-- remaining-video-progress -->.*?<!-- /remaining-video-progress -->\n*','',text);anchor='This document tracks which data sources have been converted into flashcards.\n\n';assert anchor in text;text=text.replace(anchor,anchor+'<!-- remaining-video-progress -->\n'+note+'<!-- /remaining-video-progress -->\n\n',1);tracker.write_text(text)
    completion=dict(completed_utc=datetime.now(timezone.utc).isoformat(),scope='All88remainingHomebrewsubchapters,Chapters8–12',episodes=88,exact_body_pairs=3730,seconds=progress['verified_seconds'],duration=duration,picture_fraction=1.0,within_episode_visible_diversity_fraction=fraction,chapter_audits=auditrefs,evidence_files={name:sha(BASE/name)for name in ['progress.json','batch-export-evidence.json','batch-picture-identity-audit.json','batch-visible-diversity.json']},whole_video_listening=False,physical_device_playback=False,user_acceptance=False,commit_or_upload=False)
    (BASE/'completion.json').write_text(json.dumps(completion,ensure_ascii=False,indent=2)+'\n');print('COMPLETE88/88',duration,f'{fraction:.1%}within-episodevisiblediversity')
if __name__=='__main__':main()
