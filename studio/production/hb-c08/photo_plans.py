"""Select diverse, source-identified foreground photos for concrete educational contexts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
PLANS={
'utveckling':{
9:('File:Abckiria.jpg','Actual front page of Agricola’s1543Abckiria. A primary artifact of Finnish vernacular literacy during the Reformation; not presented as a photograph of a teaching event.'),
16:('File:Nuuksio elementary school 1952 (JOKAVN4A1C44-1).tif','Actual Nuuksio elementary school in1952; a historical example of the folk-school network, not an assertion that the nineteenth-century founding occurred in1952.'),
17:('File:Lisa Hagmanin yksityisluokat -nimisen koulun piirustussali - N26429 - hkm.HKMS000005-km0000mjlg.jpg','Actual drawing room of LisaHagman’s private school; accurately identified private educational institution. No assertion about the wealth of individual depicted pupils.'),
19:('File:Karjalan kansakoulun oppilaita.jpg','Actual Karjala folk-school pupils circa1920. Illustrative historical pupils, not evidence of their families’ attitudes toward schooling.'),
21:('File:Kuusamon Heikkilän kansakoulun luokkakuva 1950 (HK7744-813).tif','Actual1950Finnish elementary class portrait illustrates school participation; not used as proof of exact legislative coverage or the1921act.'),
23:('File:Puotinharju\'s primary and upper secondary school 1969 (JOKAURR2A D011-2).tif','Actual music class inPuotinharju school,1969. Historical educational context within the source’s1950s–1960sexpansion period; not an examination ceremony.'),
35:('File:Music classroom of Vantaankoski school in Vantaa, Finland, 2010.jpg','Actual music classroom inFinland illustrates learning through school and hobbies, without claiming the depicted students’ individual activities.'),
36:('File:Adult education at Kuggom 1970 (JOKABBL3B A67-1).tif','Actual adult education atKuggom,1970. Historical example supporting the concept of continued learning after initial schooling.')},
'smabarn':{
0:('File:Child playing with unit blocks.jpeg','Actual young child playing with wooden blocks, age3according to the source. Illustrative child under school age; not identified as a Finnish daycare participant.'),
1:('File:Kindergarten Veturi in Tikkurila, Vantaa, Finland, 2022 April.jpg','Actual Finnish daycare building. Illustrative municipal early-childhood setting; ownership or a particular service entitlement is not inferred from its appearance.'),
3:('File:Unit block wagon.jpg','Actual standard wooden play blocks illustrate planned play-based learning resources; no claim that a particular brand or item is compulsory.'),
37:('File:Child engaging in colorful wooden block sorting activity.jpg','Actual child sorting wooden blocks. Illustrative hands-on play activity, not a claim about Finnish location or a specific curriculum.'),
39:('File:Kukinpolku kindergarten in Martinlaakso, Vantaa, Finland, 2021 September.jpg','Actual Finnish daycare setting related to the child-development context; does not certify the outcomes for any depicted child.'),
43:('File:Montsa kindergarten in Kuninkaala, Vantaa, Finland, 2021.jpg','Accurately identified Finnish daycare exterior; illustrates the named institution type without implying formal school lessons.'),
48:('File:Ulrika kindergarten in Asola, Vantaa, Finland, 2021 – 01.jpg','Actual Finnish daycare in a daytime exterior photograph. Illustration of a day setting, not verification of this facility opening hours.')},
'gymnasium':{
0:('File:Tölö gymnasium ”Lönkan” 02.png','Actual Tölö upper-secondary school. Concrete institution at the educational level discussed; no claim about enrollment of a depicted individual.'),
7:('File:Tölö gymnasium ”Lönkan” 03.png','Independent source photograph of Tölö upper-secondary school. Contextual image of the institution type; does not itself demonstrate grouping policy.'),
13:('File:Tölö gymnasium ”Lönkan” 04.png','Verified upper-secondary institution supporting a list of its general subject areas; no assertion that every listed subject is visible in this exterior.'),
18:('File:Tölö gymnasium ”Lönkan” 05.png','Verified upper-secondary institution context for completing a course of study; not evidence of an individual diploma.'),
32:('File:Tölö gymnasium ”Lönkan” 06.png','An independent photograph of the Finnish school setting; illustrative learning-material context without implying a particular provision visible in the photograph.')},
'hogskolor':{
0:('File:Metropolia Main Campus Helsinki.jpg','Actual Metropolia University ofAppliedSciences Myllypuro campus,Helsinki,2023. A concrete applied-sciences institution, not a representative university of alltypes.'),
1:('File:Metropolia Leppävaara campus.JPG','Actual Metropolia Leppävaara campus inEspoo. An accurately identified applied-sciences setting; no claim about a particular depicted programme.'),
3:('File:Helsinki University Library Interior B - Marit Henriksson.jpg','Actual Helsinki University Library interior,2018. Concrete academic study and knowledge setting, not a claim about a particular research finding.'),
4:('File:University of Tampere, main library Linna.jpg','Actual university library Linna inTampere. Illustrative academic/theoretical study setting, not a comparison measured from the photograph.'),
14:('File:Arabia campus library.jpg','Actual campus library inFinland. Relevant study/preparation environment; no inferred examination admission rate or programme affiliation.'),
20:('File:Myllypuro campus.jpg','Actual Myllypuro campus context for applied highereducation. Does not identify a particular internship or thesis task.'),
25:('File:Myyrmäki Campus.jpg','Actual university-of-applied-sciences campus inMyyrmäki. Concrete highereducation institution, not verification of a particular part-time schedule.'),
42:('File:Pegasus Library Oulu 20250716.jpg','Actual UniversityofOulu Pegasus library,2025. Illustrative location for reading factual texts and developing study skills, without implying a specific course there.')},
'vuxna':{
0:('File:Finnish adult education centre.jpg','Actual Finnish adult education centre, described by its creator as health andwell-being. A concrete institution of adult learning, not proof of a specific qualification offered.'),
1:('File:Helsinginkatu in Alppiharju with Helsinki Finnish Adult Education Centre on an afternoon in March 2024.jpg','Actual Helsinki adulteducation centre building. Institution context for adult courses; not a claim about an individual course or its fee.'),
38:('File:The Swedish Adult Education Centre in Porvoo 1968 (JOKAÖN3A E04-1).tif','Actual Swedish adult education centre inPorvoo,1968. Historical adult-learning institution example, not current policy evidence.'),
41:('File:The Swedish Adult Education Centre in Porvoo 1968 (JOKAÖN3A E04-2).tif','Separate historical adult-education photograph fromPorvoo1968. Used illustratively for broad adult-learning activities; source identity retained.'),
48:('File:Primary School and Adult Education Centre 1970 (JOKABBL3B A102-1).tif','Actual Finnish primaryschool/adulteducationcentre,1970. Illustrative adult educational institution rather than a claim that all listed services existed there.'),
54:('File:OSAO kauppaoppilaitos, Kaukovainio, Oulu, 2003.jpg','Actual OSAO educational institution inOulu. A concrete vocational education setting; not evidence of a specific employer partnership.')},
'grundskola':{
6:('File:Kalasataman peruskoulu (Helsinki, 2022).jpg','Actual Finnish comprehensive school,Kalasatama2022. Concrete example of institution type; ownership and funding rules come from source narration, not image inference.'),
30:('File:K-1399-3- Seminaarilaisia käsityöluokassa nykyisessä Villa Ranassa, 1924.jpg','Actual Finnish handicraftclass,1924. Historical illustration of hands-on school subjects; not current curriculum documentation.'),
33:('File:Kemian oppitunti Joensuun ammattikoulussa 1949 (KK5596-1.AK.12).tif','Actual chemistrylesson inJoensuu1949. Illustrative concrete chemistryclass, explicitly historical and vocational, not claimed to depict a contemporary primary class.'),
63:('File:K-1637-17- Seminaarin tyttöharjoituskoulun oppilaita muovailutunnilla, 1910 - 1920.jpg','Actual Finnish practice-school modellinglesson,1910–1920. Historical hands-on learning example, not a reconstruction or current policy image.')},
'yrkesutbildning':{
0:('File:Karjaa Vocational School 1955 (JOKAVN4A1F11-1).tif','Actual Karjaa vocationalschool in1955. Historical vocational education context; no assertion of current programme identity.'),
1:('File:Karjaa Vocational School 1955 (JOKAVN4A1F11-2).tif','Independent archival picture ofKarjaa vocationalschool,1955. Illustrative historical education/practice setting.'),
3:('File:Karjaa Vocational School 1955 (JOKAVN4A1F11-3).tif','Actual archival vocational-school scene,1955. Shows vocational learning context without attributing a named profession beyond visible evidence.'),
14:('File:Vocational school for girls 1961 (JOKAUAS2 7568-1).tif','Actual Finnish vocational instruction,1961. Historical practical-learning example; not present-day employment or contract evidence.'),
15:('File:Vocational school for girls 1961 (JOKAUAS2 7568-2).tif','Independent historical vocational-school photograph,1961. Illustrative practical learning; no claim that this is a modern assessed demonstration.'),
31:('File:Vocational school for girls 1961 (JOKAUAS2 7568-3).tif','Verified historical vocational-school image,1961. Illustration of vocational breadth; depicted activity will be checked visually before export.'),
35:('File:Vocational school for girls 1961 (JOKAUAS2 7568-4).tif','Verified historical vocational-school practice,1961. No assertion of modern work-based-learning legal terms.'),
48:('File:Vocational school for girls 1961 (JOKAUAS2 7568-5).tif','Verified archival vocational teaching photograph,1961. Illustrative practical task rather than a particular student’s present-day examination.')},
'stod':{
5:('File:School reportage 1967 (JOKAVN4A2H11-3).tif','Actual Finnish schoolreportage,1967. Historical school context; the image will be omitted if it does not visibly support the end-of-year school-life passage.'),
70:('File:Kuva0088.jpg','Actual Munkkiniemi upper-secondary school cafeteria. Concrete Finnish educational dining space, not a claim about a particular school meal price.'),
71:('File:Finnish school lunch.jpg','Actual example of Finnish schoollunch,2011. Relevant warm-meal photograph, not a representation of every school menu.'),
72:('File:Aleksis Kivi School 1949 (JOKAUAS2 415-9).tif','Actual1949 schoolmeal context one yearafter the source’s1948milestone; does not claim to depict the exact first national serving.'),
76:('File:School bus in Kirkkonummi 1966 (JOKAVN4A2G42-1).tif','Actual schoolbus inKirkkonummi1966. Clearly archival transport example; not verification of modern entitlement or busservice.'),
105:('File:Child engaging in colorful wooden block sorting activity.jpg','Actual hands-on child play illustrates after-schoolplay activity without claiming Finnish location or participation in a specified programme.')},
'finansiering':{
9:('File:Tölö gymnasium ”Lönkan” 07.png','Actual Finnish upper-secondary school. Concrete education type in the support-eligibility list; the photo does not establish individual eligibility.'),
10:('File:Karjaa Vocational School 1966 (JOKAVN4A2G13-1).tif','Actual vocationalschool in1966. Historical institution-type illustration; not evidence of contemporary student-aid rules.'),
11:('File:Metropolia Main Campus Helsinki.jpg','Actual Finnish highereducation institution. Institution-type context only; aid entitlements come solely from the exact archived source.'),
34:('File:Karjaa Vocational School 1955 (JOKAVN4A1F11-4).tif','Actual archival Finnish educational dining setting,1955. Historical illustration of institutional dining, not a present-day student discount amount.'),
51:('File:Tölö gymnasium ”Lönkan” 08.png','An independent Finnish school photograph illustrating a studyinstitution. It is not evidence of a specific evening or weekend timetable.')}
}
for slug,entries in PLANS.items():
 sid='hb-c08-'+slug;p=ROOT/'studio/episodes'/sid/'photograph-plan.json';old=json.loads(p.read_text()) if p.exists() else {}
 for i,(title,context) in entries.items():old['picture-'+str(i+1).zfill(3)]=dict(title=title,context=context)
 p.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n');print(sid,len(old),'photo requests')
