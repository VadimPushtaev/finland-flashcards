"""Direct exact archived home/fire safety without adding response procedures."""
from pathlib import Path
import yaml
from plan_nature import plan
R=Path(__file__).resolve().parents[3];SID='hb-c11-brandsakerhet'
ROWS=[
('Brandvarnare i bostäder','photograph','Actual domestic smoke alarm,not camera or heat detector; archived source legal statement,no added current-law interpretation.'),
('Tillräckligt många','photograph','Distinct actual domestic smoke-alarm object/room installation; no invented placement distances or standard.'),
('Varuhus och järnaffärer','photograph','Actual hardware-store setting with alarm relevance,no endorsement,current stock or prices.'),
('60 kvadratmeter','diagram','One smoke-alarm object with exact source60square-metre area,no invented installation radius or floorplan.'),
('Exempel: 65 kvadratmeter','diagram','Explicit EXAMPLE65square metres -> TWO alarms; distinct area/count illustration,not one alarm per home.'),
('Varje våning separat','diagram','IF more than one floor,measure each floor separately; never sum all floors first.'),
('Brandvarnare på varje våning','diagram','Alarm on EACH of two schematic levels,no invented ceiling clearances or placement instruction.'),
('Kontrollera funktionen','photograph','Actual smoke-alarm/test-button object; source regular checking,no invented weekly/monthly schedule or test procedure.'),
('Batterier vid behov','photograph','Actual household battery/alarm objects; IF NEEDED and preferably once a year,not mandatory exact interval or model compatibility assurance.'),
('Bastu i hemmet','photograph','Verified actual Finnish home sauna; source OFTEN,not every dwelling.'),
('Inget på bastuugnen','diagram','Sauna heater with object storage prohibited EVEN WHEN UNUSED; source fire risk,no allegation about actual household.'),
('Inte tvätt nära aggregatet','diagram','Laundry ABOVE OR NEAR heater prohibited,no invented safe distance or drying method.'),
('Inte förråd','diagram','Sauna bench/heater plus storage boxes prohibited,distinct from heater-top rule.'),
('Stäng av efter användning','photograph','Actual electric sauna-heater control with source OFF-after-use cue,no invented model-specific switch position.'),
('Lång tid utan användning','diagram','IF electric heater unused for long time,source fuse-removal relationship abstractly; no invented duration,live wiring or electrical-work steps.'),
('Kontroll före du går','diagram','Leaving-home cue plus BOTH stove AND oven AND example iron OFF,no extra device requirements.'),
('Brandsläckare hemma','photograph','Actual extinguisher as recommended object,no invented class,rating,inspection interval or discharge steps.'),
('Vissa trappuppgångar','photograph','Verified actual stairwell extinguisher; SOME apartment blocks,not guarantee in every stairwell.'),
('Var är närmaste släckare','diagram','Extinguisher-location/question relationship,no fabricated building floorplan or guaranteed access.'),
('Släckningsfilt hemma','photograph','Actual correctly identified fire blanket/case,not ordinary textile,no invented rating or handling procedure.'),
('Exempel nära spisen','photograph','Distinct fire blanket near cooking context,FOR EXAMPLE qualification,no invented height/distance.'),
('Het spis under uppsikt','diagram','Cooking pot and attentive-person cue with unattended state prohibited,no staged live hazard.'),
('Försiktighet på natten','diagram','Night/moon and cooking object: extra care IF cooking at night,not a blanket ban.'),
('Inte berusad vid matlagning','diagram','Cooking/alcohol impairment prohibition,no real person accused or invented safe amount/time.'),
('Inga föremål på spisen','photograph','Actual empty stovetop with source no-storage cue,never stage ignition.'),
('Kan sättas på av misstag','diagram','Child OR pet OR adult as source possibilities linked to cooker control,no invented actual incident/control bypass.'),
('Föremål kan fatta eld','diagram','Accidental-on stove plus stored object MAY cause fire,not certainty or live reenactment.'),
('Fettbrand: kväv elden','diagram','IF cooking FAT burns,source examples pot LID OR fire BLANKET covering flame; abstract objects,no added handling steps or guarantee.'),
('Fettbrand: inte vatten','diagram','Explicit preceding cooking-FAT-FIRE context and water prohibited,not universal claim about every fire.'),
('Stäng av elapparater','photograph','Actual household appliance plus OFF-after-use source cue,no brand-specific operating instructions.'),
('Dra ur strykjärnet','photograph','Actual iron and clearly disconnected plug,no exposed wiring or damaged live equipment.'),
('Trasig apparat eller sladd','diagram','Poor appliance condition OR damaged cord -> no use; anonymous schematic,no repair guide.'),
('Elbrand: inte vatten','diagram','IF electrical appliance burns,water prohibition; distinguish from fat-fire rule.'),
('Exempel: brandsläckare','diagram','Electrical-appliance fire context plus FOR EXAMPLE extinguisher,no invented extinguisher type/application steps.'),
('Inget på elvärme','photograph','Actual electric heater/radiator with no-covering cue,correctly identified,no invented clearance dimensions.'),
('Rök inte inomhus','diagram','Indoor house and cigarette prohibition,no real smoker allegation or added outdoor law.'),
('Ljus under uppsikt','photograph','Actual candle object with attendance cue,no claim photo proves supervision.'),
('Inte nära gardiner','diagram','Candle/curtain proximity prohibited EVEN IF person present,no invented safe distance.'),
('Läcka: avstängningsventil','photograph','Actual domestic water shutoff valve correctly identified; conditional TRY to close,no invented turn direction/plumbing repair steps.'),
('Höghus eller radhus','diagram','IF apartment block OR row house -> notify building-maintenance emergency number immediately; no fake digits or112substitution.'),
('Villa: rörfirma','diagram','IF detached house -> on-call plumbing firm; distinct from maintenance/112,no fabricated contact.'),
('Säkerhetslås när du går','photograph','Actual domestic security-lock object with away-from-home cue; IF lock exists,lock when absent,no bypass information or certification claim.'),
('Inte säkerhetslåst hemma','diagram','AT HOME -> do NOT lock source security lock,distinct from ordinary door latch; not advice to leave outside door open.'),
('Inbrott: 112','diagram','IF someone breaks into home -> source112and phone,no staged perpetrator/victim or extra confrontation advice.'),
('Täta hus på vintern','photograph','Verified Finnish winter residential setting; illustrative warmth/airtightness context,no measured performance claim.'),
('Fukt kan ge problem','diagram','Moisture MAY damage wall/floor in preceding airtight-house context,no invented mould diagnosis/threshold or named property allegation.'),
('Lite vatten vid städning','photograph','Actual damp-cleaning cloth/floor object; avoid excessive water,no invented volume,chemical or product recommendation.'),
('Torka noggrant','photograph','Distinct drying-cloth/floor object; IF wet then dry thoroughly,no invented time limit/guarantee.'),
('Ventiler för fuktig luft','photograph','Actual domestic ventilation vent,not heating grille; outward moist-air function,no invented airflow measurement.'),
('Öppna och rena året om','diagram','Ventilation stays OPEN AND CLEAN ALL YEAR; do not close,no invented cleaning interval/procedure.'),
('Brand: ring genast','diagram','IF building fire,source emergency call immediately;112from context,no extra evacuation/medical instructions.'),
('Rök i trappuppgången','diagram','Apartment building AND smoke in stairwell -> do NOT leave apartment; smoke outside door,not universal stay-home rule for every fire.'),
('Ingen hiss vid brand','diagram','IF building fire,lift use prohibited,no added escape route or claim specific lift works.'),
('Alla hemma behöver veta','diagram','Household adults AND children knowing source response,no invented procedures or claim actual photographed family practiced drill.'),
('Fri balkongdörr','photograph','Actual unobstructed balcony door; no furniture blocking it,can exit IF needed; no jump/climb instruction or universal balcony evacuation rule.')]
assert len(ROWS)==55
plan(SID,ROWS)
e=R/'studio/episodes'/SID;p=e/'script.yaml';d=yaml.safe_load(p.read_text());d['asset_requests'][0]['description']='Distinct licensed accurately identified Finnish home/fire-safety object photograph,reserved centrally; exact identity resolved during assets.'
for row in d['sentences']:
    if '112' in row['sv']:row['speech_override']=dict(text=row['sv'].replace('112','ett ett två'),reason='Speak source emergency-number digits individually; display remains exact.',review_status='pending')
for dec in d['episode_decisions']:
    if dec['id']=='fidelity':dec['decision']='Every archived Swedish sentence and reviewed Russian retained once in stored order. Exact source conditions/examples only; no invented current legal update,equipment rating,escape procedure,electrical repair or contact digits.'
    if dec['id']=='visuals':dec['decision']='Aim for at least90%distinct relevant pictures and100%body picture coverage: actual alarms,blanket,extinguisher,sauna,appliances,ventilation/home objects plus source-specific conditional diagrams; no unsafe reenactments or alleged actual incidents.'
p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));b=yaml.safe_load((e/'brief.yaml').read_text());b.update(production_status='script_ready',issues=['Detailed exact-source fire/home-safety picture plan prepared; actual assets,narration and full export checks pending.']);(e/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100));print(SID,len(ROWS),'specific plans')
