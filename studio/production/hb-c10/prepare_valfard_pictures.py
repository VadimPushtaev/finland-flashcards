"""Prepare distinct licensed photos and source-specific welfare pictorial diagrams."""
from pathlib import Path
import importlib.util,json,yaml,hashlib,copy,re,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-valfard';MEDIA=ROOT/'studio/media/hb-c10-valfard';OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('pictures',ROOT/'studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
art.BG='#233c50';art.PANEL='#2d4c63';art.SECOND='#c6d9e8';art.ACCENT='#e6c28b';art.LINE='#4b6e85'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
d=yaml.safe_load((EP/'script.yaml').read_text());allphotos=json.loads((ROOT/'studio/production/hb-c10/existing-foreground-photos.json').read_text());new=json.loads((EP/'selected-photos.json').read_text()) if (EP/'selected-photos.json').exists() else {}
retained=json.loads((EP/'retained-photo-sources.json').read_text())
# Distinct existing source identities are reused once each within this episode;
# source ownership/licenses travel with the full original asset register.
photo_indices={2:8,8:7,10:54,11:59,12:10,17:39,26:25,30:119,36:34,40:85}
# Every diagram expresses a specific relationship in the selected source sentence.
# Photographs replace schematic requests wherever a concrete identified subject helps.
diagrams={
0:['grid','Människovärdigt liv',[['people','alla invånare'],['house','liv'],['hospital','välbefinnande'],['shield','förutsättningar']],'Nordisk välfärdsstat'],
1:['grid','Tjänster bekostas med skattemedel',[['hospital','hälsovård'],['document','utbildning'],['people','barnomsorg'],['book','bibliotek']],''],
3:['flow','Ekonomiskt stöd',[['hospital','sjukdom'],['person','svår livssituation'],['coins','bidrag och förmåner']],''],
4:['flow','Tjänster och stöd',[['coins','pengar'],['hospital','tjänster'],['people','förmåner']],''],
5:['pair','Välfärdsstat',[['coins','skatt'],['hospital','välfärd']],'Inga belopp eller jämförelsetal'],
6:['flow','Skatt',[['person','individen'],['factory','företagen'],['coins','skatt']],''],
7:['pair','Välfärden är värdefull',[['document','forskning'],['people','gärna betalar skatt']],'Inga påhittade enkätresultat'],
9:['pair','Upprätthålla välfärdsstaten',[['coins','betala'],['hospital','välfärdsstaten']],''],
13:['pair','Boendekostnader',[['house','boende'],['coins','stöd']],'i vissa situationer'],
14:['pair','Sjukförsäkrad i Finland',[['shield','sjukförsäkrad'],['document','FPA-kort']],'Schematisk kortbild'],
16:['pair','Självriskdelen',[['document','räkningen'],['coins','självriskdelen']],'Inga påhittade belopp'],
18:['flow','Ansöka om en förmån',[['document','ansökan'],['gear','FPA utreder'],['shield','rätt till förmåner']],''],
19:['pair','Boende och arbete',[['house','stadigvarande boende'],['work','arbete i Finland']],''],
20:['pair','Individuell behandling',[['person','livssituation'],['document','beslut om bidrag']],'Varje sökande'],
21:['grid','Olika livssituationer',[['people','livssituation'],['hospital','behov'],['house','boende'],['work','arbete']],''],
22:['pair','Bidragens belopp och grunder',[['coins','belopp'],['document','grunder']],'varierar'],
23:['pair','Din egen situation',[['person','du'],['document','individuellt']],'utreda din egen situation'],
24:['pair','Stadigvarande boende',[['house','Finland'],['shield','FPA:s förmåner']],'Huvudregeln'],
25:['pair','Boende i lagen',[['house','stadigvarande boende'],['document','lagen']],''],
27:['flow','När du flyttar till Finland',[['house','flytt'],['gear','FPA bedömer'],['document','stadigvarande boende']],''],
28:['decision','FPA:s bedömning',[['gear','stadigvarande'],['house','boende'],['document','situationer']],'Följande situationer i källtexten'],
29:['flow','Återflyttare',[['house','utlandet'],['person','återvänder'],['house','Finland']],''],
31:['pair','Nära familjeförhållande',[['people','familjeförhållande'],['house','bor stadigvarande']],''],
32:['pair','Uppehållstillstånd',[['document','uppehållstillstånd'],['calendar','giltigt']],'om du är skyldig att ha ett'],
33:['grid','Helhetsbedömning',[['house','boende'],['work','arbete'],['people','familj'],['document','situation']],'FPA gör en helhetsbedömning'],
34:['decision','Boendet bedöms',[['gear','FPA:s bedömning'],['house','stadigvarande'],['document','inte stadigvarande']],''],
35:['pair','Inte stadigvarande flytt',[['house','flytt till Finland'],['shield','vanligen inte rätt']],'FPA:s förmåner'],
37:['pair','Studier i Finland',[['document','hur länge'],['house','från vilket land']],'rätten beror på'],
38:['grid','Socialskyddet i hemlandet',[['house','EU- eller EES-land'],['house','Schweiz'],['house','Storbritannien'],['shield','hemlandet']],'vanligen'],
39:['flow','Studier från annat land',[['document','annat land'],['calendar','minst 2 år'],['shield','en del förmåner']],'kan ha rätt'],
41:['flow','Försäkringsperioder',[['calendar','andra EU-länder'],['document','ackumulerat'],['shield','i vissa fall']],'Inga påhittade tidslängder'],
42:['pair','Internationella ärenden',[['people','FPA:s center'],['phone','Fråga mer']],'Inga påhittade kontaktuppgifter'],
}
# The existing icon vocabulary has no book symbol: depict a source education
# document instead of importing invented textbook details.
for specval in diagrams.values():
    for node in specval[2]:
        if node[0]=='book':node[0]='document'
