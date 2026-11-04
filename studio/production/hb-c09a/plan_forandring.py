"""Per-sentence pictorial direction for family history; photography added to concrete historical scenes."""
from pathlib import Path
import yaml,json,re
sid='hb-c09-forandring';ep=Path('studio/episodes')/sid;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
# Each line: relation; pictorial object | exact source label; ...
specs='''none;family1|föräldrar och minst ett barn
none;family1|kärnfamilj
none;family2|andra slags familjer;couple|familjer
flow;calendar|hela tiden;family1|förändras
none;family1|ett;family2|två barn
flow;calendar|senare;child|barn
none;person|människor;couple|par
none;couple|frivilligt barnlösa
none;couple|skulle vilja;heart|få barn
none;family1|familj;generations|släkt
none;family1|olika saker;generations|hänger samman
none;house|bor tillsammans;family1|föräldrar och barn
none;generations|far- och morföräldrar;parents|fastrar, mostrar;couple|farbröder, morbröder och kusiner
flow;couple|bestämma;family1|hur många barn
flow;calendar|1960-talet;document|familjeplanering
flow;couple|par själva;shield|preventivmedel;child|antalet barn
flow;person|kvinnornas ställning;document|familjeplanering
flow;city|Urbaniseringen;family1|familjerna
flow;farm|landet;city|städerna;work|arbete
none;calendar|1920;farm|jordbruk;calendar|1975
flow;city|städerna;factory|fabrik;work|servicebranschen
flow;work|lönearbetet;person|inte längre beroende
support;generations|familjen och släkten;money|ekonomiska och sociala stödet
flow;generations|släkten;institution|staten
support;work|lönearbete;money|stöd;person|klara sig
flow;person|Ogifta kvinnor;calendar|slutet av 1800-talet;shield|egna angelägenheter
flow;person|Gifta kvinnor;calendar|1930;shield|frigjordes
flow;generations|släkten;rings|valet av make
flow;calendar|1700-talet;couple|mannen och kvinnan;heart|frivilliga samtycke
flow;calendar|slutet av 1800-talet;heart|kärlek;rings|äktenskapet
none;person|ogift;speech|föraktades
none;split|Skilsmässor;institution|lutherska kyrkan
none;book|viktiga lagar;scales|samma rättigheter
none;calendar|1878;will|lika arvsrätt
none;calendar|1906;vote|rösta och kandidera
none;calendar|1919;work|utöva en näring
none;calendar|1921;school|rätt att lära sig
none;calendar|1922;contract|arbetsavtal
none;calendar|1930;rings|äktenskapet;scales|jämställda
none;parents|kvinnor och män;work|arbete;family1|familjeliv
none;parents|kvinnor och män;work|förvärvsarbetar
none;person|mammorna;child|riktigt små barn
none;person|Männen;house|hushållsarbetet;child|barnskötseln
none;farm|egna gården
support;person|mammorna;child|Barnen;work|arbetet
support;generations|far- och morföräldrar;house|samma hushåll;child|barnen
together;work|arbete;family1|familjeliv
flow;calendar|mitten av 1800-talet;person|kvinnor;factory|fabriker
none;person|unga kvinnor;school|lärare;hospital|sjuksköterskor
flow;calendar|1900-talet;person|gifta kvinnor;work|utanför hemmet
none;calendar|1939–1944;factory|fabrikerna;farm|lantgårdarna
none;person|Många kvinnor;work|arbetet
none;calendar|1970-talet;city|urbaniseringen;work|förvärvsarbetade
support;institution|Kommunerna;school|dagvård;person|kvinnor
flow;person|mammor;work|utanför hemmet;family1|familjen
flow;work|Arbetet;person|självständighet;money|egna pengar
flow;school|utbildade sig;work|förvärvsarbetade;person|påverka
none;calendar|hundra åren;person|individuellt;city|samhället
none;farm|jordbruksdominerade;generations|släkten;institution|religionen
flow;factory|fabriker;city|städerna;person|individen
support;institution|välfärdsstaten;hospital|de sjuka;generations|de äldre och barnen
none;person|Människorna;generations|släkten
none;person|var och en;split|individuella val
support;person|individerna;institution|välfärdssamhället
none;money|betala skatter;work|frivilligarbete
none;person|individens friheter;scales|samma rättigheter
blocked;generations|släktingar;institution|offentligt beslutsfattande
none;family1|en familj;work|en arbetsgemenskap;city|samhället
together;person|människorna;family2|gemenskap och tillhörighet
support;person|Var och en;shield|moraliska skyldigheter;generations|grupperna
flow;person|Alla oavsett kön;couple|själva välja sin livskamrat
none;couple|de unga;heart|kärleksrelationer
none;speech|diskuterar;generations|släktingar;lock|privatliv
none;generations|Släktingarna;speech|inte alltid
flow;generations|släktingar;split|förstöra relationerna
flow;person|egna beslut;family2|förändrat familjerna
flow;person|människor;couple|flera partner;calendar|sitt liv
flow;couple|sällskapar;house|flyttar ihop;rings|gifter sig
none;couple|parförhållande;heart|kärlek;family1|familjen
none;calendar|1800-talet;person|kvinnosaksrörelsen
none;parents|kvinnor och män;scales|likställdhet
none;calendar|1864;person|ogifta kvinnor;shield|befriade
none;person|De;split|sina egna angelägenheter
none;person|gifta kvinnor;lock|förmyndarskap
support;parents|föräldrarna;child|minderåriga barn;couple|gifta par
blocked;money|underhållsskyldighet;generations|släktingar
none;person|enskilda människor;generations|släktingar;money|ekonomiskt
support;institution|samhället;shield|sociala tryggheten'''.splitlines()
assert len(specs)==len(rows),(len(specs),len(rows));out=[]
for i,(line,row) in enumerate(zip(specs,rows),1):
    relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
    for node in objects:
        if node[1] not in row['sv']:
            m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(i,row['sentence_id'],node[1]);node[1]=m.group()
    out.append(dict(id=f'history-{i:03}',objects=objects,relation=relation,reason='Individually composed source-bound family-history illustration: '+', '.join(label for _,label in objects)+'. '+('Directional connection follows the stated historical or support relationship.' if relation in ['flow','support'] else 'Symbols visualize only the explicit source concepts; labels retain exact wording.')))
out[19] = {'id': 'history-020', 'objects': [['calendar', '1920'], ['farm', 'jordbruk'], ['calendar', '1975']], 'relation': 'none', 'reason': 'Exact source proportions of the Finnish population supported by agriculture: 70 percent in 1920 and 15 percent in 1975. Bar heights use one shared zero baseline; no interpolation or additional dates.', 'chart': [{'year': '1920', 'percent': 70, 'source_value': '70 procent'}, {'year': '1975', 'percent': 15, 'source_value': '15 procent'}], 'highlights': ['1920', '70 procent', '1975', '15 procent']}
out[24]['relations']=['together','flow']
out[8]['objects'][1][1]='kan inte få barn'
out[20]['relations']=['flow','or']
out[20]['title']='vanligtvis'
out[77]['relations']=['flow','or']
out[77]['title']='ofta länge innan'
out[24]['reason']='Earned work and state support jointly help people manage; no arrow implies that having a job itself causes benefit payment. Exact source goal and even-without-relatives qualification remain visible.'
out[84]['objects'][2][0]='couple_support'
out[84]['relations']=['support','none']
out[84]['reason']='Two distinct source obligations: parents financially support their underage child; married partners support each other inside a separate pictorial node. There is no financial-support arrow from the child to the spouses.'
(ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
