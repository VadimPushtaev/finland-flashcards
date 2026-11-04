"""Individual family-form illustrations; no inferred identities or personal circumstances."""
from pathlib import Path
import yaml,json,re
sid='hb-c09-familjeformer';ep=Path('studio/episodes')/sid;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
specs='''none;family1|två föräldrar och deras gemensamma barn
none;family1|föräldrarna;rings|gifta
none;parents|föräldrarna;family1|inte är gifta
none;generations|fler än två generationer
none;generations|far- eller morförälder;house|bor tillsammans
none;family2|barnfamiljer
none;couple|bara två vuxna
none;couple|Alla par;heart|nöjda med sitt liv utan barn
none;couple|En del par;heart|även om de skulle vilja
none;hospital|fertilitetsbehandlingar;child|få barn
none;couple|Par;child|adoptera ett barn
flow;child|Ett adoptivbarn;contract|adoption;parents|nya föräldrar
none;child|barn;document|utlandet
none;contract|Adoptionsprocessen;court|lag
flow;speech|adoptionsrådgivning;house|familjens livssituation
support;person|familjehemsförälder;house|ett hem;child|ett barn eller en ung person
support;person|En familjehemsförälder;house|sitt hem;shield|tryggt
support;parents|familjehemsföräldrarna;child|Barnet;calendar|tills vidare
none;singleparent|bara en vuxen
none;singleparent|En ensamförsörjare;split|skild;person|änka eller änkling
none;singleparent|bara en förälder
none;person|Kvinnor;hospital|fertilitetsbehandling;child|utan make
none;singleparent|en förälder med barnen;house|bor
none;person|Föräldern;shield|ensam eller gemensam vårdnad;child|barnet
support;person|ensamstående förälder;child|fostran av barnet
support;parents|föräldrarna;speech|tillsammans överens;child|barnets angelägenheter
none;singleparent|ensamförsörjare;child|barnomsorg;work|förvärvsarbete
none;money|ekonomiska situationen;singleparent|ensam ta hand om ett barn
support;institution|Finska staten;singleparent|ensamförsörjare
support;document|FPA;money|ensamförsörjartillägg;singleparent|familjer med en förälder
flow;split|skilt sig;couple|en ny partner;rings|gifter sig på nytt
none;family2|bonusfamilj;child|tidigare förhållanden
none;family3|bonusfamilj;child|gemensamma barn
none;child|barnen;house|två hem;house|bonusfamilj
none;child|barnen;house|den andra föräldern;calendar|en del av tiden
none;rainbowfamily|regnbågsfamiljer
none;rainbow|Regnbågen
none;rainbowfamily|olika slags regnbågsfamiljer
none;friends|två mammor;child|barn
none;rainbowfamily|Regnbågsfamiljer;child|barn på olika sätt
none;couple|lesbiska par;hospital|fertilitetsbehandlingar
none;singleparent|Den ena makan;child|barn från ett tidigare förhållande
none;friends|en vän eller ett annat par;child|barnets uppfostran;parents|fler än två vuxna
none;rainbowfamily|regnbågsfamiljer;scales|samma rättigheter;family1|en man och en kvinna
none;speech|attityder;rainbowfamily|mer accepterande
none;calendar|2017;scales|rättigheterna;rainbowfamily|regnbågsfamiljer
support;friends|två personer;child|föräldrar tillsammans
none;child|Barnet;house|båda föräldrarna;calendar|turvist
none;friends|vänner;child|föräldrar tillsammans
none;person|personer som bor ensamma;person|en annan person;child|vill ha barn
support;friends|endast;child|uppfostra ett barn tillsammans
none;friends|Föräldrapartnerskap;family1|en familjeform
none;book|studerande;house|små enrummare
none;house|gemensamma bostäder;cooking|kök;cleaning|badrum
together;friends|kompisar;house|flytta ihop
none;house|Att dela lägenhet;money|för dyrt
together;friends|de boende;heart|gemenskap
none;person|vuxna;house|ensamma
none;elder|äldre kvinnor;house|bor ofta själva
none;person|bor ensam;generations|andra släktingar;friends|viktiga vänner
none;person|bo själv;heart|ensamhet
none;couple|Gifta makar av samma kön;child|adoptera ett barn;family1|adoption inom familjen
flow;person|makan/maken;child|sin makas/makes barn;parents|barnets andra förälder
none;child|ett barn;parents|högst två juridiska föräldrar'''.splitlines()
assert len(specs)==len(rows),(len(specs),len(rows));out=[]
for i,(line,row) in enumerate(zip(specs,rows),1):
    relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
    for node in objects:
        if node[1] not in row['sv']:
            m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(i,row['sentence_id'],node[1]);node[1]=m.group()
    out.append(dict(id=f'familyform-{i:03}',objects=objects,relation=relation,reason='Individual source-based family-form composition: '+', '.join(label for _,label in objects)+'. Neutral schematic people depict only the source relationships; no real person is assigned a sensitive personal or family status.'))
(ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
