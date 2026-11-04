"""Individual legal-parentage and social-support pictorial compositions."""
from pathlib import Path
import json
import re
import yaml

PLANS = {
    'foraldraskap': '''none;child|ett barn;person|en;friends|två föräldrar
none;registry|officiella föräldraskapet;person|biologiska förälder
none;rainbowfamily|regnbågsfamilj;registry|officiellt;document|adoption
none;registry|officiella föräldraskapet;family1|familjen;unequal_scales|inte alltid
none;family1|familjemedlemmarna;heart|känslomässiga banden;house|det liv de delar
support;person|man;child|ett barn;heart|älskar
none;child|ett barn;calendar|under 18 år;book|finländsk lag
none;child|Personer under 18 år;person|minst en vårdnadshavare
none;parents|barnets föräldrar;shield|vårdnadshavare
none;baby|ett barn;rings|äktenskap;parents|båda föräldrarna tillsammans
none;woman|Kvinnan som har fött barnet;no_rings|inte är gifta;no_registry|inte har erkänts
none;woman|modern ensam;document|bestämmer;house|bo tillsammans
none;woman|barnets mamma;rings|gift med en man;man|pappa till barnet
none;couple|ett par;no_rings|inte är gifta
flow;man|mannen;registry|erkänna faderskapet
notify;man|mannen;notice|officiellt meddelar;child|barnet
none;hospital|rådgivningsbyrån;pregnant|graviditeten;baby|barnet fötts
none;man|pappan;registry|erkänt faderskapet;shield|vårdnadshavare
none;pregnant|gravid kvinna;hospital|fertilitetsbehandlingar;registry|moderskap
none;registry|Moderskapet;notice|erkännas separat;rings|gifta med varandra
none;finland|Finland;book|moderskapslag;friends|två mödrar
none;woman|Kvinnan;baby|fött barnet;heart|barnets mor
none;child|barnet;woman|ytterligare en mor;shield|om
none;baby|barnet föds;hospital|fertilitetsbehandling;couple|moderns kvinnliga partner eller make
none;parents|båda föräldrarna;contract|samtyckt;hospital|fertilitetsbehandlingen
blocked;registry|fastställas;man|ingen fader;child|barnet
none;registry|Moderskap;certificate|fastställas;rings|gifta
none;woman|Du;calendar|före barnets födelse;hospital|mödrarådgivningen
flow;institution|Myndigheten för digitalisering och befolkningsdata;registry|ditt moderskap;baby|efter barnets födelse
none;registry|erkänna moderskapet;baby|efter barnets födelse;person|barnatillsyningsmannen
flow;person|Barnatillsyningsmannen;document|utreder moderskapet;institution|Myndigheten för digitalisering och befolkningsdata
none;registry|moderskapet;certificate|fastställts
none;child|barnet;name_tag|endera moderns efternamn;name_tag|gemensamma efternamn
support;friends|båda mödrarna;money|underhåll;child|barnets
none;friends|mödrarna;shield|vårdnadshavare;person|var för sig
inherit;child|barnet;friends|båda sina mödrar;generations|deras släkt
none;registry|faderskapet;certificate|fastställts
none;child|barnet;man|faderns;name_tag|efternamn
none;man|fadern;parents|tillsammans med barnets mor;person|ensam
support;person|Vårdnadshavaren;book|uppfostran;child|barnet
support;man|fadern;money|underhåll;child|barnet
none;child|barnet;man|sin far;generations|släkten på sin fars sida
none;child|barnet;money|familjepension;man|fadern dör
flow;woman|modern;document|väcka talan;registry|fastställande av faderskapet
notify;hospital|sjukhuset;baby|Ett barns födelse;registry|befolkningsdatasystemet
none;child|barnet;registry|personnummer
none;document|Detta;shield|om
none;woman|modern;city|hemkommun;finland|Finland
none;woman|modern;registry|finsk personbeteckning
none;woman|modern;no_registry|inte är registrerad;hospital|sjukhuset
flow;person|du;speech|anvisningar;institution|Myndigheten för digitalisering och befolkningsdata
none;finland|Finland;name_tag|namnlag
none;house|hemort i Finland;name_tag|efternamn;name_tag|1–4 förnamn
none;name_tag|Förnamnen;book|lagen
blocked;friends|syskon;name_tag|samma namn som första namn
flow;parents|föräldrar;name_tag|efternamn;child|Barnet
none;parents|föräldrarna;name_tag|samma efternamn eller efternamnskombination;child|barnet
none;person|endast har en förälder;child|barnet;name_tag|denna förälders efternamn
none;parents|föräldrarna;friends|minderåriga syskon;name_tag|samma efternamn
none;split|separerat;shield|vårdnadshavare;name_tag|namn barnet får
none;speech|inte kommer överens;child|barnet;name_tag|moderns efternamn
none;parents|föräldrarna;name_tag|olika efternamn;balance_options|situationen
none;rings|gifta;parents|de;name_tag|endera makens efternamn eller efternamnskombination
none;no_rings|inte är gifta;registry|fastställts;name_tag|valfri förälders efternamn
none;no_registry|inte har fastställts;child|barnet;name_tag|moderns efternamn
none;child|första gemensamma barn;name_tag|kombination av föräldrarnas efternamn;name_tag|det andra namnet
none;baby|barnet föds;registry|registrera;speech|modersmål
none;child|Ditt barn;registry|befolkningsdatasystemet;speech|ett språk som modersmål
none;person|Du;speech|språket;clock|senare''',
    'familjetjanster': '''support;parents|Föräldrarna;child|barnet;book|uppfostran
support;institution|samhället;family1|De;shield|rätt
none;finland|Finland;institution|myndigheterna;shield|förebyggande arbete
support;institution|samhället;child|barn;family1|familjer
none;family1|familjer;shield|mer stöd;balance_options|svåra livssituationer
none;family1|Familjer;work|tjänster;shield|förhindra problem
none;hospital|rådgivningsbyråerna;school|skolan;institution|församlingen
none;family1|barnfamiljer;institution|socialtjänsterna;speech|inte är tillräckligt
none;speech|rådgivning;money|ekonomiskt stöd;person|stödperson
support;school|skolgång;toys|hobbyer;child|Barnets
support;shield|barnskyddet;person|klient;rise|mer stöd
none;person|yrkesperson;cleaning|städning;food|inköp
none;house|hemservice;family1|familjen;shield|särskilt stöd
none;person|den ena föräldern;hospital|allvarligt sjuk
support;person|stödperson;child|barnet;book|läxor
none;family1|stödfamilj;child|barnet;calendar|en helg per månad
none;child|barnet;house|hemma;family1|sin familj
none;family1|familjens situation;person|utomstående hjälp;shield|lindrigast möjliga metod
none;shield|barnskyddet;work|stödåtgärder;hospital|öppenvården
none;shield|Stödåtgärderna;heart|frivilliga;family1|samarbete med familjen
none;work|stödåtgärderna;shield|utan att vara klient hos barnskyddet
none;baby|en baby;person|utmattad;house|hemservice
none;cleaning|hushållsarbeten;child|barnpassning;family1|familjens vardag
none;family1|Barnfamiljer;clock|tillfälligt;calendar|regelbundet
none;house|Hemservicen;money|avgiftsbelagd
flow;money|Familjens inkomster;receipt|avgiften
none;receipt|räkningar;money|ekonomin;speech|rådgivning
none;money|din inkomst minskar;document|din rätt;house|bostadsbidrag
none;money|inkomster och tillgångar;food|mat;shield|grundläggande utkomststöd
none;child|ett barn;school|skolan;speech|studievägledare
none;school|skolan;person|psykolog;person|kurator
support;person|Hen;child|elever;school|skolan
none;child|ett barn;school|skolan;shield|skyldighet att ingripa
notify;speech|Berätta;person|läraren;person|rektorn
notify;speech|mobbning;court|brott;shield|polisen
none;shield|fysiskt våld;key|stjälande;court|brott
none;person|en ung;shield|hjälp;hospital|ungdomsstationen
none;hospital|Ungdomsstationer;city|många städer
none;person|ensam;parents|sina föräldrar;hospital|ungdomsstationen
none;court|Brott;child|personer under 15 år;document|påföljder
none;person|Personen;money|ersätta;document|skador
notify;shield|Polisen;child|barn under 18 år;institution|barnskyddsmyndigheten''',
    'barnskydd': '''none;finland|Finland;book|barnskyddslagen;shield|barnskyddet
none;child|barn;house|trygg uppväxtmiljö;rise|växa upp
none;book|Barnskyddslagen;child|alla barn;finland|Finland
none;institution|Barnskyddsmyndigheterna;person|experter på socialarbete;book|lagen
none;shield|barnskyddet;child|barnets intresse
none;person|de anställda;document|alla beslut;child|just det här barnet
flow;family1|en familj;speech|själv be om hjälp;shield|barnskyddet
none;speech|be om hjälp;child|ett barn;shield|skadar
none;shield|Barnskyddet;parents|föräldrarna;child|barnet
none;person|en person utanför familjen;child|ett barns välbefinnande;notice|barnskyddsanmälan
none;phone|telefon;document|skriftligt;institution|besöka byrån
none;school|skolan;notice|barnskyddsanmälan;shield|misstänker
flow;person|vem som helst;notice|barnskyddsanmälan;institution|sociala myndigheterna
none;notice|Anmälan;no_registry|anonymt
none;notice|Anmälningar;child|ett barn;school|missköter skolan
none;notice|barnskyddsanmälan;institution|sociala myndigheten;shield|skydd, hjälp eller stöd
none;institution|myndigheterna;speech|diskuterar;family1|familjen
none;speech|samtalet;friends|tolk;shield|hjälp
none;person|En socialarbetare;child|barnet;no_registry|utan föräldrarna
none;speech|samtalen;institution|myndigheterna;family1|familjen
none;document|en plan;child|barnet;family1|familjen
none;speech|rådgivning;book|handledning;heart|samtalshjälp
none;person|stödperson;family1|stödfamilj;child|barn
none;shield|barnskyddsarbetet;house|hemma;parents|föräldrarna
none;child|ett barn;clock|tillfälligt;house|någon annanstans
flow;child|barnet;shield|omedelbar fara;house|utanför hemmet
none;parents|föräldrarna;hospital|långtidssjukdom;shield|familjevåld
none;house|placering;unequal_scales|inte nödvändigtvis;shield|omhändertagande
none;shield|omhändertagande;lock|ingenting annat hjälper
none;institution|myndigheterna;heart|omsorgen;child|barnet
none;shield|Omhändertagande;balance_options|sista alternativ;child|ett barn
none;child|barn;house|utanför hemmet;institution|barnskyddsmyndigheter
none;child|Barnet;family1|familjehem;house|barn- eller ungdomshem
none;house|placering;clock|tillfällig
none;institution|Myndigheterna;calendar|regelbundet;house|återvända hem
none;house|hemma;clock|snabbt;calendar|kortvarig
none;family1|familjens;clock|långvariga
none;shield|omhändertagandet;person|myndigt;house|egen bostad
none;shield|barnskyddet;child|barnet;house|hemma hos sina föräldrar
none;institution|barnskyddsmyndigheterna;contract|tillsammans;family1|familjen
support;family1|familjen;shield|tryggt;house|återvända hem''',
}

