"""Source-specific pictorial plans for divorce, custody and family support."""
from pathlib import Path
import json
import re
import yaml

PLANS = {
    'skilsmassa': '''flow;rings|äktenskap;split|upplöses
none;parents|tillsammans;person|på egen hand;document|ansöka
none;split|skilsmässa;contract|bådas samtycke
flow;document|skriftligt;court|tingsrätt
blocked;court|Rätten;speech|varför
none;document|Ansökan;calendar|två steg
flow;document|skilsmässoansökan;institution|lämnar man in
flow;clock|betänketiden;document|en ny ansökan
flow;document|den andra ansökan;court|Domstolen;split|skilsmässa
none;court|skilsmässa;person|den andra parten;lock|motsätter sig
flow;document|den första ansökan;calendar|sex månader
none;calendar|Betänketiden;homes|skilda adresser;calendar|de senaste två åren
flow;parents|tillsammans;court|tingsrätten;clock|betänketiden
flow;person|ensam;notice|delges;clock|betänketiden
notify;court|Tingsrätten;notice|delges;person|den andra makan
none;document|den andra ansökan;calendar|inom ett år;clock|betänketiden började
none;missed_deadline|I annat fall;document|förfaller ärendet
none;house|egendom;scales|delas;contract|äktenskapsförord
none;split|skilsmässa;speech|bråk;child|barnen
support;parents|paret;court|juridisk hjälp
none;finland|Finland;split|skilsmässor;no_rings|inte tvungna att stanna
none;finland|Finland;split|skilsmässa;speech|ingen skam
flow;split|på nytt;rings|gifter sig;couple|en ny partner
none;house|Bodelningen;document|komplicerad process
none;speech|komma överens;money|tillgångar;receipt|skulder
flow;person|Ni;speech|hjälp;court|jurist
none;house|bolån;speech|komma överens;split|delar lånet
none;parents|tillsammans;person|vem av er;house|gemensamma hemmet
flow;person|vem som helst av makarna;document|kräva egendomsfördelning;split|bodelning
flow;document|den första skilsmässoansökan;house|Bodelningen
none;person|Man;clock|vänta;calendar|sex månader
flow;court|tingsrätten;person|bodelningsman;split|delar egendomen
support;money|betalt;person|Bodelningsmannen;work|arbetet
none;parents|vardera maka;house|egendom;receipt|skulder
none;globe|annat land;finland|Finland;book|lagarna
flow;person|Du;speech|råd;court|jurist
none;split|skilsmässa;document|ändras inte ditt efternamn
flow;person|du;document|ett annat efternamn
none;document|namn;clock|tidigare
flow;parents|ni;document|ansöka om;speech|medling i familjefrågor
none;speech|Medling;contract|komma överens;court|utan rättegång
none;speech|prata;child|barnens situation
none;speech|problem i parförhållandet;family1|familjerådgivningen;hospital|hälsocentralen
none;registry|uppehållstillståndet;house|egendomen;child|barnets boende
support;court|jurist;person|du
support;speech|råd;shield|dina rättigheter
flow;person|Du;court|jurist;speech|tvister
none;court|advokatbyråer;institution|juridiska byråer;institution|statens rättshjälpsbyråer
none;money|låg eller medelhög inkomst;court|juridisk hjälp;institution|statens rättshjälpsbyrå
none;institution|offentliga rättshjälpen;speech|engelska;speech|tolktjänster
flow;document|söks;institution|statens rättshjälpsbyråer
blocked;shield|rättsskyddsförsäkring;court|offentlig rättshjälp
none;house|hemförsäkringen;shield|rättsskyddsförsäkringen''',
    'vardnad': '''none;child|barn under 18 år;split|skilsmässan;speech|komma överens
none;child|barnet;house|bo
none;child|barnets;person|vårdnadshavare
none;child|umgänget;speech|Hur ordnas
none;money|Underhållsbidrag
flow;parents|föräldrarna;contract|avtalet;person|barnatillsyningsmannen
equal;contract|avtalet;court|domstolsbeslut
flow;parents|ni;speech|inte kan komma överens;speech|medling i familjefrågor
flow;contract|inte får fram ett avtal;court|tingsrätten
none;court|Domstolen;child|barnets intressen;speech|egna önskemål
none;child|barnets intressen;house|boendet
none;child|ett barn;house|ett ställe
none;split|skilsmässa;person|vilken förälder;house|officiella adress
none;child|barnet;clock|en del av tiden;person|sin andra förälder
support;money|Barnbidraget;person|den förälder;house|bor officiellt
flow;house|Barnets officiella adress;institution|FPA;shelter|bostadsbidrag
none;shield|Vårdnaden;child|ett barn
support;person|man;child|barnet
support;book|uppfostrar;child|barnet
none;person|man;document|beslutar;child|barnets angelägenheter
none;split|äktenskap slutar;parents|föräldrar;shield|vårdnaden
none;parents|gemensam vårdnad;person|ensam vårdnad
none;shield|Vårdnaden;house|vem barnet bor med
none;parents|båda föräldrarna;shield|gemensam vårdnad;document|tillsammans
none;child|barnets
none;document|namn
none;house|bostadsort
none;book|fostran
none;speech|språk
none;institution|religion
none;school|utbildning
none;hospital|hälsovård
none;child|barnets;key|egendom
none;registry|passansökan;parents|båda föräldrarnas;contract|samtycke
none;parents|Föräldrarna;shield|gemensam vårdnad;speech|komma överens
none;parents|föräldrarna;child|barnets bästa;document|beslut
none;child|Barnet;speech|kontakt;parents|båda sina föräldrar
none;child|Han eller hon;person|den förälder;house|inte bor med
none;child|barnet;calendar|vartannat veckoslut;calendar|vissa tider under loven
none;baby|barnet är mycket litet;clock|över dagen
none;child|barnet;scales|lika mycket;parents|båda föräldrarna
none;child|barnet;house|en adress
none;child|barnets intressen;document|beslut
flow;person|du;speech|problem med umgänget;person|barnatillsyningsmannen
none;person|Barnatillsyningsmannen;speech|ett möte;parents|föräldrarna
notify;child|barnets hälsa eller säkerhet;shield|äventyras;institution|socialmyndigheter
none;shield|misstanken är befogad;child|umgänget;person|socialmyndigheters uppsikt''',
    'radgivning': '''none;hospital|mödrarådgivning;family1|hela familjen;speech|vägledning och råd
none;pregnant|gravida kvinnans;shield|välbefinnande;baby|fostrets
support;family1|hela familjen;baby|den nya babyn
flow;baby|barnet fötts;hospital|hälsovårdare;rise|växer och utvecklas
none;hospital|Hälsovårdaren;speech|diskuterar;family1|familjen
none;hospital|Rådgivningsbyrån;money|avgiftsfri;family1|alla familjer
none;parents|föräldrar;baby|sitt första barn;school|familjeförberedelsekurs
none;hospital|hälsovårdare;baby|babyn;school|kursen
flow;woman|Mammor;finland|permanent bosatta i Finland;institution|FPA
none;maternity_box|moderskapsförpackning;money|pengar
none;clothes|kläder;maternity_box|åkpåse;baby|babyvård
none;maternity_box|en stor låda;baby|babyns första säng
none;calendar|1930-talet;woman|mindre bemedlade mammor;money|moderskapsunderstöd
none;woman|mammor;baby|babyer;hospital|hälsovård
none;calendar|1949;woman|alla mammor;finland|Finland
none;pregnant|mammor;hospital|förlossningssjukhus
support;hospital|barnmorska;woman|mamman
none;hospital|barnmorska;book|specialiserad på förlossningar
none;baby|babyns;person|andra förälder;hospital|förlossningen
none;finland|Finland;shield|könsstympning;court|ett brott
blocked;court|förbjudet i lag;shield|stänga slidans öppning på nytt;baby|efter en förlossning
none;child|flickor;court|allvarligt brott;calendar|flera års fängelsestraff
none;registry|finsk medborgare;child|flicka;globe|Finland eller något annat land
blocked;person|En vuxen;child|en flicka;globe|ett annat land
none;child|pojkar;hospital|offentliga hälsovården;document|utan medicinsk orsak
none;hospital|legitimerade läkare;document|utföra omskärelse
none;house|stadigvarande bosatt i Finland;work|arbeta i Finland;money|stöd
none;registry|Barnets medborgarskap;money|stöd
flow;registry|Föräldrarnas uppehållstillstånd;money|vilka stöd
none;person|du;finland|Finland;maternity_box|moderskapsunderstöd
none;maternity_box|moderskapsförpackning;money|ett fast skattefritt belopp;person|du väljer
none;maternity_box|Moderskapsförpackningen;clothes|babykläder;baby|vårdartiklar
none;shield|rätt;money|moderskapsunderstöd
none;pregnant|graviditeten;calendar|cirka fem månader
none;hospital|läkarundersökning;calendar|före utgången av den fjärde graviditetsmånaden
none;person|du;house|stadigvarande;finland|Finland''',
    'skydd': '''none;shelter|skyddshem;person|personer;shield|hjälp och trygghet
none;person|En person;house|sitt eget hem;shelter|skyddshem
none;shelter|Skyddshemmet;person|anställda;clock|dygnet runt
support;person|De anställda;shield|lösa krisen
none;shelter|skyddshem;clock|tillfälligt;person|individuella behovet
none;shelter|Skyddshemmens tjänster;money|avgiftsfria
none;house|inte är tryggt;shelter|skyddshem
none;house|hemmet;shield|inte förekomma fysiskt våld
none;speech|Psykiskt våld;shield|söka skydd
none;shelter|Skyddshemmens;friends|alla kön
flow;child|barnen;shelter|skyddshemmet
none;phone|ringa;clock|när som helst;shelter|skyddshemmen
none;woman|en mamma;baby|sin baby;shelter|mödrahem
none;pregnant|gravida mammor;baby|små babyer;shelter|mödrahem
none;person|andra föräldern eller mammans partner;shelter|mödrahemmet
none;shield|trygg miljö;baby|babyn;book|öva
none;shield|polisen;phone|112;clock|brådskande
none;phone|nödnumret;clock|brådskande fall;shield|i fara
none;phone|Nollalinja;person|du;shield|våld
none;phone|ringa;clock|när som helst
none;speech|finska;speech|svenska;speech|engelska
none;phone|Nollalinja;speech|tolktjänst
none;speech|ryska;speech|ukrainska;speech|thai
none;phone|Samtal till Nollalinja;money|kostnadsfria;receipt|inte i telefonräkningen
none;phone|ringer;registry|ditt namn
none;phone|Nollalinja;woman|kvinnor;man|män
none;hospital|SERI-stödcenter;shield|offer för sexuellt våld
support;hospital|SERI-stödcentret;person|offer för sexuellt våld;speech|råd
none;hospital|Centret;hospital|medicinsk undersökning;speech|psykologhjälp
none;hospital|Stödcentret;friends|alla;scales|oavsett kön
none;hospital|Tjänsterna;money|kostnadsfria
none;person|på egen hand;phone|ringer i förväg;hospital|SERI-stödcentret
flow;person|Du;hospital|social- och hälsocentralen
none;person|dig;shield|skydd;document|besöksförbud
blocked;person|personen;speech|kontakt;person|dig
none;document|ansöka;shield|polisen;court|tingsrätten
none;speech|råd;institution|socialbyrån;court|rättshjälpsbyrån
none;document|bevis;shield|hot och trakasserier;lock|spara dem''',
}

