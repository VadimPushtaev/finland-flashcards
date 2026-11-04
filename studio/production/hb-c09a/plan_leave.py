"""Individually illustrate archived parental/care-leave conditions and amounts."""
from pathlib import Path
import yaml,json,re
plans={
'foraldraledighet':'''none;person|Du;calendar|14–30 vardagar;baby|förlossningsdatumet
none;person|du;money|graviditetspenning
none;calendar|40 vardagar;calendar|ungefär 1,5 månader
none;shield|följande villkor;money|graviditetspenning
none;person|den förälder som ska föda barnet;calendar|154 dagar
blocked;person|Du;work|ditt arbete
none;person|Du;institution|FPA:s stöd
none;school|studerande;work|arbetslös;money|graviditetspenning
flow;calendar|graviditetspenningperioden;person|föräldraledig;money|föräldrapenning
none;institution|FPA;shield|följande villkor
none;baby|ett barn som är under två år;child|ett adoptivbarn;calendar|tagits i vård för mindre än två år sedan
blocked;person|Du;work|arbetar inte
none;person|Du;institution|FPA:s stöd
none;person|den förälder som ska föda barnet;calendar|graviditetspenningperioden;money|föräldrapenning
flow;baby|barnet har fötts;calendar|inleda föräldrapenningperioden
none;parents|Föräldrarna;calendar|320 vardagar;calendar|ungefär 13 månader
none;parents|Vardera föräldern;scales|hälften;calendar|160 dagar
none;singleparent|barnets enda vårdnadshavare;calendar|alla 320 vardagar
none;twins|tvillingar;calendar|ytterligare 84 vardagar
none;calendar|flexibelt när du vill;child|barnet fyller två år
flow;calendar|högst 63 vardagar;person|barnets andra förälder
none;money|föräldradagpenningen;money|din årsinkomst
none;money|Föräldrapenningen;scales|mindre än lönen
none;person|inte har några inkomster;money|minimibelopp
flow;person|Ta i god tid reda på;speech|betalar ut lön;work|din arbetsgivare
flow;document|denna uppgift;document|din ansökan om föräldrapenning
support;institution|FPA;money|föräldrapenningen;work|din arbetsgivare
none;child|barnet;work|deltidsarbete;money|partiell föräldrapenning
none;clock|högst fem timmar;calendar|om dagen
none;person|Du;contract|ett avtal om deltidsarbete;work|din arbetsgivare
none;parents|Föräldrarna;work|arbeta deltid;child|sköta barnet
support;institution|FPA;money|partiell föräldrapenning;parents|båda föräldrarna''',
'vardledighet':'''none;house|hemma;work|oavlönad vårdledighet;child|barnet fyller tre år
flow;person|Du;document|ansöka om hemvårdsstöd;institution|FPA
none;person|Du;work|inte har ett jobb;money|hemvårdsstöd
none;shield|alla dessa villkor;money|hemvårdsstöd
blocked;child|Barnet;school|daghem
support;person|Föräldern;generations|en släkting;child|barnet
none;baby|barnet föddes;calendar|160 vardagar;calendar|ungefär sex månader
blocked;money|föräldrapenning eller partiell föräldrapenning;child|barnet
none;shield|ett av följande krav
none;child|Barnet;finland|stadigvarande i Finland
none;finland|tillfälligt i Finland;work|minst en av föräldrarna arbetar;shield|arbetspensionsförsäkring
none;family3|flera barn under skolåldern;school|inte är på daghem;money|hemvårdsstöd
none;child|yngsta barn;calendar|tre år;money|Stödet upphör
none;money|Hemvårdsstödet;court|skattepliktigt
none;child|barnet;globe|annat land;money|Hemvårdsstöd
none;money|hemvårdsstöd;finland|Finland
none;work|arbetar i Finland;child|ditt barn;globe|annat EU- eller EES-land
none;person|du;globe|tillfälligt utomlands
none;institution|FPA;calendar|tillfällig;house|permanent
none;parents|föräldrar;work|arbetar på deltid;child|vård av barn
none;parents|båda föräldrarna;work|arbetar på deltid;clock|olika tider
none;child|ett barn i taget;money|Vårdpenning;court|skattepliktig inkomst
none;money|flexibel vårdpenning;shield|Du kan få
none;person|du;child|barnet;finland|i Finland
none;child|barnet;calendar|under tre år
none;work|arbetar;clock|högst 30 timmar;calendar|i veckan
blocked;child|barnet;school|daghem;clock|på heltid
none;child|Barnet;school|daghem;clock|på deltid
none;money|partiell vårdpenning;shield|Du kan få
none;person|du;child|barnet;finland|i Finland
none;child|barnet;school|åk 1 eller 2 i grundskolan
none;work|arbetar;clock|högst 30 timmar;calendar|i veckan
none;money|föräldradagpenning och/eller hemvårdsstöd;child|själv tar hand om dina barn;money|flexibel eller partiell vårdpenning'''}
for slug,raw in plans.items():
    ep=Path('studio/episodes')/('hb-c09-'+slug);rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences'];lines=raw.splitlines();assert len(lines)==len(rows),(slug,len(lines),len(rows));out=[]
    for i,(line,row) in enumerate(zip(lines,rows),1):
        relation,*pairs=line.split(';');objects=[p.split('|',1) for p in pairs]
        for node in objects:
            if node[1] not in row['sv']:
                m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(slug,i,node[1]);node[1]=m.group()
        out.append(dict(id=f'{slug}-{i:03}',objects=objects,relation=relation,reason='Source-specific pictorial explanation of '+', '.join(label for _,label in objects)+'. Preserve all stated ages, weekday counts, work limits and conjunctive/alternative eligibility conditions; no invented benefit amounts.'))
    if slug=='foraldraledighet':
        out[10]['title']='hemma';out[10]['relations']=['or','together']
        out[7]['objects'][1][0]='no_work';out[7]['relations']=['or','none']
        out[20]['title']='av din föräldrapenningkvot på 160 vardagar'
        out[22]['objects'][1][0]='unequal_scales'
        out[26]['title']='Om du får lön för föräldraledigheten'
        out[29]['title']='Om du har en anställning'
        out[31]['source_context_ids']=[rows[30]['sentence_id']]
    if slug=='vardledighet':
        out[26]['relations']=['none','blocked']
        out[-1]['relations']=['together','blocked']
        out[-1]['reason']='Both source conditions are shown together: receiving parental/home-care benefit AND personally caring for the child; the pictured connection to flexible/partial care allowance is blocked. The source conjunction and all displayed wording remain exact.'
    (ep/'visual-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
