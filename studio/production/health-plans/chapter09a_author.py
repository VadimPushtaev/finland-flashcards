"""Advisory-only medical source plans; root episode inputs remain untouched."""
from pathlib import Path
import hashlib
import json
import re

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PLANS = {
    'psykisk': '''group;person|människan;shield|mentala hälsan;gear|handlingskraftig
protect;people|goda sociala relationer;plant|hälsosamma levnadsvanor
contrast;shield|mentala hälsa;person|fysiska välbefinnande
group;family|sin familj;people|gemenskap;shield|jämlikt behandlad
warning;people|diskriminering;prohibited|rasism
group;person|ensamhet;coins|ekonomisk osäkerhet;hospital|svårigheter att få social- och hälsovårdstjänster
group;book_pages|nytt språk;globe|kulturella utmaningar;warning|svårigheter
group;hospital|hälsostationerna;hospital|privata läkarstationer
group;warning|depression;warning|ångest;food|ätstörningar
flow;calendar|boka en tid;person|hälsovårdare eller läkare;hospital|egna hälsostationen
group;person|Läkaren;document|hurdan hjälp
branch;document|remiss;hospital|psykiatrisk poliklinik;hospital|någon annan mentalvårdstjänst
group;people|samtal;medicine|medicinbehandling
group;calendar|boka tid;hospital|privat läkarstation
group;person|psykiatriker;person|psykologer
contrast;coins|mycket mer;hospital|offentlig hälsovård
group;phone|ringa;hospital|hälsostation;hospital|sjukhus med jour
group;clock|Akut;hospital|jourerna;hospital|psykiatriska sjukhus
group;child|barn eller en ung person;people|föräldrarna;hospital|familjerådgivningen
group;house|skolorna;people|yrkesutbildade personer;child|barn
group;person|kuratorer;person|psykologer;person|hälsovårdare och läkare
group;bottle|Alkohol;warning|droger;document|rusmedel
group;plant|cannabis;warning|opioider;warning|kokain
group;warning|Alla droger;prohibited|olagliga;flag_fi|Finland
group;document|Innehav och försäljning;coins|bötes;prohibited|fängelsestraff
group;hospital|social- och hälsovårdsstationen;house|studerandehälsovården;work|företagshälsovården
group;person|använder rusmedlen;gear|spelaren;people|närstående
group;coins|ekonomiska problem;warning|De orsakar ofta
flow;hospital|A-klinikerna;shield|vård och rehabiliteringstjänster
protect;people|närstående;shield|hjälp och stöd
group;coins|gratis;hospital|klinikerna;prohibited|avgiftning
group;prohibited|slutar;warning|rusmedel;calendar|under behandlingen
group;hospital|hälsorådgivningar;city|många städer
reuse;syringe|gamla och använda drogsprutor;syringe|nya
group;people|social- och hälsovårdsrådgivning;book_pages|handledning
group;court|Myndigheterna;syringe|gratis drogsprutor;shield|hälsoskäl
group;syringe|smutsiga sprutor;germ|sjukdomar
flow;hospital|rådgivningarna;hospital|avgiftning;shield|sluta med missbruket
flow;laptop|internet;document|Kontaktuppgifterna;hospital|hälsorådgivningen
group;globe|flyttar från ett land till ett annat;work|problem på arbetsplatsen;prohibited|förlorar sin arbetsplats
group;family|Problem i familjen;prohibited|skilsmässa;hospital|sjukdom
group;child|barn;plant|positiva saker;shield|stöd
timeline;clock|i efterhand;document|svåra erfarenheten;person|må dåligt
group;people|familjen;people|vänner;phone|tala
group;person|professionell hjälp
group;person|hälsovårdare;person|läkare;document|just dig
group;people|terapi;medicine|medicinering
group;hospital|sjukhusvård
protect;people|samtala;shield|konfidentiellt
blocked_flow;people|De;document|dina angelägenheter;person|någon annan
group;person|annan sakkunnig;database|dina uppgifter;document|tillstånd
group;person|en närstående person;people|rådfråga;hospital|social- och hälsocentralen
group;warning|mycket allvarliga eller akuta;phone|112
group;warning|självdestruktivitet;warning|kraftig våldsamhet
group;warning|mycket dåligt skick;hospital|akut psykiatrisk sjukhusvård;document|vård mot sin vilja
group;person|läkarens;document|remiss för tvångsvård
group;phone|MIELI rf:s kristelefon;people|människor i kris;people|närstående
group;phone|Samtalen;person|krisarbetare;people|utbildade frivilliga stödpersoner
group;phone|ringer;document|ditt namn
group;phone|kristelefonen;document|oväntad händelse;shield|stödande atmosfär
flow;document|traumatiska upplevelser;shield|söker hjälp
group;warning|förföljelse;prohibited|diskriminering;shield|våld
group;document|Sådana upplevelser;warning|posttraumatiskt stressyndrom
group;document|minnesbilderna;person|medvetandet;warning|kraftig ångest
protect;person|du;shield|tillfriskna
flow;person|Kontakta;hospital|social- och hälsocentral;person|läkare
flow;person|Hen;document|remiss;hospital|fortsatt vård
group;book_pages|studera;work|arbeta;coins|FPA:s stöd för psykoterapi
group;people|rehabiliterande psykoterapi
protect;hospital|A-kliniken;person|dig
group;hospital|polikliniktjänster;medicine|substitutionsbehandling;prohibited|avgiftning
group;hospital|A-kliniker;flag_fi|Finland
protect;hospital|A-kliniken;shield|konfidentiell
group;person|en ung;warning|problem;hospital|ungdomsstationen
group;hospital|Ungdomsstationer;city|många städer
group;person|ensam;people|sina föräldrar;hospital|ungdomsstationen
group;people|AA;document|sina erfarenheter;shield|hjälpa varandra
group;city|större städerna;people|grupper;document|engelska
protect;people|närstående personer;shield|Al-Anon''',
    'sjukdom': '''group;hospital|sjuk;warning|olycka;house|stanna hemma från arbetet
group;shield|finländska sjukförsäkringen;clock|efter en självrisktid;document|söka sjukdagpenning
timeline;calendar|den dag då du insjuknade;calendar|följande nio vardagar
group;calendar|över en månad;work|din arbetsgivare;coins|full lön för självrisktiden
group;coins|Sjukdagpenning;calendar|högst 300 vardagar
group;document|sökas;calendar|inom två månader efter insjuknandet
group;document|ansöka om sjukdagpenning;shield|om du
group;shield|den finländska sjukförsäkringen
group;person|18–67 år gammal
group;prohibited|arbetsoförmögen;hospital|sjukdom
group;work|arbetstagare;shop|företagare;book_pages|studerar på heltid
flow;work|din arbetsgivare;document|ansöker;coins|sjukdagpenningen
flow;coins|sjukdagpenningen;work|din arbetsgivare
flow;court|FPA;coins|sjukdagpenningen;person|dig
group;coins|Sjukdagpenningens belopp;work|inkomsterna
merge;document|ansökan;document|läkarintyg om arbetsoförmåga;paper|bifoga
group;person|18–67-åriga;work|heltidsarbetande anställda eller företagare;shield|sociala tryggheten i Finland
group;medicine|sjuk;work|fortsätta att arbeta;work|återgå till arbetet
group;person|din läkare;work|din arbetsgivare;document|partiell sjukdagpenning
group;person|Företagshälsovårdsläkaren;work|deltidsarbeta;hospital|sjuk
group;warning|funktionsnedsättning eller en sjukdom;calendar|minst ett år;coins|handikappbidrag
group;document|läkarintyg;document|ansöka om handikappbidrag
group;coins|rätt till FPA:s förmåner;calendar|minst tre år;globe|Finland eller i något annat EU- eller EES-land eller i Schweiz
group;coins|Handikappbidrag för vuxna;person|16–64-åringar
group;warning|olägenhet;people|hjälp och handledning;coins|Handikappbidragets storlek
group;house|i hemmet;people|en närstående med funktionsnedsättning;coins|stöd för närståendevård
group;people|funktionshinderservicen;document|rådgivningen om närståendevård
group;child|under 16 år;calendar|minst sex månaders tid;coins|handikappförmån
flow;document|ansöker;child|barn under 16 år;court|FPA
group;coins|Handikappförmånet;calendar|bestämd period
timeline;calendar|perioden har gått;document|ansöka om förlängning
group;child|ett barn;hospital|vård eller rehabilitering;prohibited|kan inte arbeta
contrast;coins|specialvårdspenning;coins|rehabiliteringspenning
group;coins|specialvårdspenning;court|FPA
group;child|under 7 år;hospital|sjukhus- eller poliklinikvården
group;child|7–15 år;hospital|sjukhus- eller poliklinikvården;warning|svår sjukdom
group;child|0–15 år;hospital|rehabiliteringen
group;child|under 16 år;house|hemma;hospital|kopplad till barnets sjukhus- eller poliklinikvård
group;clock|i beredskap;house|skol- eller dagvårdsförsök;warning|svår sjukdom
group;person|En pensionär;calendar|sammanlagt minst ett år;coins|vårdbidrag för pensionstagare
group;people|regelbunden hjälp;shield|handledning och övervakning;coins|stöd
group;coins|Hur stort stöd;people|hur mycket hjälp
flow;person|Du;document|ansöka;court|FPA''',
    'sexuell': '''group;shield|Sexuell hälsa;hospital|reproduktiv hälsa
group;document|Dessa;document|bland annat
protect;shield|förebyggande;hospital|behandling av könssjukdomar
group;condom_pack|preventivmetoder;shield|tillförlitliga
group;calendar|uppföljning;hospital|vård vid graviditet
protect;hospital|förlossningar;shield|trygga
group;document|utredningar;hospital|behandlingar av barnlöshet
protect;hospital|aborter;shield|säkra
group;hospital|hälsostationer;hospital|mödrarådgivningarna;house|skol- och studerandehälsovården
group;coins|avgiftsfria;condom_pack|preventivmedel;person|under 20 eller 25 år
group;house|skolorna;book_pages|sexualundervisning;child|barn och unga
protect;person|den ungas;document|information
protect;shield|främja och skydda;person|den ungas
group;people|sociala färdigheter;shield|emotionella;people|mångfalden av sexuella läggningar och kön
group;book_pages|Forskning;document|information om sexualitet;shield|hälsa
blocked_flow;house|sexualundervisningen;document|tidiga sexuella experiment
group;house|skolan;book_pages|lära sig;shield|naturlig och hälsosam del
group;book_pages|lektionerna;shield|självbestämmanderätt;person|personlig integritet
protect;person|De unga;shield|ingen behöver göra något som den inte vill
group;people|alla parter;shield|tydligt samtycke
group;child|små barn;house|daghemmen;shield|barns integritet
protect;child|Barnen;shield|rätt till fysisk integritet
group;child|Barnen;shield|skydda sig själva;people|med tanke på sin ålder
protect;child|barnen;shield|undvika situationer
protect;child|Barnen;shield|sina gränser
flow;person|du;hospital|mödrarådgivningen;house|familjecentret
group;hospital|rådgivningsbyrån;house|familjecentret;house|hemkommun i Finland
group;hospital|rådgivningsbyrån;coins|inte betala
group;document|asylsökande;hospital|mödrarådgivningen
group;document|utan uppehållstillstånd;hospital|mödrarådgivningen;coins|betala kostnaderna själv
group;person|hälsovårdare;shield|ditt hälsotillstånd;child|babyns hälsa
group;document|anvisningar;shield|trygg graviditet och förlossning
group;document|viktig information;family|barnfamiljer;flag_fi|Finland
group;people|båda föräldrar;hospital|rådgivningsbyrån
group;person|Du;people|stödperson
group;person|sköterskan;people|tolk;calendar|besöken
group;person|Tolken;calendar|vuxen
group;flag_fi|Finland;hospital|privata mödrarådgivningar
group;hospital|privata hälso- och sjukvårdstjänster;coins|avgiftsbelagda
group;person|kvinnorna;hospital|sjukhus;flag_fi|Finland
flow;people|Fråga;hospital|mödrarådgivningen;hospital|vilket sjukhus
group;house|hemkommun i Finland;hospital|förlossningen;coins|inte särskilt mycket
group;person|andra förälder;hospital|förlossningen
group;people|annan släkting;person|en vän
flow;person|du;people|prata;hospital|rådgivningsbyrån
group;shield|hjälp;warning|rädslan;hospital|polikliniken för förlossningsrädsla
group;condom_pack|kondomer;shop|affärer;pharmacy|apotek
group;condom_pack|kondomer;document|inget recept
group;medicine|p-piller;person|läkaren;document|recept
flow;document|receptet;medicine|dina piller;pharmacy|apoteket
flow;calendar|Boka en tid;person|läkaren;document|receptet
group;child|minderårig;document|receptet;people|vårdnadshavarens tillstånd
group;city|Vissa områden;person|unga;condom_pack|kostnadsfria preventivmedel
branch;people|fråga;hospital|social- och hälsocentralen;person|hälsovårdaren på din skola
group;hospital|Barnlöshet;shield|behandlas
group;person|kvinnan;person|mannen;document|Orsaken till barnlöshet
group;document|medicinsk orsak;prohibited|ingen
contrast;hospital|offentliga;hospital|privata kliniker
group;calendar|kvinnans ålder;shield|rätten till fertilitetsbehandling;hospital|offentliga hälsovårdstjänsterna
group;warning|misstänker;hospital|social- och hälsocentralen;hospital|privat läkarstation
group;phone|kontakta;hospital|preventivmedels- och familjeplaneringsrådgivningen
flow;people|Fråga;hospital|social- och hälsocentral
group;condom_pack|kondom;barrier_sheet|slicklapp;shield|de flesta könssjukdomarna
group;document|papperslösa;document|asylsökande;hospital|behandling för könssjukdomar
group;flag_fi|Finland;document|utan uppehållstillstånd;coins|betala för vården''',
}