for slug, raw in PLANS.items():
    episode = Path('studio/episodes') / ('hb-c09-' + slug)
    rows = yaml.safe_load((episode / 'script.yaml').read_text())['sentences']
    lines = raw.splitlines()
    assert len(lines) == len(rows), (slug, len(lines), len(rows))
    plan = []
    for index, (line, row) in enumerate(zip(lines, rows), 1):
        relation, *pairs = line.split(';')
        objects = [pair.split('|', 1) for pair in pairs]
        for node in objects:
            match = re.search(re.escape(node[1]), row['sv'], re.I)
            assert match, (slug, index, node[1])
            node[1] = match.group()
        plan.append(dict(
            id=f'{slug}-{index:03}', objects=objects, relation=relation,
            reason='Exact-source pictorial relationship: '
                   + ', '.join(label for _, label in objects)
                   + '. Distinguish source conditions and actual legal roles; '
                     'all figures are symbolic and do not identify a real '
                     'parent, client, victim or child in care.',
        ))
    if slug == 'foraldraskap':
        for index in [10, 18, 24, 25, 26, 46, 47, 48, 49, 63, 64]:
            plan[index]['reason'] += ' Preserve the stated conjunction and eligibility qualifications; no unconditional entitlement is pictured.'
        plan[10]['relations'] = ['together', 'together']
        plan[16]['title'] = 'eller hos en barnatillsyningsman'
        plan[17]['title'] = 'Först efter att pappan erkänt faderskapet'
        plan[18]['title'] = 'innan barnet föds'
        for index in range(23, 26):
            plan[index]['source_context_ids'] = [rows[22]['sentence_id']]
        for index in range(32, 36):
            plan[index]['source_context_ids'] = [rows[31]['sentence_id']]
        for index in [37, 38, 40, 41, 42]:
            plan[index]['source_context_ids'] = [rows[36]['sentence_id']]
        plan[41]['relations'] = ['inherit', 'inherit']
        plan[41]['title'] = 'och tvärtom'
        plan[58]['objects'][1][0] = 'children'
        plan[42]['title'] = 'om fadern dör'
        for index in [47, 48]:
            plan[index]['source_context_ids'] = [rows[46]['sentence_id']]
        plan[63]['title'] = 'om faderskapet eller den icke-födande moderns moderskap har fastställts'
        plan[64]['title'] = 'Om föräldraskapet inte har fastställts'
    elif slug == 'familjetjanster':
        plan[3]['title'] = 'innan problemen blir stora'
        plan[3]['layout'] = 'tree'
        plan[3]['tree_edge_start_y'] = 350
        plan[12]['title'] = 'om familjen behöver särskilt stöd'
        plan[18]['objects'][-1][0] = 'house'
        plan[19]['relations'] = ['none', 'together']
        plan[23]['title'] = 'om familjens situation kräver detta'
        plan[28]['title'] = 'Om dina inkomster och tillgångar inte räcker till'
        plan[31]['source_context_ids'] = [rows[30]['sentence_id']]
        plan[35]['objects'][0][0] = 'alert'
        plan[41]['objects'] = [['shield','Polisen'],['parents','föräldrarna'],['institution','barnskyddsmyndigheten']]
        plan[41]['layout'] = 'tree'
        plan[41]['tree_edge_start_y'] = 350
        plan[41]['title'] = 'barn under 18 år'
    elif slug == 'barnskydd':
        plan[7]['objects'][-1][0] = 'alert'
        plan[25]['objects'][1][0] = 'alert'
        plan[25]['title'] = 'Om barnet är i omedelbar fara'
        plan[26]['objects'][-1][0] = 'alert'
        plan[8]['title'] = 'om föräldrarna inte kan ta hand om sitt barn'
        plan[18]['relations'] = ['none', 'none']
        plan[23]['title'] = 'i de flesta fall'
        plan[27]['title'] = 'inte nödvändigtvis omhändertagande'
        plan[28]['title'] = 'om ingenting annat hjälper'
        plan[37]['title'] = 'tills barnet blir myndigt'
    (episode / 'visual-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
