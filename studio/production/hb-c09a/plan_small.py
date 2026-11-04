"""Direct short Chapter9 benefit/rights episodes with exact source conditions."""
from pathlib import Path
import json,yaml,re
plans={
'barnbidrag':'''support;institution|FPA;child|alla barn;calendar|varje månad
support;money|barnbidraget;family1|familjens ekonomi
none;institution|FPA;calendar|slutet av den månad;child|17 år
none;institution|FPA;child|varje barn;finland|stadigvarande i Finland
support;singleparent|En förälder som bor ensam;money|förhöjt barnbidrag
blocked;money|barnbidraget;court|ingen skatt
none;family1|familjen;globe|utomlands;money|barnbidrag
none;child|bosatt utomlands;person|barnets förälder;work|arbetar i Finland''',
    'tolv':'''none;child|Barnets;document|för- eller efternamn;lock|barnets tillstånd
none;child|Barnet;institution|trossamfund;lock|barnets tillstånd
none;child|Barnets;lock|tillstånd;institution|utträde ur ett trossamfund
none;split|föräldrar skiljer sig;child|barnet;parents|båda sina föräldrar
none;child|barnet;speech|Barnets åsikt;calendar|tolv år gammalt
none;child|barnet;person|någon av föräldrarna;speech|sin åsikt
none;child|Barnets åsikt;speech|beslut;house|barnet ska bo
flow;child|barnet;speech|själv be om;house|vård utom hemmet
none;child|barnet;house|någon annanstans;parents|sina föräldrar
none;child|barnkapning;shield|Det är fråga om
none;child|ett barn under 16 år;globe|utomlands;lock|utan vårdnadshavarens tillstånd
none;child|ett barn;finland|Finland;clock|avtalad tidpunkt
none;finland|Finland;child|barnkapning;court|brott
flow;person|Ta kontakt;shield|polisen;house|din hemort''',
'underhall':'''support;parents|föräldern;child|ett barn under 18 år;school|vård och utbildning
support;parents|båda föräldrarna;child|barnets underhåll
flow;split|föräldrarna skiljer sig;contract|komma överens;child|barnets underhåll
support;person|Den förälder som inte bor med barnet;money|underhållsbidrag;singleparent|den förälder hos vilken barnet bor
none;child|barnets underhållsbehov;scales|belopp;parents|föräldrarnas underhållsförmåga
none;child|barnet;money|penningbelopp;calendar|varje månad
none;food|mat;clothes|kläder;school|småbarnspedagogik
support;parents|föräldrarna;child|Barnets underhållsbehov
none;money|inkomsterna;receipt|skatter och övriga obligatoriska utgifter;scales|Underhållsförmågan
flow;person|Du;speech|hjälp;scales|beräkna underhållsbidraget
none;parents|båda sina föräldrar;child|barnet;money|underhållsbidrag
none;person|den andra föräldern;scales|underhållsförmåga;money|barnets levnadskostnader
flow;singleparent|den förälder som bor med barnet;document|ansöka om;institution|FPA
flow;person|Du;document|ansöka om;institution|FPA
blocked;person|den andra föräldern;money|underhållsbidrag
none;money|små inkomster;document|Inget underhållsbidrag
none;document|Underhållsbidraget;registry|föräldraskapet
none;money|små inkomster;scales|mindre än underhållsstödet
none;singleparent|Du;child|adopterat ett barn ensam
none;child|Barnet;registry|fadern har inte fastställts;parents|inte två underhållsskyldiga föräldrar
none;finland|stadigvarande bosatt i Finland;globe|tillfälligt utomlands;calendar|högst sex månader
none;globe|EU- eller EES-land eller Schweiz;finland|Finland;work|för att arbeta
none;child|barnet;finland|i Finland;house|bo med dig'''}
for slug,raw in plans.items():
    ep=Path('studio/episodes')/('hb-c09-'+slug);rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences'];specs=raw.splitlines();assert len(specs)==len(rows),(slug,len(specs),len(rows));out=[]
    for i,(line,row) in enumerate(zip(specs,rows),1):
        relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
        for node in objects:
            if node[1] not in row['sv']:
                match=re.search(re.escape(node[1]),row['sv'],re.I);assert match,(slug,i,node[1]);node[1]=match.group()
        out.append(dict(id=f'{slug}-{i:03}',objects=objects,relation=relation,reason='Exact-source pictorial explanation of '+', '.join(label for _,label in objects)+'. Every source qualifier remains in the bilingual text; no invented benefit amount,country membership,deadline or entitlement.'))
    if slug=='underhall':
        out[8]['relations']=['minus','equal']
        out[17]['objects'][1][0]='unequal_scales'
        out[18]['objects'][0][0]='person'
        out[19]['objects'][2][0]='person'
    if slug=='tolv':
        out[10]['title']='som är bosatt i Finland'
        out[11]['objects'][2]=['missed_deadline','inte har lämnats tillbaka']
        out[11]['title']='vid avtalad tidpunkt'
    (ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
