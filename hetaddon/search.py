from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch()

doc = {
    'text': "EUROPEAN COMMISSION  Employment, Social Affairs and Inclusion DG    Employment and Social Governance  Social dialogue   " +
"   BUDGET HEADING 04 03 01 08   Industrial relations and social dialogue         CALL FOR PROPOSALS   Support for social" +
" dialogue   VP/2016/001                             Any questions should be sent by email to: empl-vp-social-dialogue@ec" +
".europa.eu   To ensure a rapid response to requests for information, applicants are invited   to send their queries in E" +
"nglish, French or German where possible   The text is available in English.   Applicants are invited to read the present" +
" document in conjunction with the Financial  Guidelines for Applicants for this call as well as the financial rules appl" +
"icable to the   general budget of the Union and their rules of application:   http://ec.europa.eu/budget/biblio/document" +
"s/regulations/regulations_en.cfm                   TABLE OF CONTENTS      1.   3.   INTRODUCTION – BACKGROUND..........." +
".....................................................................4  Legal base ....................................." +
"................................................................................4  1.1.  2.  OBJECTIVE(S) – PRIORITIES –" +
" EXPECTED RESULTS.......................................................4  2.1.  Objectives – Priorities – Expected resu" +
"lts.....................................................................4  2.2.  Type of activities to be funded ......." +
"..............................................................................6  2.3.  Other elements to be taken into a" +
"ccount ....................................................................7  TIMETABLE................................." +
".................................................................................. 7  Starting date and duration of the " +
"projects...................................................................7  3.1.  4.  AVAILABLE BUDGET................" +
".....................................................................................8  4.1.  Co-financing rate ........" +
"..................................................................................................8  5.  ADMISSIBILITY R" +
"EQUIREMENTS ..................................................................................8  ELIGIBILITY CRITERIA .." +
".................................................................................................9  6.  6.1.  Eligibilit" +
"y of the applicants (lead and co-applicants) and affiliated entities.................9  6.2.  Eligibility of actions...." +
"...................................................................................................9  6.3.  Eligible act" +
"ivities .........................................................................................................10  6.4" +
".  Ineligible activities ..............................................................................................." +
".......10  EXCLUSION CRITERIA..........................................................................................." +
"......10  SELECTION CRITERIA............................................................................................" +
"......11  8.1.  Financial capacity......................................................................................" +
"..................11  8.2.  Operational capacity........................................................................" +
"...........................11  9.  AWARD CRITERIA......................................................................." +
"................................12  10.  LEGAL COMMITMENTS.............................................................." +
"................................13  11.  FINANCIAL PROVISIONS..........................................................." +
"..................................13  12.  PROCEDURE FOR THE SUBMISSION OF PROPOSALS...................................." +
".............14  13.  COMMUNICATION....................................................................................." +
"................15  14.  REQUIRED DOCUMENTS............................................................................." +
"...............17  ANNEX I:  FINANCIAL GUIDELINES FOR APPLICANTS ......................................................." +
".22  ANNEX     MODEL  FOR  TENDER  SPECIFICATIONS  FOR  SUBCONTRACTING   7.  8.   II   EXTERNAL EXPERTISE .............." +
"..................................................................................23   2         Important points of att" +
"ention   Applicants should carefully read the entire text of this call for proposals in order to  ensure compliance of t" +
"heir application with all requirements. Particular attention  is drawn to the following provisions:   •  Applicants are " +
"strongly invited to take the requirements described in section  2.3  of  the  call  fully  into  account  when  drafting" +
"  their  proposals,  as  this  will  contribute to their quality.   •  The  lead  applicant  must  be  a  social  partne" +
"r  organisation  at  European,  national  or  regional  level.  If  this  is  not  the  case,  the  application  will  n" +
"ot  be  considered eligible and will be rejected.   •   If a social partner organisation representing workers is the lea" +
"d applicant, the  proposal  must  have  genuine  involvement,  i.e.  as  co-applicant  or  associate  organisation, of a" +
" social partner organisation representing employers. If this  is  not  the  case,  the  application  will  not  be  cons" +
"idered  eligible  and  will  be  rejected.   •  Proposals submitted by a national or regional social partner organisatio" +
"n must  have  genuine  involvement,  i.e.  as  co-applicant  or  associate  organisation,  from a European-level social " +
"partner organisation. If this is not the case, the  application will not be considered eligible and will be rejected.   " +
"•  Projects will not be considered for funding if they do not obtain the minimum   threshold for the following criteria " +
"(see section 9 of the call):  -   the extent to which the action meets the objectives and priorities of the  call for pr" +
"oposals;  the extent to which the action has a genuine transnational dimension;  the  extent  to  which  the  action  co" +
"ntributes  to  the  priorities,  activities  or  results of European social dialogue.   -  -   Applicants  should  consi" +
"der  carefully  whether  their  proposed  action  can  be  expected to receive a sufficient score for these criteria bef" +
"ore submitting a  request for funding.   •  Applicants should use the checklist included in section 14 of the call in or" +
"der to  verify  completeness  of  their  file.  Section  14  also  includes  additional  instructions regarding the form" +
"at and content of certain documents, including  the detailed work programme and the budget explanation.   •  Proposals  " +
"that  aim  mainly  at  improving  expertise  in  the  field  of  industrial   relations are not covered by this call for" +
" proposals.         3   1.   INTRODUCTION – BACKGROUND   1.1.  Legal base   In  line  with  the  remarks  in  the  budge" +
"t  of  the  European  Union,  budget  heading  04 03 01 08 is intended to cover grants for promoting social dialogue at " +
"cross-industry  and sectoral level in accordance with Article 154 of the Treaty on the Functioning of the  European  Uni" +
"on  (TFEU),  and  for  developing  European  social  dialogue  in  its  different  dimensions  of  information  exchange" +
",  consultation,  negotiation  and  joint  action.  This  call  will  therefore  be  used  to  finance  consultations,  " +
"meetings,  negotiations  and  other  actions  designed  to  achieve  these  objectives  and  to  promote  actions  outli" +
"ned  in  the  European  Commission's  Communication  on  The  European  social  dialogue,  a  force  for  innovation and" +
" change (COM(2002)341), the Communication on Partnership for change  in  an  enlarged  Europe  –  Enhancing  the  contri" +
"bution  of  European  social  dialogue  (COM(2004)557) and the Commission Staff Working Document on the Functioning and " +
" potential of European sectoral social dialogue (SEC(2010)964).    The  measures  should  help  the  social  partner  or" +
"ganisations  (representatives  of  management and labour) to contribute to addressing the overarching EU employment  and" +
" social policy challenges as laid down in particular in:  •   the  Commission  Communication  On  steps  towards  Comple" +
"ting  Economic  and  Monetary Union (COM(2015)600);  the Annual Growth Survey, the Joint Employment Report and the recom" +
"mendations  addressed to the Member States in the context of the European Semester;  the  Political  Guidelines  present" +
"ed  by  Jean-Claude  Juncker  in  the  Agenda  for  Jobs,  Growth, Fairness and Democratic Change and the Commission Wor" +
"k Programmes.   •   •   The  budget  heading  can  be  used  to  finance  actions  involving  representatives  of  the  " +
"social  partners  from  the  Candidate  Countries1.  It  is  also  intended  to  promote  equal  participation of women " +
"and men in the decision-making bodies of both trade unions and  employers' organisations. These last two components are " +
"cross-cutting.   2.  OBJECTIVES – PRIORITIES – EXPECTED RESULTS – ACTIVITIES   2.1.  Objectives – Priorities – Expected " +
"results   Objectives of this call include measures and initiatives related to the adaptation of social  dialogue  to  ch" +
"anges  in  employment  and  work  related  challenges,  such  as  addressing  modernisation  of  the  labour  market,  j" +
"ob  creation  and  job  matching,  quality  of  work,  anticipation, preparation and management of change and restructur" +
"ing, digitalisation of  the  economy  and  society,  the  greening  of  the  economy,  flexicurity,  skills,  (intra-EU)" +
"  labour mobility, migration, youth employment, health and safety at work, modernisation                                " +
"                     1  Where  reference  is  made  to  the  Candidate  Countries  in  this  call  for  proposals,  it  " +
"concerns  the  Candidate  Countries  at  the  time  of  the  deadline  for  the  submission  of  applications  of  this " +
" call  for  proposals http://ec.europa.eu/enlargement/countries/check-current-status/index_en.htm.   4   of  social  pro" +
"tection  systems,  reconciliation  of  work  and  family  life,  gender  equality,  action  in  the  field  of  anti-dis" +
"crimination,  active  ageing,  healthier  and  longer  working  lives, active inclusion and decent work.    Projects  pr" +
"oposed  jointly  by  employers'  and  workers'  organisations  which  aim  at  implementing (parts of) the work programm" +
"e of European social dialogue committees,  as well as measures to foster the implementation of European social dialogue " +
"outcomes,  reinforce  their  impact  and  visibility,  and  support  follow-up  and  reporting  are  a  high  priority. " +
"   Strengthening  synergies  and  exchanges  between  European  sectoral  social  dialogue  committees  and/or  between " +
" the  sectoral  committees  and  the  cross-industry  level,  including through projects developing a multi-sectoral app" +
"roach on themes of common  interest, is also considered a priority.    Actions  are  expected  to  contribute  to  the  " +
"priorities  and  activities  of  European  social  dialogue, including those that form part of the European Commission's" +
" commitment to  strengthen social dialogue. In that context, particular emphasis is put on the following  objectives:   " +
" •  strengthening  the  involvement  of  social  partners  in  the  European  Semester  and   enhancing their contributi" +
"on to EU policy making;   •  building  and  reinforcing  the  capacity  of  national  (cross-industry  and/or  sectoral)" +
"  social  partners  to  engage  in  national  social  dialogue  and  to  participate  in  and  contribute to European so" +
"cial dialogue, in particular in those Member States where  social dialogue is underdeveloped2.     Measures  which  cont" +
"ribute  to  addressing  the  employment  and  social  and  economic  dimensions of EU priorities relating to the recover" +
"y from the crisis, taking into account  the need for social convergence between Member States, and to reaching the objec" +
"tives  and  targets  of  the  Europe  2020  Strategy  and  its  flagship  initiatives,  will  also  be  particularly wel" +
"come.    The same goes for measures to support the European social partners and social dialogue  committees in their con" +
"tribution to impact assessment of the employment and social  dimensions of EU initiatives.    Applications  will  be  ex" +
"amined  and  selected  taking  account  of  the  remarks  in  the  EU  budget, the criteria laid down in this document a" +
"nd the principle of balanced support.    Access for people with disabilities should be guaranteed for measures funded un" +
"der this  call for proposals.                                                     2  National  capacity-building  activi" +
"ties  which  could  be  funded  under  the  European  Social  Fund   (Regulation (EU) No 1304/2013 on the European Socia" +
"l Fund, Article 6.2) are not eligible.   5   2.2.  Type of activities to be funded   The following categories of actions" +
" are targeted:   •  measures  to  prepare  European  social  dialogue,  such  as  preparatory  surveys,   meetings and c" +
"onferences;   •  measures regarded as part of social dialogue within the meaning of Articles 154 and  155 TFEU, such as " +
"negotiations, preparatory meetings for negotiations or activities  relating  to  the  implementation  of  negotiated  ag" +
"reements  and  other  negotiated  outcomes;   •  measures to implement the European social partners' work programmes (su" +
"ch as the   organisation of round tables, exchanges of experience and networks of key actors);   •  measures to dissemin" +
"ate, promote, monitor and evaluate European social dialogue  activities and outcomes, e.g. through European or national " +
"events, peer learning or  reviews, studies and (paper or electronic) publications (including the translation);   •  meas" +
"ures  to  improve  the  coordination,  functioning  and  effectiveness  of  European  social  dialogue,  including  thro" +
"ugh  the  identification  and  development  of  joint  approaches  by  the  social  dialogue  committees,  such  as  the" +
"  exchange  of  good  practice and related joint training events;   •  measures  to  strengthen  the  capacity  of  soci" +
"al  partners  to  contribute  to  European  social dialogue with particular attention to Central and Eastern European Me" +
"mber  States  and  Candidate  Countries3,  e.g.  through  information  and  training  seminars  aiming  at  developing  " +
"legal  expertise  or  organisational/administrative  skills,  or  at  expanding membership and representativeness;   •  " +
"measures  to  further  develop  and  strengthen  the  membership  of  European  social   partner organisations;   •  mea" +
"sures by social partners which contribute to the process of strengthening social  dialogue  initiated  by  the  European" +
"  Commission,  with  regard  in  particular  to  the  involvement of social partners in the European Semester and their " +
"contribution to  EU policy making;   •  measures  by  social  partners  which  contribute  to  the  employment  and  soc" +
"ial  and  economic  dimensions  of  the  Europe  2020  Strategy,  including  the  monitoring  and  analysis of its impac" +
"t on labour markets;   •  measures  to  support  the  contributions  that  European  social  partners  and  social  dial" +
"ogue  committees  provide  to  impact  assessment  of  the  employment  and  social  dimensions of EU initiatives.   Mea" +
"sures  that  aim  mainly  at  improving  expertise  in  the  field  of  industrial  relations  through  analysis  and  r" +
"esearch  and  by  promoting  the  exchange  of  information  and  experience among relevant actors, are not covered by t" +
"his call for proposals. This type of  actions will be funded under a separate call for proposals.                       " +
"                              3  National  capacity-building  activities  which  could  be  funded  under  the  European" +
"  Social  Fund   (Regulation (EU) No 1304/2013 on the European Social Fund, Article 6.2) are not eligible.   6   2.3.  O" +
"ther elements to be taken into account   When  drafting  the  proposal,  applicants  are  invited  to  pay  particular  " +
"attention  to  the  following elements:   •  The  proposal  should  provide  a  clear  explanation  of  the  rationale  " +
"and  problem  definition/analysis  underpinning  the  proposed  action,  as  well  as  the  specific  contribution of th" +
"e action to the objectives of the call for proposals and its expected  impact.  In case of recurrent applications by the" +
" same applicant on similar or related topics,  the added value of the new project proposal as compared to ongoing and pr" +
"evious  actions4 should be clearly explained.   •   •  The choice of organisations involved and countries covered should" +
" be duly explained  and justified as regards their relevance towards the specific objectives of the action.   Taking  ac" +
"count  of  beneficiaries'  interest,  the  Commission  may  organise  a  networking  day  in  Brussels  for  beneficiari" +
"es  under  the  2016  call  (date  to  be  defined).  Applicants  must therefore ensure that the travel, daily subsisten" +
"ce allowances and accommodation  costs for up to 2 persons – the Project Manager and possibly the Financial Manager – to" +
"  attend this meeting are included in their proposed project budget. If the applicant fails  to do this, the Commission " +
"will not be able to fund the beneficiary's participation in the  networking day.   3.  TIMETABLE      Stages   a)   Publ" +
"ication of the call   b)  Deadline for submitting proposals   c)   Evaluation period (indicative)   d)   Information to " +
"applicants (indicative)   e)   Signature of the grant agreement (indicative)   3.1.  Starting date and duration of the p" +
"rojects   Date or period   April 2016   30 June 2016   Until end September   2016   From beginning of   November5   From" +
" mid-November6   The actual starting date of the action will be the first day of the month following the  date when the " +
"last of the two parties signs the grant agreement.                                                     4  5  6   Includi" +
"ng projects funded under other budget headings.  And in any case no later than 6 months after the submission deadline.  " +
"And in any case no later than 3 months after the date of information to applicants.   7   Since the actual starting date" +
" may not correspond to the start date of the action that  applicants have set in their application file, it is advisable" +
" to number the months in the  work programme instead of indicating the precise name of the months.   The  Commission  we" +
"lcomes  in  particular  projects  that  provide  for  a  full  project  cycle,  including  preparatory,  implementation " +
" and  dissemination,  follow-up  and  reporting  activities. The indicative duration of projects is 24 months.   4.  AVA" +
"ILABLE BUDGET   The  total  budget  earmarked  for  the  EU  co-financing  of  projects  under  this  call  is  estimate" +
"d at EUR 9 300 000.   As an indication, the requested EU grants are expected to be between EUR 150 000 and  EUR 500 000." +
"   The Commission reserves the right not to distribute all the funds available.   4.1.  Co-financing rate   Under this c" +
"all for proposals, the EU grant may not exceed 90 % of the total eligible costs  of the action.  In  derogation  from  t" +
"he  previous  paragraph,  the  European  Commission  may  decide  to  finance up to 95% of the total cost of social dial" +
"ogue actions involving negotiations in  accordance with Articles 154 and 155 TFEU, meetings to prepare for these negotia" +
"tions  (second bullet point under targeted measures), or joint social partner actions relating to  the implementation of" +
" the agreements resulting from these negotiations.    The applicants must guarantee their co-financing of the remaining " +
"amount covered by  the  applicants'  own  resources  or  from  other  sources  other  than  the  European  Union  budget" +
".   5.  ADMISSIBILITY REQUIREMENTS   •  Applications must be sent no later than the deadline for submission referred to " +
"in   section 3.   •  Applications must be submitted using the electronic submission system available at  https://webgate" +
".ec.europa.eu/swim, and by sending a signed, printed version of the  application form and its annexes by post or courier" +
" service (see section 12).   Failure to comply with the above requirements will lead to the rejection of the application" +
".   Applicants are encouraged to submit their project proposal in English, French or German  in  order  to  facilitate  " +
"the  treatment  of  the  proposals  and  speed  up  the  evaluation  process.   8   6.  ELIGIBILITY CRITERIA   6.1.  Eli" +
"gibility of the applicants (lead and co-applicants) and affiliated entities7   To be eligible:  •  The  lead  applicant " +
" must  be  a  social  partner  organisation  at  European,  national  or   regional level;   •  The lead applicant must " +
"have its registered office in one of the EU Member States;  •  Co-applicants8 must have their registered office in one o" +
"f the EU Member States or   the Candidate Countries9.   •  Applicants must be properly constituted and registered legal " +
"persons. In application  of Article 131 of the Financial Regulation, social partner organisations without legal  persona" +
"lity are also eligible provided that the conditions of the Financial Regulation  related thereto are met.   Legal entiti" +
"es having a legal or capital link with applicants, which is neither limited to the  action nor established for the sole " +
"purpose of its implementation and which satisfy the  eligibility  criteria,  may  take  part  in  the  action  as  affil" +
"iated  entities,  and  may  declare  eligible costs.   For that purpose, applicants shall identify such affiliated entit" +
"ies in the application form.   6.2.  Eligibility of actions   To be eligible, actions must:  •  Have  the  involvement  " +
"of  applicants,  affiliated  entities  or  associate  organisations10  from more than one Member State and/or Candidate " +
"Country in the case of projects  which are not submitted by a European-level social partner organisation;   •  Have  gen" +
"uine  involvement,  i.e.  as  co-applicant  or  associate  organisation,  from  a  European-level  social  partner  orga" +
"nisation11,  if  the  proposal  is  submitted  by  a  national or regional social partner organisation;                 " +
"                                    7  8   See section 2 of the Financial Guidelines for definitions.  The same conditio" +
"n applies to affiliated entities – as do the other eligibility and non-exclusion criteria  that apply to co-applicants. " +
" In derogation from this requirement, international organisations, such as UN agencies, active in the  fields of social " +
"dialogue and/or industrial relations, whose registered headquarters are outside the EU  Member States, are also eligible" +
".   9   10  See section 2 of the Financial Guidelines for definitions.      Letters  of  commitment  must  be  submitted" +
"  from  each  co-applicant,  affiliated  entity  that  they  are  willing to participate in the project with a brief des" +
"cription of their role and indicating any financial  contribution as applicable, and from associate organisations that t" +
"hey are willing to participate in the  project with a brief description of their role (see section 14, checklist point 4" +
").   11  These include the European social partner organisations that are consulted in accordance with Article  154  TFE" +
"U  (an  up-to-date  list  of  these  organisations  can  be  found  under  \"List  of  consulted  organisations\"  on  w" +
"ebpage  http://ec.europa.eu/social/main.jsp?catId=329&langId=en),  as  well  as   9   •   If  a  social  partner  organi" +
"sation  representing  workers  is  the  lead  applicant,  have  genuine  involvement,  i.e.  as  co-applicant  or  assoc" +
"iate  organisation,  of  a  social  partner organisation representing employers12;   •  Be fully carried out in the Memb" +
"er States of the European Union or the Candidate   Countries13.   If  a  co-applicant,  affiliated  entity  or  associat" +
"e  organisation  is  considered  not  to  be  eligible,  this  partner  will  be  removed  from  the  consortium  and  t" +
"he  eligibility  of  the  modified consortium will be re-evaluated. If the modified consortium is still eligible, the  a" +
"pplication will be evaluated on that basis. In addition, the costs that are allocated to a  non-eligible  co-applicant  " +
"or  affiliated  entity  will  be  removed  from  the  budget.  If  the  application is accepted, the work programme will" +
" have to be adapted as appropriate.   6.3.  Eligible activities   The grant will finance inter alia the activities indic" +
"ated in section 2.2.   The project management of the action and the role of coordinator (in case of a multi- beneficiary" +
" grant agreement) as laid down in Article II.2.3 of the grant agreement, are  considered to be core activities and may n" +
"ot be subcontracted14.   6.4.  Ineligible activities   Financial support to third parties as defined in point 3 of the F" +
"inancial Guidelines is not  eligible under this call.   National  capacity-building  activities  which  could  be  funde" +
"d  under  the  European  Social  Fund (Regulation (EU) No 1304/2013 on the European Social Fund, Article 6.2) are not  e" +
"ligible.   7.  EXCLUSION CRITERIA   Applicants  (lead  and  co-applicants)  must  sign  a  declaration  on  their  honou" +
"r  certifying  that they are not in one of the situations referred to in article 106(1) and 107.1(b) and  (c)  of  the  " +
"Financial  Regulation  concerning  exclusion  and  rejection  from  the  procedure  respectively,  using  the  relevant " +
" form  attached  to  the  application  form  available  at  https://webgate.ec.europa.eu/swim/external/displayWelcome.do" +
".   The same exclusion criteria apply to any affiliated entities.                                                       " +
"                                                                                               other European-level soci" +
"al partner organisations that are not included in this list, but who are for  example involved in the preparation and la" +
"unch of European social dialogue at sector level.   12  Chambers  of  Commerce  and  business/trade  associations  are  " +
"as  a  rule  not  considered  to  be  social   partner organisations, unless they can demonstrate that they are involved" +
" in social dialogue.   13  See section 11 for specific provisions regarding daily subsistence allowances and travel expe" +
"nses.  14   See  section  4.2.2.3  of  the  Financial  Guidelines  for  detailed  information  on  procedures  regarding" +
"   subcontracting and implementing contracts.   10   Only  proposals  which  comply  with  the  requirements  of  the  a" +
"bove  eligibility  and  exclusion criteria will be considered for further evaluation.   8.  SELECTION CRITERIA   The app" +
"licants (lead and co-applicant) must have the financial and operational capacity  to  complete  the  activity  for  whic" +
"h  funding  is  requested.  Only  organisations  with  the  necessary financial and operational capacity may be consider" +
"ed for a grant.   8.1.  Financial capacity   Applicants (lead and co-applicants) must have access to solid and adequate " +
"funding to  maintain their activities for the period of the action and to help finance it as necessary.   The  ratio  be" +
"tween  the  total  assets  in  the  applicants'  (lead  and  co-applicants)  balance  sheet and the total budget of the " +
"project or the part of the project budget for which that  organisation is responsible according to the budget in the app" +
"lication form, should be  greater than 0.70. In addition, the Commission will take into account any other relevant  info" +
"rmation  on  financial  capacity  provided  by  the  applicant.  In  this  context,  the  Commission will in particular " +
"take account of the information provided in section F.2 of  the SWIM application form and of the following supporting do" +
"cuments to be submitted  with the application:   •  Declaration  on  honour  (including  financial  capacity  to  carry " +
" out  the  activity)  (see   section 14, checklist point 3);   •  Annual balance sheets for the last financial year avai" +
"lable (see section 14, checklist   point 16);   •  For action grants of EUR 750 000 or more, an audit report produced by" +
" an approved  external  auditor  certifying  the  accounts  for  the  last  financial  year  available  (see  section 14" +
", checklist point 17).   8.2.  Operational capacity   Applicants  (lead  and  co-applicants)  must  have  the  operation" +
"al  resources  (technical,  management), as well as the professional competencies and appropriate qualifications  to  co" +
"mplete  the  proposed  action.  They  must  have  a  sufficient  track  record  of  competence and experience in the fie" +
"ld and in particular in the type of action proposed.   When assessing the operational capacity of applicants, the Commis" +
"sion will in particular  take account of the following elements:  •   the  information  provided  in  sections  F.1  of " +
" the  SWIM  application  form  on  the  operational  structure  of  the  lead  applicant  and  co-applicants  and  on  p" +
"revious  and  current actions undertaken by them;   •  The  CV  of  the  proposed  project  manager,  showing  his/her  " +
"relevant  professional   experience (see section 14, checklist point 14);   •  Declaration on honour (including operatio" +
"nal capacity to carry out the activity) (see   section 14, checklist point 3)   11     If  the  lead  applicant  is  con" +
"sidered  not  to  have  the  required  financial  or  operational  capacity, the application as a whole will be rejected" +
". If a co-applicant is considered not  to have the required financial or operational capacity, this co-applicant will be" +
" removed  from the consortium and the application will be evaluated on that basis15. In addition,  the costs that are al" +
"located to the non-eligible co-applicant will be removed from the  budget. If the application is accepted, the work prog" +
"ramme will have to be adapted as  appropriate.   9.  AWARD CRITERIA   The proposals which fulfil the eligibility, exclus" +
"ion and selection criteria will be assessed  according to the following award criteria:   i.  The extent to which the ac" +
"tion meets the objectives and priorities of the call for   proposals   ii.  The extent to which the action has a genuine" +
" transnational dimension  iii.  The  quality  of  the  consortium  and  broader  partnership,  including  the  degree  o" +
"f  the  social   the  application  stage  of   involvement  and  commitment  at  partners/stakeholders in the action16  " +
" iv.  The extent to which the action contributes to the priorities, activities or results of   European social dialogue " +
"  v.  The added value, i.e. the lasting impact and/or multiplier effect17 of the action18  vi.  The cost-effectiveness o" +
"f the action  vii.  The  arrangements  to  publicise  the  action  and  disseminate  the  results,  including    the qua" +
"lity and/or innovativeness of dissemination plans   viii.  The  overall  quality,  clarity  and  completeness  of  the  " +
"proposal  and  budget   explanation     When  assessing  the  proposals  according  to  the  abovementioned  award  crit" +
"eria,  the  following method will be applied:  •  Applications with a score below 50% for criteria i, ii or iv will not " +
"be considered for   award.   •  Applications with an overall score of less than 60% will not be considered for award.   " +
"                                                  15  This includes a re-evaluation of the eligibility of the modified c" +
"onsortium.  16    Independent  consultants,  conference  organisers,  etc.  must  not  be  included  as  co-applicants. " +
" See  chapter 4.2.2.3 Costs of services of the Financial Guidelines.   17   The multiplier effect refers to how the proj" +
"ect and its results will promote change in other fields, such   as geographical, sectoral and thematic.   18   The  Comm" +
"ission  also  reserves  the  right  when  assessing  proposals  to  take  into  account  the  effectiveness  and  added " +
" value  of  previous  or  ongoing  projects  undertaken  by  the  applicant  with  European Union funding.   12   •  Tak" +
"ing account of the budget available for this call for proposals, the proposals with   the highest overall evaluation sco" +
"res will be selected for award.     Cost estimates should be reasonable, justified and comply with the principle of soun" +
"d  financial management, in particular regarding economy and efficiency (see also section  14). It should be noted that " +
"the cost-effectiveness of actions will be evaluated on the  basis of the proposed budget. The Commission  reserves the r" +
"ight to make corrections  and/or  cut  non-eligible  expenditure  from  the  proposed  budget,  but  it  will  not  make" +
"  adjustments in order to improve cost-effectiveness of proposals.   10.  LEGAL COMMITMENTS   In  the  event  of  a  gra" +
"nt  awarded  by  the  Commission,  a  grant  agreement,  drawn  up  in  euro and detailing the conditions and level of f" +
"unding, will be sent to the beneficiary, or  to the coordinator in the case of multi-beneficiary grant agreements.   The" +
"  2  copies  of  the  original  agreement  must  be  signed  by  the  beneficiary,  or  the  coordinator  in  the  case " +
" of  multi-beneficiary  grant  agreements,  and  returned  to  the  Commission immediately. The Commission will sign it " +
"last.   A model grant agreement is published on the Europa website under the relevant call:  http://ec.europa.eu/social/" +
"main.jsp?catId=629&langId=en&callId=477.   Please note that the award of a grant does not establish an entitlement for s" +
"ubsequent  years.   11.  FINANCIAL PROVISIONS    Details  on  financial  provisions  are  laid  out  in  the  Financial " +
" Guidelines  for  Applicants  (Annex  I  to  the  call)  and  the  model  grant  agreement,  both  published  on  the  E" +
"uropa  website under the relevant call:  http://ec.europa.eu/social/main.jsp?catId=629&langId=en&callId=477.      Specif" +
"ic provisions   •  Where  the  value  of  a  foreseen  procurement  contract  exceeds  EUR 60  000,  the  applicant  mus" +
"t  provide  with  the  grant  application  a  copy  of  the  draft  tender  specifications.  To  assist  applicants,  a " +
" model  for  tender  specifications  is  included  in  Annex II to this call. Important additional information concernin" +
"g procurement can  be found in the Financial Guidelines (section 4.2.2.3). The draft tender specifications  should be su" +
"bmitted in English, French or German.  In addition, the applicant will have to be able to prove, if requested, that they" +
" have  sought  bids  from  at  least  five  different  tenderers,  including  proof  that  they  have  published  the  c" +
"all  for  tender  or  invitation  to  tender  at  least  on  their  website  and  provide d a detailed description of th" +
"e selection procedure.  This requirement does not apply to public authorities which are already governed by  a system of" +
" public procurement rules.   13   •  As regards daily subsistence allowances and travel expenses, only those related to " +
" participants  and  speakers  travelling  between  EU  Member  States  and/or  Candidate  countries will be accepted as " +
"eligible costs.  This  provision  does  not  apply  to  staff  of  international  organisations,  such  as  UN  agencies" +
",  who  are  invited  by  the  beneficiary  to  participate  in  a  project  event  as  a  speaker/expert,  including  w" +
"here  the  international  organisation  is  an  associate  organisation  to  the  project,  or  where  the  internationa" +
"l  organisation  is  a  co- beneficiary in the project.   12.  PROCEDURE FOR THE SUBMISSION OF PROPOSALS   The procedure" +
" to submit proposals electronically is explained in point 14 of the \"Financial  Guidelines for Applicants\" (Annex I to" +
" this call). Before starting, please read carefully the  SWIM user manual:  http://ec.europa.eu/employment_social/calls/" +
"pdf/swim_manual_en.pdf.   Once the application form is filled in, applicants must submit it both electronically and in  " +
"hard copy, before the deadline set in section 3 above.   The  SWIM  electronic  application  form  is  available  until " +
" midnight  on  the  day  of  the  submission deadline. Since the applicants must first submit the form electronically, a" +
"nd  then print, sign and send it by post service or hand delivery by the submission deadline,  it  is  the  applicant's " +
" responsibility  to  ensure  that  the  appropriate  postal  or  courier  services are locally available on the day of t" +
"he deadline.   The  hard  copy  of  the  proposal  must  be  duly  signed  and  sent  in  2  copies  (one  marked  “orig" +
"inal” and one marked “copy”), including all documents listed in the checklist in section  14, by the deadline (the postm" +
"ark or the express courier receipt date serving as proof) to  the following address:   European Commission   Call for pr" +
"oposals VP/2016/001   DG EMPL/A.2, J-54 – 01/004   B-1049 Brussels   Belgium   Please  send  your  proposal  by  registe" +
"red  post,  express  courier  service  or  by  hand  delivery only. Proof of posting or express courier receipt should b" +
"e kept as it could be  requested  by  the  European  Commission  in  cases  of  doubt  regarding  the  date  of  submiss" +
"ion.   Hand-delivered proposals must be received by the European Commission before 4 p.m.  on the last day for submissio" +
"n at the following address:   14   European Commission  Central Mail Service19   Avenue du Bourget 1   Call for proposal" +
"s VP/2016/001 – DG EMPL/A.2   B-1140 Evere   Belgium   At that time the European Commission's Mail Service will provide " +
"a signed receipt which  should be conserved as proof of delivery.   If  an  applicant  submits  more  than  one  proposa" +
"l,  each  proposal  must  be  submitted  separately.   Additional  documents  sent  by  post,  by  fax  or  by  electron" +
"ic  mail  after  the  deadlines  mentioned  above  will  not  be  considered  for  evaluation  unless  requested  by  th" +
"e  European Commission.   The  applicant's  attention  is  also  drawn  to  the  fact  that  incomplete  or  unsigned  a" +
"pplication forms, hand-written forms and those sent by fax or e-mail will not be taken  into consideration.   13.  COMMU" +
"NICATION   Communication during the application period   The  information  contained  in  the  present  call  document  " +
"together  with  the  Financial  Guidelines  for  Applicants  provides  all  the  information  you  require  to  submit  " +
"an  application. Please read it carefully before doing so, paying particular attention to the  priorities of the present" +
" call.     All enquiries must be made by e-mail only to:   empl-vp-social-dialogue@ec.europa.eu   For technical problems" +
" please contact: empl-swim-support@ec.europa.eu     Questions may be sent to the above address no later than 10 days bef" +
"ore the deadline  for  the  submission  of  proposals.  The  Commission  has  no  obligation  to  provide  clarification" +
"s to questions received after this date.   Replies  will  be  given  no  later  than  5  days  before  the  deadline  fo" +
"r  submission  of  proposals. To ensure equal treatment of applicants, the Commission will not give a prior  opinion on " +
"the eligibility of applicants or affiliated entities, an action or specific activities.   As a rule, no individual repli" +
"es to questions will be sent but all questions together with  the  answers  and  other  important  notices  will  be  pu" +
"blished  (FAQ  –  Frequently  Asked                                                     19  http://ec.europa.eu/contact/" +
"mailing_en.htm   15   Questions) at regular intervals on the Europa website:  http://ec.europa.eu/social/main.jsp?catId=" +
"629&langId=en&callId=477.      The  Commission  may,  on  its  own  initiative,  inform  interested  parties  of  any  e" +
"rror,  inaccuracy,  omission  or  clerical  error  in  the  text  of  the  call  for  proposals  on  the  mentioned  Eur" +
"opa  website.  It  is  therefore  advisable  to  consult  the  above  mentioned  website regularly in order to be inform" +
"ed of the questions and answers published.   No  modification  to  the  proposal  is  allowed  once  the  deadline  for " +
" submission  has  elapsed. If there is a need to clarify certain aspects or to correct clerical mistakes, the  Commissio" +
"n may contact the applicant for this purpose during the evaluation process.  This is generally done by e-mail. It is ent" +
"irely the responsibility of applicants to ensure  that all contact information provided is accurate and functioning. In " +
"case of any change  of contact details, please send an e-mail with the application VP reference and the new  contact det" +
"ails to empl-vp-social-dialogue@ec.europa.eu.   All communication regarding an application will be done with the lead ap" +
"plicant only,  unless there are specific reasons to do otherwise.   Information on the outcome of the procedure   Applic" +
"ants will be informed in writing about the results of the selection process.   Unsuccessful  applicants  will  be  infor" +
"med  of  the  reasons  for  rejection.  Successful  applicants will receive 2 copies of the original agreement for accep" +
"tance and signature  (see also section 10 above).   No  information  regarding  the  award  procedure  will  be  disclos" +
"ed  until  the  notification  letters have been sent to the beneficiaries.   Participation of the Commission in project " +
"events   Following the award of a grant, if the successful applicant would like the Commission to  participate  in  any " +
" project  events,  the  applicant  must  take  immediate  contact  (in  any  case, at least 2 months before the event) w" +
"ith the Commission official responsible for  following  the  action  (named  in  the  letter  accompanying  the  grant  " +
"agreement).  The  successful  applicant  should  therefore  not  finalise  the  programming  of  such  events  without t" +
"he Commission's prior approval and confirmation of participation.   The Commission's acceptance of the grant application" +
" does not prejudge its decision on  whether to attend an event included in the work programme. Such a decision is always" +
"  subject to a separate examination of the event programme and prior agreement on the  dates  and  practicalities.  In  " +
"this  context  it  should  be  noted  that  the  probability  of  Commission officials participating in project events w" +
"ill be higher if the latter take place  in Brussels.   16   14.  REQUIRED DOCUMENTS   The  table  below  includes  the  " +
"documents  that  must  be  provided  on  submission  of  the  proposal. It also indicates where originals are required. " +
"We recommend that applicants  use the table as a checklist in order to verify compliance with all requirements.   In ord" +
"er to allow the Commission to evaluate proposals, files must be complete.   While  some  information  must  be  supplied" +
"  using  the  templates  available  in  the  SWIM,  other  documents  may  need  to  be  completed  and/or  attached  el" +
"ectronically,  usually  either administrative documents or free format text descriptions. The SWIM application  indicate" +
"s in each section where SWIM templates should be used as well as which and  where free format documents can be uploaded " +
"electronically.   Regarding the detailed work programme and budget explanation, applicants should take  account of the f" +
"ollowing instructions.   •  The  detailed  work  programme  (see  checklist  point  12)  should  not  repeat   informati" +
"on that is already provided in the SWIM application form20.  o   It  should  provide  a  detailed  and  structured  over" +
"view  of  the  different  project  activities,  the  foreseen  timing  (indicating  numbers  of  months,  not  names  of" +
"  months)  and  the  role  and  responsibility  of  each  partner  organisation  (not  individual staff members) in the " +
"implementation of these activities, as well as, to  the extent possible, draft agendas of the main project events.   o  " +
"Where appropriate, risk factors as regards implementation and/or impact of the   o   o   activities should be identified" +
" and mitigating measures defined.  It  offers  an  opportunity  to  develop  further  the  rationale  and  problem  anal" +
"ysis  underpinning the action.  If  any  subcontracting  of  tasks  is  foreseen,  the  detailed  work  programme  must " +
" provide detailed information on the tasks to be subcontracted and the reasons  for  doing  so.  Core  tasks  as  define" +
"d  in  section  6.3  of  the  call  cannot  be  subcontracted.   o  All  other  information  on  the  action  should  in" +
"  principle  be  given  in  the  SWIM  application form. The detailed work programme is therefore expected not to be  mu" +
"ch longer than 5 pages, with an absolute maximum of 10 pages.     •  The budget explanation (see checklist point 13) mus" +
"t provide additional information  to  explain  and  justify  items  of  the  proposed  budget  as  submitted  in  the  S" +
"WIM  application form. It should in particular explain: how the number of working days of  staff involved in the impleme" +
"ntation of the action has been fixed; how average travel  costs  were  calculated;  unless  this  is  self-explanatory, " +
" how  costs  of  services  and  administration costs were defined.   At the submission of the application, copies of the" +
" signed originals will be accepted for  most  of  the  documents  to  be  submitted  by  the  co-applicants.  However,  " +
"the  lead                                                    20  The corresponding section in the SWIM form (E.6 Workpla" +
"n) can therefore be kept rather succinct.   17   applicant shall keep the original signed versions for its records, beca" +
"use originals may  have to be submitted for certain documents at a later stage. If the lead applicant fails to  submit  " +
"these  original  documents  within  the  deadline  given  by  the  Commission,  the  proposal will be rejected for lack " +
"of administrative compliance.   follow the order of documents as listed in the checklist;   Regarding the compilation of" +
" the application file, it is recommended to:  •  •  print the documents double-sided;  •  use 2-hole folders (do not bin" +
"d or glue; stapling is acceptable).      18   CHECKLIST for required documents  This table includes the documents that m" +
"ust be provided and indicates where originals are required. We strongly recommend using the table as a checklist in orde" +
"r to  verify compliance with all requirements. Notes: highlighted documents do not need to be provided by public entitie" +
"s. Documents marked with * are obligatorily to be  attached online in SWIM as well.      ? d e n g i s   y l l  a n i g " +
"i r O     x o b k c e h C  --  (cid:134)   (cid:57)  (cid:134)      e t a  i c o s s A     n o i t a s i n a g r o     y" +
" t r a p d r i h t   /  --   --   The document must be provided by   each      d a e L    t n a c i l  p p a  (cid:57)  " +
" (cid:57)     t n a c i l  p p a - o C  --   --      d e t a  i l i f f A     y t i t n e  --   --   --   .    Document " +
" o N  Specification and content   1  Official cover letter  of the application   This free format letter must quote the " +
"reference of the call for proposals and the proposal  reference number generated by SWIM (e.g. VP/20XX/0XX/xxxx).   Sign" +
"ed SWIM  application form  submitted online   The SWIM application form submitted online must be printed and dated and s" +
"igned by the  authorised legal representative and send by hard copies as foreseen in Section 12. Note: the  online form " +
"must be electronically submitted before printing. After electronic submission, no  further changes to the proposal are p" +
"ermitted.   2   3   Declaration on  honour*   The template is available in SWIM and must be written on the official lett" +
"erhead of the  organisation, bearing the original signature of the authorised legal representative.  Copies of the origi" +
"nal signed declaration of co-applicants are accepted at the submission of the  application; originals to be submitted up" +
"on request.   (cid:57)   (cid:57)   --   (cid:57)  (cid:134)   4   Letter of  commitment*   The template is available in" +
" SWIM and must explain the nature of the organisation's  involvement and specify the amount of any funding provided. The" +
" letter must be written on  the official letterhead of the organisation and bear the original signature of the legal  re" +
"presentative.  Copies of the original signed letters of commitment are accepted at the submission of the  application; o" +
"riginals to be submitted upon request.   5   Letter of mandate*   The template is available in SWIM and must be written " +
"on the official letterhead of the  organisation, dated and signed by the authorised legal representative.  Copies of the" +
" original signed letters of mandate are accepted at the submission of the  application; originals to be submitted upon r" +
"equest.   --   (cid:57)   (cid:57)   (cid:57)   --  (cid:134)   --   (cid:57)   --   --   --  (cid:134)   19   .    Docu" +
"ment  o N  Specification and content      d a e L    t n a c i l  p p a  The document must be provided by   each      d " +
"e t a  i l i f f A     y t i t n e     e t a  i c o s s A     n o i t a s i n a g r o     y t r a p d r i h t   /    t n" +
" a c i l  p p a - o C  --      ? d e n g i s   y l l  a n i g i r O     x o b k c e h C  (cid:57)   --   --  (cid:134)  " +
" --   --   --   --   --   --   --  (cid:134)   --   --  (cid:134)   --   --  (cid:134)   --   --   --  (cid:134)   (cid:" +
"57)  (cid:134)   6   Legal/capital link  with lead or co- applicant*   7   Legal entity form*   Affiliated entities are " +
"required to provide proof of the legal and/or capital link with the lead or  co-applicant.   --   The template is availa" +
"ble in SWIM and online  (http://ec.europa.eu/budget/contracts_grants/info_contracts/legal_entities/legal_entities_e n.cf" +
"m) and must be duly signed and dated by the legal representative.  Exclusively in the case of social partner organisatio" +
"ns without legal personality, a signed  letter of the legal representative certifying his/her capacity to undertake lega" +
"l obligations on  behalf of the organisation.   (cid:57)   (cid:57)   8   Proof of registration   A certificate of offic" +
"ial registration or other official document attesting the establishment of  the entity (for public bodies: the law, decr" +
"ee, decision, etc., establishing the entity).   (cid:57)   (cid:57)   9   Statutes   The articles of association/foundin" +
"g act/constitution/statutes or equivalent, proving the  eligibility of the organisation.  It is recommended not to inclu" +
"de a paper copy of statutes in the application file, but to attach  only an electronic copy in the SWIM application form" +
".  Organisations of Candidate Countries are requested to provide a translation in English, French  or German of the requ" +
"ired documents.   10  VAT certificate   A document showing the identification number for tax purposes or the VAT number," +
" if  applicable.   11   Financial  identification form*   The template is available in SWIM and online  (http://ec.europ" +
"a.eu/budget/contracts_grants/info_contracts/financial_id/financial_id_en.cf m) and must be duly signed and dated by the " +
"account holder and bearing the bank stamp and  signature of the bank representative (or a copy of recent bank statement " +
"attached).   (cid:57)   (cid:57)   (cid:57)   (cid:57)   (cid:57)   --   20   .    Document  o N  Specification and cont" +
"ent      d a e L    t n a c i l  p p a  12  Detailed work  programme*   This is a separate free-format document in addit" +
"ion to the on-line application form and it  must also be submitted both electronically and on paper. The paper version m" +
"ust be identical  to the electronic version of the detailed work programme.  The detailed work programme should be submi" +
"tted in English, French or German.   (cid:57)     t n a c i l  p p a - o C  --      ? d e n g i s   y l l  a n i g i r O" +
"     x o b k c e h C  --   --   --  (cid:134)   The document must be provided by   each      d e t a  i l i f f A     y " +
"t i t n e     e t a  i c o s s A     n o i t a s i n a g r o     y t r a p d r i h t   /  13  Budget Explanation   for t" +
"he project*   This is a separate free-format document in addition to the budget section of the on-line  application form" +
" and it must also be submitted electronically in annex to the on-line  application form. The paper version must be ident" +
"ical to the electronic version of the budget  explanation.  The Commission may request applicants to submit additional j" +
"ustifications of proposed  eligible costs during the evaluation procedure.  The document should be submitted in English," +
" French or German.   14  Curriculum vitae of  the project manager   Detailed CV of the person responsible for managing t" +
"he action (named in section A.3 of the online  application form). The CV should indicate clearly the current employer.  " +
"The CV should be submitted in English, French or German.   15  Draft tender  specifications   To be submitted for procur" +
"ement contracts with a value that exceeds EUR 60 000 (see also section  11 of the call).   16  Balance sheet   17  Audit" +
" report   The most recent balance sheet, including assets and liabilities, specifying the currency used.  Organisations " +
"that are not required by law to establish an official balance sheet must  nevertheless provide information on their asse" +
"ts and liabilities. A statement of income and  expenses is not sufficient.   For grant requests of EUR 750,000: an exter" +
"nal audit report produced by an approved auditor,  certifying the accounts for the last financial year available. The th" +
"reshold applies to each co- applicant in line with their share of the action budget. The report should be submitted in  " +
"English, French or German.   (cid:57)   --   --   --   --  (cid:134)   (cid:57)   (cid:57)   (cid:57)   --   (cid:57)   " +
"(cid:57)   --   (cid:57)   --   --   --   --   --  (cid:134)   --  (cid:134)   --  (cid:134)   (cid:57)   (cid:57)   -- " +
"  --   --  (cid:134)   21   ANNEX I:    FINANCIAL GUIDELINES FOR APPLICANTS      Annex I is available on the Europa webs" +
"ite under the relevant call:    http://ec.europa.eu/social/main.jsp?catId=629&langId=en&callId=477      22   ANNEX II   " +
" MODEL FOR TENDER SPECIFICATIONS FOR SUBCONTRACTING EXTERNAL EXPERTISE       Tender Specifications – ……………           1. " +
" Background    2.    3.     Purpose of the Contract   Tasks to be performed by the Contractor   10.1  Content of the bid" +
"s    10.2  Presentation of the bids        23   3.1  Description of tasks    3.2  Guidance and indications on tasks exec" +
"ution and methodology   Expertise required   Time schedule and reporting   Payments and standard contract     4.    5.  " +
"  6.    7.    8.    9.    The contract will be awarded to the tenderer whose offer represents the best value for  money " +
"- taking into account the following criteria:   Price   Selection criteria   Award criteria   (cid:31)  ……………………….  (cid" +
":31)  ………………………  (cid:31)  ………………………     It should be noted that the contract will not be awarded to a tenderer who rece" +
"ives less  than 70% on the Award Criteria.    10.  Content and presentation of the bids     "
}
index_name = "test-index2"
res = es.index(index=index_name, doc_type='document', id=1, body=doc)
print(res['created'])

es.indices.refresh(index=index_name)

index = es.indices[index_name]
termInfo = index.get('employ')
for(pos in termInfo):
    return pos.startOffset

res = es.search(index="test-index", body={"query": {"match": {"text":"Employment"}}})
print("Got %d Hits:" % res['hits']['total'])

for hit in res['hits']['hits']:
    print("%(text)s" % hit["_source"])

def findPosition(query):
    return 5

def findDates():
    timeTablePosition = findPosition("timetable")