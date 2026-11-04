"""Source-read advisory art direction; never modify C10 producer workspaces."""
from pathlib import Path
import hashlib
import json

import yaml

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def save(section,lines,photos=None,conditions=None):
    path=ROOT/'studio/episodes'/section/'script.yaml'
    script=yaml.safe_load(path.read_text())
    specs=[line.strip().split(' | ') for line in lines.strip().splitlines() if line.strip()]
    assert len(specs)==len(script['sentences']),(section,len(specs),len(script['sentences']))
    plans=[]
    for index,(spec,row) in enumerate(zip(specs,script['sentences']),1):
        composition,*fields,logic=spec
        nodes=[]
        for field in fields:
            label,icon=field.rsplit(':',1)
            at=row['sv'].casefold().find(label.casefold())
            assert at>=0,(section,index,label)
            nodes.append(dict(label=row['sv'][at:at+len(label)],icon=icon))
        plan=dict(id=f'picture-{index:03d}',source_sentence_ids=[row['sentence_id']],
                  visual_type='diagram',composition=composition,nodes=nodes,
                  description=logic,required_logic=logic)
        if conditions and index in conditions:
            label,indices=conditions[index];at=row['sv'].casefold().find(label.casefold());assert at>=0
            plan['conditions']=[dict(label=row['sv'][at:at+len(label)],node_indices=indices)]
        if photos and index in photos:
            plan['photo_request']=dict(subject=photos[index],acquisition_status='Advisory only; producer verifies identity,licence,credit and actual relevance before use.',fallback='An accurate source-specific original picture; never a generic renamed icon card.')
        assert 1<=len(nodes)<=3
        plans.append(plan)
    HERE.mkdir(exist_ok=True,parents=True)
    (HERE/(section+'.json')).write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
    handoff=dict(section_id=section,source_script_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                 source_section_sha256=script['source_section_sha256'],translation_file_sha256=script['translation_file_sha256'],
                 pairs_read=len(plans),labels_conditions='Every label checked as exact referenced Swedish source substring; all Swedish/Russian pairs read.',
                 ownership='Advisory only. Producer C10 retains exclusive script,media and job ownership and adapts preferred objects to its renderer.',
                 limits='No acquired photos,rendered art,timing,pronunciation or final export approval in this advice. Exact archived text and source order retained,including repeated content and list fragments.')
    (HERE/(section+'-handoff.json')).write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
    print(section,len(plans),'source-specific advisories validated')


