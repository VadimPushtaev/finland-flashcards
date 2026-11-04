"""Direct exact-source traffic and licence rules without invented maps or permissions."""
from pathlib import Path
import yaml
from plan_nature import plan
R=Path(__file__).resolve().parents[3];SID='hb-c11-trafik'
ROWS=[
('Högertrafik','photograph','Verified Finnish roadway/traffic scene illustrating right-hand traffic; do not use a left-driving-country photo or infer a current traffic incident.'),
('Till fots','photograph','Actual Finnish pedestrian street/footpath context; no real person assigned immigration or health status.'),
('Trygg gångmiljö','photograph','Distinct accurately identified Finnish pedestrian environment; illustrative planning context,not a guarantee that a photographed route is safe now.'),
('Övergångsställe och trafikljus','photograph','Actual Finnish pedestrian crossing/traffic signals with country identity verified; source says signals OFTEN,not at every crossing.'),
('Landsbygd utan trottoar','photograph','Verified Finnish rural road with visible verge; no assertion that every rural road lacks a pavement or the current photographed route is safe.'),
('Vänstra kanten','diagram','Under the preceding no-sidewalk context,a walker on the LEFT edge relative to their own travel direction; explicit direction arrows,not a reversed viewer-left convention or new distance rule.'),
('Cykel','photograph','Actual bicycle used as a transport object; accurately identified,no brand recommendation.'),
('En del cyklar på vintern','photograph','Verified actual winter cycling or bicycle-in-snow scene; source SOME riders,not a universal expectation or assertion of safe winter conditions.'),
('Små barn på trottoaren','diagram','ONLY small-child cycling permission on sidewalk,with child/adult distinction; do not invent a numeric age limit absent from this source.'),
('Cykelbana eller cykelfält','photograph','Actual Finnish cycle path/lane and recognisable relevant sign/markings; no invented lane layout or extra priority rule.'),
('Om cykelbana saknas','diagram','Explicit IF no separate bike path/lane,cycling uses carriageway. Preserve the preceding ordinary-rider context,not an unconditional ride-anywhere rule.'),
('Hjälm och lykta','photograph','Verified actual bicycle helmet and bicycle light objects,or carefully sourced composite; source darkness condition applies to the light. No asserted fit certification or invented light specification.'),
('Kollektivtrafik i stora städer','photograph','Actual Finnish city public-transport scene without current schedule,route-frequency or ticket-price claims.'),
('Buss, tåg, metro och spårvagn','photograph','Four correctly identified actual Finnish transport-mode images as a useful collage; no substituted intercity train for a specifically claimed local service or invented network map.'),
('Olika biljetter','diagram','Single,series and monthly ticket categories as anonymous schematic objects; no fake valid fare media,price or invented official app interface.'),
('Färre linjer, glesare trafik','photograph','Accurately identified smaller-town/rural public-transport setting,qualified by the exact source; no fabricated timetable or claim a pictured stop lacks service.'),
('Resa runt i Finland','photograph','Actual Finnish bus/train/aircraft/boat example or varied collage; source MOST places,not guaranteed access to every location.'),
('En del trafik går sällan','diagram','Qualitative sparse service marks on an unnumbered timeline; no invented departures,waiting times or route-specific timetable.'),
('Kostnader för egen bil','photograph','Actual car/fuel-pump/maintenance object setting,with the stated insurance/tax categories in source text; no invented amounts or brand recommendation.'),
('Vanligtvis ingen egen bil','photograph','Distinct large Finnish city transit/walkable context; preserve usually qualifier,not a ban or assertion about a real household\'s needs.'),
('Bil kan behövas på mindre ort','photograph','Verified small-town/rural road and ordinary car setting; source MAY be needed,not a universal requirement or unsafe route recommendation.'),
('Följ trafikreglerna','photograph','Accurate actual Finnish traffic-sign/road context; do not invent a speed limit,priority rule or official sign.'),
('Polisens övervakning','photograph','Verified Finnish police vehicle or traffic camera/sign object; source IF rule violation then fine,no claim a photographed driver committed an offence.'),
('Inte alkohol och bilkörning','diagram','Alcohol/driving prohibition relationship without depicting a real person as intoxicated,estimating safe drinks or suggesting a safe impairment level.'),
('0,5 promille i källan','diagram','Exact source0.5per-mille value with explicit promille unit; never convert to0.5percent or draw a green safe-to-drive zone below the limit.'),
('Trafikförsäkring','diagram','IF owning a car,the source traffic-insurance obligation; anonymous policy document,not comprehensive-cover guarantees or invented premiums.'),
('Försäkringsbolag','photograph','Verified actual Finnish insurance institution exterior if licensed,or neutral anonymous insurance-document object; no company endorsement or invented coverage.'),
('Besiktning och registrering','diagram','BOTH inspection AND registration are source requirements; do not merge them into one event or insert frequency/deadline absent from source.'),
('Besiktningsstation','photograph','Accurately identified actual Finnish vehicle-inspection station; not a car wash,repair shop or foreign licensing authority.'),
('Registrering: exempel på platser','diagram','Three source example channels—inspection station,insurer,dealer—with clear for-example qualification. No invented mandatory single channel.'),
('Traficoms webbplats','photograph','Verified actual Traficom institution or neutral computer object; no fake government interface,current URL/button flow or unprovided application result.'),
('Giltigt körkort','diagram','ONLY with valid driving licence may one drive in the source context; clearly schematic anonymous card,no real identity or counterfeit-ready document.'),
('Utfärdande stat erkänd av Finland','diagram','Issuing-state recognition as the source rule,with validity and later exceptions still visible in source context. No invented country-recognition map/list or unconditional all-card approval.'),
('Bosatt vid utfärdandet','diagram','Explicit IF holder lived in Finland WHEN foreign card was issued,it is not accepted. Temporal residence/issuance gate,not a prohibition of all foreign licences.'),
('Latinska bokstäver eller översättning','diagram','OR logic: Latin-letter licence text OR accompanied translation into Finnish/Swedish/English. No fictitious real card or claim other translations automatically suffice.'),
('Ålders- och hälsokrav','diagram','BOTH Finnish age AND health requirements,unnumbered calendar and neutral health symbols; no invented minimum age,vision threshold,diagnosis or examination procedure.'),
('EU/EES och giltighet','diagram','EU/EES-issued card AND still valid -> source driving permission for validity period. No invented member-country map or permission after expiry.'),
('Byte: stadigvarande eller studier','diagram','CAN exchange in this EU/EES section IF permanent Finnish residence OR at least six months STUDY in Finland. Keep six-month study threshold tied to study,not all residence.'),
('Byte efter giltighetstidens slut','diagram','For PASSENGER-CAR licence,exchange within two years AFTER validity expired; this is an exchange deadline,NOT permission to drive an expired card. Do not invent a calendar date.'),
('Läkarutlåtande vid utgånget kort','diagram','IF expired card,a medical statement is needed; anonymous document,no real health record,diagnosis or extra testing threshold.'),
('Konventionsland utanför EU','diagram','Outside-EU issuing country joined Geneva OR Vienna road-traffic convention -> source maximum two-year driving period in Finland. No invented start anchor,country list or extra duration.'),
('Hongkong, Macao och Taiwan','diagram','Three exact source issuing-region names and maximum two years. No added sovereignty/recognition classification,border map or extension beyond source period.'),
('Byte när stadigvarande bosatt','diagram','In the preceding convention/Hongkong/Macao/Taiwan context,CAN exchange when permanently resident. Do not generalize to every foreign licence regardless of later validity conditions.'),
('Två år för bytet efter flytt','diagram','Move to Finland AND permanent residence start the stated two-year exchange window. Clearly label exchange deadline,not a fresh period of card validity.'),
('Giltigt vid bytet','diagram','Card must be valid AT THE EXCHANGE moment in this source group; preserve distinction from the earlier EU/EES expired-card exchange statement.'),
('Läkarutlåtande behövs också','diagram','Anonymous medical-statement document as an additional source requirement,not evidence of a person\'s health or an unprovided test result.'),
('För sent eller ogiltigt kort','diagram','IF late exchange OR no longer valid -> Finnish driving examination containing BOTH theory AND driving tests. Explicit OR causes and AND test components,no costs or new exemptions.'),
('Annat land: ett år från registrering','diagram','Issuing country joined NEITHER Geneva NOR Vienna convention -> one-year period AFTER Finnish population-system registration. Do not use arrival,permanent-move or card-expiry as a substituted start anchor.'),
('Förarexamen för att fortsätta','diagram','AFTER that source one-year period,IF wishing to continue driving,complete Finnish driving examination. No automatic licence,extra delay or unprovided exam category.')]
assert len(ROWS)==49
plan(SID,ROWS)
e=R/'studio/episodes'/SID;p=e/'script.yaml';d=yaml.safe_load(p.read_text());d['asset_requests'][0]['description']='Distinct licensed source-verified Finnish street/traffic photograph,reserved centrally; exact identity resolved during assets.'
for decision in d['episode_decisions']:
    if decision['id']=='fidelity':decision['decision']='Every exact archived source sentence once,in stored order,with current reviewed Russian. Retain literal source wording including duplicated Du in hb-c11-u0258-s002. No invented countries,borders,traffic exceptions,prices,impairment advice,age/health threshold or licence-deadline anchor.'
    if decision['id']=='visuals':decision['decision']='Aim for at least90%distinct relevant picture sources and100%body picture coverage; actual verified Finnish transport,signs,road and equipment photographs for concrete topics,with source-specific diagrams for qualified licence/insurance rules. No merely renamed templates or allegations against photographed drivers.'
assert d['render']['background_style']['resampling']=='bilinear';p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));b=yaml.safe_load((e/'brief.yaml').read_text());b.update(production_status='script_ready',issues=['Detailed exact-source picture/narration plan prepared; actual assets,narration and full export checks pending.','Archived hb-c11-u0258-s002 literally says Du kan du; source wording retained.']);(e/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100));print(SID,'49 source-specific picture requests; all validity/exchange/test gates preserved.')
