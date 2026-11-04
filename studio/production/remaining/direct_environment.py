"""Direct the environment episode from each exact source statement."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from author import apply

ROWS=[
('energy','object','spara energi','bulb',None,None,'Actual LED bulb or original bulb illustration: an energy-saving object, without an invented saving percentage.'),
('bills','merge','energi','bulb','vatten','water','Energy and water saving jointly reduce bills; two inputs converge on a bill/coin object rather than implying energy causes water.'),
('environment','flow','spara energi','bulb','miljön','tree','Energy saving supports environmental protection; only the source-stated relationship.'),
('home_water','object','vatten','water',None,None,'Actual running tap as a concrete household water-use object; no claim about its precise consumption.'),
('climate_protection','flow','mindre energi','bulb','skydda jorden','globe','Less energy use supports protection of Earth from climate change, without numerical trends.'),
('temperature','pair','jorden','globe','gradvis ökar','thermometer','Earth and a thermometer depict gradual warming qualitatively; no invented temperature value.'),
('life','group','människornas','people','djurens liv','paw','Human and animal life across Earth; no pictured individual is labelled as a climate victim.'),
('agriculture','pair','temperaturen','thermometer','jordbruk','field','Warmer conditions and agricultural difficulty shown with a thermometer and field; no fabricated crop-loss figures.'),
('extremes','contrast','torrare och varmare','fire','fuktigare eller kallare','water','Contrasting dry/hot and wet/cold conditions, preserving the source contrast without attributing a particular event.'),
('danger','warning','människorna','people','vår livsmiljö','tree','Warning over human life and habitat, expressing only the stated danger.'),
('species_loss','pair','Sjukdomar sprider sig','germ','djurarter dör ut','paw','Two parallel source consequences, disease spread and species loss; no arrow claiming one directly causes the other.'),
('conservation','group','djur- och växtarter','tree','naturens mångfald','flower','Accurately identified Finnish protected forest photograph or biodiversity still life, not a fabricated species inventory.'),
('biodiversity','group','djur','paw','växter','flower','Different organism categories illustrate biodiversity without counts or named species not in the source.'),
('human_effects','warning','nedskräpning','bottle','förorening','water','Litter and pollution pictorial examples; no invented chemical,spill location or quantitative pollution data.'),
('law','protect','Miljöskyddslagen','document','natur och miljö','tree','Source-named environmental law protects the depicted natural environment; no additional legal rule.'),
('protection_sources','group','finsk lag','flag_fi','EU-lagstiftning','flag_eu','Finnish and EU legal protection shown with accurate flags, alongside natural habitat; no invented borders or member list.'),
('ministry_1983','timeline','Miljöministeriet','bank','år 1983','calendar','The named ministry and its exact source founding year; generic institutional icon rather than an unverified building identity.'),
('sustainability','pair','naturresurserna','tree','naturens mångfald','flower','Natural resources and biodiversity as the two explicit monitoring subjects, without new sustainability thresholds.'),
('animal_categories','group','vilda djur','paw','husdjur','cow','Wild,domestic and companion animal categories under the stated ethical-treatment principle; no invented husbandry conditions.'),
('animal_welfare','protect','Djurskyddslagen','document','djurens välmående','paw','Animal-welfare law and protected animal symbol, avoiding graphic anatomy or claims about a photographed animal.'),
('care_conditions','pair','djur ska skötas','paw','omständigheter','house','Animal care and conditions shown schematically; no particular enclosure dimension is asserted.'),
('livestock','pair','Myndigheterna','bank','produktionsdjur','paw','Actual identified cattle photograph or an authority/animal supervision diagram, without identifying a photographed farmer status.'),
('pets','pair','hundar och katter','paw','sällskapsdjuren','house','Actual dog-and-cat photograph, correctly identified as companion-animal context.'),
('city_country','contrast','människor i städer','bank','på landet','house','City and countryside pet settings; no inference about the ownership or residence of a pictured individual.'),
]


def main():
    plans=[]
    for name,composition,label1,icon1,label2,icon2,description in ROWS:
        nodes=[dict(label=label1,icon=icon1)]
        if label2:nodes.append(dict(label=label2,icon=icon2))
        if name=='bills':nodes.append(dict(label='blir lägre',icon='coins'))
        if name=='life':nodes.append(dict(label='hela jordklotet',icon='globe'))
        if name=='biodiversity':nodes.append(dict(label='andra organismer',icon='plant'))
        if name=='protection_sources':nodes.append(dict(label='naturen',icon='tree'))
        if name=='animal_categories':nodes.append(dict(label='sällskapsdjur',icon='pet'))
        plans.append(dict(id=name,description=description,visual_type='diagram',composition=composition,nodes=nodes))
    apply('hb-c11-miljo',plans,
          'Exact consecutive source topics: household saving,climate consequences,biodiversity,environmental institutions and ethical animal care. Every source sentence appears once in stored order.',
          'Comfortable Mystery 2 — Kevin MacLeod,CC BY4.0',
          'Distinct source-verified Finnish national-park landscape photograph,continuous decorative natural context.')


if __name__=='__main__':main()