PENSION='''
timeline | pensionsåldern:calendar | ålderspension:person | Possible old-age pension at pension age; does not mean automatic payment,which source13 explicitly excludes.
flow | när du är född:calendar | Åldersgränsen:person | Birth year determines the age limit; no universal age or invented table.
timeline | född 1964:calendar | 65 år:person | Keep both source example values together; never present65as everyone's retirement age.
split | Pensioner:coins | arbetspensionsanstalter:bank | FPA:document | Two named paying-institution categories; no assumption all pensions come from both.
flow | Arbetspensionsanstalterna:bank | arbetspension:coins | Earnings-related institution pays earnings-related pension.
merge | lönen:coins | andra arbetsinkomster:work | Den:bank | The pronoun refers to earnings-related pension; two stated earnings bases,no rate invented.
flow | arbetspensionen är liten:coins | pension från FPA:bank | Small earnings-related pension may permit FPA pension,not automatic approval.
pair | arbeta:work | pensionerad:person | Optional work while retired; avoid implying a duty to work.
contrast | arbetsinkomst:work | pensionens storlek:coins | In old-age pension context work income does not change pension size; do not extend this to disability pension.
timeline | ny pension:coins | högsta pensionsåldern:calendar | New pension earned from work is paid at the upper accrual age; preserve distinction from existing pension.
timeline | inte längre tjänar in ny pension:bank | fortsätter arbeta:work | Upper age stops new accrual even if work continues; not loss of pension already earned.
branch | räknare:laptop | Pensionsskyddscentralens:bank | arbetspensionsanstaltens:document | Calculator alternatives for personal lower/upper ages; no invented calculator interface or result.
flow | själv ansöka:document | arbetspensionsanstalt:bank | Application is the person's responsibility; payments do not start automatically.
pair | skatt:document | pensionerna:coins | Pensions are taxed; do not invent a tax rate or net amount.
flow | din lön:coins | arbetspensionsavgifter:bank | Pension contributions paid from wages; no fictional deduction percentage.
merge | högre lön:coins | längre du arbetar:calendar | större blir din arbetspension:bank | Qualitative earnings-plus-working-time relation,without a fabricated growth chart or amount.
group | Arbetspensionsförsäkringsbolag:bank | pensionskassor:document | stiftelser:shield | Three source pension-insurance institution types; no named private provider recommendation.
object | Pensionsskyddscentralen:bank | Centralized pension-security administration; actual institution photograph preferable if correctly identified.
pair | själv följa upp:person | arbetspensionsutdrag:document | Check that all own earned income appears; schematic document only,no fabricated personal record.
flow | uppgifterna är fel:document | kontakta din pensionsanstalt:phone | If record data is wrong,contact pension institution; no invented dispute deadline.
branch | inte har någon arbetspension:coins | väldigt liten:bank | ansöka om folkpension:document | No earnings-related pension OR very small pension permits applying,not guaranteed payment.
timeline | bott eller arbetat:house | Folkpensionens belopp:coins | Duration of Finnish residence/work affects national-pension amount; no proportional formula invented.
merge | familjeförhållanden:family | andra kontinuerliga pensionsinkomster:coins | folkpensionens belopp:bank | Both stated factors affect amount; no marriage-based entitlement shortcut.
split | FPA:bank | folkpensionerna:document | garantipensionerna:shield | FPA administers two distinct pension categories.
merge | Finländska socialskyddet:shield | minst tre år efter att du fyllde 16 år:calendar | söka folkpension och garantipension:document | Cumulative social-security coverage AND stated residence history for APPLYING; preserve after16,min3years and source wording,not current advice.
pair | annat EU- eller EES-land:globe | delvis beaktas:calendar | Other EU/EEA residence may count partly; do not equate EU membership with all EEA states or full automatic credit.
protect | Garantipensionen:shield | existensminimum:coins | Guarantee pension safeguards minimum subsistence; no euro amount or guaranteed individual award invented.
contrast | övriga pensionerna:coins | garantipensionens fulla belopp:bank | Show the stated difference concept on the same basis; no invented euro example or reversed subtraction label.
blocked_flow | övriga pensioner:coins | garantipension:shield | Other pensions above full guarantee-pension amount exclude guarantee pension; preserve threshold comparison without invented amount.
protect | Pensionsförsäkringen för företagare:shield | sjukpension eller ålderspension:person | företagsverksamheten upphör:shop | FöPL security for disability/old-age pension AND business ending; do not imply any voluntary business closure automatically awards benefits.
flow | företagaren avlider:person | Anhöriga:family | familjepension:coins | Relatives MAY receive survivor pension after entrepreneur dies; no graphic death depiction or invented inheritance share.
split | FöPL:shield | arbetspensionen:bank | FPA:s stöd:coins | FöPL affects pension and support amounts; source examples are sickness,unemployment,parental allowances,not eligibility guarantees.
branch | arbetspension är liten:coins | folkpension:bank | garantipension:shield | Small earnings-related pension may be supplemented by either named FPA category; no automatic stacking of all full amounts.
branch | mer information:phone | FPA:bank | arbetspensionsanstalten:document | Two source advice destinations,not a new form or website.
pair | inte har ett socialskyddsavtal:document | själv ta reda:globe | For work in nonagreement countries,the individual checks possible pension rights; not a universal exclusion.
flow | kan få pension:coins | själv ansöka:document | A possible pension still requires applying personally; application is not payment approval.
branch | meddela FPA:phone | varaktig flytt utomlands:globe | över tre månader:calendar | Notify permanent move OR stay longer than3months; do not confuse notification threshold with pension-payment duration rule.
timeline | under ett år:calendar | vanligtvis din pension som vanligt:coins | Temporary foreign stay below1year usually retains FPA payment; retain usually,not a universal guarantee.
blocked_flow | över ett år:calendar | FPA:s ålderspension eller invalidpension:bank | Move abroad above1year usually prevents these FPA pensions; do not extend to all earnings-related pensions or remove source exceptions41.
blocked_flow | garantipension:shield | utlandet:globe | Source says guarantee pension not paid abroad; retain exact archived statement without adding a current-law claim.
flow | socialskyddsavtal:document | betala pension:coins | In some cases FPA pays to social-security-agreement countries; exception to prior general rule,not all agreement-country residents qualifying.
group | USA:globe | Kanada:house | Australien:ship | Three named examples from full five-country source list; representative objects/maps must not invent a route or imply exhaustive list.
timeline | 61 eller 62 år:person | före din lägsta ålderspensionsålder:calendar | Source alternative age limits depend on birth year44; never show all61yearolds as entitled.
flow | vilket år du är född:calendar | Åldersgränsen:person | Birth year determines partial-pension age limit; no invented birth-cohort table.
object | partiell förtida ålderspension:bank | Name the preceding partial early old-age pension; distinct from partial national pension69 and disability pension53.
branch | välja:person | 25 procent:coins | 50 procent:bank | Optional quarter OR half of MONTHLY EARNINGS-RELATED pension,same basis; correct quarter/half schematic,no personal income amounts.
branch | fortsätta arbeta:work | heltid:calendar | kortare arbetstid:document | May work full time OR agree shorter hours with employer; shorter work is by agreement,not unilateral entitlement.
object | sluta arbeta:work | May also stop working; no duty to retire or benefit increase promised.
warning | partiella förtida ålderspensionen:calendar | permanent minskar:coins | Early partial pension permanently reduces final old-age amount; do not depict a reversible pause or invent reduction rate.
flow | fråga mer:phone | pensionsanstalt:bank | Ask pension institution for more information; no invented advice script.
timeline | sjukdagpenning:medicine | ungefär ett år:calendar | Long illness usually first leads to sickness allowance for approximately1year; keep usual/approximate qualifiers.
branch | inte kan återgå till arbetet:work | sjukpension:bank | rehabiliteringsstöd:shield | Illness OR injury prevents return,then may APPLY for disability pension OR rehabilitation support; not automatic payment.
protect | arbetsförmåga är nedsatt:person | arbeta på deltid:work | partiella sjukpensionen:coins | Reduced ability together with remaining part-time ability; preserve both conditions without diagnosing a pictured person.
contrast | partiella sjukpensionen:coins | hälften av sjukpensionen:bank | Correct half-of-disability-pension relationship; no euros or half-of-total-income substitution.
branch | hur mycket du får tjäna:coins | FPA:bank | arbetspensionsanstalt:document | Work or business while on disability pension requires asking allowed earnings; do not invent an earnings ceiling.
flow | tillräckligt hög inkomst:coins | pension vila:calendar | Sufficient monthly earnings may permit suspending pension; do not depict a known numerical threshold.
object | paus i lyftandet av pensionen:calendar | Pause drawing payment,not permanent cancellation of right.
timeline | minst tre månader:calendar | högst två år:document | Pension-payment pause bounds3months to2years; separate from foreign-stay notification3months and travel65rules.
protect | inte rätten:shield | sjukpension:bank | Right to disability pension retained during this pause; no automatic payment throughout pause.
flow | pensionstagare med låga inkomster:person | bostadsbidrag:house | FPA may additionally pay low-income pensioner housing allowance,not every pensioner.
branch | långtidssjuka:medicine | handikappade:person | vårdbidrag för pensionstagare:shield | Long-term illness OR disability may permit pensioner care allowance; no diagnosis or automatic approval.
pair | Fråga mer:phone | FPA:bank | Short source continuation requesting more information atFPA; preserve in order.
group | tåg:train | buss:bus | flygresor:plane | Possible pensioner discounts on these Finnish journeys; no fares,percentages or universal ticket promise.
flow | fyllt 65 år:person | identitetsbevis:document | Source age65plus identity document for travel discount; do not merge with birth-cohort pension-age rules.
merge | inte har fyllt 65 år:person | personbevis:document | arbetspensionskort eller folkpensionärskort:bank | Under65pensioner MAY get discount by source personal certificate AND one of two pension cards; preserve innerOR/outerAND.
flow | Kontrollera villkoren:document | biljettkontoren:shop | Check specific discount terms at ticket offices; no current carrier policy invented.
group | motion:ball | kultur:book_pages | Possible activity/culture discounts,not blanket free admission or invented price.
group | arbetspension:bank | folkpension:person | garantipension:shield | Three pension-system components; no assumption one person receives all three full amounts.
merge | arbetspension:work | partiell folkpension:coins | persons pension:person | Source example combining earnings pension with PARTIAL NATIONAL pension; explicitly different from partial early old-age pension45.
object | Största delen:coins | arbetspensioner:bank | Qualitative majority only; no invented pie-chart percentage.
flow | pensionsförsäkringsavgifter:document | sin lön:coins | Arbetspensionens belopp:bank | Amount based on paid pension-insurance contributions; no fabricated formula or wage rate.
merge | arbetstagaren:person | arbetsgivaren:shop | försäkringsavgifterna:coins | Both employee and employer pay shares; no invented percentages or equal-share assertion.
merge | lönens nivå:coins | antalet arbetsår:calendar | Pensionens belopp:bank | Stated example determinants affect amount; no extrapolated numeric growth chart.
flow | arbetspensionsanstalt:bank | Arbetspensionen:coins | Institutional payer,not FPA for earnings pension.
flow | företagare:shop | själva:person | pensionsförsäkringsavgifter:coins | Entrepreneurs may receive earnings pension but pay own contributions; no invented premium rate.
flow | inte längre kan arbeta:work | invalidpension:shield | Illness/injury prevents working; possible pension through earnings institution,not automatic solely from diagnosis.
timeline | redan före:calendar | officiella pensionsåldern:person | This disability pension may precede official pension age; do not imply it is the optional early old-age pension.
branch | Invalidpensionen:shield | full:coins | partiell:bank | Full OR partial disability pension as alternative levels; no invented percentages here.
pair | Partiell invalidpension:shield | arbetar deltid:work | Partial disability-pension context with part-time work; no arbitrary maximum hours.
merge | lön:work | pension:coins | inkomster:bank | Income combines wage and pension; no invented proportions.
group | alla de länder:globe | bott och arbetat:house | Possible accrual across places of residence/work; source broad statement,not a new international agreement claim.
flow | arbeta:work | pension:bank | General work-based accrual; keep inallmänhet,not absolute exclusion of other accrual.
pair | samma blankett:document | Finland:flag_fi | Some countries allow application with same Finnish form; not all countries or automatic foreign application.
flow | söks:document | direkt hos pensionsanstalterna:bank | Other countries require direct application; no named country invented.
flow | pensioner från utlandet:globe | skattedeklarationen:document | Foreign pensions must also be declared for tax; no tax rate or double-tax treaty advice.
flow | flyttar utomlands:globe | anmäla det till FPA:phone | Pensioner must always notify FPA of foreign move; no payment eligibility inferred from notification.
flow | Finska pensioner:bank | utlandet:globe | May be received abroad under certain conditions; do not erase earlier FPA/guarantee restrictions.
pair | i förväg:calendar | villkoren uppfylls:document | Check conditions before moving; no approval badge or invented eligibility decision.
flow | pension i Finland:bank | annat land:globe | In some cases may apply for Finnish pension while retiring elsewhere; application is not guaranteed award.
pair | pensionerad:person | arbeta:work | Optional work after pension; source recap,not obligation.
flow | Arbete:work | ökar arbetspensionens belopp:coins | Pensioner work raises earnings-related pension amount in source; no euro increase invented.
branch | pensionär:person | deltid:calendar | heltid:work | Part-time OR full-time options; no fixed hours attached.
protect | invalidpension:shield | begränsad utsträckning:work | Disability-pension work is limited; do not apply unlimited old-age-pension work rule here.
flow | arbetsinkomsterna överskrider:coins | invalidpensionen avbrytas:calendar | Income above an unspecified ceiling MAY suspend disability-pension payment; not guaranteed loss of entitlement or permanent cancellation.
'''


