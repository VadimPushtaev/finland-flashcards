"""Individually direct the civil-status/cohabitation source relationships."""
from pathlib import Path
import json,yaml,re
SID='hb-c09-samlevnad';ep=Path('studio/episodes')/SID;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
# Per-source-sentence figurative content and explicit relation, no added legal facts.
plans=[
    ('registry','person|Civilstånd;registry|befolkningsdatasystem', 'notify','A person record enters the population information registry.'),
    ('couple','person|Civilståndet;couple|parförhållande', 'none','An individual civil-status record and the relationship it describes.'),
    ('status','rings|gift;split|skild;person|änka eller änkling', 'none','Three pictured examples from the source enumeration, without suggesting an exhaustive visual list.'),
    ('cohabit','couple|par;house|stadigvarande förhållande', 'together','A couple shares a stable domestic setting without using wedding imagery.'),
    ('samehome','couple|två makar;house|bor tillsammans', 'together','Two partners and one shared dwelling depict cohabitation.'),
    ('partners','couple|sambor', 'none','Two adults linked as partners; no rings or marriage contract.'),
    ('unregistered','house|Samboförhållande;registry|befolkningsdatasystemet', 'blocked','A home-sharing relationship is not a registered civil-status entry; block only the registry connection.'),
    ('nocontract','couple|samboförhållande;contract|skriftligt avtal', 'blocked','No mandatory written cohabitation contract is represented; no additional obligations are implied.'),
    ('differentrights','couple|Sambor;rings|gifta par', 'none','Cohabiting and married relationship symbols shown side by side with visually separate legal frames.'),
    ('nosupport','person|den ena maken;money|försörja den andra', 'blocked','The pictured transfer of partner support is crossed out to explain absence of a duty in this archived sentence.'),
    ('noinherit','person|den ena maken;will|testamente;person|den andra', 'inherit','A will is explicitly interposed between the deceased partner and the surviving partner; it is the source condition for inheritance.'),
    ('sharedbudget','couple|Samborna;money|inkomster och utgifter', 'together','Two partners jointly arrange their household budget; no currency amounts are invented.'),
    ('childstatus','child|Barnets ställning;parents|föräldrar', 'none','A child is central alongside the parental pair; no marriage requirement is drawn.'),
    ('childrights','child|Barnet;will|ärva;money|familjepension', 'inherit','The child and source-stated inheritance and survivor benefit objects are shown without implying amounts.'),
    ('parentssupport','parents|Båda föräldrarna;child|sitt barn', 'support','Both parents provide care and support toward the child regardless of marriage.'),
    ('surname','couple|Ni;document|gemensamt efternamn', 'flow','Both partners point to a shared surname document; following source fragments supply the conditions.'),
    ('commonchild','parents|ni;child|gemensamma barn', 'together','The source first alternative condition is a shared child, represented by parents and child.'),
    ('fiveyears','house|bott tillsammans;calendar|minst fem år', 'together','A shared dwelling and calendar show the second source alternative, labelled with the exact five-year threshold.'),
    ('household','couple|ni;house|samma hushåll', 'together','Partners in one residence are represented as one household.'),
    ('allowance','house|bostadsbidrag;document|FPA', 'flow','Household housing and the FPA benefit application are linked without adding eligibility claims.'),
    ('endhome','house|samma adress;split|upphör', 'flow','A separated residence/branch symbol depicts the end of sharing an address.'),
    ('effect','split|Upphörandet;money|stöd;school|dagvårdsavgifter', 'flow','Changed cohabitation points to source-stated benefit and daycare-fee consequences.'),
    ('notify','person|Du;notice|meddela;registry|samboförhållandet har upphört', 'notify','The individual submits an end-of-cohabitation notice; no automatic registration is implied.'),
    ('ownproperty','person|vardera part;key|sin egen egendom', 'none','A person and property key stay in one personal ownership frame.'),
    ('returnproperty','split|upphör;person|båda parterna;key|sin egen egendom', 'flow','After separation, each party keeps their own property; no equal division of all property is implied.'),
    ('jointbuy','parents|båda parterna;receipt|alla kvitton', 'together','Both buyers link to the retained joint purchase receipt.'),
    ('equaljoint','house|denna egendom;scales|jämnt', 'equal','The jointly purchased property is divided equally, with balanced scales and no monetary amounts.'),
    ('singlebuyer','receipt|bara en av parterna;person|ägare', 'flow','A purchase document in one party name points to that owner.'),
    ('unclear','couple|Sambor;key|egendom;speech|inte har en överenskommelse', 'none','Partners and disputed ownership are separated from the absent agreement; no court outcome is invented.'),
    ('unknownhalf','house|denna egendom;scales|delas på hälft', 'equal','For the source case of unclear ownership, the property is pictured with balanced half division.'),
    ('adjustment','person|den ena sambon;scales|jämkning;person|den andra sambon', 'flow','A discretionary adjustment is represented by scales between the two former partners.'),
    ('contribution','work|genom arbete;house|utöka sin egendom;scales|orättvist', 'flow','Labour contribution increases the other partner property; fairness scales mark the stated adjustment rationale, without guaranteeing a result.'),
    ('will','couple|Sambor;will|testamente', 'flow','Partners may create a will for a death contingency; optionality remains in the exact bilingual text.'),
    ('homewill','will|Genom testamente;house|den gemensamma bostaden;person|sambon', 'inherit','The will links the shared home to the surviving partner, exactly as the source example.'),
    ('agreement','couple|Sambor;contract|skriftligt avtal;split|går isär', 'flow','An optional written property agreement links partners to a possible future separation.'),
    ('advice','will|testamente;speech|råd;court|rättshjälpsbyrån', 'flow','A draft will or agreement leads to legal advice at a legal aid office; no additional entitlement is claimed.')
]
assert len(plans)==len(rows),(len(plans),len(rows))
result=[]
for row,(name,nodes,relation,reason) in zip(rows,plans):
    objects=[x.split('|',1) for x in nodes.split(';')]
    for node in objects:
        label=node[1]
        if label not in row['sv']:
            match=re.search(re.escape(label),row['sv'],re.IGNORECASE)
            assert match,(row['sentence_id'],label)
            node[1]=match.group()
    result.append(dict(id=name,objects=objects,relation=relation,reason=reason))
(ep/'visual-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
