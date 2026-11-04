"""Acquire actual ageing-support objects,domestic settings and documented buildings."""
from pathlib import Path
import json,subprocess,re,shutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;SID='hb-c10-aldre';E=R/'studio/episodes'/SID;S=R/'studio/media'/SID/'sources';S.mkdir(parents=True,exist_ok=True);selected={}
choices={
9:('health-object-stethoscope-research.json','File:Littmann Stethoscope.jpg','Actual isolated stethoscope as healthcare object;no diagnosis,examination instruction,treatment claim or product recommendation.'),
51:('elderly-meals-research.json',"File:Meals on Wheels HotShot.JPG",'Actual Meals-on-Wheels meal-delivery vehicle,HamburgTownship,Michigan. Meal-delivery category only;not Finnish county fleet,named localprovider,service entitlement or fixed deliveryschedule.'),
53:('elderly-medical-alert-research.json','File:Neat Hausnotruf NEO.jpg','Primary description identifies Neat NEO medical home-alarm device. Isolated object example,not ordinarysmartphone. No112label,automatic ambulance guarantee,medical measurement,endorsement or current countyvendor promise.'),
60:('elderly-servicecentre-research.json','File:Kontulan Monipuolinen Palvelukeskus - panoramio.jpg','Verified Kontula multipurpose service-centre premises,Helsinki. Service-centre category,not institutionalresidence andno current named-site timetable,admission,price orcare guarantee.'),
70:('elderly-servicehouse-research.json','File:Huhtasuon palvelutalo 2018.jpg','Primary title identifies Huhtasuo service-house premises,Jyvaskyla2018. Sheltered/servicehousing category distinct institutionalcare,no specific current staffing,ownership,payment or age-only placement guarantee.'),
73:('elderly-home-research.json','File:Living room with 1960s objects.jpg','Actual domestic furniture:sofas,loungechair,storage furniture andcurtains. Object-category example of furnishing with ownbelongings;not attributed to a servicehouse or identifiable olderresident.'),
80:('health-object-rollator-research.json','File:Rollator 2.jpg','Primary description identifies actual standard folding rollator with basket,tray,wheels andparkingbrakes. Loan-aidexample only;no brand recommendation,loan eligibility or prescribed adjustment dimensions.'),
81:('health-object-rollator-research.json','File:Rollator-carbon.jpg','Actual carbon walking rollator withbag andbrakes. Correct walking support object,not wheelchair. Different documented model for definition;no recommendation,loan entitlement or demonstration technique.')}
for i,(metadata,title,context)in choices.items():
 p=next(p for p in json.loads((P/metadata).read_text())['query']['pages'].values()if p['title']==title);pi=p['imageinfo'][0];artist=re.sub('<[^>]+>','',pi['extmetadata'].get('Artist',{}).get('value','')).strip();assert artist and len(artist)<160,(title,artist);url=pi.get('thumburl',pi['url']).replace('https://thumb.wikimedia.org/','https://upload.wikimedia.org/').split('?')[0];dest=S/f'foreground-{i+1:02}.jpg';subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/download.py','--url',url,'--output',str(dest),'--timeout','300'],cwd=R,check=True);selected[str(i)]=dict(title=title,imageinfo=pi,path=str(dest.relative_to(R)),download_url=url,context=context);(E/'selected-photos.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');print(i,title,flush=True)
reuse={
18:('hb-c10-folkhalsa',16,'Actual varied vegetables in grocery store,Paris. One visible dietary-habit example;no amount,product recommendation,diagnosis,older-person status or omission of other habits from exact panel. Meaningful earlier source reuse.'),
23:('hb-c11-fritid',0,'Actual Helsinki Esplanadi park2022,ordinary enjoyable publicplace. No photographedvisitor assigned age,diagnosis or socialservice status;no guarantee of medical outcome.'),
47:('hb-c10-psykisk',7,'Actual Klaukkala publichealth-centre premises. Ownhealthstation category for applying for homenursing;not evidence of current local counter/hours or guaranteed homevisit.'),
63:('hb-c11-fritid',5,'Actual Oulu theatre exterior. Source culturalactivity example only;no current daycentre outing,ticket price,freeentry or universal access guarantee.'),
64:('hb-c10-vard',33,'Actual Vantaa taxi2008. Transportmode category for county-arranged daycentretravel,not a named countycontractor,freefare,guaranteed accessibility or schedule. Exact source retainsusuallymeal andpossible separatefee.')}
for i,(sid,index,context)in reuse.items():
 p=json.loads((R/'studio/episodes'/sid/'selected-photos.json').read_text())[str(index)].copy();raw=R/p['path'];dest=S/f'foreground-{i+1:02}.jpg';
 if not dest.exists():shutil.copyfile(raw,dest)
 assert dest.read_bytes()==raw.read_bytes();p.update(path=str(dest.relative_to(R)),context=context,retained_source_episode=sid);selected[str(i)]=p
# One verified apartment photograph is a category of domestic housing,not a pensioner'sactualprivatehome.
p=json.loads((R/'studio/episodes/hb-c10-pension/selected-photos.json').read_text())['59'].copy();raw=R/p['path'];dest=S/'foreground-36.jpg'
if not dest.exists():shutil.copyfile(raw,dest)
assert dest.read_bytes()==raw.read_bytes();p.update(path=str(dest.relative_to(R)),context='Verified Helsinki apartmentbuilding2020. Domestic housingcategory only,no resident assigned age,health,tenancy,pension,dependency or benefitstatus.',retained_source_episode='hb-c10-pension');selected['35']=p
(E/'selected-photos.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n');(E/'retained-photo-assets.json').write_text('{}\n');print('Acquired',len(selected),'actual photographs;raw inspection required.',flush=True)