OLDER='''
branch | lever:house | själva:person | sin make:parties | Older residents often live alone OR with spouse; source descriptive often,not everybody's living arrangement.
timeline | folkpensionslagen:document | år 1957:calendar | Historical law entering into force1957 enabled independence; keep historical date,not a new current eligibility rule.
protect | alla äldre:people | pension:coins | Historical national-pension law included people who had not worked; source chronology matters,not universal present-day eligibility.
group | tidigare:calendar | familj:family | flera generationer:people | Earlier multigenerational household context; do not imply all families followed this arrangement.
pair | familjen:family | varandra:people | Family/relatives cared for one another; reciprocal assistance rather than one gender assigned all care.
flow | inte hade någon familj:person | kommunalhem:house | Historical municipal home when no family; not a current admission rule or detention implication.
object | inrättning:house | anspråkslösa:chair | Historical modest conditions; never use a modern care-home photograph as proof of poor conditions.
merge | kvinnorna började arbeta:work | familjerna blev mindre:family | svårare att ta hand om de äldre hemma:house | Two stated historical changes made home care harder; no blame or new claim about women's duty to care.
flow | höjdes levnadsstandarden:coins | självständigt liv:person | Rising living standards enabled independent living; qualitative,no invented historical income chart.
protect | blir äldre:person | sin hälsa:shield | Continue caring for health while ageing; no specific treatment or disease diagnosis invented.
group | hälsan:medicine | välbefinnandet:flower | funktionsförmågan:person | Three source aspects of maintaining wellbeing/capability; not a diagnostic score.
flow | Åldrandet:calendar | kropp:person | Ageing brings body changes; no invented universal disability or appearance stereotype.
pair | röra sig:person | mindre krafter:shield | Mobility/strength MAY become harder/lower; retain uncertainty rather than all older people shown incapable.
object | problem med minnet:brain | Possible memory difficulty; brain object not a diagnostic scan or assertion all older people have dementia.
flow | Olika sjukdomar:medicine | funktionsförmåga:person | Diseases MAY change body/capability; no specific treatment,prognosis or universal decline.
group | minnessjukdomar:brain | hjärtsjukdomar:heart | lungsjukdomar:lungs | Three representative named disease categories from full source list; no pictured person assigned any diagnosis.
timeline | levnadsvanor:calendar | hela livet:person | Lifelong habits can influence health/wellbeing; no guarantee of preventing all illnesses.
merge | träffar andra människor:people | är aktiv:ball | funktionsförmåga:person | Social contact AND activity linked to maintained capability in source; no medical guarantee or invented exercise dose.
group | äta mångsidigt:food | motionera:ball | låta blir att röka:cigarette | Representative source habits; smoking object crossed out,not encouragement. Main panel retains all alcohol/weight qualifiers and archived typo låta blir.
split | god funktionsförmåga:person | ta hand om sig själv:shield | sitt hem:house | Everyday self-care andhome-care outcomes,not compulsory independent living despite support needs.
flow | kriser, förändringar och förluster:calendar | humör:person | Life changes affect mood; do not show a real bereaved person or infer a diagnosis.
protect | bra vardag:house | god psykisk hälsa:brain | Everyday wellbeing supports mental health; not a substitute for clinical care or a treatment promise.
pair | ofta minnet sämre:brain | glömmer saker:document | Source often/forgetfulness statement; not universal dementia,retain ofta.
object | njuta av sitt liv:flower | alla åldrar:people | Joy across all ages; no infantilization or invented hobby requirement.
merge | aktivt liv:ball | träffa andra människor:people | glädje i vardagen:flower | Two named positive activities; no guaranteed cure of mood disorder.
flow | Kommunerna:bank | fritidsverksamhet för äldre:ball | Municipalities organize leisure,distinct from wellbeing counties arranging care31.
group | föreningar:people | organisationer:parties | församlingar:church | Three stated activity/club organizers; no invented local timetable,address or faith requirement.
flow | frivilligarbete:person | påverka samhället:people | Many older people volunteer by choice; not compulsory unpaid labour or condition for pension.
pair | Frivilligarbete:people | glädje:flower | Source says volunteering gives joy to volunteer; no income or health guarantee inferred.
branch | hjälpa:shield | barnfamiljer:family | ensamma människor:person | Two source examples of volunteering; no pictured family/person assigned vulnerability or service need.
flow | Välfärdsområdena:bank | tjänsterna för äldre:person | Wellbeing counties responsible for older people's services; keep distinct from municipal leisure26.
split | välfärdsområdet:bank | boendeservice:house | social- och hälsovårdstjänster:hospital | Two broad service categories; no entitlement to every intervention inferred.
flow | behöver tjänster:person | bedömning av vårdbehovet:document | Need for services triggers authority assessment; no automatic placement or age-only threshold.
pair | bedöms:document | personen behöver:person | Assessment identifies individual service need; no fictional scoring form.
flow | individuella behovet:person | beviljar tjänster:document | Services based on individual need; avoid a generic age-based approval stamp.
object | Hemmet:house | viktig plats:person | Home matters to everyone; physical domestic scene preferable,without private resident data.
branch | eget hem:house | själva:person | sin make:parties | Older residents mostly at home alone OR with spouse; source often context not compulsory family status.
protect | vill:person | bo hemma:house | Many people prefer home in old age; preference not entitlement to every requested service or refusal of institutional care.
pair | bo ensam:person | utmanande:house | Living alone can be challenging; not all solo residents incapable or lonely.
group | röra sig:cane | sämre syn eller hörsel:glasses | komma ihåg saker:brain | Representative mobility,sensory,memory difficulties MAY occur; no universal age diagnosis.
flow | Ändringar:gear | enklare att bo hemma:house | Home/surroundings adaptations can help; no unapproved structural advice or construction instructions.
contrast | dörrar breddas:door_wide | strösklar avlägsnas:door | Two source adaptation examples,not building code dimensions or unsafe do-it-yourself steps; preserve archived strösklar wording.
protect | trygg:shield | sitt hem:house | Feeling safe at home matters; no commercial alarm recommendation.
branch | Välfärdsområdet:bank | hemvård:house | hemsjukvård:medicine | County MAY arrange home care OR home nursing; not identical services or automatic award.
pair | hemservicen:person | på egen hand:house | Staff assist with things no longer manageable independently; respectful support,not total incapacity.
group | äta:food | duscha:water | klä på sig:shirt | Representative source daily tasks; no intimate care imagery or technique instructions. Main text also retains toilet assistance.
flow | behöver hemsjukvård:house | sjukskötare:person | Needed home nursing may result in a nurse visit,not a guaranteed schedule orcare entitlement from age alone.
flow | Hemsjukvård:medicine | egna hälsostationen:hospital | Apply for home nursing through own health station; no invented address or telephone number.
merge | välfärdsområdena:bank | privata företag:shop | hemservice och hemsjukvård:house | Both public county and private-company providers; no claim private care is free.
flow | servicesedlar:document | köpa vårdtjänster av företag:shop | County MAY issue service vouchers to buy company care; no euro value,universal award ornew voucher-design invented.
contrast | servicesedel:document | välfärdsområdet erbjuder:bank | Voucher-purchased service is an alternative,not an automatic cash payment or mandatory private purchase.
flow | måltidsservice:food | Boende hemma:house | Meal delivery can support staying home; no dietary prescription or guaranteed individual service.
flow | färdiga måltider:food | varje dag eller några gånger i veckan:calendar | Prepared meals delivered daily OR several times weekly; do not pick a fixed invented schedule.
protect | svårt att klara vardagen:person | Trygghetsservice:phone | Safety service/device intended for difficulty with daily life OR illness; not a diagnosis or ordinary smartphone substitute.
object | trygghetsarmband:bracelet | Source example of a personal safety bracelet; actual identifiable device object preferable,not smartwatch health claim.
flow | knappen på armbandet:bracelet | larmcentralen:phone | Pressing button contacts monitoring centre aroundtheclock; do NOT label it112or promise automatic ambulance dispatch.
pair | familj:family | hemma:house | Family sometimes chooses home caregiving; not compulsory duty of every relative.
split | en av familjemedlemmarna:person | hand om den äldre:house | stöd för närståendevård:coins | One family member cares andcounty pays support to CAREGIVER,not necessarily to older person or every relative.
merge | hjälp hela tiden:person | bindande och krävande:calendar | Stöd för närståendevård:coins | Both continual help AND binding/demanding care conditions; can receive,not automatic approval fromone condition alone.
pair | Närståendevårdaren:person | lediga dagar:calendar | Caregiver also has right to days off; no number of days invented.
flow | dagcenter:house | dagverksamhet för äldre:people | County day-centre activities; no invented timetable or eligibility age.
split | Verksamheten:people | klara sig hemma:house | närståendevårdaren att orka:person | Activities support both resident at home AND caregiver stamina,not replacement of all home care.
group | tillbringa tid:clock | dagcentret:house | träffa andra människor:people | Social time at daycentre,not residential admission or compelled attendance.
group | motions:ball | rekreations:flower | teaterföreställningar:theater | Representative stated leisure/culture options; no prescribed exercise intensity or universal free theatre tickets.
split | Välfärdsområdet:bank | transporten:bus | en måltid:food | County arranges transport andusually meal; qualify meal with vanligtvis,not all meals or free transport.
pair | färdtjänsten:bus | separat avgift:coins | Separate transport fee MAY be charged; no amount or blanket free transport claim.
branch | inte längre kan bo hemma:house | servicehus:people | inrättning:hospital | When home no longer possible,county arranges servicehouse OR institution; preserve distinction and no age-only placement rule.
flow | privata företag:shop | serviceboende:house | Private firms also organize service housing; no endorsement or automatic public funding.
protect | tryggt:shield | meningsfullt liv:flower | Aim is safe,meaningful life in service housing; no invented clinical outcome guarantee.
flow | Den äldre:person | själv:coins | Usually pays service housing personally; no price or assertion all residents pay full cost.
pair | hjälp och omsorg:shield | dygnet runt:clock | Servicehouse residence when roundtheclock help/care needed; not every minor assistance need.
group | servicehus:house | alltid personal:people | Staff always present in source service-house description; no invented staffing ratio or response time.
split | Alla boende:people | egen bostad eller ett eget rum:house | gemensamma utrymmen:chair | Own dwelling OR room andshared spaces; do not depict everybody owning the property or compelled room-sharing.
object | egna saker:chair | sin bostad:house | Resident may furnish/decorate with own belongings; physical furniture object preferable to a generic labelled icon.
flow | inte längre kan bo hemma eller på ett servicehus:house | institutionsvård:hospital | Institution when neither home NOR servicehouse works; preserve source stored order u0273beforeu0268,do not sort IDs.
protect | kontinuerligt krävande vård:medicine | säkert sätt:shield | Continuous demanding care cannot safely be arranged elsewhere; not any illness or age alone leading to institution.
group | sjukdom:medicine | många vårdare:people | varje dag:calendar | Source example of intensive daily care needs; no specific disease diagnosis,staffing ratio or treatment invented.
flow | familjen vill:family | delta i vården:people | Family may participate if it wishes; no obligation or transfer of staff responsibilities.
split | institutionsvården:hospital | funktionsförmåga:person | livskvalitet och mående:flower | Aims maintain capability andimprove qualityoflife/wellbeing,not cure guarantee.
flow | hälsostationerna:hospital | låna olika hjälpmedel:cane | Loan aids through health stations; no claim all aids arefree/permanent possessions.
branch | låna:document | promenadkäpp:cane | rollator:rollator | Cane OR rollator loan examples; actual objects or correct custom drawings,no wheelchair substituted for rollator.
object | rollator:rollator | stödja sig på när man går:person | Rollator supports walking; depict correct walking frame with wheels,not a chair or transport wheelchair.
flow | tjänster:shield | bo hemma:house | Available support may ease everyday life andhome living; not every service automatically awarded.
flow | hemkommun i Finland:house | tjänsterna för äldre:person | Finnish municipality-of-residence condition for county services; individual need assessment still in source33–35.
merge | hälsotillstånd är dåligt:medicine | behöver hjälp:person | ansöka om hemvård:document | Poor health AND need daily help permit applying at area's social services; application not automatic award.
group | hemtjänster:house | hemsjukvård:medicine | stödtjänster:shield | Home care includes three stated categories; no new service category or universal package promised.
'''