LOGIC = {
    'psykisk': {
        2: 'Examples of protective factors; no guarantee that relationships or lifestyle prevent every disorder.',
        3: 'Equal importance of mental and physical wellbeing; do not rank them by invented numerical scores.',
        4: 'Often, among examples, family/community/religious belief/equal treatment support newcomers. No real photographed person is assigned migrant or religious status.',
        7: 'New language/cultural challenges MAY cause difficulties, not an inevitable diagnosis.',
        9: 'Illustrative disorder categories, not a diagnostic checklist or an equation between sadness and depression.',
        10: 'IF services needed, source first step is appointment with nurse OR doctor at own centre.',
        11: 'Clinical assessment of needed help; no self-diagnosis or treatment selected by diagram.',
        12: 'Clinician MAY write referral to psychiatric outpatient clinic OR another service, not automatic hospital admission.',
        13: 'Care generally includes conversation; medication is USUALLY ALSO included. No universal drug requirement, brand, dose, self-medication or exact schedule.',
        16: 'Private doctor costs substantially more than public centre in the archived source; no invented price or paid/free blanket claim.',
        17: 'IF urgent care needed, MAY call health centre OR hospital with emergency duty; no invented local opening hours.',
        19: 'IF child/youth has mental-health problems, parents MAY contact own wellbeing-area family counselling; no identifiable child labelled a patient.',
        22: 'Alcohol and illicit-drug categories in source context. Do not label legitimate prescribed medicine as illegal.',
        23: 'Archived list of illicit-use substances, including opioid term, not a statement that every prescribed opioid medicine is unlawful. No branded medication or consumption method.',
        24: 'Preserve archived broad wording about drugs; avoid visually extending this statement to lawful prescription treatment.',
        25: 'Possession/sale refers to prior illicit-drug context. Fine OR imprisonment; not both necessarily and no sentence length.',
        26: 'IF substance or another dependence -> possible help at three service categories. No promise of a particular place or immediate appointment.',
        27: 'Dependencies MAY harm user/player AND close people; do not identify a photographed person as dependent.',
        28: 'Economic problems are OFTEN associated, not an inevitable debt or invented money amount.',
        31: 'Free care and detoxification refer to A-clinics in this source context, not all private health services.',
        32: 'Detoxification described as stopping use DURING TREATMENT. Do not depict unsupervised abrupt cessation as a self-care instruction.',
        33: 'Services exist in MANY cities, not every municipality; no site/location invented.',
        34: 'Harm-reduction exchange of used syringes FOR NEW ones, not reusing or sharing the same syringe. Show bare isolated medical objects, no injection procedure.',
        36: 'Health-purpose distribution of free syringes; do not conflate with illegal-drug supply or prescribed medicines.',
        37: 'IF dirty syringes used, diseases can spread through them. No route-of-administration demonstration, dosage or infection-rate claim.',
        38: 'Counselling can connect to detoxification; not guaranteed admission and not encouragement to self-detox.',
        40: 'Examples of demanding situations, not evidence that every migrant or unemployed person is mentally ill.',
        42: 'Even positive events MAY create support needs; no pathological claim about having children.',
        43: 'Distress MAY emerge later, after difficult events have calmed; timeline does not assert it always will.',
        44: 'OFTEN conversation helps; no cure guarantee or substitute-for-urgent-care instruction.',
        45: 'SOMETIMES professional help also needed.',
        46: 'Individual discussion with nurse/doctor about suitable support; no diagram chooses a medication.',
        47: 'OFTEN therapy OR medication OR a combination helps. Neither always both nor guaranteed recovery; no drug names or dosing.',
        48: 'SOMETIMES hospital care needed, not automatic admission following outpatient therapy.',
        49: 'Professional conversation is confidential as stated in source; no identifiable case records.',
        50: 'Source confidentiality statement; preserve literal punctuation and do not invent statutory exceptions or disclose an actual person data.',
        51: 'IF another professional needs records, applicant separately asked for permission to disclose; no automatic public sharing.',
        52: 'Concern AND belief relative may need help -> may ask nurse/doctor for advice; no diagnosis by appearance.',
        53: '112 ONLY in the source very-serious-or-acute symptom condition. Do not give 112 as the routine line for all distress.',
        54: 'Examples explaining preceding severe/acute condition; non-graphic symbols only, no staged self-harm or violence.',
        55: 'Very poor condition AND need for ACUTE PSYCHIATRIC HOSPITAL CARE -> involuntary care MAY occur. No arbitrary detention implication.',
        56: 'Physician referral is required for preceding involuntary-care context; do not show police deciding alone.',
        59: 'Caller need not give name to this crisis helpline; not a blanket claim about anonymous clinical records.',
        61: 'After difficult traumatic experiences, source encourages seeking help; no trauma assigned to real person.',
        62: 'Possible trauma contexts are examples. Never stage sexual violence, war injuries, torture or abuse.',
        63: 'Experiences MAY cause PTSD, not certain diagnosis.',
        64: 'Source description of intrusive memories and severe anxiety; no replay of graphic scenes.',
        65: 'Recovery is possible and help available; no timeline or guaranteed outcome.',
        67: 'Referral IF needed, not automatic referral for every visitor.',
        68: 'Difficulty studying/working DUE TO mental ill-health -> MAY POSSIBLY APPLY for Kela psychotherapy support. Not automatic eligibility or payment.',
        69: 'Name of preceding supported therapy; retain reference to source 68.',
        71: 'Examples of A-clinic services; substitution treatment is medically provided treatment, not the illicit-drug context of source 24.',
        74: 'Youth with alcohol/drug/gambling problem MAY get youth-clinic help. Neutral symbolic people only.',
        76: 'Youth may attend ALONE OR with parents; do not require parents for all visits.',
        77: 'Peer-support association, not clinical detoxification or guaranteed cure. Literal archived AA on är wording remains in source.',
        78: 'Groups in many places; ENGLISH groups specifically in LARGER CITIES, not promised everywhere.',
        79: 'Al-Anon support is for close people of someone with alcoholism, distinct from AA member self-support.',
    },
    'sjukdom': {
        1: 'IF sick OR accident -> source right to stay home from work. No duration or automatic sick-pay claim.',
        2: 'Covered by FINNISH HEALTH INSURANCE AND AFTER waiting period -> right to APPLY for sickness allowance. Not immediate or automatic payment.',
        3: 'USUALLY illness day PLUS following NINE WEEKDAYS; not nine calendar days or total nine including illness day.',
        4: 'Employment lasted MORE THAN ONE MONTH before illness -> employer full salary DURING waiting period. Not every worker or all sickness time.',
        5: 'MAXIMUM 300 WEEKDAYS, not calendar days or a guarantee of the maximum.',
        6: 'Apply WITHIN TWO MONTHS AFTER illness began; do not invent an absolute date.',
        7: 'Introduces cumulative eligibility list; right to apply, not granted benefit.',
        8: 'Finnish health-insurance coverage is one list condition, not sufficient by itself.',
        9: 'Age 18 THROUGH 67, alongside the other list conditions.',
        10: 'Unable to work BECAUSE of illness; do not equate any diagnosis with work incapacity.',
        11: 'Listed employment/study/job-seeking/own-household statuses are ALTERNATIVES within this item; not all simultaneously required.',
        12: 'IF salary paid during sick leave, EMPLOYER applies for sickness allowance.',
        13: 'Payment to employer ONLY in preceding salary-paid case. Never show all benefits automatically going to employer.',
        14: 'Long illness AND employer no longer pays sick-leave salary -> Kela pays APPLICANT. Both gates required.',
        15: 'Amount depends on earnings; no invented rate or guaranteed full wage replacement.',
        16: 'Attach medical work-incapacity certificate to allowance application, not a generic prescription.',
        17: 'PARTIAL sickness allowance: age 18–67 AND full-time employee OR entrepreneur AND Finnish social-security coverage. Do not use adult disability-benefit 16–64 range.',
        18: 'Purpose is continued/returned work despite illness; no claim everyone should work while sick.',
        19: 'Discuss FIRST with occupational physician AND employer about applying; no unilateral work instruction.',
        20: 'Occupational physician determines whether part-time work is possible during illness.',
        21: 'Disability OR illness impairs functioning CONTINUOUSLY for AT LEAST ONE YEAR -> MAY get disability allowance. Distinct from pensioner TOTAL year in source 40.',
        22: 'Medical certificate REQUIRED to APPLY; still no guarantee of grant.',
        23: 'Entitled to Kela benefits AND AT LEAST THREE YEARS residence in Finland OR other EU/EEA country OR Switzerland. Country alternatives do not replace shared entitlement/time gates.',
        24: 'Adult DISABILITY allowance source age 16–64; separate from sickness/partial-sickness source age 18–67. Preserve archived wording.',
        25: 'Amount depends on impact and need for help/guidance; no invented payment bands.',
        26: 'IF caring AT HOME for close person with disability, MAY receive informal-care support from OWN WELLBEING AREA, not automatically Kela.',
        28: 'Child UNDER 16 AND due to illness/disability needs REGULAR care, attention and rehabilitation for AT LEAST SIX MONTHS -> MAY receive benefit. Preserve all gates.',
        29: 'Application at Kela, child UNDER 16; not automatic payment.',
        30: 'USUALLY fixed period; preserve literal archived Handikappförmånet spelling.',
        31: 'When that period ends, MAY APPLY for extension. No automatic renewal.',
        32: 'Must participate in care/rehabilitation of severely ill/disabled child AND cannot work BECAUSE OF THAT -> MAY APPLY for special-care allowance.',
        33: 'Rehabilitation allowance is an ALTERNATIVE during child rehabilitation, not an additional simultaneous identical payment.',
        34: 'Header: MAY get special-care allowance IF one of following source-listed situations; preserve preceding inability-to-work context.',
        35: 'Participating in hospital OR outpatient care of child UNDER 7. Do not silently add the explicit severe-illness qualifier from next age case to this literal item.',
        36: 'Participating in hospital OR outpatient care of child age 7–15 WITH SEVERE illness; severity belongs to this case.',
        37: 'Participating in rehabilitation of child age 0–15; not child under 7 only.',
        38: 'Child UNDER 16 WITH SEVERE illness AND HOME care LINKED to hospital/outpatient care. All cumulative, no unconditional home-care benefit.',
        39: 'On standby during SCHOOL/DAYCARE TRIAL associated with severe illness. Not general standby for any school day.',
        40: 'PENSIONER whose functioning impaired due to illness/injury for a TOTAL of AT LEAST ONE YEAR -> MAY get pensioner care allowance. Total is not continuous source-21 requirement.',
        41: 'IF due to disability/illness needs regular help OR guidance AND supervision as source phrased; preserve wording without silently simplifying conjunction scope.',
        42: 'Amount depends on help needed, not income necessarily; no invented values.',
        43: 'PENSIONER care-allowance application to Kela; no conflation with adult/child disability allowance.',
    },
    'sexuell': {
        1: 'General sexual/reproductive health relationship, no sexual act depicted.',
        2: 'Introduces non-exhaustive list of health topics, not separate medical advice.',
        4: 'Modern reliable contraception category; do not imply one method prevents both pregnancy and every STI.',
        6: 'Safe childbirth goal, not a guarantee of zero risk.',
        7: 'Infertility investigations/treatment, no blame or identity assigned to real couple.',
        8: 'Access to SAFE abortion; no procedure or self-treatment instructions.',
        10: 'SOME areas offer FREE contraception to young people UNDER 20 OR 25 according to area. Not nationwide, not uniform under-25 entitlement.',
        11: 'Education appropriate to AGE AND DEVELOPMENT LEVEL; never sexualised imagery of minors.',
        13: 'Support/protection of youth development; no explicit activity.',
        14: 'Emotional/social skills and diversity; neutral symbolic people, no orientation assigned to photographed people.',
        16: 'Research statement: education DOES NOT lead to early experimentation OR affect youth sexual identity. Do not draw an arrow implying it does.',
        18: 'Self-determination and personal integrity; no genital illustration needed.',
        19: 'No one needs to do unwanted sexual things; no pressure or act staged.',
        20: 'ALWAYS CLEAR CONSENT OF ALL PARTIES. Do not substitute marriage, silence or a majority vote for consent. No written form or signature requirement is stated; use a consent/protection glyph instead of a signed document.',
        21: 'Emotional/body-boundary education MAY begin for small children; entirely non-sexual clothed symbols.',
        23: 'AGE-APPROPRIATE body respect/protection and response to unwanted touching; no touching or anatomy demonstration.',
        24: 'Skills MAY help avoid harassment; not a guarantee or victim-blaming responsibility.',
        26: 'On discovering pregnancy, contact local maternity clinic OR family centre. Do not show all pregnancy care routed only to hospital.',
        27: 'Use of these services IF Finnish home municipality; preserve next asylum/no-permit cases separately.',
        28: 'No fee for referenced counselling-clinic services, not all private healthcare or childbirth.',
        29: 'Asylum applicants ALSO can use maternity services; no actual applicant photo.',
        30: 'Without residence permit MAY still use maternity care, but OFTEN must pay own costs. Never imply denial of care or universal free care.',
        31: 'Nurse monitors pregnant person and baby health; no diagnostic output or treatment instructions.',
        34: 'BOTH parents welcome, no compulsory attendance of both.',
        35: 'IF desired may request support person; not a mandatory guardian.',
        36: 'IF interpreter needed, nurse MAY arrange interpreter at visits. No promised language roster.',
        37: 'Interpreter must be ADULT; do not depict child interpreting.',
        39: 'PRIVATE health services are charged; distinguish from clinic free-service source 28.',
        40: 'Women MOST OFTEN give birth at hospital, not always.',
        42: 'IF Finnish home municipality, childbirth not particularly expensive in archived source. Not free, no price, no nationality-based rule.',
        43: 'Other parent MAY accompany childbirth; no guarantee of presence regardless of all circumstances.',
        44: 'IF desired may ask another relative OR friend to accompany; not compulsory.',
        45: 'IF childbirth fear, discuss at counselling; no diagnosis by diagram.',
        46: 'MAY get help, specialised clinic is EXAMPLE; no cure or appointment guarantee.',
        47: 'CONDOMS obtainable at listed retail categories; show isolated sealed supply objects, no demonstration of use.',
        48: 'NO PRESCRIPTION refers ONLY to CONDOMS from preceding source 47. Never extend to contraceptive pills in next source.',
        49: 'Contraceptive PILLS require PHYSICIAN PRESCRIPTION. Distinct from condom retail route; no brand, dosage or recommendation.',
        50: 'WITH PRESCRIPTION obtain those pills at PHARMACY, not ordinary grocery retail.',
        51: 'Physician appointment for that prescription; no automatic issue promised.',
        52: 'MINOR does NOT need guardian PERMISSION FOR THIS PRESCRIPTION. Not a claim that prescription itself is unnecessary, or that parents are forbidden from involvement.',
        53: 'SOME AREAS free youth contraception, not universal geography or age cut-off here.',
        55: 'Infertility can OFTEN be treated, not guaranteed pregnancy.',
        56: 'Cause MAY lie with woman OR man; no blame or stereotype.',
        57: 'SOMETIMES no medical cause found, not proof absence of infertility.',
        58: 'Both public and private clinics; no automatic public entitlement.',
        59: 'Woman age is an EXAMPLE affecting right to PUBLIC fertility treatment; no cut-off value invented.',
        60: 'IF suspected STI, MAY book public social/health centre OR private physician. No diagnosis from symptoms alone.',
        61: 'In SOME areas may contact contraception/family planning clinic; not guaranteed nationwide.',
        62: 'Literal archived din egen på wording stays unchanged; no silent source repair.',
        63: 'Condom OR dental dam protects against MOST STIs, not all; no intercourse, placement or use demonstration.',
        64: 'Undocumented people AND asylum applicants have right to STI treatment; no pictured person assigned status.',
        65: 'Without residence permit MAY need to pay; right to treatment is not the same as universal free care.',
    },
}

