"""Author advisory-only exact-source plans; never edit root episode inputs."""
from pathlib import Path
import hashlib
import json
import re

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PLANS = {
    'familjeband': '''warning;document|tidsbestämt uppehållstillstånd;parties|äktenskapet;prohibited|upphör
group;person|familjemedlemmens;document|uppehållstillståndet;house|familjeförening i Finland
warning;people|familjebandet;document|uppehållstillståndet;clock|inte förlängs
warning;document|existerande tillstånd;prohibited|upphävs
group;shield|oskäligt att vägra;people|starka band;flag_fi|Finland
group;people|sådana;document|Exempel
group;child|barn;family|andra familjemedlemmar;flag_fi|Finland
group;work|arbetsplats;shop|eget företag;flag_fi|Finland
group;book_pages|studieplats;flag_fi|Finland
group;prohibited|skilsmässan;shield|våldsam mot dig eller ditt barn;document|uppehållstillstånd
flow;hospital|läkarintyg;document|redovisning;people|familjerådgivning
merge;document|ansökan om uppehållstillstånd;document|din egen redovisning;paper|Bifoga
branch;shield|arbetsgivarens utnyttjande;document|fortsatt tillstånd;paper|intyg om utvidgad rätt att arbeta
group;document|Ansök om fortsatt tillstånd;clock|nuvarande uppehållstillstånd ska utgå;work|inte har en ny arbetsgivare
group;paper|Ansök om intyg;document|giltigt uppehållstillstånd;work|en ny arbetsgivare
flow;paper|intyget eller det fortsatta tillståndet;work|vilken bransch som helst
group;shield|offer för människohandel;magnify|motiverade skäl att misstänka;document|uppehållstillstånd i Finland
group;person|Du;flag_fi|i Finland;document|ansöka om uppehållstillstånd
group;shield|speciellt sårbar ställning;document|kontinuerligt uppehållstillstånd''',
    'beslut': '''group;flag_fi|redan är i Finland;document|negativt beslut;globe|lämna Finland
warning;paper|beslut om avlägsnande ur landet;prohibited|avvisas eller utvisas;flag_fi|Finland
flow;document|beslutet;court|överklaga
group;court|överklagar;globe|avlägsnas ur Finland
group;document|ansökt om uppehållstillstånd;globe|utomlands;court|överklaga
group;clock|vänta;paper|behandlingen av besvären;globe|utomlands
merge;document|beslutet;paper|besvärsanvisning;envelope|bifogas
flow;paper|Besvären;court|förvaltningsdomstolen
branch;court|Förvaltningsdomstolen;prohibited|avslå besvären;document|ny behandling
group;prohibited|Avslag;document|beslut;shield|gällande
group;court|förvaltningsdomstolen;document|besvärstillstånd;court|högsta förvaltningsdomstolen
flow;court|högsta förvaltningsdomstolen;document|besvärstillstånd;paper|besvären
group;person|privat jurist;court|statlig rättshjälpsbyrå;shield|Flyktingrådgivningen rf
group;prohibited|avslag;court|förvaltningsrätten;globe|lämna Finland
group;person|Du;globe|lämna landet frivilligt
contrast;calendar|30 dagar;clock|genast
flow;document|beslutsdokumentet;calendar|exakta tidsfristen
group;clock|inte lämnar landet inom tidsfristen;police|polisen;shield|gränsbevakningsväsendet
protect;person|du;shield|inte utvisas
group;document|uppehållstillstånd;court|endast Migrationsverket
flow;globe|flyttar utomlands;notice|anmäla flytten;database|Myndigheten för digitalisering och befolkningsdata
branch;document|anmälan;laptop|internet;paper|blankett
group;globe|flyttar utomlands;coins|FPA:s förmåner;card|europeiska sjukvårdskortet
flow;globe|utomlands;notice|anmäla ändringar;court|FPA
group;family|ändrade familjeförhållanden;work|börjar arbeta;coins|FPA:s förmåner
group;person|du;globe|ditt hemland;coins|stöd för frivilligt återvändande
contrast;coins|pengar;gear|tjänster
group;flag_eu|inte är ett EU-land;person|medborgare;document|frivilligt återvändande
group;document|ansökt om asyl;prohibited|fått avslag
group;document|ansökt om asyl;prohibited|dragit tillbaka din asylansökan
timeline;shield|tidigare beviljats internationellt skydd;prohibited|upphört''',
    'utan-tillstand': '''group;flag_fi|Finland;document|visum eller uppehållstillstånd;warning|illegal
group;document|asylansökan;clock|handläggningen;flag_fi|rätt att vistas i Finland
timeline;flag_fi|kommit lagligt till Finland;clock|senare;warning|olaglig
group;document|följande situationer;warning|Detta kan hända
group;document|uppehållstillstånd;document|asylansökan;prohibited|negativt beslut
group;document|uppehållstillstånd;clock|går ut;paper|ansöker inte om fortsatt tillstånd i tid
timeline;document|visum;clock|går ut
group;clock|vistelsetiden utan visum har gått ut;document|inte längre har någon laglig grund
group;house|nödinkvartering;food|mathjälp;coins|inte har pengar till mat
group;court|Kommuner;house|församlingar;people|vissa organisationer
flow;person|jurist;shield|Flyktingrådgivningen;paper|juridisk rådgivning
group;paper|Rådgivningen;coins|kostnadsfri
group;hospital|brådskande och nödvändig vård;hospital|hälsostation;hospital|sjukhus
group;hospital|Offentliga hälsovårdstjänster;court|välfärdsområdena;flag_fi|Finland
flow;person|du;phone|kontakta;hospital|social- och hälsocentralen''',
    'medborgarskap': '''group;clock|bott i Finland tillräckligt länge;speech|lärt dig ett lokalt språk;document|ansöka om finskt medborgarskap
flow;person|en förälder;flag_fi|finsk medborgare;child|Du
group;paper|anmälan;flag_fi|medborgarskap
group;child|född i Finland;flag_fi|medborgarskap
contrast;flag_fi|Finskt medborgarskap;document|uppehållstillstånd
group;child|Barnet;calendar|vid födseln;flag_fi|finskt medborgarskap
group;person|barnets mor;flag_fi|finsk medborgare
group;person|barnets far är finsk medborgare;parties|gift med barnets mor
group;flag_fi|barnet föds i Finland;person|barnets far är finsk medborgare;database|faderskapet har bekräftats
group;flag_fi|barnet föds i Finland;person|barnets mor som inte har fött barnet är finsk medborgare;database|moderskap har bekräftats
group;globe|barnet föds utomlands;people|en finsk far eller en finsk mor som inte har fött barnet;parties|föräldrarna inte är gifta med varandra
group;globe|utländska föräldrar;flag_fi|föds i Finland;document|inte får medborgarskap i något annat land av sina föräldrar
group;people|Följande personer;paper|medborgarskapsanmälan
group;clock|tidigare;flag_fi|finsk medborgare
group;globe|ett barn som föds utomlands;parties|utom äktenskapet;people|en finsk far eller till en finsk mor som inte har fött barnet
group;person|18–22 år gamla personer;house|bott i Finland flera år
group;child|12–17 år gammalt adoptivbarn;person|finsk medborgare
group;person|medborgare i ett nordiskt land;flag_fi|bott i Finland;calendar|de senaste fem åren''',
}

