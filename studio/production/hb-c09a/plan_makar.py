"""Individually direct married-partner rights and property source statements."""
from pathlib import Path
import json,yaml,re
SID='hb-c09-makar';ep=Path('studio/episodes')/SID;rows=yaml.safe_load((ep/'script.yaml').read_text())['sentences']
plans=[
    ('workchoice','person|Vardera maken;work|förvärvsarbete','flow','Each partner independently chooses participation in work and social life; a person selects a briefcase.'),
    ('householdsupport','parents|Vardera maken;house|gemensamma hushåll;money|underhåll','support','Both partners contribute to the common household and mutual support according to ability.'),
    ('foodclothes','person|den förmögnare maken;money|kostnader;food|mat','support','The wealthier partner covers source-stated everyday costs when the other does not work; no amounts depicted.'),
    ('autonomy','person|varje människa;shield|sexuell självbestämmanderätt','together','A protected individual signifies sexual self-determination within marriage and every relationship.'),
    ('assault','person|en annan;shield|våldtäkt;court|tvingar','none','Protective shield and law symbols accompany the source statement about coerced intercourse; no explicit or sensational depiction.'),
    ('crimeinsideoutside','rings|äktenskapet;court|brott','none','Wedding and justice symbols show that the stated offence remains a crime within marriage.'),
    ('partnerviolence','couple|parrelationer;court|brott','none','Relationship and justice symbols explain the source criminal classification without portraying violence.'),
    ('neverharm','person|sin make;shield|aldrig slå eller skada','together','An intact protected person illustrates the prohibition on striking or harming a spouse.'),
    ('medicalconsent','hospital|läkare;lock|makens samtycke;document|hälsotillstånd','flow','Medical information is protected behind the spouse consent condition; no disclosure beyond the source is implied.'),
    ('caredecision','person|En make;hospital|vård;shield|exceptionella omständigheter','none','A spouse, care setting and exception marker depict that substitute care decisions are exceptional, not routine.'),
    ('propertykinds','couple|Makarna;house|gemensam egendom;key|egen egendom','none','The married pair may hold common property and personal property, shown as distinct objects.'),
    ('nosellothers','person|Den ena maken;key|den andra makens egendom','blocked','Sale of the other partner personal property is blocked; no blanket ban on all sales is drawn.'),
    ('sharedhomeconsent','house|det gemensamma hemmet;lock|den andras lov','together','The shared home and furnishings remain subject to the other partner permission for sale.'),
    ('owndebt','person|Vardera maken;receipt|den skuld','none','A debt document stays with the individual who took the debt before or during marriage.'),
    ('householddebt','receipt|lån;food|mat;parents|båda makarna','flow','The source exception for a family-support loan links everyday food costs to both partners responsibility.'),
    ('jointdebt','couple|makarna;receipt|gemensamma skulder','together','Both partners voluntarily undertake a shared debt document.'),
    ('jointrepay','parents|de;money|återbetala skulderna tillsammans','support','Both partners jointly repay the shared debt; no repayment schedule or sum is supplied.'),
    ('maritalright','couple|Makarnas;shield|giftorätten','together','A protective marital-property right links the two partners financial position.'),
    ('halfdivorce','house|hela egendom;split|skilsmässa;scales|delas på hälften','flow','At divorce the source marital right combines property for half division; no current ownership transfer during marriage is implied.'),
    ('beforeestate','house|egendomar;scales|delas;will|före arvskiftet','flow','Property combination and division precede the estate distribution in the source death contingency.'),
    ('notwill','will|testamente;lock|Giftorätten;contract|äktenskapsförord','none','A will and prenuptial agreement are contrasted around the marital right; exact text states which can alter it.'),
    ('rightstarts','split|ett äktenskap upphör;shield|Giftorätten','flow','The end of marriage triggers the marital-property right in this archived source statement.'),
    ('namedowner','document|vars namn;key|en egendom;person|den make','flow','A property title bearing the named spouse points to that spouse ownership during marriage.'),
    ('preservevalue','parents|Makarna;house|egendom;shield|värde inte minskar','support','Both partners manage covered property to avoid needless loss of value; no invented value scale.'),
    ('separateagreement','house|egendomar;contract|äktenskapsförord','flow','Partners may keep property separate using the stated agreement.'),
    ('partial','contract|äktenskapsförord;house|en del av makarnas egendom','none','A prenuptial document applies to the source option of part of the property; no numerical share is invented.'),
    ('divisionagreement','contract|äktenskapsförord;house|egendom;split|skilsmässa','flow','The agreement specifies division on death or divorce; one source contingency is pictured alongside the exact full text.'),
    ('voluntary','person|Äktenskapsförord;contract|frivilligt','none','An optional agreement sits beside a freely choosing person; no obligatory signing is suggested.'),
    ('exclude','contract|äktenskapsförord;house|den andras egendom;lock|helt eller delvis','flow','The agreement may fully or partly exclude the stated right in the other spouse property.'),
    ('beforeafter','calendar|före äktenskapet;rings|under det;contract|Äktenskapsförord','none','The agreement can be made before or during marriage; no deadline or waiting period added.'),
    ('signwitness','parents|Båda makarna;contract|underteckna;friends|två ojäviga vittnen','flow','Both spouses signatures and two impartial witnesses attest the document; the source number is preserved.'),
    ('register','contract|äktenskapsförordet;registry|Myndigheten för digitalisering och befolkningsdata','notify','Registration of the agreement with the stated authority is required for effect; institution is schematic, not an actual logo.'),
    ('usualhalf','split|skilsmässa;house|egendomen;scales|jämnt','flow','The usual equal property division at divorce is pictured without hiding the following exceptions.'),
    ('exceptionunequal','house|egendomen;unequal_scales|inte jämnt','none','Unbalanced division is marked as the source exception using separate property groups, without quantifying shares.'),
    ('divisionadjust','house|bodelningen;scales|jämkas','flow','Property division is subject to possible adjustment in the stated exception.'),
    ('reasonable','scales|rimligt','none','Fairness scales illustrate the source assessment of what is reasonable; no formula or guaranteed result.'),
    ('underfive','calendar|under fem år;house|egendomen;balance_options|inte nödvändigtvis jämnt','none','A marriage shorter than five years is the source example for potentially unequal division, not an automatic rule.'),
    ('request','person|någon av makarna;notice|separat kräver;scales|jämkas','notify','A spouse separately requests adjustment; scales follow the request, without guaranteeing success.')
]
assert len(plans)==len(rows),(len(plans),len(rows));result=[]
for row,(name,nodes,relation,reason) in zip(rows,plans):
    objects=[x.split('|',1) for x in nodes.split(';')]
    for node in objects:
        if node[1] not in row['sv']:
            m=re.search(re.escape(node[1]),row['sv'],re.I);assert m,(row['sentence_id'],node[1]);node[1]=m.group()
    result.append(dict(id=name,objects=objects,relation=relation,reason=reason))
(ep/'visual-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
