"""Non-graphic upbringing and violence-prevention source illustrations."""
from pathlib import Path
import json
import re
import yaml

PLANS = {
    'uppfostran': '''none;speech|uppfattning;child|barn
none;child|barn;person|vuxna;heart|relationen
none;city|samhället;child|barn;house|vardagen
none;book|lagar;child|barn;school|skolornas läroplaner
none;finland|Finland;child|barn;rise|aktiva aktörer
none;person|de vuxna;child|Barn;speech|egna tankar och åsikter
none;parents|Föräldrarna;child|barnens;document|ansvarsfulla beslut
none;child|barn;shield|skyddas
none;speech|barnets åsikter;balance_options|stå i strid;shield|skydda barnet
none;person|de vuxna;scales|bedöma;child|bästa för barnet
none;finland|finländska;toys|lek;child|barn
support;toys|lek;book|färdigheter;child|barnen
none;toys|Leken;happy_face|glädje;child|barnen
none;child|Alla barn;shield|rätt;toys|leka
none;person|förälder;clock|tiden;split|förändrats
none;person|en bra förälder;heart|kärleksfull;clock|tålmodig
none;person|Hen;clock|mycket tid;child|barnet
none;clock|Förr;lock|lydnad;person|förälderns auktoritet
none;parents|föräldrarna;speech|diskutera;child|sina barn
none;person|en bra förälder;balance_options|många sätt
none;child|barnets;heart|älskad;happy_face|uppskattad
none;child|Barnet;shield|tryggt;food|basbehov
none;person|en förälder;alert|våld;child|ett barn
none;finland|Finland;alert|Aga;court|förbjudna i lag
none;person|Fysisk bestraffning;speech|psykiskt våld;alert|straff
none;child|barnet;sad_face|smärta;baby|en baby
none;speech|hota med våld;sad_face|håna;child|barnet
none;alert|Aga;child|barnets;alert|utveckling
none;book|undersökningar;globe|världen;alert|negativa följderna
none;child|barnet;sad_face|smärta;fear|rädsla
none;clock|På lång sikt;child|barnets;fear|rädslor
none;alert|Den;book|uppfostringsmetod;no_registry|ineffektiv och skadlig
flow;child|Barn;person|vuxna;hospital|sjukare
none;boundary|gränser;child|barn;balance_options|utmanande
none;parents|Alla föräldrar;book|lära sig;shield|utan våld
none;parents|föräldrarna;heart|känslor;child|sitt barn
none;child|barn;speech|tydligt berättar;person|vuxna
none;person|en bra förälder;scales|rättvis;shield|konsekvent
none;person|Hen;speech|lyssnar;child|barnet
none;finland|Finland;person|människor;shield|självständiga
none;child|barnen
none;child|små barn;clothes|ytterkläderna
none;person|de vuxna;clock|tålamod
none;finland|Finland;child|barnen;shield|ta ansvar
none;child|Barnen;happy_face|framgång;person|på egen hand
none;child|barn;land|utomhus;person|på egen hand
none;child|sjuåriga förstaklassare;school|skolan
none;child|barns självständighet;shield|trygg miljö;house|nära hemmet
none;book|lära barnen;traffic|trafiken;shield|tryggt
none;person|man;rise|för mycket självständighet;child|barnen
none;child|barn;person|individer
none;child|En del barn;clock|yngre ålder;clock|mer tid
none;person|De vuxna;shield|säkerställa;child|hen är redo för
none;child|barnen;land|utomhus;weather|väder och årstid
none;school|daghemmen;clock|mycket tid utomhus;tree|skogsutfärder
none;child|Barnen;clothes|utomhuskläder;weather|olika väder
none;child|barnen;clothes|smutsiga;happy_face|roligt
none;friends|Vänskapsförhållanden;school|skolan;toys|hobbyer
none;child|Barnen;friends|sina vänner;toys|leker tillsammans
none;parents|Föräldrar;child|små barn;friends|barnens vänner
none;child|barn och unga;bed|sover över;finland|Finland
none;child|barnet;child|en vän;bed|en natt
none;parents|föräldrarna;shield|trygg för barnet;bed|sova över
none;bed|sover över;child|barn och unga;friends|vänskapsförhållanden
none;child|ett barn;rise|puberteten;parents|sina föräldrar
none;parents|Föräldrarna;person|den unga;land|utrymme
none;person|en ung person;shield|ta ansvar;document|ansvarsfullt sätt
none;person|den unga;parents|sina föräldrar;boundary|gränser
none;finland|Finland;child|barn;calendar|deras ålder
none;child|barnet växer;rise|ökar;shield|självbestämmanderätten
none;clothes|kläder;friends|vänner;school|studerar
none;parents|föräldrarna;person|den unga;shield|ta ansvar för sig själv
none;clock|senare;house|hemma på kvällen;elder|äldre
blocked;person|den unga;speech|berättar allt;parents|sina föräldrar
none;parents|föräldrarna;heart|intresse;person|den unga
none;person|den unga;speech|diskutera;parents|sina föräldrar
support;family1|familjen;shield|tryggt stöd;person|den unga
none;finland|Finland;child|barn;court|förbjuden
none;child|Barn;shield|får inte;alert|bestraffas fysiskt
none;book|lagen;shield|vårdnad om barn och umgängesrätt;calendar|1984
none;alert|våld;child|barn;court|brott
none;boundary|gränser;document|regler;child|barn och unga
none;contract|komma överens;document|gemensamma regler;parents|andra föräldrar
none;tobacco|tobak;alcohol|alkohol;child|barn under 18 år
none;person|en person;calendar|18 år;shield|myndig
none;person|den unga;shield|rätt;document|besluta om sitt eget liv
none;child|barn under 18;document|beslut;shield|vissa ärenden''',
    'vald': '''none;alert|Våld;court|brott;finland|Finland
none;alert|våld;family1|familjer
none;person|förövaren;person|offret;heart|en nära relation
none;couple|maken, partnern;child|ett barn;generations|en släkting
none;alert|Våld;house|familjen
none;alert|Det;family1|alla familjemedlemmar;person|den som utsätts
none;person|Fysiskt;speech|känna igen;alert|våld
none;alert|slag;speech|knuffar;work|föremål
none;speech|Psykiskt;alert|våld
none;speech|skäller på;lock|övervakar;friends|sociala relationer
none;alert|Våld;money|ekonomiskt
none;person|den ena maken;lock|inte har tillgång;money|egna pengar
none;person|någon;lock|pressa eller tvinga;alert|sexuellt våld
none;alert|utan samtycke;court|brott;rings|gifta med varandra
none;heart|nära relationer;speech|psykiskt våld;lock|kontrollerande beteende
none;clock|Med tiden;rise|allvarligare;person|fysiskt våld
notify;family1|familjen;notice|anmäla;shield|polisen
none;notice|anmäls;document|en liten del;shield|polisen
none;speech|Folk tänker;alert|våld;lock|privatsak
none;speech|tiger;person|de
none;alert|Våld;court|straffbar handling;family1|familjen
none;child|ett barn;hospital|allvarliga skador;alert|dödsfall
none;child|Barnet;fear|trauman;alert|utveckling
none;child|barn;fear|rädsla;shield|förlora tilliten
flow;person|en vuxen;child|Barnet;clock|hela livet
none;parents|en förälder;child|ett barn;court|särskilt allvarligt
none;fear|trauman;child|barnets;alert|utveckling
none;child|Ett barn;shield|aldrig skyldigt;person|den vuxne
none;child|barn;speech|berätta;family1|familjemedlem
none;family1|familjemedlemmar;shield|skyldiga att ingripa;speech|misstänker
none;alert|Våld;child|barnen;shield|även om
none;parents|föräldrarna;fear|psykiska konsekvenser;child|barnet
none;alert|en upplevelse av våld;clock|livslånga;child|barnet
none;child|Barn;woman|mamman;fear|skrämmande
none;child|barnen;house|familjen;fear|spända stämningen
none;child|barnet;fear|ångest;bed|sömnsvårigheter
none;child|Barnets;hospital|hälsa;alert|äventyras
none;child|Barn;book|inlärnings- och koncentrationssvårigheter;school|skolan
none;shield|Skyddsåldersgränsen;calendar|16 år
none;child|ett barn under 16 år;court|brott
none;friends|ungdomar;scales|samma stadium i utvecklingen;shield|inte ett brott
none;money|Köp;child|ett barn under 18 år;court|brott
support;person|De vuxna;shield|skydda;child|barn
blocked;person|Ingen;lock|locka eller tvinga;child|ett barn''',
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
            reason='Source-specific non-graphic explanation: '
                   + ', '.join(label for _, label in objects)
                   + '. No violence, sexual act or identifiable victim is staged. '
                     'Exact source qualifications remain visible in both languages.',
        ))
    if slug == 'uppfostran':
        plan[24]['reason'] += ' Symbolic body and speech indicate physical and psychological categories, not an instruction or enacted punishment.'
        plan[32]['objects'][0][1] = 'Barn som har upplevt aga'
        plan[32]['title'] = 'än barn som inte har agats'
        for index in [57,58,59,63]:
            for node in plan[index]['objects']:
                if node[0] == 'friends':
                    node[0] = 'children'
        plan[72]['objects'][-1][0] = 'person'
        plan[73]['relation'] = 'none'
        plan[73]['title'] = 'Man kan inte kräva'
        plan[40]['source_context_ids'] = [rows[39]['sentence_id']]
        plan[48]['title'] = 'innan de får röra sig utomhus på egen hand'
        plan[52]['title'] = 'inte kräver mer av barnet än hen är redo för'
        plan[62]['relations'] = ['together', 'together']
        plan[68]['title'] = 'i den mån det är möjligt med tanke på deras ålder'
        plan[83]['title'] = 'man inte får ge'
        plan[83]['relations'] = ['none', 'blocked']
    else:
        plan[7]['objects'][1][0] = 'person'
        plan[13]['title'] = 'Sex utan samtycke är ett brott'
        plan[18]['title'] = 'Folk tänker ofta'
        plan[23]['objects'][-1][0] = 'no_shield'
        plan[24]['objects'][0][1] = 'en vuxen som beter sig våldsamt'
        plan[24]['objects'][-1][1] = 'problem genom hela livet'
        plan[24]['title'] = 'Om barnet tar modell'
        plan[25]['objects'][0][0] = 'person'
        plan[27]['title'] = 'ansvaret ligger alltid hos den vuxne'
        plan[30]['title'] = 'även om våldet inte skulle rikta sig mot dem'
        plan[40]['title'] = 'samma stadium i utvecklingen'
    (episode / 'visual-plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
