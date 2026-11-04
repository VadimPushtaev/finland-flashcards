"""Source-specific diagrams distinguish stereotypes from endorsed norms."""
from pathlib import Path
import yaml,json,re
sid='hb-c09-kon';ep=Path('studio/episodes')/sid;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
specs='''none;family1|Familjerna;scales|jämställdheten
none;house|arbetsfördelningen;family1|familjerna;scales|jämställdhetsfråga
flow;house|Den;work|arbetsmarknaden;scales|könens ställning
none;parents|familjerna;child|flickor och pojkar;scales|samma sätt
flow;child|som barn;person|senare i livet
none;speech|förenklad och generaliserande uppfattning;person|personer
none;person|en person;registry|könet, nationaliteten;calendar|åldern
none;speech|generalisering;person|alla kvinnor;people|alla tonåringar
none;speech|Stereotyper om kön;house|många områden av livet
none;speech|generaliserande uppfattningar;parents|kvinnor och män
none;clothes|kläder;speech|Stereotyper;book|filmer
flow;speech|stereotyper;document|normer
none;speech|förväntningar;person|människor
none;document|könsnorm;parents|kvinnor och män
none;speech|stereotyp;person|kvinnor;clothes|utseende
none;document|könsnorm;person|en kvinna;clothes|utseende
none;person|hon;speech|accepteras;document|normen
none;document|oskrivna regler;parents|kvinnor och män
flow;document|dessa regler;person|socialt straff
none;speech|förvåning;speech|skratt;speech|ogillande
none;shield|våld;person|utestängning;friends|gemenskapen
none;person|människor;document|normen
none;speech|könsstereotyper;document|könsnormer;person|människors beteende
blocked;person|välbefinnande;scales|jämställdheten
flow;calendar|över tid;speech|Könsstereotyper;document|könsnormer
none;friends|olika gemenskaper;document|olika
none;scales|Hur allvarliga;document|normerna;person|sociala straffen
none;city|stora städerna;house|små orter
none;cleaning|hushållsarbetet;child|barnen;work|arbeta utanför hemmet
flow;speech|stereotyper;house|arbetsfördelningen
none;house|Arbetsfördelningen;scales|mer jämställd
none;person|kvinnor;clock|mer tid;cleaning|hushållsarbete
none;person|Männen;clock|mer tid;work|förvärvsarbete
none;person|Kvinnorna;cleaning|hushållsarbete;calendar|30 år sedan
none;person|Männen;child|barnskötsel;cooking|matlagning
equal;parents|Många familjer;cleaning|hushållsarbetet;child|barnskötseln
none;family1|familjens;heart|välbefinnande
support;parents|båda makarna;money|försörja familjen
none;money|familjens ekonomi;work|arbetslös;hospital|sjuk
none;parents|kvinnor och män;cleaning|hushållsarbetet;money|försörja familjen
none;speech|Könsstereotyper;document|mindre starka;house|arbetsfördelning
none;person|män;child|omvårdande;work|kvinnor
none;speech|många fortfarande anser;person|mammans uppgift;baby|små spädbarn
flow;child|Barn;speech|könsstereotyper;document|könsnormer
flow;child|som barn;person|som vuxen;scales|jämställdhet
none;child|barn;school|skolan;scales|jämställdhet
none;child|Ett barns;split|vad hen kan göra
none;parents|de vuxna;shield|uppmärksamhet;child|barnuppfostran
flow;parents|Vuxna;child|barn;speech|könsstereotyper
none;doll|en docka;toycar|en leksaksbil
none;child|barnen;speech|vissa saker;parents|kvinnor och andra till män
none;toys|leksaker;clothes|kläder;child|Barns tankesätt
flow;child|barnen;speech|könsstereotyper;document|könsnormer
flow;child|de;school|studera;work|yrke
none;child|ett barns;shield|välbefinnande
none;child|en pojke;clothes|en prinsessklänning;speech|inte är passande
none;school|småbarnspedagogiken;child|barnen;split|olika roller
none;child|Barnen;heart|precis som de är
none;parents|vuxna;toys|leksaker;child|barn
none;person|beteenden;shield|svårare att lägga märke till
none;child|flickor;cleaning|hushållssysslorna
none;child|pojkar;speech|skrika;child|flickor
flow;parents|vuxna;child|flickor och pojkar;document|könsnormerna
none;child|flickorna;friends|andra;house|utrymme
none;child|Pojkar;shield|självsäkra
flow;child|barndomen;calendar|årtionden framöver;scales|jämställdheten'''.splitlines()
assert len(specs)==len(rows),(len(specs),len(rows));out=[]
for i,(line,row) in enumerate(zip(specs,rows),1):
    relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
    for node in objects:
        if node[0]=='people':node[0]='friends'
        if node[1] not in row['sv']:
            m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(i,row['sentence_id'],node[1]);node[1]=m.group()
    out.append(dict(id=f'equality-{i:03}',objects=objects,relation=relation,reason='Source-specific pictorial composition: '+', '.join(label for _,label in objects)+'. When the sentence discusses stereotypes or norms, speech/document symbols denote social expectations being described, not innate truths or endorsed gender rules.'))
out[20]['objects'][0][0]='alert'
out[54]['objects']=[['child','ett barns'],['alert','skadligt'],['shield','välbefinnande']]
out[54]['title']='om hen upplever att hen är fel på något sätt'
out[59]['objects'][1][0]='eye'
out[59]['title']='svårare att lägga märke till'
(ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