# Small exact-source bars carry modality and pivotal qualifications; longer
# cumulative rules remain in required_logic and the exact bilingual source.
CONDITIONS = {
    'familjeband': {
        1: ['Om du har', 'kan'], 2: ['kan påverka', 'om'],
        3: ['Om familjebandet inte längre existerar', 'kan det hända'],
        4: ['möjligt'], 5: ['kan dock förlängas', 'och'],
        10: ['kan', 'trots skilsmässan'], 13: ['Om du redan har uppehållstillstånd i Finland', 'kan du ansöka'],
        14: ['om', 'och'], 15: ['om', 'och'], 17: ['eller', 'kan du beviljas'],
        18: ['måste vara i Finland'], 19: ['Om', 'kan'],
    },
    'beslut': {
        1: ['Om', 'måste'], 2: ['kan'], 3: ['om du är missnöjd med det'],
        4: ['kan', 'trots'], 5: ['också om'], 6: ['måste'],
        7: ['alltid'], 9: ['antingen', 'eller'], 11: ['Om', 'i vissa fall'],
        12: ['Om', 'beviljar besvärstillstånd'],
        13: ['endast asylsökande'], 14: ['Om', 'eller'],
        16: ['vanligtvis', 'eller'], 18: ['Om'],
        19: ['om du hotas av'], 20: ['endast Migrationsverket'],
        23: ['om', 'eller'], 24: ['och har rätt till FPA:s förmåner'],
        25: ['kan påverka'], 26: ['i vissa fall'], 27: ['antingen', 'eller'],
        28: ['och'], 30: ['eller'],
    },
    'utan-tillstand': {
        1: ['Om', 'men inte har det', 'kan'],
        2: ['Om du är asylsökande', 'så länge som'],
        3: ['Även om', 'kan'], 4: ['till exempel'],
        6: ['och', 'eller'], 7: ['eller'], 8: ['eller'],
        9: ['om du inte har pengar till mat eller någonstans att övernatta'],
        13: ['Om du blir sjuk eller skadas', 'brådskande och nödvändig'],
        15: ['Om du behöver hälso- och sjukvårdstjänster'],
    },
    'medborgarskap': {
        1: ['kan ansöka', 'och bland annat'], 2: ['kan'],
        3: ['I vissa situationer', 'kan'], 4: ['I vissa undantagsfall', 'kan'],
        5: ['inte samma sak'], 6: ['automatiskt', 'i följande fall'],
        8: ['och'], 9: ['och', 'eller'],
        10: ['och', '1.4.2019 eller senare'],
        11: ['kan', 'och föräldrarna inte är gifta med varandra'],
        12: ['kan', 'om'], 13: ['kan'],
        15: ['utom äktenskapet'], 16: ['som har bott i Finland flera år'],
        17: ['12–17 år'], 18: ['de senaste fem åren'],
    },
}

