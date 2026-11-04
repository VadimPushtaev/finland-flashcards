"""Individual pictorial direction for exact marriage/ceremony source statements."""
from pathlib import Path
import json,yaml,re
SID='hb-c09-aktenskap';ep=Path('studio/episodes')/SID;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
plans=[
    ('married2023','calendar|2023;couple|två miljoner;rings|gifta','none','The source historical year and approximate married population are labelled exactly; no pictogram count represents a population ratio.'),
    ('marriedpair','couple|varandras makar;rings|äktenskap','together','Two spouses and joined rings depict marriage.'),
    ('lawrelationship','couple|två människor;court|lag','together','The relationship between two people is linked to law.'),
    ('rightsandduties','parents|makar;scales|rättigheter och skyldigheter','together','Partners are linked to balanced rights and responsibilities.'),
    ('equal','parents|Makarna;scales|jämlika;rings|äktenskapet','equal','The two partners stand with equal rights in marriage; balanced scales visualize equality.'),
    ('eligibility','person|Du;rings|gifta dig','flow','An individual approaches marriage subject to conditions in the following exact source fragments.'),
    ('adult','person|minst 18 år gammal','none','An adult silhouette carries only the exact minimum-age label; no invented birthdate.'),
    ('notprevious','person|inte är gift;rings|sedan tidigare;registry|registrerat parförhållande','blocked','Existing marriage or registered partnership is a barrier; diagram blocks the existing-status connection.'),
    ('samesex','couple|samkönade par;rings|gifta sig','flow','Gender-neutral equal partner silhouettes link to marriage without restricting depicted gender.'),
    ('closerelative','generations|Nära släktingar;rings|gifta sig','blocked','Close relatives are separated from marriage by a prohibition marker, without inventing a prohibited-degree chart.'),
    ('freechoice','person|frivilligt val;rings|Äktenskapet','flow','A freely choosing person approaches the marriage symbol; no coercion shown.'),
    ('parentcoerce','parents|föräldrarna;child|sitt barn;rings|gifta sig','blocked','Parental coercion toward a child marriage is blocked with protective separation; no explicit harmful imagery.'),
    ('coercecrime','rings|äktenskap;court|brott','none','Justice and marriage symbols mark forced marriage as the source-stated crime.'),
    ('choosepartner','person|kvinnor och män;couple|själva besluta','flow','Individuals make their own choice of partner; no family approval gate shown.'),
    ('nopermission','generations|släktingar;document|tillstånd','blocked','A relatives-permission document is crossed out for the source statement that permission is unnecessary.'),
    ('lawchanges','calendar|genom tiderna;book|äktenskapslag','flow','A timeline calendar and legal book illustrate changes over time without adding dates.'),
    ('equal2017','calendar|2017;scales|jämlik;rings|äktenskapslagen','equal','The exact2017year links to equal marriage legislation.'),
    ('samegender','couple|par av samma kön;rings|ingå äktenskap','flow','Equal partner silhouettes may enter marriage; no additional eligibility rules added.'),
    ('oldregistration','parents|manliga par och kvinnliga par;registry|registrera sitt parförhållande','flow','The earlier registration form is pictured distinctly from marriage and the exact text preserves the earlier timeframe.'),
    ('limitedpartnership','contract|registrerat partnerskap;scales|inte hade alla de rättigheter;rings|äktenskap','none','Registered partnership and marriage are contrasted around differing rights without implying identical legal status.'),
    ('nobarrier','person|en person;shield|inte finns något hinder;rings|ingå äktenskap','flow','A person reaches marriage after the absence of impediments, shown by a cleared protective check.'),
    ('check','registry|en myndighet;document|hinder för äktenskapet','flow','The authority examines marriage impediments; institution remains schematic.'),
    ('certificate','couple|paret;certificate|intyg om hindersprövning','flow','The couple receives the stated impediment-check certificate when conditions are met.'),
    ('engage','couple|ett par;rings|Förlovning;calendar|senare','flow','Engagement is a voluntary promise of later marriage, pictured with partners, rings and future calendar.'),
    ('notcontract','rings|förlovning;contract|juridiskt avtal','blocked','Engagement is separated from a binding legal contract; no binding duties are drawn.'),
    ('nowait','clock|viss längd;rings|förlovning;court|Lagen','none','A clock is shown as unconstrained by a statutory engagement length; no required period is invented.'),
    ('engagementrings','rings|förlovningsringar','none','Engagement rings are the physical object explicitly discussed; replace with verified ring photography when acquired.'),
    ('breakengage','couple|Par;split|bryta en förlovning','flow','Either or both partners may end engagement, represented by an open branch instead of broken people.'),
    ('nonotice','rings|bryter förlovningen;notice|meddela myndigheterna','blocked','Ending engagement has no authority-notification requirement in the source statement.'),
    ('civilplaces','registry|Myndigheten för digitalisering och befolkningsdata;court|tingsrätt','none','The two official civil ceremony venues are illustrated as distinct institutional possibilities.'),
    ('officiant','person|en tjänsteman;couple|Paret;rings|vigselrätt','flow','An authorized official conducts the couple ceremony; no real person identity implied.'),
    ('otherlocation','person|Tjänstemannen;house|andra ställen;money|avgiftsbelagt','flow','The official can travel to another venue for a fee; no price invented.'),
    ('church','institution|evangelisk-lutherska;book|ortodoxa kyrkan;rings|kyrklig vigsel','none','Two source church traditions are acknowledged around ceremony; verified church architecture can illustrate one named tradition.'),
    ('othercommunity','person|representant;registry|registrerat i Finland;rings|vigselrätt','flow','A religious community representative requires the source authority-granted ceremony right.'),
    ('authorized','person|officiell vigselrätt;rings|äktenskap;shield|officiellt','flow','An authorized officiant makes the religious ceremony official; no unregistered ceremony is labelled valid.'),
    ('checkbefore','document|prövning av hinder;clock|före vigseln;rings|äktenskapet','flow','The impediment check precedes ceremony; exact chronology is shown.'),
    ('bothpresent','couple|Båda makarna;rings|vigseltillfället;clock|vigseltillfället','together','Both partners are physically present together at the ceremony.'),
    ('witnesses','friends|minst två vittnen;calendar|15 år','together','At least two witnesses have reached the exact source15-yearthreshold; no extra witness requirements.'),
    ('civilright','person|Alla;court|borgerlig vigsel;institution|trossamfund','none','Civil ceremony remains available alongside religious affiliation; no forced choice of belief.'),
    ('surnamechoice','couple|ett par;document|gemensamt efternamn','flow','A married pair can optionally choose a shared surname.'),
    ('oldwife','person|kvinnan;document|mannens efternamn','flow','The historical source custom of the woman taking the man surname is shown as a past practice.'),
    ('oldnamelaw','calendar|1930;book|Namnlagen;calendar|1986','flow','The exact historical1930–1986span accompanies the source surname law, without suggesting current obligation.'),
    ('husbandname','person|mannen;document|kvinnans efternamn','flow','A man may take the woman surname under the source present-day option.'),
    ('surnameoptions','couple|Båda;document|sina efternamn;document|helt nytt, gemensamt efternamn','none','Retaining personal surnames and taking an entirely new joint name are distinct source options.'),
    ('combined','document|sitt eget namn;document|den andras namn;couple|båda makarna','together','Partners may combine personal and other partner names; symbolic pages contain no invented personal names.')
]
assert len(plans)==len(rows),(len(plans),len(rows));result=[]
for row,(name,nodes,relation,reason) in zip(rows,plans):
    objects=[x.split('|',1) for x in nodes.split(';')]
    for node in objects:
        if node[1] not in row['sv']:
            m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(row['sentence_id'],node[1]);node[1]=m.group()
    result.append(dict(id=name,objects=objects,relation=relation,reason=reason))
(ep/'visual-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
