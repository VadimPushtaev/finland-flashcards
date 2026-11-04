"""Source-specific sorting,return and material-reuse illustrations."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from author import apply


def picture(name,composition,description,*nodes,**extra):
    values=[dict(label=n[0],icon=n[1],**(n[2] if len(n)>2 else {})) for n in nodes]
    return dict(id=name,composition=composition,description=description,visual_type='diagram',nodes=values,**extra)


P=picture
PLANS=[
P('home_sort','flow','Sort at home before placing waste into its bin; household-to-bin process.',('hemma','house'),('sopkärlet','bin')),
P('material_examples','group','Three representative named materials from the longer source list; no invented universal bin colors.',('papper','paper'),('kartong','cardboard'),('glasförpackningar','bottle')),
P('new_products','flow','Correctly sorted waste can become new products; the first label retains the sorting condition.',('soporna sorteras rätt','bin'),('nya produkter','factory')),
P('local_instructions','pair','Instructions vary by locality; document and local setting without a fabricated municipality-specific rule.',('Anvisningarna','document'),('olika delar av landet','house')),
P('bin_labels','pair','The source directs attention to instructions at the building waste bins.',('Anvisningarna','paper'),('sopbehållarna','bin')),
P('ask_contact','branch','Contact either municipality or landlord when instructions are absent; parallel alternatives.',('kontakta','phone'),('kommunen','bank'),('hyresvärd','person'),connective='eller'),
P('no_dumping','blocked_flow','Prohibited dumping in the forest as one explicit example; main panel retains window and street prohibitions too.',('avfallet','bottle'),('skogen','tree')),
P('by_material','group','Waste and a representative material object emphasize material-based sorting,not an added color scheme.',('avfallet','bin'),('material','cardboard')),
P('not_drain','blocked_flow','No chemicals into the drain,one named example of prohibited disposal; retain the original source spelling kemikaler.',('kemikaler','flask'),('avloppet','sink')),
P('hazard_collection','flow','Hazardous waste goes to a collection point,not an ordinary household bin.',('farligt avfall','battery'),('insamlingsställe','collection')),
P('available_bins','group','Some buildings lack some collection-bin types; retain the explicit not-always qualifier.',('alla hus','house'),('samtliga insamlingskärl','bin'),conditions=[dict(label='inte alltid',node_indices=[1])]),
P('not_other_house','blocked_flow','Do not transfer own waste to bins belonging to another building.',('ditt eget avfall','bin'),('ett annat hus','house')),
P('not_business','blocked_flow','Business waste must not be placed in the own-home bins; no invented business exemption.',('ditt företag','factory'),('ditt eget hus','house')),
P('resources','protect','Natural resources and environment under the source conservation principle.',('naturresurser','tree'),('miljön','globe')),
P('collection_transport','flow','Household waste moves from collection bins to transport; no specific route or company invented.',('hushållens sopor','bin'),('transporteras bort','truck')),
P('reuse_savings','split','Material reuse saves both resources and money; two parallel effects,not a required sequence.',('användas på nytt','cardboard'),('naturresurser','tree'),('pengar','coins')),
P('less_landfill','object','Qualitative decrease in waste sent to landfill,without invented quantities.',('minskar mängden avfall','landfill_down')),
P('bad_sorting_costs','flow','Incorrect sorting slows management and causes extra costs; warning marks the error,not normal use of bins.',('sorterar avfallet fel','bin_warning'),('långsammare','clock'),('extra avgifter','coins')),
P('shared_costs','pair','The source says everyone bears those costs; no currency amounts or distribution invented.',('Alla människor','people'),('dessa avgifter','coins')),
P('housing_extra','merge','Either bad sorting OR waste left next to bins can cause extra building fees; explicit OR junction.',('avfallet är dåligt sorterat','bin_warning'),('avfall har lämnats bredvid sopkärlen','bag'),('extra avgifter','coins'),connective='eller'),
P('housing_charges','flow','The costs affect housing charges and rents; no invented increase percentage.',('Detta','coins'),('vederlagen och hyrorna','house')),
P('biowaste_examples','group','Representative food residues and peels from the source list,not an exhaustive added list.',('matrester','food'),('fruktskal','fruit_peel'),('äggskal','eggshell')),
P('compost_soil','flow','Biowaste compost becomes soil; no new composting instructions.',('Bioavfallet','food'),('mylla','soil')),
P('cardboard_types','group','Three named cardboard package types.',('matförpackningar av papp','cardboard'),('papplådor','cardboard'),('mjölk- och saftförpackningar','milk_carton')),
P('rinse_dry','pair','Rinsing when needed and exclusion of wet packaging remain separate conditions.',('sköljas','water'),('inga våta förpackningar','cardboard',dict(crossed=True))),
P('flatten','flow','A three-dimensional box becomes flat before disposal; no invented bin capacity.',('lådorna','cardboard'),('plattas till','flat_cardboard')),
P('cardboard_reuse','flow','Recovered cardboard becomes new paperboard/cardboard.',('återvunnen kartong','cardboard'),('ny papp och kartong','flat_cardboard')),
P('paper_types','group','Named paper examples include envelopes and book pages without covers.',('Tidningar','paper'),('kuvert','paper'),('böcker utan pärmar','book_pages')),
P('paper_reuse','reuse','Collected paper becomes new paper; paper objects carry the previous sentence reference.',('dessa','paper'),('nytt papper','paper')),
P('plastic_packages','group','Plastic box,bag and bottle examples retain the food/cosmetic packaging condition.',('askar','plastic_box'),('påsar','bag'),('flaskor','plastic_bottle'),conditions=[dict(label='förpacka livsmedel eller kosmetika',node_indices=[0,1,2])]),
P('empty_clean','pair','Empty packages and wiping clean; no added detergent or washing requirement.',('tomma','plastic_bottle'),('torkas rena','wipe')),
P('plastic_reuse','flow','Plastic becomes raw material and new plastic products; schematic product example,no resin code invented.',('plasten','plastic_bottle'),('råmaterial','pellets'),('nya plastprodukter','chair')),
P('glass_packages','pair','Glass jars and bottles explicitly without a deposit.',('glasburkar','jar'),('glasflaskor utan pant','bottle')),
P('excluded_glass','group','All three named excluded glass types are crossed out in the glass-collection context.',('dricksglas','cup',dict(crossed=True)),('fönsterglas','window',dict(crossed=True)),('spegelglas','mirror',dict(crossed=True))),
P('glass_reuse','reuse','Recovered glass becomes new glass; no claim that excluded glass belongs here.',('återvunnet glas','bottle'),('nytt glas','jar')),
P('metal_types','group','Named metal examples; small objects retain the requirement to fit easily into the bin.',('konservburkar','can'),('aluminiumfolie','foil'),('små metallföremål som enkelt ryms i kärlet','gear')),
P('metal_exclusions','group','Battery exclusion and nonempty spray/paint-can exclusions; qualifier explicitly attached to the two can objects.',('batterier','battery',dict(crossed=True)),('sprayburkar','spray_can',dict(crossed=True)),('färgburkar','paint_can',dict(crossed=True)),conditions=[dict(label='som inte är tomma',node_indices=[1,2])]),
P('metal_reuse','flow','Sorted metal becomes new metal products; no added processing details.',('Metallen','can'),('nya metallprodukter','gear')),
P('mixed_definition','flow','Unsortability into the other bins is the source condition for mixed waste; no hazardous example depicted.',('inte kan sorteras','bin_warning'),('Blandavfall','bin')),
P('energy_recovery','flow','Mixed waste is burned to produce energy; an industrial building avoids suggesting home burning.',('Blandavfallet','bin'),('bränns','factory'),('energi','plug')),
P('heat_power','split','Energy serves heat AND electricity; two parallel source uses.',('Energin','plug'),('värme','fire'),('el','plug')),
P('hazard_separate','contrast','Hazardous waste remains separate from other collection; no ordinary-bin arrow.',('farligt avfall','battery'),('separat','bin')),
P('toxic_risk','flow','Conditional toxic-release risk when hazardous waste is mixed; a warning marks the bad scenario.',('farligt avfall slängs i blandavfallet','bin_warning'),('giftiga ämnen','flask'),('naturen','tree')),
P('hazard_examples','group','Representative source-listed lamps,batteries and chemicals; no hazardous handling added.',('lysrör','tube_light'),('ackumulatorer och batterier','battery'),('kemikalier','flask')),
P('hazard_destinations','branch','Two source collection alternatives for the hazardous examples.',('De','battery'),('insamlingsställe för farligt avfall','collection'),('återvinningscentral','collection'),connective='eller'),
P('retail_returns','merge','Named battery/lamp types may be taken to shops that sell them; retain the retailer condition.',('Batterier','battery'),('lågenergilampor och lysrör','tube_light'),('affärer som säljer dem','shop')),
P('electronics_separate','contrast','Electrical/electronic waste is collected separately,with the source computer example.',('el- och elektronikavfall','laptop'),('separat','bin')),
P('electronics_shop','flow','Old electrical equipment may go to an electrical-goods shop.',('Gamla elapparater','plug'),('elaffär','shop')),
P('medicines','flow','Old medicines go to the pharmacy; no medicine advice or patient depicted.',('Gamla läkemedel och mediciner','medicine'),('apoteket','pharmacy')),
P('medicine_bag','flow','Medicines travel to the pharmacy in a transparent sealed bag; bottle visible inside the schematic bag.',('genomskinlig, tät plastpåse','medicine_bag'),('apoteket','pharmacy')),
P('empty_medicine','branch','Empty medicine containers follow their actual material into glass or plastic collection.',('Tomma medicinburkar','medicine'),('glas','jar'),('plastinsamlingen','plastic_bottle'),connective='eller',conditions=[dict(label='enligt materialet',node_indices=[1,2])]),
P('give_sell','branch','Unneeded items can be given away OR sold; no implication of mandatory resale.',('saker som man inte längre behöver','shirt'),('ge bort','people'),('sälja','coins'),connective='eller'),
P('usable_goods','group','Clothes,furniture and functioning household appliances retain the good-condition qualification.',('kläder','shirt'),('möbler','chair'),('fungerande hushållsapparater','plug'),conditions=[dict(label='i bra skick',node_indices=[0,1,2])]),
P('donate','branch','Donation alternatives: recycling centre or charity-run flea market; qualifier stays with the market.',('doneras','shirt'),('återvinningscentral','collection'),('loppmarknad','shop'),connective='eller',conditions=[dict(label='drivs av en välgörenhetsorganisation',node_indices=[2])]),
P('deposit','group','Deposit association for a large proportion of drink containers,without saying all containers have a deposit.',('dryckesflaskor','bottle'),('dryckesburkar','can'),('pant','coins'),conditions=[dict(label='en stor del',node_indices=[0,1])]),
P('deposit_return','flow','Returning such an empty container to the store leads to the small deposit refund; no amount invented.',('en sådan tom flaska eller burk','bottle'),('affären','shop'),('en liten pant','coins')),
P('deposit_reuse','reuse','Companies reuse the deposited containers; no invented recycling rate or processing method.',('Olika företag','factory'),('flaskorna och burkarna','bottle')),
]


if __name__=='__main__':
    apply('hb-c11-atervinning',PLANS,
          'Every source sentence in stored order: household sorting/local variation,costs,each source material stream,hazardous/electronic/medicine returns,reuse/donation and container deposits. All conditions remain in the bilingual main text and are made explicit in relevant diagrams.',
          'Comfortable Mystery 3 — Kevin MacLeod,CC BY4.0',
          'Distinct verified Finnish collection/recycling photograph; contextual infrastructure,not a universal bin-color standard.')
