"""Respectful source-based death administration, funeral and language diagrams."""
from pathlib import Path
import json
import re
import yaml

PLANS = {
    'dodsfall': '''none;family1|familjen;heart|sorgen;document|många olika saker
flow;house|hemma;phone|nödcentralen;hospital|en läkare
none;hospital|Läkaren;document|dödsfallet;microscope|obduktion
none;clock|plötsligt;calendar|en helg;shield|polisen
none;document|Dödsfall;hospital|läkare
support;hospital|Läkaren;certificate|begravningstillstånd;family1|familjen
notify;hospital|Läkaren;notice|dödsfallet;registry|befolkningsdatasystemet
flow;registry|befolkningsdatasystemet;institution|FPA;work|bank
none;friends|De närstående;work|arbetsgivare;house|hyresvärden
none;document|dödsattest;microscope|orsaken
none;hospital|läkaren;document|dödsattesten;calendar|månader efter dödsfallet
none;family1|Familjen;document|dödsattesten;institution|myndigheter
none;family1|familjen;document|Dödsattesten;shield|livförsäkringsärenden
none;microscope|dödsorsaken inte är klar;hospital|obduceras
flow;microscope|obduktion;hospital|läkaren;document|varför personen dog
blocked;grave|begravas;microscope|innan dödsorsaken har utretts
none;hospital|medicinsk;shield|rättsmedicinsk;microscope|obduktion
none;microscope|medicinsk utredning;hospital|läkare
none;person|en människa;hospital|sjukdom
support;microscope|utredning av dödsorsaken;hospital|hälso- och sjukvården
none;family1|Familjen;contract|tillstånd;hospital|medicinsk obduktion
blocked;microscope|Den;lock|utan tillstånd
none;shield|Polisen;microscope|rättsmedicinska utredningar
none;shield|Polisen;microscope|rättsmedicinsk obduktion;clock|plötsligt
none;shield|Polisen;contract|familjens tillstånd
flow;person|en människa;donation|organen och vävnaderna;friends|andra människor
support;donation|donerade organen;shield|liv;person|annan människa
none;finland|finsk lag;donation|organdonator;contract|inte har motsatt sig
none;hospital|läkaren;speech|den avlidnes vilja;donation|organdonation
none;person|personen;contract|samtyckt;donation|organdonation
flow;person|en person;will|organdonationstestamente
none;will|Av det;speech|personens vilja
none;family1|Familjen;lock|kan inte vägra;donation|organdonation
none;will|testamentera;person|sin kropp;microscope|medicinsk forskning
none;contract|underteckna ett avtal;person|sin kropp;school|undervisningsbruk''',
    'begravning': '''none;finland|Finland;calendar|flera veckor;grave|begravningar
none;clock|tid;document|praktiska arrangemang;grave|begravningsplatserna
none;coffin|begravas;microscope|dödsorsaken har utretts;certificate|begravningstillstånd
none;person|Var och en;coffin|begravning;speech|den avlidnes önskemål
none;institution|olika religioner;grave|olika begravningstraditioner
support;work|begravningsbyråer;person|hjälp;finland|Finland
none;work|Begravningsbyråer;coffin|begravningar
none;person|själv;document|ordna begravningen
none;person|den avlidne själv;family1|familjen;document|bestämmer
none;coffin|kista;urn|brännas
none;coffin|Kistbegravningar;finland|Finland
none;coffin|kista;grave|begravningsplatser;certificate|behörigt tillstånd
none;urn|Kremering;rise|vanligare;calendar|de senaste årtiondena
none;money|förmånligaste;grave|begravningssättet
flow;urn|askurna;grave|begravningsplats
none;grave|urnlund;urn|urnan;land|marken
none;family1|familj;land|egen mark;sea|havet
none;land|någon annans mark;contract|tillstånd;person|den som äger
none;urn|All aska;land|ett och samma ställe;lock|inte dela
none;finland|Finland;grave|majoriteten av begravningsplatserna;institution|evangelisk-lutherska kyrkan
none;grave|dem;person|personer;institution|andra trossamfund
none;grave|begravningsplatser;split|separata områden;no_registry|inte varit medlemmar
none;city|Kommunerna;grave|begravningsplatser;institution|olika religiösa samfund
none;institution|religiösa eller icke-religiösa samfund;grave|privata begravningsplatser
support;institution|religiösa samfundet;work|begravningsbyråerna;document|information
flow;coffin|kropp eller aska;globe|ett annat land;institution|ambassad
support;institution|ambassader;family1|familjer;coffin|avlidna anhöriga
none;family1|Familjen;money|betalar själv;globe|transporten
none;hospital|social- och hälsocentralen;phone|MIELI ry:s kristelefon;institution|församlingarna
none;speech|finska;speech|svenska;speech|engelska
none;person|Du;speech|tolk
none;phone|Mieli ry:s kristelefon;speech|ukrainska;speech|ryska
none;registry|medborgare;finland|Finland;book|finsk lag
notify;hospital|sjukhus;document|dödsfallet;institution|beskickningen
notify;institution|Beskickningen;notice|informationen;friends|närstående
none;coffin|begraven;institution|beskickningen;city|lokala myndigheterna
none;coffin|begravs;urn|kremeras;finland|finsk praxis
none;money|begravningsbidrag;work|sista anställning;friends|fackförbund
none;speech|Fråga;work|arbetsgivaren;friends|fackförbundet
flow;money|begravningskostnaderna;document|ansöka om utkomststöd;institution|FPA
support;money|familjepension;person|maka/make;child|barn
none;money|familjepensionen;person|änkans/änklingens;child|barnens uppehälle
none;institution|FPA;speech|två olika familjepensioner;work|arbetspensionssystemet
none;work|arbetat som anställd eller företagare;finland|Finland;money|familjepension
none;globe|annat land;clock|länge;money|familjepension
none;document|villkoren;finland|Finland;globe|ursprungslandet''',
    'flersprakighet': '''flow;family1|familj;globe|annat land;finland|Finland
none;parents|föräldrarna;book|kulturen, värderingarna och samhället;finland|Finland
none;book|vet;person|de;land|landet
support;book|kunskap och förståelse;family1|familjen;heart|må bra
support;parents|föräldrarna;child|sina barn;finland|Finland
none;child|barnen;school|skolan;school|småbarnspedagogik
none;child|barnet;speech|finska eller svenska;friends|kompisar
none;school|skolan;parents|föräldrarna;work|arbeta
none;globe|nya landet;family1|familjen;split|rollerna
none;family1|Alla familjemedlemmarna;clock|sin egen takt
none;child|Barnen;rise|snabbare;parents|föräldrarna
none;child|barnen;book|nya värderingar och vanor;speech|bråk i familjen
none;parents|föräldrarna;speech|diskuterar;child|barnen
none;clock|Med tiden;family1|alla familjemedlemmar;finland|Finland
none;couple|parförhållandet;globe|nya omständigheter
none;woman|kvinnans;man|Mannens;globe|gamla hemlandet
support;person|den ena maken;speech|språket;person|sin partner
none;parents|båda;speech|språket;shield|inte blir för beroende
support;heart|stärker;couple|parförhållandet
none;person|en människa;globe|ett nytt land;house|på egen hand
none;person|hen;family1|ingen välbekant och trygg familj
none;clock|tid;person|en människa;split|stora förändringar
none;family1|alla familjemedlemmar;speech|finska;speech|svenska
none;parents|föräldrarna;child|barnet;school|skolan
none;parents|föräldrarna;speech|nya språket;house|hemma
none;parents|De kanske tänker;speech|föräldrarnas språk;finland|Finland
none;book|Forskning;child|barn;speech|sitt modersmål bra
none;speech|Modersmålet;heart|känslospråk
none;parents|föräldrarna;speech|det språk som de själva kan bäst;child|barnet
none;speech|Modersmålet;registry|identitet;book|kultur
none;child|Alla barn;shield|rätt;speech|sitt eget språk
none;speech|sitt modersmål;generations|släktingar;friends|vänner
none;family1|familj;speech|många olika språk
none;child|Barnen;speech|många språk samtidigt;speech|fler än ett modersmål
none;speech|pratar;child|barnet;book|läser
none;book|Finlands grundlag;shield|rätt;speech|sitt språk
none;school|skolan;book|undervisning;speech|sitt modersmål''',
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
            reason='Individually composed source explanation of '
                   + ', '.join(label for _, label in objects)
                   + '. All source conditions remain in the exact bilingual text. '
                     'Neutral symbolic people, no identifiable deceased person, '
                     'clinical procedure, national stereotype or invented number.',
        ))
    if slug == 'dodsfall':
        plan[11]['title'] = 'behöver inte dödsattesten'
        plan[21]['source_context_ids'] = [rows[20]['sentence_id']]
        plan[21]['footer'] = 'medicinsk obduktion'
        plan[24]['source_context_ids'] = [rows[22]['sentence_id'], rows[23]['sentence_id']]
        plan[24]['footer'] = 'rättsmedicinska utredningar av dödsorsak'
        plan[24]['title'] = 'behöver inte familjens tillstånd'
        plan[27]['title'] = 'om hen inte har motsatt sig det medan hen levde'
        plan[29]['title'] = 'om man inte känner till att hen varit emot det'
        plan[32]['title'] = 'om personen själv har önskat donera sina organ'
    elif slug == 'begravning':
        plan[2]['relations'] = ['together', 'together']
        plan[9]['relations'] = ['or']
        plan[13]['source_context_ids'] = [rows[12]['sentence_id']]
        plan[20]['source_context_ids'] = [rows[19]['sentence_id']]
        plan[35]['title'] = 'Om ingen nära anhörig ser till'
        plan[42]['relations'] = ['none', 'none']
        plan[44]['title'] = 'innan hen flyttade till Finland'
    else:
        plan[24]['title'] = 'föräldrarna tänker'
        plan[25]['title'] = 'De kanske tänker'
        plan[26]['title'] = 'om de kan sitt modersmål bra'
    (episode / 'visual-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