assets=[];downloads=[];screen=[]
for i,r in enumerate(d['sentences']):
    key=f'picture-{i+1:02}';path=OUT/f'sentence-{i+1:02}.png';asset=None
    if i in photo_indices:
        origin=allphotos[photo_indices[i]];a=copy.deepcopy(origin['asset']);record=retained.get(str(photo_indices[i]));raw=ROOT/(record['path'] if record else a['files'][0]['path']);im=Image.open(raw).convert('RGB');im.thumbnail((1100,1000));im.save(path)
        if record:downloads.append(record)
        asset={k:v for k,v in a.items() if k not in ['files','asset_id','creation_method']};asset.update(asset_id=key,files=[info(path)],creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),retained_source_asset=str(Path('studio/episodes')/origin['episode']/'assets.yaml'),transform='Complete retained licensed photograph proportionally resized; no new identity claims.'))
        contexts={0:'Public anti-racism gathering in Finland illustrates dignity of all residents, not their benefit status.',2:'Actual Oodi library interior illustrates public low-cost services.',7:'Finnish academic defence photograph illustrates research, not a specific taxation survey.',8:'Actual Finnish Parliament building illustrates debate on publicly funded services.',10:'Finnish election posters illustrate differing party views, not current party policies.',11:'An accurately identified Finnish association meeting illustrates free discussion.',12:'A parent-child disc-golf activity illustrates one beneficiary category, families; it does not identify benefit recipients.',17:'Actual Supreme Court building illustrates legal basis of benefits, not a particular statute or judgment.',23:'Oodi digital workshop illustrates seeking assistance for one’s circumstances; no benefit status inferred.',26:'Actual Finnish office buildings illustrate work in Finland without implying personal entitlement.',30:'Actual Hakaniemi market hall businesses illustrate lasting employment as a source condition; no depicted contract is asserted.',36:'Actual Finnish industrial workplace illustrates possible work-based benefit rights without implying approval.',38:'European Parliament illustrates the source EU/EEA/Swiss/UK cross-border-security passage; it is not a membership map.',40:'Actual Helsinki municipal building illustrates residence-related public administration without implying an individual history.'}
        asset['relevance_verification']=contexts[i]+' Retained source verification: '+a.get('relevance_verification','')
        screen.append(a.get('source_url','').split('/wiki/')[-1].replace('_',' ')+' — '+a.get('creator','')+' · '+a.get('reuse_terms','').split('https:')[0])
    elif i==15 and 'File:Punkaharjun apteekki.JPG' in new:
        rec=new['File:Punkaharjun apteekki.JPG'];pi=rec['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]*>','',meta.get(k,{}).get('value','')).strip();raw=ROOT/rec['path'];im=Image.open(raw).convert('RGB');im.thumbnail((1100,1000));im.save(path)
        asset=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(path)],source_url=pi['descriptionurl'],creator=clean('Artist'),reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),required_credits='Punkaharjun apteekki.JPG — '+clean('Artist')+'. '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; source terms retained.',relevance_verification='Verified Punkaharju pharmacy exterior illustrates source pharmacy reimbursements, not any particular eligibility or current transaction.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Complete photograph proportionally resized.'));downloads.append(dict(**info(raw),url=rec['download_url']));screen.append('Punkaharju pharmacy — '+clean('Artist')+' · '+clean('LicenseShortName'))
    else:
        if i==15:sp=['pair','Ersättning',[['document','FPA-kort'],['shop','apoteken']],'kostnader']
        else:sp=diagrams[i]
        if sp[3].startswith('Inga'):sp[3]=''
        art.diagram(sp,path)
        asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(path)],creator='Homebrew video studio',reuse_terms='Original source-based schematic artwork under repository MIT license; source wording retains original publisher terms.',required_credits='Original schematic illustrations: Homebrew video studio; source text credited in sources.yaml and canonical CREDITS.md.',relevance_verification='Source-specific original pictorial explanation of '+r['sentence_id']+'. '+next(x['request'] for x in json.loads((EP/'picture-plan.json').read_text()) if x['sentence_id']==r['sentence_id'])+' No invented money amounts, legal guarantees or quantitative comparison.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),diagram_specification=sp,source_sentence_ids=[r['sentence_id']]))
    r['render_image']=str(path.relative_to(ROOT));r['render_caption']=False;assets.append(asset)
d['render']['credits']=d['render']['credits'][:2]
for j in range(0,len(screen),2):d['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i medföljande CREDITS.md.']))
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n')
print('Prepared',len(assets),'distinct pictures; photographs',sum(a['visual_type']=='photograph' for a in assets))
