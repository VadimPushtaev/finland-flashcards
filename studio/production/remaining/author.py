"""Apply explicitly authored sentence picture plans to untouched source scaffolds.

The caller supplies the creative plan; this helper only shares settled layout,
voice, source-credit and file conventions. It never changes source-owned text.
"""
from pathlib import Path
import copy
import json

import yaml

ROOT = Path(__file__).resolve().parents[3]
PALETTES = {
    'hb-c11': dict(background='#243c32', text='#faf3e8', secondary='#c5dfce', highlight='#e3c58c', separator='#4d7560'),
    'hb-c12': dict(background='#352e49', text='#faf3e8', secondary='#d7cce7', highlight='#e2c58b', separator='#685881'),
}


def apply(section, plans, story, music_title, background_description):
    """Each plan supplies id, description, visual_type, composition and nodes."""
    episode = ROOT/'studio/episodes'/section
    script = yaml.safe_load((episode/'script.yaml').read_text())
    if script['episode_decisions']:
        raise ValueError('Resume curated episode deliberately; do not overwrite: '+section)
    if len(plans) != len(script['sentences']):
        raise ValueError('Every body sentence needs its own explicit picture plan')
    chapter = script['chapter_id']
    script['episode_decisions'] = [dict(id=key,decision=value,status='proposed',resolve_during=stage)
        for key,value,stage in [
            ('opening','Exact unspoken bilingual source heading,3seconds; no added speech.','script'),
            ('story_structure',story,'script'),
            ('text_and_layout',f'1920x1080/24fps; Liberation Sans48/40, stable right bilingual panel and fixed left foreground. Chapter palette: {PALETTES[chapter]}. Use permitted44/36 or40/34 only if necessary; manually segment oversized pairs.','script'),
            ('pace','Full measured local narration once per source sentence/list fragment,0.25second text lead,1.7second ordinary pauses and2.2seconds at source-paragraph boundaries; longer pairs2.5seconds.','script'),
            ('voice_selection','Local Swedish Supertonic3/F1,32steps,speed0.95,seed42,44100HzmonoPCM16. Initial allocation2ONNXthreads; metrics record actual per-invocation settings and retained takes. Whole-video listening pending.','script'),
            ('foreground_selection','Individually authored source-specific pictures for almost every body slide. Actual object/place photographs where useful; original diagrams visualize only stated relationships. Inspect every picture; do not use irrelevant filler.','script'),
            ('visual_motion',background_description+' Continuous full-timeline15%relative pan/zoom,140second smooth cycles,42%darkening and2.5pxblur; foreground and text remain steady.','assets'),
            ('music_selection',music_title+'; distinct centrally reserved source,verified creator/license in assets. Keep one cohesive instrumental throughout,accepted+2dB adjustment,ducking/fades and4second loop crossfades as needed.','assets'),
            ('closing','Readable source/media credits and matching canonical sidecar,derived from this episode actual sources.yaml and media sources. No spoken credits.','script'),
            ('exceptions','No exception. Exact archived wording and current reviewed Russian remain unchanged. Record source typos/pronunciation diagnostics for whole-video review.','script'),
        ]]
    script['scenes'] = []
    script['asset_requests'] = [dict(id=key,kind=kind,description=description,fallback=fallback)
        for key,kind,description,fallback in [
            ('episode_background','background',background_description,'Another distinct verified relevant photograph; revise central reservation before use.'),
            ('music_bed','music',music_title,'Another unique licensed gentle instrumental; retain music throughout.'),
            ('narration','narration','One complete local Swedish F1clip per source sentence in stored order.','Only diagnostic-led bounded retakes in a separate folder,retaining existing takes/metrics.'),
        ]]
    seen = []
    specifications = {}
    for index,(row,plan) in enumerate(zip(script['sentences'],plans)):
        unit = row['sentence_id'].rsplit('-s',1)[0]
        if unit not in seen:
            seen.append(unit)
            script['scenes'].append(dict(id=unit,description=row['sv']))
        key = plan['id']
        for node in plan.get('nodes',[]):
            text=node['label'];at=row['sv'].casefold().find(text.casefold())
            if at < 0:
                raise ValueError(f'Picture label not in source {section}:{index}: {text}')
            node['label']=row['sv'][at:at+len(text)]
        row.update(scene_id=unit,asset_ids=['episode_background',key],text_highlights=[],
                   visual_cue=plan['description'],render_caption=False,
                   render_image=f'studio/media/{section}/pictures/{key}.png',
                   pronunciation_notes=['Names,source numerals,compounds and any archived typos require whole-video listening; ASR is diagnostic only.'],
                   pause_after_seconds=2.5 if len(row['sv'])+len(row['ru'])>330 else 1.7)
        script['asset_requests'].append(dict(id=key,kind='foreground',description=plan['description'],
            fallback='Another accurate source-based pictorial composition or verified relevant photograph; document any genuinely necessary omission.'))
        specifications[key]={**copy.deepcopy(plan),'source_sentence_ids':[row['sentence_id']]}
    for before,after in zip(script['sentences'],script['sentences'][1:]):
        if before['scene_id']!=after['scene_id']:
            before['pause_after_seconds']=max(before['pause_after_seconds'],2.2)
    base=yaml.safe_load((ROOT/'studio/episodes/hb-c11-konsumentskydd/script.yaml').read_text())
    settings=copy.deepcopy(base['render'])
    settings.update(palette=PALETTES[chapter],music_path=f'studio/media/{section}/sources/music-bed.flac',
                    background_image=f'studio/media/{section}/sources/background.jpg')
    settings.pop('background_identity',None)
    settings['background_style'].pop('motion_cycles',None)
    sources=yaml.safe_load((episode/'sources.yaml').read_text())['sources']
    settings['credits']=[dict(heading='Källor · Источники',paragraphs=[
        'Svensk källtext med granskad rysk översättning.',
        *list(dict.fromkeys(source['attribution']['credit'] for source in sources)),
        'Fullständiga artiklar,bokpassager,licenser och ändringar i CREDITS.md.']),
        dict(heading='Bild,musik & röst · Изображения,музыка и голос',paragraphs=[
            'Fullständig bildattribution och licenser i medföljande CREDITS.md.',
            music_title,'Svensk lokal berättarröst: Supertonic3 · F1.',
            'Original källbaserad schematisk grafik: Homebrew video studio.'])]
    settings['adaptation_notes']=['Exact archived Swedish and reviewed Russian retained in source order; no added narration.',
        'Individual source-specific original diagrams and verified photographs; contextual photos do not prove a rule or a pictured person status.',
        'Background cropped,darkened,softened and animated continuously; source license retained.',
        'Music faded,ducked,+2dB adjusted and repeated with4second crossfades when needed.']
    script['render']=settings
    (episode/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
    (episode/'picture-plan.json').write_text(json.dumps(specifications,ensure_ascii=False,indent=2)+'\n')
    return script
