"""Select source-specific real photographs without implying anyone's legal status."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
PLANS={
'integration':{
18:('Cafe Ihana in Sompasaari, Helsinki, Finland, 2012.jpg','Actual Helsinki outdoor cafe,2012, illustrating a setting where people meet. No pictured person is identified as a migrant or integration-service recipient.'),
28:('Fazer Café Kluuvikatu, Helsinki (52891092950).jpg','Actual Helsinki cafe as contextual social meeting place. No claim about the legal status or personal social networks of customers.')},
'tjanster':{
31:('Kela building in Ivalo front.jpg','Actual Kela/FPA office exterior in Ivalo as an example of the named institution; no assertion about current local opening hours or individual benefit entitlement.'),
49:('Rauhanasema 2023 (202327;+G72587).jpg','Rauhanasema community/NGO house,Helsinki,2023, as context for associations and community support. Not identified as a particular integration-advice appointment office.')},
'sprak':{
1:('Bilingual street sign of John Stenbergin ranta in Helsinki, Finland, 2021.jpg','Actual Finnish/Swedish bilingual street-name sign in Helsinki. Its visible languages illustrate the two named integration-language alternatives.'),
4:('Mustasaari municipal border sign 20190705.jpg','Actual bilingual Mustasaari/Korsholm municipal sign,July2019, illustrating a real bilingual municipality. Does not establish individual language-course availability.')},
'tolkning':{
13:('Woman talks on laptop in a cafe while sitting at a wooden table surrounded by fruit.jpg','Actual contextual photograph of remote communication on a laptop. The photographed person is not identified as an interpreter or Finnish authority customer; no interface or personal details are added.')},
'myndigheter':{
1:('Pasilan virastokeskus.JPG','Actual government office centre in Pasila,Helsinki, as context for public authorities. Does not identify this entire building as any single named agency.'),
14:('Lohja, Verotoimisto.jpg','Actual tax-office building in Lohja as an example of the source-named tax administration. Source photograph date/identity retained; no current office-address recommendation.'),
18:('Kansaneläkelaitos KELA tekstilogo 2017.jpg','Actual photographed Kela/FPA wordmark in2017, identifying the named social-insurance institution without implying benefit eligibility.'),
31:('Interior of Helsinki Central Library Oodi in 2019 (46535194044).jpg','Actual Helsinki public-library interior,2019, illustrating the source-named municipal library service.'),
36:('Vuosaaren terveys- ja hyvinvointikeskus - Helsinki - 1.jpg','Actual Vuosaari health and wellbeing centre,Helsinki, as an example of a physical health-service building. No claim about an individual entitlement or today’s specific service arrangement.')},
'egna-arenden':{
12:('Haapaniemenkatu 7, Helsingin verotoimisto - N220595 - hkm.HKMS000005-km002uuj.jpg','Archival Helsinki tax-office photograph,used only as an example of the named tax authority. It is not presented as a current office address or a real customer tax declaration.')},
'personuppgifter':{
8:('Helsingin Osakepankki 1951 (JOKAUAS2 877-2).tif','Archival Finnish bank/customer-service photograph,1951, illustrating the banking institution named as an example. No depicted document is used to assert an actual person’s identifier or current banking procedure.'),
40:('City Hall in Helsinki, Finland, 2021 November.jpg','Actual Helsinki city hall as one concrete large-city municipality example,November2021. It does not determine any viewer’s municipality of residence.'),
48:('Mailbox in Utsjoki.jpg','Actual Finnish postal-service object in Utsjoki, illustrating a postal address alternative. No private home address or invented personal identifier is added.')},
'hemkommun':{
1:('Helsinki City Hall A- Marit Henriksson.jpg','Actual Helsinki city-hall photograph as context for municipal services. No claim about a particular viewer’s entitlement.'),
21:('Mustasaari municipal border sign 20210617.jpg','Actual Mustasaari/Korsholm municipal boundary sign,2021, illustrating the municipality in which a person lives. No individual residence is identified.')},
'e-tjanster':{
2:('Beautiful senior couple working on laptop in the garden.jpg','Actual contextual photograph of adults using a laptop together. They are not identified as Finnish authority customers and no real service transaction is inferred.'),
16:('Smart card reader JCR721 white.png','Actual external contact smart-card reader device,illustrating the source’s requirement for a reader with chip-card e-services. No claim that this exact model has been tested with Finnish ID cards.'),
24:('Laptop smart card reader.jpg','Actual built-in smart-card-reader slot on a laptop. Illustrates a physical personal identification tool; no card number or login credential displayed.')},
'norden-eu':{
1:('Haparanda-Tornio (E4) border crossing 2026-07-24 01.jpg','Actual Haparanda–Tornio border crossing,July2026, as geographical context for Nordic movement. Does not assert current border controls or an individual’s legal eligibility.'),
13:('Finnish passport cover PRADO.jpg','Actual Finnish passport cover; no bearer personal-data page. The image illustrates a travel-document object and does not imply that a non-Finnish EU citizen needs a Finnish passport.')}
}
for slug,choices in PLANS.items():
 p=ROOT/'studio/episodes'/('hb-c12-'+slug)/'photograph-plan.json';p.write_text(json.dumps({'picture-'+str(i).zfill(3):dict(title='File:'+title,context=context) for i,(title,context) in choices.items()},ensure_ascii=False,indent=2)+'\n')
print('Prepared',sum(map(len,PLANS.values())),'distinct relevant photo source identities')
