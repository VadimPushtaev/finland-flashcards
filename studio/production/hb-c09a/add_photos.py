"""Pin verified physical-subject photographs from already acquired Commons metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,requests,re,yaml,hashlib,time,subprocess
R=Path.cwd();P=R/'studio/production/hb-c09a'
choices=[
('aktenskap',24,'File:Gold and diamond engagement ring.jpg','Engagement ring; illustrative object photograph, no claim about any particular couple.'),
('aktenskap',27,'File:Engagement rings photo by Ygor Oliveira.jpg','Engagement rings, the physical objects explicitly stated by this sentence.'),
('aktenskap',33,'File:Lascar Temppeliaukio Church (4548628589).jpg','Actual Temppeliaukio Lutheran church architecture in Helsinki, one of the source-named traditions. Not evidence of a particular ceremony or official authorization.'),
('forandring',44,'File:Dairy maids by a "river sauna" in Alajoki, Ilmajoki, 1920s 01.png','Identified1920sFinnish agrarian context, shown for work around the farm; does not identify the unnamed source family.'),
('forandring',48,'File:Suomen Tekstiilitehdas (Finska Textilfabriken) 1911 (HK8304-7.7).tif','Actual1911textilefactory image used as later context for industrialization that began in the19thcentury; not labelled as a mid19thcenturyphotograph.'),
('forandring',49,'File:K-1382-85- Seminaarin naisopettajia joulukuussa, 1912.jpg','Identified female seminary teachers photographed in1912, illustrating the source employment field, not asserting individual class or marital status.'),
('forandring',51,'File:Tampereen Pukutehdas talvisodan aikana.jpg','Actual Tampere clothing-factory photograph during the Winter War, directly relevant to wartime factory work.'),
('forandring',52,'File:Textile factory Tricol Ltd in Inkoo 1965 (JOKAVN4A2F41-1).tif','Identified1965textilefactory scene for continued postwar work; no marital or family status inferred for pictured workers.'),
('forandring',53,'File:Työtä tehtaassa Nokialla 1965 (HK19880108-11233).tif','Identified1965Nokiafactory work, illustrative postwarindustrial context; not presented as an image dated1970.'),
('forandring',54,'File:Virkkala daycare 1958 (JOKAVN4A1I53-2).tif','Actual Virkkala daycare photograph1958 for the source daycare topic; do not infer individual family arrangements or employment.'),
('kon',35,'File:What S Cooking Dad (123615287).jpeg','Illustrative father cooking scene for the explicit source discussion of men cooking; photo is not asserted to depict Finland.'),
('kon',50,'File:CreativeTools.se - PackshotCreator - Toy car (4294245549).jpg','Actual toy car, the source explicit example of a toy; does not prescribe which gender should use it.'),
('kon',52,'File:Doll in Stockholm Toy Museum.jpg','Museum doll and toy cradle, actual toys illustrating the discussion of socially dividing toys; no normative gender assignment added.'),
('kon',61,'File:Laundry time.jpg','Illustrative laundry objects and household work; does not identify any person as bearing a gender-defined duty.'),
('familjeformer',56,'File:Koskitie 4 Oulu 20230121.jpg','Actual apartment building in Oulu as housing context; no claim about its prices, residents or shared apartment arrangements.')]
metadata={}
for p in list(P.glob('*.json'))+list((P/'research').glob('*.json')):
    try:d=json.loads(p.read_text())
    except:continue
    if isinstance(d,dict):
        for v in d.get('query',{}).get('pages',{}).values():
            if v.get('imageinfo'):metadata[v['title']]=v['imageinfo'][0]
def run(c):
    slug,index,title,context=c;sid='hb-c09-'+slug;ep=R/'studio/episodes'/sid;sources=R/'studio/media'/sid/'sources';sources.mkdir(exist_ok=True,parents=True)
    record_path=ep/f'photo-source-{index:03}.json'
    if record_path.exists():
        retained=json.loads(record_path.read_text())
        if retained['title']==title:
            retained_raw=R/retained['raw_path']
            retained_url=retained['imageinfo'].get('thumburl',retained['imageinfo']['url'])
            result=subprocess.run(['.venv/bin/python','studio/production/remaining/download.py','--url',retained_url,'--output',str(retained_raw),'--sha256',retained['download_sha256']],capture_output=True,text=True)
            if result.returncode:print('RESTORE DEFERRED',title,result.stderr or result.stdout,flush=True);return
            print(sid,index,'retained pinned photograph and curated attribution',flush=True);return
    if title not in metadata:print('MISSING META',title,flush=True);return
    pi=metadata[title];m=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',str(m.get(k,{}).get('value',''))).strip()
    license=clean('LicenseShortName');artist=clean('Artist')
    if not any(t in license.lower() for t in ['cc','public','pd']):print('UNRESOLVED LICENSE',title,license,flush=True);return
    raw=sources/f'photo-{index:03}.jpg';url=pi.get('thumburl',pi['url'])
    if not raw.exists():
        result=subprocess.run(['.venv/bin/python','studio/production/remaining/download.py','--url',url,'--output',str(raw)],capture_output=True,text=True)
        if result.returncode:
            print('DOWNLOAD DEFERRED',title,result.stderr or result.stdout,flush=True);return
    if not artist:
        # Preserve truthful unrecorded-photographer status and credit the credited museum collection.
        artist='Photographer unrecorded in Commons metadata; Finnish Heritage Agency / JOKA Press Photo Archive' if 'JOKA' in str(m) else 'Creator unrecorded in Commons metadata; see linked museum catalogue and source metadata'
    rec=dict(index=index,title=title,imageinfo=pi,raw_path=str(raw.relative_to(R)),context=context,attribution=artist,license=license,license_url=clean('LicenseUrl'),description=clean('ImageDescription'),metadata_source='Commons imageinfo extmetadata retained unchanged',download_sha256=hashlib.sha256(raw.read_bytes()).hexdigest())
    (ep/f'photo-source-{index:03}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');print(sid,index,title,license,'acquired',flush=True)
for choice in choices:run(choice)
