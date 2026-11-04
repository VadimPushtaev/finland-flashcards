"""Individually directed household budgeting and debt source illustrations."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from author import apply
from direct_recycling import picture as P

ECONOMY=[
P('balance','contrast','Expenses must not exceed income; qualitative comparison, no invented amounts.',('utgifterna','coins'),('inkomsterna','work'),conditions=[dict(label='inte överstiger',node_indices=[0,1])]),
P('save_after','flow','Set savings aside after paying expenses, preserving the source goal rather than a guarantee.',('alla utgifter är betalda','document'),('sätta undan pengar','bank')),
P('buffer','protect','Savings buffer against temporarily lower income, no emergency-fund amount invented.',('Besparingarna','bank'),('inkomsterna tillfälligt blir lägre','coins')),
P('large_purchase','flow','Savings permit paying one larger purchase at once.',('besparingarna','bank'),('större anskaffning','shop')),
P('budget','merge','Budgeting brings income and expenses together without a fictional worked example.',('inkomster','coins'),('utgifter','document'),('budgetering','calendar')),
P('available_money','pair','Count available funds for the stated month or week alternatives.',('pengar','coins'),('en månad eller en vecka','calendar')),
P('allocate','split','Divide the available sum among expenses; two representative blank categories, no percentages.',('beloppet','coins'),('olika typer av utgifter','document')),
P('necessities','group','Named essential costs: rent, medicines and necessary bills.',('hyra','house'),('läkemedel','medicine'),('nödvändiga fakturor','document')),
P('remainder','flow','Only the remaining sum goes toward other expenses.',('resterande beloppet','coins'),('övriga utgifter','shop')),
P('food_leisure','branch','Budget reveals monthly food/leisure spending capacity, not a prescribed allocation.',('en månad','calendar'),('mat','food'),('fritidsaktiviteter','ball')),
P('review_changes','merge','Review consumption whenever income OR expenses change.',('inkomsterna','coins'),('utgifterna förändras','document'),('se över sin konsumtion','shop'),connective='eller'),
P('childcare_fee','flow','Income increase can raise childcare fees after a possible low-income exemption; do not promise exemption.',('inkomsterna ökar','coins'),('höjs också avgifterna','child')),
P('revise_budget','pair','The preceding change triggers another budget review.',('se över','document'),('budget','calendar')),
P('borrow_cost','pair','Borrowing has a cost; no interest-free claim.',('lånade pengar','bank'),('inte är gratis','coins')),
P('repay_interest','split','Borrowing entails future payments and often interest; qualify interest with ofta.',('tar lån','bank'),('kommande betalningarna','calendar'),('betala ränta','coins'),conditions=[dict(label='ofta',node_indices=[2])]),
P('interest_price','pair','Interest is the price of borrowed money.',('Räntan','coins'),('lånade pengarna','bank')),
P('purchase_choices','branch','Sometimes a loan or instalments may be justified for a larger purchase; no recommendation for a specific product.',('större anskaffning','shop'),('ta lån','bank'),('avbetalning','calendar'),connective='eller',conditions=[dict(label='Ibland',node_indices=[0,1,2])]),
P('consider','protect','Consider the decision carefully; no automatic green approval sign.',('väl övervägt beslut','document')),
P('loan_terms','pair','Check both contract terms and ability to repay before borrowing.',('villkoren för lånet','document'),('betala tillbaka','coins')),
P('repayment_horizon','pair','Assess payment sizes throughout the entire repayment period; no invented monthly amount.',('återbetalningsbeloppen','coins'),('hela återbetalningstiden','calendar')),
P('future_consumption','flow','Credit purchases affect future consumption without inventing a proportion.',('Anskaffningar på kredit','shop'),('framtida konsumtionen','calendar')),
P('check_rate','pair','Check the interest rate in the terms; no fabricated numeric rate.',('kontrollera','document'),('räntan','coins')),
P('high_interest','flow','High interest can make a loan costly; conditional, qualitative relationship.',('räntan är hög','coins'),('mycket dyrt','bank'),conditions=[dict(label='kan',node_indices=[1])]),
P('loan_duration','object','Choose and consider the loan duration, with no preferred duration.',('lång lånetid','calendar')),
P('longer_cost','split','Long term means smaller instalments but higher total cost due to interest; qualitative labels only.',('lång lånetid','calendar'),('mindre delbetalningar','coins'),('totalpriset högre','bank')),
P('private_loan','merge','Written agreement about repayment and terms when lending to a friend or relative.',('kompis eller en släkting','people'),('återbetalningen','coins'),('skriftligt komma överens','document')),
P('considered_loans','protect','Source describes well-considered, grounded borrowing as common in Finland; not an instruction to borrow.',('väl övervägt och välgrundat','document'),('ta lån i Finland','bank')),
P('mortgage','pair','Homes are expensive and few can buy without a mortgage; no invented house price.',('bostäderna','house'),('bostadslån','bank')),
P('car_loan','pair','A car is the source loan example; no payment plan or model recommendation.',('lån','bank'),('bil','car')),
P('sustainable_payment','protect','Repayment ability and manageable impact condition a nonproblematic loan; retain both.',('betala tillbaka','coins'),('ekonomin','bank'),conditions=[dict(label='inte påfrestar ekonomin för mycket',node_indices=[0,1])]),
P('rollover','blocked_flow','New borrowing to repay old loans is not sustainable in the long run.',('nytt lån','bank'),('gamla lån','document')),
P('consolidation','branch','Where there are several high-interest consumer loans, investigate a reasonable bank loan OR social credit; no automatic approval.',('flera konsumtionskrediter med hög ränta','document'),('banklån med rimlig ränta','bank'),('social kredit','coins'),connective='eller'),
P('social_credit','flow','Apply to own wellbeing-services county for social credit.',('social kredit','document'),('egna välfärdsområdet','hospital')),
P('guarantee','flow','Foundation may guarantee a reasonable-rate bank loan in certain cases; retain both qualifications.',('Garantistiftelsen','shield'),('banklån med rimlig ränta','bank'),conditions=[dict(label='i vissa fall',node_indices=[0,1])]),
P('bill_shortfall','pair','A bill deadline can approach while the account lacks funds; no invented date or balance.',('förfallodagen','calendar'),('inte tillräckligt med pengar','bank')),
P('contact_sender','flow','Contact the bill sender promptly; an electricity supplier is the source example.',('genast kontakta','phone'),('elbolaget','plug')),
P('extra_time','flow','Explaining the situation usually permits extra payment time, not guaranteed forgiveness.',('förklarar situationen','phone'),('extra tid','calendar'),conditions=[dict(label='vanligtvis möjligt',node_indices=[1])]),
P('instalment_agreement','pair','Paying in parts may be agreed; no entitlement or schedule invented.',('avtala','document'),('betala fakturan i delar','coins'),conditions=[dict(label='möjligt',node_indices=[0,1])]),
P('prioritize','group','When money is short, prioritize important bills without an invented order here.',('lite pengar','coins'),('fakturor som är viktigast','document')),
P('housing_first','flow','Pay housing first; rent debt can cause home loss, with the source conditional can.',('Utgifter för boende','house'),('förlorar sitt hem','key'),conditions=[dict(label='kan leda',node_indices=[1])]),
P('electricity_cut','flow','Unpaid electricity bills can lead to disconnection; no invented notice period.',('elräkningarna inte betalas','document'),('elen kan stängas av','plug',dict(crossed=True))),
P('ask_help','flow','Act and ask for help promptly when needed.',('vara aktiv','person'),('be om hjälp genast','phone')),
P('worsening','merge','Ignoring bills OR taking high-interest consumer credit can worsen small difficulties; no automatic prediction.',('låter bli att betala','document'),('konsumtionskrediter med hög ränta','bank'),('små svårigheter blir stora','warning'),connective='eller'),
]

DEBTS=[
P('contact_now','flow','If unable to pay, contact bill sender directly.',('inte kan betala','coins'),('kontakta avsändaren direkt','phone')),
P('extension','object','Payment time can often be extended, not guaranteed.',('betalningstiden förlängd','calendar'),conditions=[dict(label='Ofta',node_indices=[0])]),
P('late_fee','pair','Extension usually adds a small late fee; no amount invented.',('räkningen','document'),('liten förseningsavgift','coins'),conditions=[dict(label='vanligtvis',node_indices=[1])]),
P('collection_costs','group','Unpaid/unextended bill may require reminder costs, collection costs and late interest; exact main text retains full trigger.',('påminnelse- och inkassokostnader','document'),('dröjsmålsränta','coins')),
P('reminder','flow','Bill unpaid by due date leads to reminder.',('förfallodagen','calendar'),('betalningspåminnelse','document')),
P('agency','flow','After one or two reminders the bill may go to a collection agency.',('en eller två påminnelser','document'),('inkassobyrå','shop'),conditions=[dict(label='kan',node_indices=[1])]),
P('demand','flow','Agency sends a payment demand.',('Inkassobyrån','shop'),('betalningskrav','document')),
P('payment_plan','flow','If unable to pay at once, contact agency to agree a plan.',('kontakta inkassobyrån','phone'),('betalningsplan','calendar')),
P('enforcement','flow','No payment or plan can ultimately lead to enforcement; main source condition intact.',('skulden','document'),('utmätning','court'),conditions=[dict(label='kan',node_indices=[1])]),
P('income_share','flow','Enforcement authority can take part of income; no percentage invented.',('en del av dina inkomster','coins'),('betalning av skulder','court')),
P('property_sale','flow','Authority may sell valuable property to pay debt; no complete asset seizure implied.',('värdefull egendom','house'),('betala skulden','coins'),conditions=[dict(label='kan även sälja',node_indices=[0])]),
P('court_often','pair','Court decision is often needed for enforcement, not always.',('domstolsbeslut','court'),('utmätning','document'),conditions=[dict(label='Ofta',node_indices=[0])]),
P('direct_exception','flow','Some payments go directly to enforcement, preserving the exception.',('Vissa betalningar','document'),('direkt till utmätning','court')),
P('direct_examples','group','Source examples of direct-enforcement fees, no complete list invented.',('skatter','coins'),('hälsocentralsavgifter','hospital'),('dagvårdsavgifter','child')),
P('credit_record','flow','Nonpayment can lead to a credit-default entry; no automatic threshold invented.',('inte betalar','document'),('kreditupplysningsregistret','database'),conditions=[dict(label='kan du få',node_indices=[1])]),
P('difficulties','object','Warn of difficulties without inventing a specific consequence on this short continuation.',('många svårigheter','warning')),
P('record_checks','merge','Landlords and banks often check credit data.',('Hyresvärdar','house'),('banker','bank'),('kredituppgifterna','database'),connective='och'),
P('credit_barriers','group','A default can hinder rental housing, bank loan or credit card; no universal denial.',('hyresbostad','house'),('banklån','bank'),('kreditkort','document'),conditions=[dict(label='inte nödvändigtvis',node_indices=[0,1,2])]),
P('employer_cases','pair','Employers may require no defaults in some situations; not a universal employment ban.',('arbetsgivaren','work'),('inte har betalningsanmärkningar','database'),conditions=[dict(label='i vissa situationer',node_indices=[0,1])]),
P('lease_rescission','flow','Nonpayment permits landlord to rescind the lease; distinguish later court eviction.',('inte betalar din hyra','coins'),('häva hyresavtalet','document')),
P('notify_tenant','flow','Landlord must notify tenant of rescission.',('Hyresvärden','person'),('meddela hyresgästen','document')),
P('still_agree','pair','Usually still possible to agree rent payment at this stage; no guaranteed recovery.',('komma överens','document'),('hyresbetalningen','coins'),conditions=[dict(label='vanligtvis',node_indices=[0,1])]),
P('court_eviction','flow','Landlord can apply to court for eviction when rent unpaid; no private forcible eviction implied.',('hyresvärden','house'),('avhysningsbeslut i domstol','court')),
P('leave_pay','split','Eviction means moving out AND paying unpaid rent.',('Det','court'),('flytta ut ur bostaden','key'),('betala de obetalda hyrorna','coins'),connective='och'),
P('rent_contact','flow','Rent difficulties: contact landlord.',('svårigheter att betala hyran','house'),('kontakt med hyresvärden','phone')),
P('rent_extension','pair','Try to agree a postponed due date with landlord.',('komma överens','document'),('flytta fram förfallodagen','calendar')),
P('social_advice','flow','Local social services can provide advice.',('be om råd','phone'),('socialservicen','people')),
P('check_benefits','branch','Check possible housing allowance OR income support entitlement, no automatic award.',('Kontrollera','document'),('bostadsbidrag','house'),('utkomststöd','coins'),connective='eller'),
P('kela_rights','flow','Ask FPA about benefit rights; no person labelled a recipient.',('rätt till bostadsbidrag och utkomststöd','document'),('FPA','bank')),
P('debt_counselling','flow','Contact legal-aid financial/debt counselling for bill and debt problems.',('problem med att betala','coins'),('ekonomi- och skuldrådgivning','phone')),
P('free_state','pair','Counselling is free and state-organized.',('kostnadsfri','coins',dict(crossed=True)),('staten','court')),
P('adviser','object','Introduce adviser before the following verbatim list fragments.',('Ekonomi- och skuldrådgivaren','person')),
P('assess_together','pair','Adviser assesses finances together with the person; not independently taking control.',('ekonomiska situation','document'),('med dig','people')),
P('consider_options','branch','Consider different options together without adding a particular solution to this fragment.',('överväga','person'),('olika lösningsalternativ','document')),
P('agreements','pair','Help draw up payment agreements.',('hjälper','person'),('betalningsavtal','document')),
P('restructuring_advice','branch','Advice on applying for restructuring loan and debt restructuring; no guarantee of admission.',('råd','phone'),('skuldsaneringslån','bank'),('skuldsanering','document')),
P('foundation_help','flow','Takuusäätiö provides help/advice on debt payment.',('Takuusäätiö','shield'),('hjälp med och råd','phone')),
P('combine_loans','merge','Foundation can help combine debts into one loan; no interest rate added.',('dina skulder','document'),('ett lån','bank')),
P('foundation_guarantee','flow','Apply for a foundation loan guarantee when needing a bank loan to repay debts.',('lånegaranti','shield'),('banklån','bank')),
P('small_oneoff','group','Representative one-off small-loan expenses; no recurring-income claim, approval or amount.',('hushållsmaskin','washing_machine'),('hyresdeposition','key'),('glasögon','glasses'),conditions=[dict(label='utgift av engångskaraktär',node_indices=[0,1,2])]),
]

if __name__=='__main__':
    if sys.argv[1]=='ekonomi':
        apply('hb-c11-ekonomi',ECONOMY,'Follow source order: balanced budget,savings,loan costs and deliberation,limited consolidation possibilities,then prompt contact and priority bills. Qualitative figures only; no invented personal financial advice,amounts,rates or thresholds.','Dreamer — Kevin MacLeod,CC BY4.0','Unique relevant Finnish banking/street photograph; contextual setting only.')
    elif sys.argv[1]=='skulder':
        apply('hb-c11-skulder',DEBTS,'Follow exact source and list-fragment order through contact,reminders,collection,enforcement,credit records,rent difficulties and free debt counselling. Keep conditional can/often,specific exceptions and court versus landlord roles explicit.','Lobby Time — Kevin MacLeod,CC BY4.0','Unique verified Finnish legal-aid/courthouse exterior; no individual assigned debt or default status.')
    else:raise ValueError(sys.argv[1])