# Each value is one literal source bar; all other modality remains explicit in
# required_logic and exact bilingual source. Never overlap multiple bars.
BARS = {
    'psykisk': {2: 'till exempel', 4: 'ofta', 7: 'kan', 9: 'till exempel',
        10: 'Om man behöver mentalvårdstjänster', 12: 'kan', 13: 'vanligtvis också',
        17: 'Om man behöver brådskande vård', 19: 'Om', 25: 'eller', 26: 'Om',
        27: 'kan', 28: 'ofta', 30: 'kan', 31: 'gratis', 32: 'under behandlingen',
        33: 'I många städer', 36: 'av hälsoskäl', 37: 'Om', 38: 'kan', 40: 'till exempel',
        41: 'kan', 42: 'kan', 43: 'Ibland', 44: 'Ofta', 45: 'Ibland',
        47: 'eller en kombination av båda', 48: 'Ibland', 49: 'konfidentiellt',
        51: 'tillfrågas du separat om tillstånd', 52: 'kan', 53: 'Om symtomen är mycket allvarliga eller akuta',
        54: 'till exempel', 55: 'kan', 56: 'behövs läkarens remiss', 59: 'inte uppge ditt namn',
        61: 'Om', 62: 'kan', 63: 'kan', 65: 'kan', 67: 'vid behov',
        68: 'kan du eventuellt ansöka', 70: 'kan', 71: 'bland annat', 73: 'konfidentiell',
        74: 'kan', 76: 'ensam eller med sina föräldrar', 78: 'i de större städerna'},
    'sjukdom': {1: 'Om', 2: 'efter en självrisktid', 3: 'vanligen', 4: 'Om',
        5: 'högst', 6: 'inom två månader efter insjuknandet', 7: 'kan ansöka',
        11: 'eller', 12: 'Om du får lön under sjukledigheten', 14: 'och',
        17: 'omfattas av den sociala tryggheten i Finland', 19: 'först',
        21: 'sammanhängande under minst ett år', 22: 'måste', 23: 'och',
        26: 'kan', 28: 'regelbunden vård, omsorg och rehabilitering', 30: 'vanligtvis',
        31: 'kan man ansöka', 32: 'och kan inte arbeta på grund av det',
        33: 'under rehabilitering av barnet', 34: 'om du',
        36: 'som har en svår sjukdom', 38: 'som har en svår sjukdom',
        39: 'i anslutning till en svår sjukdom', 40: 'sammanlagt minst ett år',
        41: 'om', 43: 'kan ansöka'},
    'sexuell': {2: 'bland annat', 10: 'En del områden', 11: 'enligt sin ålder och utvecklingsnivå',
        15: 'Forskning visar', 16: 'inte', 19: 'ingen behöver göra något som den inte vill',
        20: 'alltid ett tydligt samtycke av alla parter', 21: 'kan',
        23: 'på ett lämpligt sätt med tanke på sin ålder', 24: 'kan',
        27: 'om du har en hemkommun i Finland', 30: 'oftast', 35: 'Om du vill',
        36: 'Om du behöver tolk', 37: 'vuxen', 39: 'avgiftsbelagda', 40: 'oftast',
        42: 'Om du har en hemkommun i Finland', 43: 'kan', 44: 'Om du vill',
        45: 'Om du är rädd inför förlossningen', 46: 'till exempel', 49: 'ett recept från läkaren',
        52: 'inte ha vårdnadshavarens tillstånd för receptet', 53: 'Vissa områden',
        55: 'oftast', 56: 'kan', 57: 'Ibland', 59: 'till exempel', 60: 'Om du misstänker',
        61: 'I vissa områden', 63: 'de flesta', 65: 'kan'},
}
CONTEXT = {
    'psykisk': {15: [14], 21: [20], 24: [22], 25: [24], 28: [27],
        30: [29], 31: [29], 32: [29, 31], 34: [33], 36: [33], 37: [34],
        47: [46], 50: [49], 54: [53], 56: [55], 59: [57], 63: [62],
        64: [63], 67: [66], 69: [68], 71: [70], 73: [70], 76: [74], 78: [77]},
    'sjukdom': {3: [2], 6: [5], 8: [7], 9: [7], 10: [7], 11: [7],
        13: [12], 24: [21], 30: [28], 31: [30], 35: [32, 34],
        36: [32, 34], 37: [32, 34], 38: [32, 34], 39: [32, 34],
        41: [40], 42: [40], 43: [40]},
    'sexuell': {2: [1], 3: [1], 4: [1], 5: [1], 6: [1], 7: [1], 8: [1],
        28: [27], 29: [26], 30: [26], 37: [36], 39: [38],
        48: [47], 50: [49], 51: [49], 52: [49], 54: [53], 57: [55],
        59: [58], 61: [60], 62: [60], 65: [64]},
}
SUPPORTED = {'parties', 'person', 'people', 'work', 'court', 'prohibited',
    'police', 'document', 'calendar', 'database', 'coins', 'shop', 'window',
    'traffic', 'car', 'house', 'shield', 'bank', 'hospital', 'factory', 'field',
    'plant', 'tree', 'ship', 'laptop', 'phone', 'flask', 'gear', 'bulb', 'ball',
    'family', 'child', 'globe', 'warning', 'flag_fi', 'flag_eu', 'clock', 'food',
    'paper', 'book_pages', 'bottle', 'germ', 'medicine', 'pharmacy'}