LOGIC = {
    'familjeband': {
        1: 'Fixed-term permit AND family-ties basis. Relationship ending MAY affect it; never automatic revocation.',
        2: 'Death MAY affect the permit IF this relative was the person who applied for family reunification in Finland.',
        3: 'Family relationship no longer exists -> possible non-extension, not a certain outcome.',
        4: 'Existing permit MAY be revoked; inherit family-ties context from preceding source.',
        5: 'Possible extension IF refusal would be unreasonable AND strong ties to Finland persist. Both gates are cumulative.',
        6: 'Only introduces examples of strong ties; no independent entitlement.',
        7: 'Example of strong ties; inherits cumulative source-5 conditions, not automatic extension.',
        8: 'Work OR own enterprise is one strong-ties example; source-5 gates still apply.',
        9: 'Study place is an example; source-5 gates still apply.',
        10: 'Divorce BECAUSE spouse was violent to applicant OR applicant child -> permit MAY be extended despite divorce. No victim photograph.',
        11: 'Required supporting report; medical certificate OR family-counselling statement are examples, not an exhaustive or simultaneous demand.',
        12: 'Also attach applicant own account to the permit application; no medical/victim record is fabricated.',
        13: 'Already has permit in Finland AND employer exploitation -> may APPLY for extension OR extended-work-right certificate. Do not show either automatically granted.',
        14: 'Extension route IF current permit is expiring AND no new employer. Both conditions are cumulative.',
        15: 'Certificate route IF existing permit remains valid AND a new employer exists. Distinct from preceding extension route.',
        16: 'Any-industry work is supported by either certificate OR continued permit; source context must remain.',
        17: 'Human-trafficking victim OR justified suspicion -> permit MAY be granted. Do not imply certainty or require confirmed victim status in the suspicion branch.',
        18: 'Must be in Finland to APPLY through trafficking-victim route. No automatic grant.',
        19: 'Especially vulnerable situation -> MAY get continuous permit; this remains the preceding trafficking context.',
    },
    'beslut': {
        1: 'Already in Finland AND negative residence decision -> source says must leave. No automatic assumption that every applicant is currently inside Finland.',
        2: 'Removal decision MAY also be made; distinguish possible decision from inevitable instantaneous removal.',
        3: 'May appeal IF dissatisfied; do not imply success.',
        4: 'Appeal does not automatically suspend possible removal; a pending appeal is not a guaranteed right to remain.',
        5: 'Appeal remains possible when original application was submitted abroad.',
        6: 'In preceding abroad-application case, appeal processing must be awaited abroad.',
        7: 'Appeal instructions accompany the decision; no invented deadline.',
        8: 'Administrative court processes appeal, not a district court despite generic court icon.',
        9: 'Administrative court MAY reject OR return to Migri for new processing. Return is not a granted permit.',
        10: 'Rejection leaves Migri original decision in force; do not show new processing.',
        11: 'IF administrative court rejects -> IN SOME CASES may APPLY for leave to appeal to highest administrative court. No guaranteed leave or automatic second full appeal.',
        12: 'Highest court examines appeal only IF leave to appeal is granted.',
        13: 'Private lawyer OR state legal aid OR refugee advice. ONLY the refugee-advice option has the source asylum-applicant limitation; do not extend that restriction to lawyers/legal aid generally.',
        14: 'Permit refusal OR administrative rejection of appeal -> source must leave.',
        15: 'Opportunity to leave voluntarily, not a promise of support or a 30-day guarantee.',
        16: 'Usually 30 days OR immediate removal. The 30-day time is not universal.',
        17: 'Actual precise deadline is in the decision document; no invented date.',
        18: 'IF does not leave within deadline -> police OR border guard remove. Do not remove the deadline gate.',
        19: 'Non-refoulement: no deportation IF source-listed death penalty/torture/persecution/inhuman or degrading treatment threatens in homeland. Generic shield, no staged violence.',
        20: 'Only Migri decides residence permits; previous courts decide appeals and can remit. Avoid a graphic implying courts issue permits.',
        21: 'Moving abroad from Finland -> notify population authority; symbolic source institution, no personal data.',
        22: 'Internet OR form; forms obtainable from post office OR population-authority service point.',
        23: 'Moving abroad AND (receives Kela benefits OR has EHIC) -> notify Kela. Not an unconditional obligation attached to citizenship.',
        24: 'Abroad AND still entitled to Kela benefits -> always report changed circumstances to Kela.',
        25: 'Family changes OR starting work MAY affect benefit entitlement; no certainty or specific payment change.',
        26: 'Wants to return to homeland -> IN SOME CASES may receive voluntary-return support.',
        27: 'Support is money OR services, not both necessarily.',
        28: 'Eligibility list is NON-EU citizenship AND at least one of following asylum/protection alternatives. This row ends AND; never depict non-EU citizenship alone as sufficient.',
        29: 'NON-EU citizenship from source 28 AND asylum applied for AND refusal received. This is one alternative, not a requirement added to sources 30 and 31.',
        30: 'NON-EU citizenship from source 28 AND asylum applied for AND application withdrawn. Alternative to source 29 and source 31.',
        31: 'NON-EU citizenship from source 28 AND international protection previously granted BUT now ended. Alternative to sources 29 and 30.',
    },
    'utan-tillstand': {
        1: 'Needs visa OR residence permit AND lacks it -> stay MAY be illegal. Do not label all people without a permit unlawful.',
        2: 'Asylum applicant may stay without visa/permit WHILE asylum application processing is ongoing. This is a lawful-stay exception, not an expiry graphic.',
        3: 'Lawful arrival MAY later become unlawful stay; timeline must retain possibility rather than inevitability.',
        4: 'Introduces non-exhaustive possible situations; inherit source 3 MAY, no instant removal implied.',
        5: 'Refusal of permit OR asylum is one possible source-listed case, not an immediate-removal date claim.',
        6: 'Permit expires AND continued permit not applied for in time. Never portray expiry alone as this full two-part condition.',
        7: 'Entered with visa AND visa expires; another list alternative.',
        8: 'Visa-free period expired OR no longer any lawful ground. Preserve both alternatives without country/day assumptions.',
        9: 'Emergency accommodation/food help is conditional on lacking food money/place to sleep as literally worded. Russian is reviewed data, not authority to silently rewrite Swedish connective scope.',
        10: 'Municipalities, parishes and some organisations arrange emergency accommodation; no current site or bed availability promised.',
        11: 'Legal advice on undocumented status by refugee-advice lawyer; no photographed person assigned a status.',
        12: 'Previous legal advice is free; do not apply free-of-charge claim to all care/services in later sentences.',
        13: 'IF sick or injured -> urgent AND necessary PUBLIC care. Do not broaden to all elective care or assert free treatment.',
        14: 'Wellbeing services counties organise public care; no exact site promise.',
        15: 'If needs health services -> contact nearest local social/health centre. No emergency number or fee invented.',
    },
    'medborgarskap': {
        1: 'May APPLY after sufficient residence AND, among other things, learning a local language. Non-exhaustive criteria; no years count, level or automatic citizenship invented.',
        2: 'May acquire through a Finnish-citizen parent; later case list supplies exact parentage/location qualifiers.',
        3: 'IN CERTAIN situations through notification; no universal notification route.',
        4: 'Only SOME EXCEPTIONAL cases based on birth in Finland; do not depict general birthplace citizenship.',
        5: 'Citizenship and residence permit are distinct legal concepts, not superior/inferior document versions.',
        6: 'Header: AUTOMATIC citizenship AT BIRTH applies only to the following alternative cases.',
        7: 'Automatic-at-birth case: child mother is Finnish citizen. Inherit source-6 scope.',
        8: 'Automatic-at-birth case: father is Finnish citizen AND married to child mother. Citizenship alone is not this complete case.',
        9: 'Automatic-at-birth case: child born IN FINLAND AND father Finnish citizen AND paternity CONFIRMED. All three cumulative gates. Source final OR introduces next independent case.',
        10: 'Automatic-at-birth case: born IN FINLAND AND NON-BIRTH mother Finnish citizen AND that non-birth maternity CONFIRMED ON/AFTER 1 APRIL 2019. The date qualifies maternity confirmation, not birth date or parent citizenship. All conditions cumulative.',
        11: 'NOT automatic: child MAY get via NOTIFICATION IF born ABROAD AND (Finnish father OR Finnish NON-BIRTH mother) AND parents NOT MARRIED. Parent alternatives are inside the shared abroad/unmarried gates.',
        12: 'Child of FOREIGN parents, born IN FINLAND, MAY receive citizenship IF no citizenship from any other country through parents. Birth in Finland alone does not suffice.',
        13: 'Header introduces cases that MAY use faster/cheaper NOTIFICATION route. No automatic grant or numeric price invented.',
        14: 'Former Finnish citizen; inherits possible notification route, not automatic restoration.',
        15: 'Child born ABROAD OUTSIDE MARRIAGE AND (Finnish father OR Finnish NON-BIRTH mother). Notification-route list item. Do not collapse to any Finnish parent.',
        16: 'Age 18–22 AND several years residence in Finland; source does not specify a numeric residence count.',
        17: 'ADOPTED child aged 12–17 AND adopter Finnish citizen. Keep adopted status and both age bounds.',
        18: 'Citizen of a NORDIC country AND residence in Finland during the LAST FIVE YEARS. Not EU citizenship, not cumulative historic five years.',
    },
}