for slug, raw in PLANS.items():
    episode = Path('studio/episodes') / ('hb-c09-' + slug)
    rows = yaml.safe_load((episode / 'script.yaml').read_text())['sentences']
    lines = raw.splitlines()
    assert len(lines) == len(rows), (slug, len(lines), len(rows))
    specifications = []
    for index, (line, row) in enumerate(zip(lines, rows), 1):
        relation, *pairs = line.split(';')
        objects = [pair.split('|', 1) for pair in pairs]
        for node in objects:
            match = re.search(re.escape(node[1]), row['sv'], re.I)
            assert match, (slug, index, node[1])
            node[1] = match.group()
            if node[0] == 'shelter' and slug == 'vardnad':
                node[0] = 'house'
        specifications.append(dict(
            id=f'{slug}-{index:03}', objects=objects, relation=relation,
            reason='Source-specific pictured objects and relationships: '
                   + ', '.join(label for _, label in objects)
                   + '. Exact source qualifiers remain visible; no invented '
                     'eligibility, deadlines, current service promises or victim identities.',
        ))
    if slug == 'skilsmassa':
        specifications[2]['title'] = 'behövs inte bådas samtycke'
        specifications[11]['title'] = 'förutom om'
        specifications[15]['title'] = 'efter att betänketiden började'
        specifications[30]['title'] = 'behöver alltså inte vänta'
        specifications[40]['title'] = 'kan ofta vara nyttig'
        specifications[48]['title'] = 'gratis eller delvis ersättningsgill'
        specifications[51]['title'] = 'som ersätter dina utgifter'
    elif slug == 'vardnad':
        specifications[16]['source_context_ids'] = [rows[16]['sentence_id']]
        specifications[22]['title'] = 'är inte beroende av'
        specifications[33]['source_context_ids'] = [rows[23]['sentence_id']]
        specifications[33]['footer'] = 'gemensam vårdnad'
        for index in range(25, 33):
            specifications[index]['source_context_ids'] = [rows[23]['sentence_id']]
    elif slug == 'radgivning':
        specifications[23]['title'] = 'för att tvinga henne att genomgå könsstympning'
        specifications[24]['relations'] = ['none', 'blocked']
        specifications[26]['relations'] = ['or', 'support']
        specifications[27]['title'] = 'påverkar inte'
        specifications[28]['title'] = 'kan påverka'
        specifications[29]['title'] = 'kan du ha rätt'
        specifications[30]['relations'] = ['or', 'none']
        specifications[34]['title'] = 'före utgången'
    elif slug == 'skydd':
        specifications[17]['title'] = 'endast i brådskande fall'
        specifications[22]['reason'] += ' Three source languages pictured as examples; full nine-language list remains exact on the right.'
        specifications[24]['title'] = 'behöver inte uppge ditt namn'
    (episode / 'visual-plan.json').write_text(
        json.dumps(specifications, ensure_ascii=False, indent=2) + '\n')