ALIASES = {'city': 'house'}
CUSTOM = {
    'syringe': 'Isolated bare medical syringe object, no dose markings, patient, injection site, preparation or use sequence; distinguish old/new with exact labels and source exchange arrows.',
    'condom_pack': 'Sealed, unbranded condom wrapper/object; no person, anatomy, placement or use demonstration. Must differ visibly from prescription-pill medicine icon.',
    'barrier_sheet': 'Flat unbranded dental-dam barrier sheet as a medical object; no person, anatomy, placement or use demonstration.',
}

handoff = []
for slug, raw in PLANS.items():
    section_id = 'hb-c10-' + slug
    source_path = ROOT / 'studio/episodes' / section_id / 'script.yaml'
    fingerprint = hashlib.sha256(source_path.read_bytes()).hexdigest()
    script = yaml.safe_load(source_path.read_text())
    rows = script['sentences']
    lines = raw.splitlines()
    assert len(lines) == len(rows), (slug, len(lines), len(rows))
    plans = []
    for number, (line, row) in enumerate(zip(lines, rows), 1):
        composition, *nodes = line.split(';')
        references = [number] + CONTEXT.get(slug, {}).get(number, [])
        context = ' '.join(rows[index - 1]['sv'] for index in references)
        parsed = []
        for value in nodes:
            kind, label = value.split('|', 1)
            kind = ALIASES.get(kind, kind)
            assert kind in SUPPORTED or kind in CUSTOM, kind
            match = re.search(re.escape(label), context, re.I)
            assert match, (slug, number, label)
            node = dict(label=match.group(), icon=kind)
            if kind in CUSTOM:
                node['custom_icon_request'] = CUSTOM[kind]
                node['acquisition_status'] = 'Advisory only; C10 owner must draw or acquire/verify this physical object. No false supported-icon claim.'
            parsed.append(node)
        logic = LOGIC.get(slug, {}).get(number,
            'Picture only the exact source concepts and relationships. No diagnosis, invented eligibility, treatment guarantee, dosage, administration instruction or identifiable patient status.')
        plan = dict(id=f'picture-{number:03}', visual_type='diagram',
                    composition=composition, nodes=parsed, description=logic,
                    required_logic=logic, source_text=row['sv'],
                    reviewed_translation=row['ru'],
                    source_sentence_ids=[rows[index - 1]['sentence_id'] for index in references],
                    advisory_only=True)
        if number in BARS.get(slug, {}):
            label = BARS[slug][number]
            assert label in context, (slug, number, label)
            scope = list(range(len(parsed)))
            if slug == 'psykisk' and number == 13:
                scope = [1]
            if slug == 'psykisk' and number == 78:
                scope = [2]
            plan['conditions'] = [dict(label=label, node_indices=scope)]
            plan['condition_layout_advisory'] = 'Inspect the single literal bar at final font/size; every further gate remains explicit in required_logic and full bilingual source. Do not drop qualifications to fit.'
        if (slug == 'psykisk' and number in [25, 50, 59]
                or slug == 'sexuell' and number in [16, 48, 52, 57]):
            if slug == 'sexuell' and number == 48:
                plan['nodes'][1]['crossed'] = True
            elif slug == 'sexuell' and number == 52:
                plan['nodes'][2]['crossed'] = True
            elif slug == 'psykisk' and number == 59:
                plan['nodes'][1]['crossed'] = True
        if (any(node['icon'] in CUSTOM for node in parsed)
                or slug == 'psykisk' and number in [8, 10, 14, 17, 18, 20, 29, 33, 39, 57, 66, 72, 75]
                or slug == 'sjukdom' and number in [6, 12, 16, 19, 22, 27, 29, 43]
                or slug == 'sexuell' and number in [9, 26, 31, 38, 41, 49, 50, 51, 54, 58, 60]):
            plan['photo_request'] = dict(
                subject='Verified neutral institution exterior/sign or isolated unbranded source object relevant to this exact row. No identifiable patient, diagnosis, addiction, migration status, sexual activity or medical record.',
                acquisition_status='Advisory request only; identity/rights/credit must be researched by C10 owner.',
                fallback='Source-specific original pictorial composition; custom physical-object requests must be fulfilled rather than silently substituted with an unrelated icon.',
            )
        plans.append(plan)
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == fingerprint
    output = HERE / (section_id + '.json')
    output.write_text(json.dumps(plans, ensure_ascii=False, indent=2) + '\n')
    handoff.append(dict(section_id=section_id, plans=len(plans),
                        source_script_sha256=fingerprint,
                        source_pairs_read=len(plans),
                        advisory_plan=str(output.relative_to(ROOT)),
                        root_episode_unchanged=True,
                        custom_icon_requests=sorted({node['icon'] for plan in plans for node in plan['nodes'] if node['icon'] in CUSTOM}),
                        layout_status='Advisory only; actual layout, licensed photos, custom object drawing and medical-source listening remain with C10 producer.'))
(HERE / 'chapter09a-handoff.json').write_text(json.dumps(dict(
    scope='187 exact-source advisory pairs only; C10 scripts/media/jobs untouched.',
    episodes=handoff, total_pairs=sum(row['plans'] for row in handoff),
    source_wording_priorities=[
        'Psykisk hb-c10-u0138-s001: literal archived AA on är preserved; no silent repair.',
        'Sjukdom hb-c10-u0209-s003: literal Handikappförmånet preserved.',
        'Sexuell hb-c10-u0172-s003: literal din egen på preserved; no silent repair.',
        'Archived broad illicit-drug wording must not be visualised as prohibiting lawful prescription medicines.',
    ],
    custom_icon_requests=CUSTOM,
    custom_icon_implementation='studio/production/health-plans/medical_object_icons.py',
    custom_icon_preview='studio/production/health-plans/medical-object-advisory-preview.png',
), ensure_ascii=False, indent=2) + '\n')
print('Wrote', len(handoff), 'health advisory plans,', sum(row['plans'] for row in handoff), 'exact source pairs.')
