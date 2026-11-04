"""Source-bound inheritance and protection diagrams with neutral anonymous figures."""
from pathlib import Path
import yaml,json,re
plans={
'arv':'''none;money|pengar;house|en bostad
none;house|egendom;will|arv
none;court|lagen;scales|delas;generations|arvingarna
none;child|den avlidnes barn;split|om något av barnet har dött;generations|barnbarnen, deras barn
none;person|maken eller makan;parents|föräldrarna;friends|syskonen
blocked;friends|kusiner;will|arvingar
flow;person|en människa;will|ett testamente;house|egendom
none;child|den avlidnes barn;scales|åtminstone hälften;will|testamente
none;will|testamente;house|sin egendom;person|någon annan
none;calendar|1878;scales|lika arvsrätt
none;parents|kvinnor och män;scales|samma rätt;will|arv
flow;house|egendom;institution|staten
none;will|ett arv;document|bouppteckning
none;document|En bouppteckning;house|tillgångar;receipt|skulder
none;person|änka eller änkling;child|barn
none;calendar|inom tre månader;friends|samtliga av den avlidnes arvingar;notice|bjudas in
flow;house|den avlidnes egendom;document|en förteckning
none;document|Förteckningen;document|bouppteckningshandling
none;person|en advokat;person|någon av arvingarna;document|Handlingen
none;house|förmögenhet och skulder;generations|arvingar;will|testamentet
blocked;generations|Arvingarna;receipt|skulder;document|korrekt antecknade i bouppteckningen
none;court|lagen;generations|Vem som ärver;house|egendom
none;person|Du;split|till vilka personer;house|din egendom
flow;person|Du;will|ett testamente;generations|vem som ärver
none;will|Ett testamente;friends|två ojäviga vittnen
none;will|testamentet;no_will|inte legitimt
flow;person|en jurist;will|testamente
none;receipt|två;receipt|arvsskatteklasser
none;generations|närmaste släktingar;money|mindre skatt
none;person|mer avlägset släkt;money|skatten högre
flow;coins|större arvet;receipt|Skatteprocenten;scales|högre''',
'heder':'''none;family1|familjen;generations|släkten;shield|Hedersrelaterat våld
none;family1|familjens;speech|heder
none;person|en människa;friends|respekt från andra
none;generations|Släkten;family1|hela familjens;document|angelägenhet
none;person|en individs gärningar;document|regler och seder;shield|våld eller hota med våld
none;family1|en familj;generations|släkt;document|normerna i gemenskapen
none;person|en ung person;friends|kompisar;clothes|klär sig
none;friends|gemenskapsorienterade kulturer;parents|män;unequal_scales|mycket mer makt än kvinnor
none;finland|Finland;shield|Det förekommer också
none;person|flickor och kvinnor;rainbow|sexuella minoriteter eller könsminoriteter;shield|våldet
none;person|pojkar och män;shield|hedersrelaterat våld
none;person|De;speech|pressas;shield|våld mot andra
none;shield|psykiskt;shield|fysiskt
none;rings|tvingas att gifta sig;clothes|klä sig som hen vill;friends|vem hen sällskapar med
none;globe|det gamla hemlandet;shield|andra hot;split|förhindrande av skilsmässa
none;finland|Finlands lag;shield|hedersrelaterat våld;court|brott
none;person|offret;shield|känna igen våldet;clock|det inledande skedet
none;speech|påtryckningar;shield|våld
flow;person|söka hjälp;speech|situationen ännu inte är så allvarlig
none;couple|den ena eller båda makarna;no_rings|inte fritt;person|valet av make
none;speech|påtryckningar eller utpressning;shield|våld eller hota med våld;rings|äktenskap
none;person|hota;family1|familjen;friends|gemenskapen
none;person|flickor och kvinnor;person|pojkar och män;no_rings|tvingade att gifta sig
none;couple|den ena eller båda personerna;child|minderåriga
none;child|Personer under 18 år;no_rings|inte officiellt ingå äktenskap;finland|Finland
none;child|Ett barn;globe|ett annat land;no_registry|utan någon officiell vigsel
none;no_rings|tvinga någon in i äktenskap;court|brott;finland|Finland
none;book|finsk lagstiftning;no_rings|tvångsäktenskap;shield|människohandel
none;parents|barnets vårdnadshavare;child|sitt barn;court|dömas för brott
support;shield|Hjälpsystemet för offer för människohandel;person|offer för tvångsäktenskap;speech|information'''}
for slug,raw in plans.items():
    ep=Path('studio/episodes')/('hb-c09-'+slug);rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences'];lines=raw.splitlines();assert len(lines)==len(rows),(slug,len(lines),len(rows));out=[]
    for i,(line,row) in enumerate(zip(lines,rows),1):
        relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
        for node in objects:
            if node[1] not in row['sv']:
                m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(slug,i,node[1]);node[1]=m.group()
        reason='Individual source-based composition: '+', '.join(label for _,label in objects)+'. '
        reason+=('Only anonymous neutral figures and protective/authority symbols are used; no ethnicity, religion or real person is identified as a perpetrator or victim.' if slug=='heder' else 'Only the archived source relationships and qualifiers are illustrated; no monetary amounts, tax rates or additional inheritance hierarchy is invented.')
        out.append(dict(id=f'{slug}-{i:03}',objects=objects,relation=relation,reason=reason))
    if slug=='arv':
        out[7].update(objects=[['child','den avlidnes barn'],['no_will','om det inte fanns något testamente'],['scales','åtminstone hälften']],title='det belopp som de enligt lag skulle få',reason='The protected minimum is at least half of the child statutory share without a will, not automatically half of the entire estate.')
        out[8].update(objects=[['child',''],['will','testamente'],['person','någon annan']],source_context_ids=[rows[7]['sentence_id']],reason='The child protected share from the preceding source sentence remains relevant even where a will names someone else.')
        out[11].update(objects=[['no_will','inte har upprättat något testamente'],['house','egendom'],['institution','staten']],title='inte har några arvingar',relations=['none','flow'],reason='Both conditions are visible: no heirs and no will. Only under that source condition does property pass to the state.')
        out[20].update(relations=['blocked','notify'],reason='Heirs-to-debt liability is blocked only with the source condition that debts are correctly entered in the estate inventory.')
        out[30]['objects']=[['coins','större arvet'],['rise','högre'],['receipt','Skatteprocenten']]
    (ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