# Use only the root renderer's actually available icon names.
ALIASES = {'magnify': 'document', 'envelope': 'document', 'notice': 'document',
           'card': 'document', 'speech': 'document'}
SUPPORTED = {
    'parties', 'person', 'people', 'work', 'court', 'prohibited', 'police',
    'document', 'calendar', 'database', 'coins', 'shop', 'window', 'traffic',
    'car', 'house', 'shield', 'bank', 'hospital', 'factory', 'field', 'plant',
    'tree', 'ship', 'laptop', 'phone', 'flask', 'gear', 'bulb', 'ball',
    'family', 'child', 'globe', 'warning', 'flag_fi', 'flag_eu', 'clock',
    'food', 'paper', 'book_pages',
}

handoff = []
for slug, raw in PLANS.items():
    section_id = 'hb-c12-' + slug
    path = ROOT / 'studio/episodes' / section_id / 'script.yaml'
    original_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    script = yaml.safe_load(path.read_text())
    rows = script['sentences']
    lines = raw.splitlines()
    assert len(lines) == len(rows)
    out = []
    for number, (line, row) in enumerate(zip(lines, rows), 1):
        composition, *nodes = line.split(';')
        parsed = []
        for value in nodes:
            kind, label = value.split('|', 1)
            kind = ALIASES.get(kind, kind)
            assert kind in SUPPORTED, kind
            match = re.search(re.escape(label), row['sv'], re.I)
            assert match, (section_id, number, label)
            parsed.append(dict(label=match.group(), icon=kind))
        result = dict(
            id=f'picture-{number:03}', visual_type='diagram',
            composition=composition, nodes=parsed,
            description=LOGIC[slug][number], required_logic=LOGIC[slug][number],
            source_sentence_ids=[row['sentence_id']],
            source_text=row['sv'], reviewed_translation=row['ru'],
            advisory_only=True,
        )
        condition_labels = CONDITIONS.get(slug, {}).get(number, [])
        # Multiple adjacent short modality words form one source-exact bar only
        # if contiguous; separate bars otherwise need their own node scope.
        conditions = []
        for offset, label in enumerate(condition_labels):
            assert label in row['sv'], (slug, number, label)
            scope = list(range(len(parsed)))
            if slug == 'medborgarskap' and number == 10 and offset == 1:
                scope = [2]
            elif slug == 'beslut' and number == 13:
                scope = [2]
            elif len(condition_labels) > 1:
                scope = [min(offset, len(parsed) - 1)]
            conditions.append(dict(label=label, node_indices=scope))
        if conditions:
            result['conditions'] = conditions
            result['condition_layout_advisory'] = 'Keep each modifier visibly attached to its stated scope; root should review multiline bars before rendering. Do not stack overlapping bars or drop any required_logic gate to fit.'
        if conditions:
            result['source_modifiers'] = condition_labels
            bars = {
                'familjeband': {
                    1: 'med familjeband som grund', 2: 'om denna familjemedlem var den person som ansökte om familjeförening i Finland',
                    3: 'kan det hända', 4: 'möjligt', 5: 'och', 10: 'kan ditt uppehållstillstånd förlängas trots skilsmässan',
                    13: 'Om du redan har uppehållstillstånd i Finland', 14: 'och', 15: 'och',
                    17: 'kan du beviljas uppehållstillstånd i Finland', 18: 'måste vara i Finland', 19: 'kan',
                },
                'beslut': {
                    1: 'Om du redan är i Finland', 2: 'kan', 3: 'om du är missnöjd med det',
                    4: 'trots att du överklagar', 5: 'om du har ansökt om uppehållstillstånd utomlands',
                    6: 'måste', 7: 'alltid', 9: 'antingen', 11: 'i vissa fall', 12: 'beviljar besvärstillstånd',
                    13: 'endast asylsökande', 14: 'eller', 16: 'vanligtvis', 18: 'Om du inte lämnar landet inom tidsfristen',
                    19: 'om du hotas av', 20: 'endast Migrationsverket', 23: 'om du får FPA:s förmåner eller om du har det europeiska sjukvårdskortet',
                    24: 'och har rätt till FPA:s förmåner', 25: 'kan påverka', 26: 'i vissa fall', 27: 'antingen', 28: 'och', 30: 'eller',
                },
                'utan-tillstand': {
                    1: 'kan', 2: 'så länge som handläggningen av din asylansökan pågår', 3: 'kan', 4: 'till exempel',
                    6: 'och', 7: 'eller', 8: 'eller',
                    9: 'om du inte har pengar till mat eller någonstans att övernatta',
                    13: 'Om du blir sjuk eller skadas', 15: 'Om du behöver hälso- och sjukvårdstjänster',
                },
                'medborgarskap': {
                    1: 'och bland annat', 2: 'kan', 3: 'I vissa situationer', 4: 'I vissa undantagsfall', 5: 'inte samma sak',
                    6: 'automatiskt', 8: 'och', 9: 'och', 10: '1.4.2019 eller senare',
                    11: 'kan få finskt medborgarskap genom anmälan', 12: 'om hen inte får medborgarskap i något annat land av sina föräldrar',
                    13: 'kan', 15: 'utom äktenskapet', 16: 'som har bott i Finland flera år', 17: '12–17 år', 18: 'de senaste fem åren',
                },
            }
            bar = bars[slug][number]
            assert bar in row['sv']
            scope = [2] if ((slug == 'medborgarskap' and number == 10)
                            or (slug == 'beslut' and number == 13)) else list(range(len(parsed)))
            result['conditions'] = [dict(label=bar, node_indices=scope)]
            result['condition_layout_advisory'] = 'One displayed bar avoids overlapping qualifier boxes. Source modifiers and required_logic preserve every further gate; inspect actual wrapping before render.'
        if slug == 'familjeband' and number in [4, 6, 7, 8, 9, 11, 12, 16, 19]:
            context = 5 if number in [6, 7, 8, 9] else {4: 3, 11: 10, 12: 10, 16: 13, 19: 17}[number]
            result['source_sentence_ids'].append(rows[context - 1]['sentence_id'])
        if slug == 'beslut' and number in [29, 30, 31]:
            result['source_sentence_ids'].append(rows[27]['sentence_id'])
            result['conditions'] = [dict(label='medborgare i ett land som inte är ett EU-land', node_indices=list(range(len(parsed))))]
        if slug == 'utan-tillstand' and number in [5, 6, 7, 8]:
            result['source_sentence_ids'].append(rows[2]['sentence_id'])
        if slug == 'utan-tillstand' and number == 12:
            result['source_sentence_ids'].append(rows[10]['sentence_id'])
        if slug == 'medborgarskap' and 7 <= number <= 10:
            result['source_sentence_ids'].append(rows[5]['sentence_id'])
        if slug == 'medborgarskap' and 14 <= number <= 18:
            result['source_sentence_ids'].append(rows[12]['sentence_id'])
        if slug == 'beslut' and number == 28:
            result['nodes'][0]['crossed'] = True
        if slug == 'medborgarskap' and number in [11, 15]:
            result['nodes'][2 if number == 11 else 1]['crossed'] = True
        if (slug == 'familjeband' and number in [11, 12, 14, 15, 18]
                or slug == 'beslut' and number in [7, 8, 13, 17, 20, 22, 23]
                or slug == 'utan-tillstand' and number in [10, 11, 13, 14, 15]
                or slug == 'medborgarskap' and number in [3, 5]):
            result['photo_request'] = dict(
                subject='Verified actual public institution exterior/sign or blank administrative/document object relevant to this exact source; no named applicant, citizen, victim or personal record.',
                acquisition_status='Advisory request only; no source acquired or license claimed.',
                fallback='This individually authored exact-source diagram.',
            )
        out.append(result)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == original_sha256
    output = HERE / (section_id + '.json')
    output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    handoff.append(dict(section_id=section_id, plans=len(out),
                        source_script_sha256=original_sha256,
                        advisory_plan=str(output.relative_to(ROOT)),
                        source_pairs_read=len(out),
                        source_conditions='Exact source substrings, scoped gates and explicit AND/OR/modality explanations.',
                        root_episode_unchanged=True,
                        layout_status='Advisory only; root producer must inspect node/bar layout and choose verified object photos. No rendering/listening claimed.'))
(HERE / 'chapter09a-handoff.json').write_text(json.dumps(dict(
    scope='Four advisory plans only; root scripts/media/jobs untouched.',
    episodes=handoff, total_pairs=sum(row['plans'] for row in handoff),
), ensure_ascii=False, indent=2) + '\n')
print('Wrote four advisory plans for', sum(row['plans'] for row in handoff), 'exact source pairs.')