if __name__=='__main__':
    save('hb-c10-pension',PENSION,
         photos={4:'Verified FPA or pension institution exterior; identify actual institution,not an unknown bank.',
                 8:'Neutral ordinary work setting or object; do not label a real worker as retired.',
                 12:'A neutral calculator object,not an invented official calculator result.',
                 18:'Actual Pensionsskyddscentralen/Eläketurvakeskus premises if licensed and identified.',
                 19:'Blank statement/document object with no private wage/pension data.',
                 34:'Different correctly identified actual FPA/pension-service building fromsource4.',
                 37:'Neutral airport luggage/object context; no pictured person assigned emigrant or pensioner status.',
                 42:'A neutral source-named country setting,clearly contextual,not a benefits agreement map.',
                 63:'Actual Finnish train/bus/aircraft object; no unsupported claim this carrier currently gives a discount.',
                 66:'Actual public ticket-counter object without private customer details.',
                 67:'A source-relevant exercise/culture object or venue,no person labelled a pensioner.',
                 85:'Blank tax-form object,clearly generic andwithout private data.',
                 90:'A distinct neutral work tool or workplace object,no inferred benefit status.'},
         conditions={7:('kan du också få',[1]),9:('Om du får ålderspension',[0,1]),
                     16:('Ju högre',[0]),21:('kan ansöka',[2]),25:('kan söka',[2]),
                     26:('kan delvis beaktas',[0,1]),29:('överskrider',[0]),31:('kan få',[1,2]),
                     33:('kan',[0,1,2]),35:('inte har ett socialskyddsavtal',[0,1]),
                     38:('vanligtvis',[1]),39:('vanligtvis inte',[1]),41:('I vissa fall',[0,1]),
                     43:('kan du få',[0,1]),47:('Om du vill',[0,1,2]),
                     49:('permanent',[0,1]),51:('vanligtvis först',[0]),52:('kan du ansöka',[0,1,2]),
                     55:('samtidigt som du får sjukpension',[0,1,2]),56:('kan',[1]),
                     60:('kan FPA',[0,1]),61:('kan FPA',[0,1,2]),65:('kan få rabatt',[0,1,2]),
                     69:('till exempel',[0,1,2]),76:('kan hen få',[1]),82:('I allmänhet',[0,1]),
                     83:('I en del länder',[0,1]),87:('vissa villkor',[0,1]),89:('i vissa fall',[0,1]),
                     94:('kan',[1])})
    save('hb-c10-aldre',OLDER,
         photos={1:'An ordinary documented Finnish home scene,no real person assigned dependency orbenefit status.',
                 4:'Verified historical multi-generation domestic photograph if period/place/attribution are sound; otherwise original diagram.',
                 6:'Verified historical municipal carehome archival photograph,clearly dated; never a modern institution as proof ofhistoric poor conditions.',
                 10:'Neutral health-maintenance object or nonidentifying activity context,no patient diagnosis inferred.',
                 14:'A neutral memory notebook/reminder object; no real person labelled as having memory disease.',
                 19:'Actual varied food or exercise object,no prescribed quantities ormedical dietary claims.',
                 24:'A leisure/nature/culture object illustrating joy,without presumed emotional orhealth status ofa photographed person.',
                 26:'A correctly identified municipal activity venue; no current programme/schedule claim.',
                 27:'A correctly identified association/church activity setting; no religion requirement inferred.',
                 28:'Documented volunteer equipment/activity context without attributing benefit status to volunteers.',
                 36:'A distinct actual domestic interior/object scene without private resident details.',
                 40:'An actual cane,glasses or hearing aid object; do not diagnose an individual.',
                 42:'Actual accessible widened doorway/level threshold,not architectural dimensions orDIYinstructions.',
                 46:'An ordinary meal,shower or clothing object; no intimate care imagery.',
                 48:'A distinct correctly identified Finnish public healthstation exterior.',
                 52:'Actual packaged prepared-meal/delivery object; no implication a specific company provides the statutory service.',
                 55:'Actual personal-alarm bracelet identified by source; no smartwatch ormedical-measurement claim.',
                 60:'Rest/leisure object for caregiver days off; no invented day count.',
                 64:'A real theatre or leisure-activity venue/object; no free ticket orlive schedule claim.',
                 65:'Actual accessible transport vehicle object; do not infer free fare.',
                 67:'A correctly identified actual servicehouse exterior; distinguish residential servicehouse from hospital institution.',
                 74:'Domestic furniture belongings; no identified resident ownership ormedical status.',
                 80:'Actual mobility aid loan equipment orhealthstation object,no unsupported loanterms.',
                 81:'Actual cane and/orrollator object,preferably clearly showing distinction.',
                 82:'A clearly identified rollator photo; no wheelchair orchair substitution.'},
         conditions={1:('ofta',[0,1,2]),3:('garanterade',[0,1]),4:('tidigare',[0,1,2]),
                     6:('Om en äldre inte hade någon familj',[0,1]),13:('kan',[0,1]),14:('kan',[0]),
                     15:('kan',[0,1]),16:('till exempel',[0,1,2]),18:('och',[0,1]),
                     23:('ofta',[0,1]),30:('till exempel',[1,2]),35:('individuella behovet',[0,1]),
                     37:('för det mesta',[0,1,2]),39:('kan',[0,1]),40:('kan till exempel',[0,1,2]),
                     44:('kan ordna',[0,1,2]),47:('Om den äldre behöver hemsjukvård',[0,1]),
                     50:('kan ge',[0,1]),54:('har svårt att klara vardagen',[0,1]),
                     57:('Ibland vill',[0,1]),59:('kan fås',[2]),65:('vanligtvis',[2]),
                     66:('kan tas ut',[1]),70:('i allmänhet',[0,1]),71:('dygnet runt',[0,1]),
                     75:('inte längre kan bo hemma eller på ett servicehus',[0,1]),
                     77:('till exempel',[0,1,2]),78:('Om familjen vill',[0,1]),
                     84:('Om du har hemkommun i Finland',[0,1]),85:('kan du ansöka',[2])})
