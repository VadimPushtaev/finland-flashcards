"""Direct the full exact-source 112/preparedness section with qualified picture intent."""
from pathlib import Path
import json,yaml
from plan_nature import plan
R=Path(__file__).resolve().parents[3];SID='hb-c11-nodsituationer'
ROWS=[
('Nödnumret 112','diagram','A physical telephone and the exact source112digits,not a simulated live call or an invented contact number.'),
('Bara akut nödsituation','diagram','Explicit ONLY acute-emergency gate before calling112; no invented symptom score,time limit or triage rule.'),
('Liv, hälsa, egendom och omgivning','diagram','Four distinct source danger categories shown through person/heart,home/property and natural-environment objects. No real victim or fabricated incident.'),
('Hjälp via nödnumret','photograph','Verified actual Finnish police/fire/ambulance vehicle photos as source examples,with social authority represented accurately; no claim a particular vehicle is dispatched to an invented incident.'),
('Nödcentralen bedömer','diagram','Caller reaches emergency centre,which decides WHETHER help is needed AND WHICH authority; no automatic-all-services dispatch promise.'),
('Samtalet är gratis','photograph','A real ordinary telephone object with a clear source no-charge cue; no tariff amount,brand recommendation or active number beyond112.'),
('Anvisningar för samtalet','diagram','Source call checklist with phone,speech,address and listening symbols; do not add first-aid steps or a new call script.'),
('Berätta vad som hänt','diagram','Caller and operator connected by a speech bubble indicating the actual-event description; no invented example emergency,patient or address.'),
('Svara på frågorna','diagram','Distinct two-way question/answer bubbles between caller and operator,without fictional answers or extra identification demands.'),
('Exakt adress och kommun','photograph','Actual Finnish public street-name/address sign,accurately identified; exact main wording still requires BOTH address AND municipality/city. No claimed incident at the photographed place.'),
('Följ anvisningarna','diagram','Operator guidance followed by caller; unnumbered check mark,not a new medical procedure or fabricated emergency instruction.'),
('Avsluta först när du får lov','diagram','Explicit permission-before-ending-call gate. No fake phone UI or suggestion that silence automatically means permission.'),
('Varifrån du ringer','diagram','Caller-location address field and building/location marker; preserve this source wording separately from earlier help-needed address wording. No invented apartment number.'),
('Hjälpen till rätt ställe','diagram','Retain the preceding meaningful location picture across this direct continuation; location allows help to reach the right place,without promising a named vehicle.'),
('Vilken bostad i höghuset','diagram','Anonymous apartment building with several unlabelled units and question marker: technical call tracing does NOT tell the operator the particular apartment. No invented unit/address.'),
('Berätta själv','diagram','Retain the apartment-specific location explanation across this direct source continuation; caller supplies the missing unit information.'),
('Tolk vid behov','diagram','Caller,operator and interpreter in one connected conversation,with explicit IF NEEDED qualification; no universal immediate-language availability guarantee.'),
('Säg språk i början','diagram','IF interpreter needed,tell the desired language clearly at the beginning; source timing is qualitative,no invented seconds or extra languages.'),
('Stanna i samtalet','diagram','Retain the relevant interpreter-connection picture across this direct continuation,showing the call remains connected while translation is arranged.'),
('Inte ringa i onödan','diagram','Non-emergency question is separated from the112acute-emergency route; no accusation against a real photographed caller.'),
('Ring inte vid följande fall','diagram','Pictorial introduction limited to the following source non-emergency examples; preserve the conditions and ordinary-case scope.'),
('Vanlig sjukdom, till exempel influensa','diagram','Ordinary/non-emergency illness example,without implying all influenza is harmless or adding a fever threshold/clinical assessment.'),
('Hälsovårdscentralen som exempel','photograph','Verified Finnish health centre exterior as one alternative in the source ordinary-illness context; no fabricated phone number,current opening hours or individual appointment guarantee.'),
('Allmänna frågor','diagram','Three actual source subject categories—healthcare,traffic,fire safety—shown as general information queries,not active emergencies.'),
('Inget nödfall','diagram','General question and non-emergency scope remain explicit; the112route is blocked only for that source case.'),
('Elavbrott eller kö utan fara','photograph','Actual power-outage object or traffic queue image only as an illustrative setting. Preserve IF NO ONE IS IN DANGER; do not infer absence of danger from an actual incident photo.'),
('Andra slags ärenden','diagram','Source non-emergency utility/traffic questions outside emergency-centre responsibility; no additional agency contact or current service promise.'),
('Inte brådskande','diagram','Explicit IF matter is not urgent,do not call112; no new definition of urgency or symptom criteria.'),
('Vanliga sjukdomsfall','diagram','Ordinary illness separated from acute-emergency care,using neutral medicine/clinic objects without assigning a diagnosis to a real person.'),
('Polisens tillståndsärenden','photograph','Verified Finnish police institution or generic anonymous permit document; contextual ordinary permit query,not an allegation of an actual offence.'),
('Hjälpen kan försenas','diagram','Unnecessary call occupies an operator while a real-emergency route waits; qualitative possible delay only,no invented queue time or number of calls.'),
('Missbruk kan straffas','diagram','Conditional legal consequence for misuse,using statute/scales; no fine amount,prison term,actual offender or invented case.'),
('Utbildad operatör','photograph','Accurately identified emergency-centre workplace or ordinary headset object; avoid real caller records,screens with personal data and unverified worker identities.'),
('Frågor och hjälpbehov','diagram','Operator questions feed a help-needs assessment,without diagnosing or inventing categories beyond the source.'),
('Därefter larmas hjälp','photograph','Distinct actual Finnish response vehicle/agency context,without a fabricated current dispatch or guarantee which service attends.'),
('Operatörens anvisningar','diagram','Different source-specific guidance relationship: operator explains what caller should do; do not add medical or rescue instructions.'),
('Besvara frågorna noga','diagram','Operator remains the source call interlocutor rather than transferring it to a named responder; do not misrepresent later interpreter-bridge statements as impossible.'),
('Gratis från alla telefoner','photograph','Distinct real telephone object,not a fake live call. Illustrate the source no-charge statement without adding claims about absent network coverage or switched-off devices.'),
('Inget riktnummer','diagram','The exact112digits with a visibly unnecessary prefix field; no example country/area code that could be mistaken for actual instructions.'),
('Utländskt mobilabonnemang','diagram','Foreign mobile subscription still uses112without prefix,matching source; no invented roaming charge,network or country-specific rule.'),
('112 i EU','flag','Accurate verified EU flag and telephone112symbol; no fabricated country borders,membership list or non-EU scope.'),
('Finska, svenska och engelska','diagram','Three exact source service languages clearly distinguished; no inferred nationality or language ability of a real person.'),
('Telefontolk vid språkbehov','diagram','IF none of the three source languages are known,an interpreter may be used; no automatic instant-connection guarantee.'),
('Börja med ditt språk','diagram','State your actual language first,with an empty language field/phone symbol rather than an invented language utterance or caller identity.'),
('Vänta på tolken','diagram','Retain the preceding relevant language-connection image across the direct continuation; wait for operator to connect interpreter,no fabricated waiting time.'),
('Vanligen tryggt','photograph','Verified calm Finnish public environment,illustrative only. Keep usually/vanligen qualification; no invented risk statistics or claim serious crises never occur.'),
('Förberedd sedan länge','photograph','Neutral household preparedness object or source-specific home/long-standing-practice diagram; no unprovided stockpile list,quantities or preparedness rule.'),
('Exempel på oväntade situationer','photograph','Accurately identified actual storm/flood/power-outage setting as one source-listed example; not a current emergency or invented cause. Other source examples remain in full exact text.'),
('Förberedelse hjälper dig att agera','diagram','Prepared home/person plus response plan and shield,showing source preparedness relationship without adding new actions,guarantees or kit quantities.')]
assert len(ROWS)==49
plan(SID,ROWS)
e=R/'studio/episodes'/SID;p=e/'script.yaml';d=yaml.safe_load(p.read_text());d['asset_requests'][0]['description']='A distinct licensed accurately identified Finnish emergency-services or preparedness photograph,reserved centrally; exact identity resolved during assets.'
for row in d['sentences']:
    if '112' in row['sv']:row['speech_override']=dict(text=row['sv'].replace('112','ett ett två'),reason='Speak the exact emergency telephone digits individually in Swedish; source display and meaning unchanged.',review_status='pending')
for decision in d['episode_decisions']:
    if decision['id']=='fidelity':decision['decision']='Read every exact archived source sentence/list fragment once,in stored order,with current reviewed Russian. Only112digit speech is expanded. No invented emergency,triage,first-aid,address,translation-availability,penalty or preparedness instruction.'
    if decision['id']=='visuals':decision['decision']='Aim for at least90%distinct relevant picture sources and100%body picture coverage; prioritize actual verified vehicles,phones,address signs,agency settings and Finnish environments,with useful individually composed logic diagrams. Four direct source continuations may deliberately retain their meaningful illustration. No fake variants or real-person victim/diagnosis assignments.'
assert d['render']['background_style']['resampling']=='bilinear';p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));b=yaml.safe_load((e/'brief.yaml').read_text());b.update(production_status='script_ready',issues=['Detailed exact-source visual and narration plan prepared; actual licensed assets,narration and complete export checks pending.']);(e/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100));print(SID,'49 exact-source picture requests; explicit bilinear sampler;112digit-only speech expansions.')
