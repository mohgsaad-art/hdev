'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=(n,d=0)=>Number(n).toLocaleString('en-GB',{maximumFractionDigits:d,minimumFractionDigits:d}).replace('-','−');
const sum=a=>a.reduce((x,y)=>x+y,0);
const clone=o=>JSON.parse(JSON.stringify(o));
const hrs=t=>{const m=/^(\d{1,2}):(\d{2})$/.exec(t||'');return m?(+m[1])+(+m[2])/60:NaN;};
const hm=h=>{h=((h%24)+24)%24;let H=Math.floor(h+1e-9),M=Math.round((h-H)*60);if(M===60){H=(H+1)%24;M=0;}return String(H).padStart(2,'0')+':'+String(M).padStart(2,'0');};
const plural=(n,w)=>n+' '+w+(n===1?'':'s');

/* ---------- demo engine constants: every one is listed on the Sources page ---------- */
const DEMO={rho:1.2,g:9.81,acc:1.0,regen:0.88,worstF:1.15,cold:1.08,elStart:2026};
const MONTH_F=[1.18,1.16,1.08,1.0,0.95,0.92,0.92,0.93,0.96,1.02,1.1,1.16];
const SIZES=[22,40,50,60,90,120,150];
const PRICE_F={low:0.8,exp:1,high:1.25}, PLAN_F={cost:0.85,grid:0.92,early:1.0};
const PLAN_N={cost:'Lowest cost',grid:'Grid-friendly',early:'Ready earliest'};
const BANDS=[[22,12500,10000,35],[43.5,120000,16000,80],[50,150000,50000,80],[80,200000,150000,125],[150,400000,250000,250],[400,700000,500000,650]];
const EF_PATH={2026:19.35,2027:16.64,2028:14.75,2029:11.92,2030:10.27,2031:9.09,2032:8.85,2033:8.61,2034:8.26};
const FEE={radius:{base:17950,perA:1280,ref:'Radius connection charge, as listed in the COWI truck cost sheet. May be out of date'},cerius:{base:23500,perA:1812.5,ref:'Cerius price list 2026, category C, incl. VAT'},n1:{base:0,perA:0,ref:'No price list in the sources read. Fee left out'},trefor:{base:0,perA:0,ref:'No price list in the sources read. Fee left out'},other:{base:0,perA:0,ref:'No price list in the demo. Fee left out'}};
const CLS=[['1','Rigid 4×2, 7.5 to 10 t',7.1],['2','Rigid 4×2, 10 to 12 t',7.2],['3','Rigid 4×2, 12 to 16 t',7.4],['4','Rigid 4×2, over 16 t',8.4],['9','Rigid 6×2',8.5],['11','Rigid 6×4',8.5],['16','Rigid 8×4',9.0],['5','Tractor 4×2',8.7],['10','Tractor 6×2',8.8],['12','Tractor 6×4',8.8]];
const ROAD_V={deep:30,urban:50,non:80};
const HOL26=[[0,1],[3,2],[3,3],[3,5],[3,6],[4,14],[4,24],[4,25],[11,25],[11,26]];
const MONTHS=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

function opDays(s){let c=0;for(let m=0;m<12;m++){const dn=new Date(2026,m+1,0).getDate();for(let d=1;d<=dn;d++){const w=new Date(2026,m,d).getDay();
  const work=s.days==='all'||(s.days==='ms'&&w!==0)||(s.days==='mf'&&w>0&&w<6);if(!work)continue;
  if(s.hol==='dk'&&HOL26.some(h=>h[0]===m&&h[1]===d))continue;c++;}}return c;}
const residPct=y=>y<=6?15:y===7?12.5:y===8?10:y===9?7.5:y===10?5:0;
const pmt=(r,n,pv,fv)=>{if(!r)return(pv-fv)/n;const f=Math.pow(1+r,n);return r*(pv*f-fv)/((1+r)*(f-1));};
const amps=kw=>kw*1000/(Math.sqrt(3)*400);
const band=kw=>BANDS.find(b=>b[0]>=kw)||BANDS[BANDS.length-1];

/* ---------- field definitions: one list drives the forms, the checks and the Sources page ---------- */
const SRCN={std:'Standard',sample:'Sample value',assume:'Assumption',calc:'Calculated',you:'Your value',need:'Needed',blank:'',plain:'Starting choice'};
const F=(k,l,u,t,s,r,x)=>Object.assign({k,l,u,t,s,r},x||{});
const isStop=o=>o.type==='stop', notNone=o=>o.type!=='none', typed=o=>o.method==='typed', thermal=o=>o.hvacMode==='thermal';
const NB='Not used by the demo engine yet';
const HEIGHT={'1':3.6,'2':3.75,'3':3.9,'4':4,'5':4,'9':4,'10':4,'11':4,'12':4,'16':3.6};
const YN=[['no','No'],['yes','Yes']];
/* pop: the field sits in a named popup. opt: may stay empty. Fields the demo engine reads are listed in USED */
const DEFS={
  proj:{title:'Project',fields:[
    F('name','Project name','','txt','sample',''),
    F('scen','Scenario name','','txt','sample',''),
    F('mode','How should charging be worked out?','','radio','','',{o:[['sizing','Sizing','Charger power from the energy needed and the time parked.'],['sim','Simulation, step by step','Not part of this demo.',1]]}),
    F('brand','Brand-neutral comparison for tenders','','tog','','Hides make and model in the offer sheet')]},
  veh:{one:'vehicle',many:'vehicles',title:'Vehicle',lead:'The truck: its weight, its battery and what it replaces.',fields:[
    F('src','Where does the vehicle data come from?','','radio','','',{o:[['manual','I enter it',''],['lib','Pick from the vehicle library','EEA 2024 to 2025 registrations. Not part of this demo.',1]]}),
    F('cls','VECTO vehicle group','','sel','sample','',{o:CLS.map(c=>[c[0],'Group '+c[0]+': '+c[1]])}),
    F('curb','Chassis weight, empty','kg','num','sample','No datasheet'),
    F('bodyMass','Body weight','kg','num','std','EU standard value for a refuse body'),
    F('gvw','Gross vehicle weight','kg','num','sample',''),
    F('pmax','Largest motor power','kW','num','','',{opt:1}),
    F('dUse','Diesel the truck uses today','l/100 km','num','sample','',{dec:1}),
    F('battMode','Battery','','radio','','',{o:[['size','Let the tool size it','The smallest battery that still covers the hardest day at year 8.'],['sheet','I have a battery size','From a datasheet or a supplier offer.']]}),
    F('battKwh','Installed battery','kWh','num','','',{when:o=>o.battMode==='sheet'}),
    F('guar','Battery capacity guaranteed at year 8','%','num','assume','Rambøll 2023: warranties often go down to 70 %. Use the value in the offer or tender',{max:100}),
    F('trMass','Trailer weight','kg','num','','',{pop:'Trailer and wheels',opt:1}),
    F('mRed','Weight of the rotating wheels','kg','num','','',{pop:'Trailer and wheels',opt:1}),
    F('thetaRed','Inertia reduction factor','','num','','',{pop:'Trailer and wheels',opt:1,dec:3}),
    F('cdxa','Air drag area','m²','num','std','VECTO standard value for the vehicle group. Verify before use',{pop:'Air drag and size',dec:1}),
    F('height','Vehicle height','m','num','std','VECTO reference height for the vehicle group',{pop:'Air drag and size',dec:2}),
    F('cdFile','Air drag by wind angle, from the maker','','file','','',{pop:'Air drag and size'}),
    F('crr','Tyre rolling resistance','N/kN','num','sample','Placeholder, no source yet',{pop:'Tyres',dec:1}),
    F('rdyn','Tyre radius when rolling','m','num','','',{pop:'Tyres',opt:1,dec:3}),
    F('loadIdx','Tyre load index','','num','','',{pop:'Tyres',opt:1}),
    F('kt','Cold-tyre factor','','num','','Planned: 0.006 above load index 121, otherwise 0.010. Not decided',{pop:'Tyres',opt:1,dec:3}),
    F('wet','Road surface','','sel','assume','Wet and icy roads are planned, not built',{pop:'Tyres',o:[['dry','Dry']]}),
    F('effMethod','Efficiency method','','sel','assume','Loss maps are planned. The demo uses three efficiencies',{pop:'Drivetrain',o:[['eff','Separate efficiencies']]}),
    F('effMot','Motor efficiency','','num','assume','Placeholder until measured loss maps are used',{pop:'Drivetrain',dec:2,max:1}),
    F('effInv','Inverter efficiency','','num','assume','Placeholder until measured loss maps are used',{pop:'Drivetrain',dec:2,max:1}),
    F('effGb','Gearbox efficiency','','num','assume','Placeholder until measured loss maps are used',{pop:'Drivetrain',dec:2,max:1}),
    F('gear','Gearbox','','sel','','',{pop:'Drivetrain',o:[['one','Single speed'],['multi','Several gears']]}),
    F('ratio','Total gear ratio','','num','','',{pop:'Drivetrain',opt:1,dec:2}),
    F('jrot','Rotor inertia','kg·m²','num','','No fleet default exists',{pop:'Drivetrain',opt:1,dec:3}),
    F('lossFile','Loss maps for motor, inverter and gearbox','','file','','',{pop:'Drivetrain'}),
    F('vNoRegen','No braking energy back below','km/h','num','','',{pop:'Braking energy',opt:1}),
    F('pRegen','Largest braking power back','kW','num','','',{pop:'Braking energy',opt:1}),
    F('effRegen','Efficiency when braking','','num','','',{pop:'Braking energy',opt:1,dec:2,max:1}),
    F('usable','Usable share of the battery','%','num','sample','',{pop:'Battery details',max:100}),
    
    F('battMass','Battery weight','kg','num','','',{pop:'Battery details',opt:1}),
    F('chem','Cell chemistry','','sel','','',{pop:'Battery details',o:[['','Not given'],['lfp','LFP'],['nmc','NMC'],['other','Other']]}),
    F('dcMax','Fastest DC charging','kW','num','','',{pop:'Battery details',opt:1}),
    F('conn','Charging connector','','sel','','',{pop:'Battery details',o:[['','Not given'],['ccs','CCS2'],['mcs','MCS']]}),
    F('cRate','Largest charging rate up to 80 %','C','num','std','Reg. 2017/2400 Annex Xb, Appendix 10',{pop:'Battery details',dec:1}),
    F('ocv0','Cell voltage at 0 %, share of nominal','','num','std','Reg. 2017/2400 Annex Xb, Appendix 10',{pop:'Battery voltage and resistance',dec:2}),
    F('ocv10','At 10 %','','num','std','As above',{pop:'Battery voltage and resistance',dec:2}),
    F('ocv50','At 50 %','','num','std','As above',{pop:'Battery voltage and resistance',dec:2}),
    F('ocv90','At 90 %','','num','std','As above',{pop:'Battery voltage and resistance',dec:2}),
    F('ocv100','At 100 %','','num','std','As above',{pop:'Battery voltage and resistance',dec:2}),
    F('ri2','Internal resistance after 2 s','mΩ·Ah','num','std','Reg. 2017/2400 Annex Xb, Appendix 10, high-energy battery',{pop:'Battery voltage and resistance'}),
    F('ri10','After 10 s','mΩ·Ah','num','std','As above',{pop:'Battery voltage and resistance'}),
    F('ri20','After 20 s','mΩ·Ah','num','std','As above',{pop:'Battery voltage and resistance'}),
    F('ri120','After 120 s','mΩ·Ah','num','std','As above',{pop:'Battery voltage and resistance'}),
    F('esW','Electrical system','W','num','std','EU standard value',{pop:'On-board systems',min0:1}),
    F('psW','Air system for brakes and suspension','W','num','std','EU standard value',{pop:'On-board systems',min0:1}),
    F('spW','Power steering','W','num','std','EU standard method',{pop:'On-board systems',min0:1}),
    F('condW','Battery and motor cooling','W','num','std','EU standard value',{pop:'On-board systems',min0:1}),
    F('ptoOn','Equipment that is always on','W','num','','',{pop:'On-board systems',opt:1}),
    F('fES','Factor on the electrical system','','num','std','VECTO',{pop:'On-board systems',dec:2}),
    F('fPS','Factor on the air system','','num','std','VECTO',{pop:'On-board systems',dec:2}),
    F('fSP','Factor on power steering','','num','std','VECTO',{pop:'On-board systems',dec:2}),
    F('fHV','Factor on heating and cooling','','num','std','VECTO. 1.0 in the thermal model',{pop:'On-board systems',dec:2}),
    F('fCo','Factor on cooling of battery and motor','','num','std','VECTO',{pop:'On-board systems',dec:2}),
    F('priceEV','Electric truck price','DKK','num','sample','No source yet',{pg:'costs'}),
    F('priceD','Diesel truck price','DKK','num','sample','No source yet',{pg:'costs'}),
    F('svcEV','Service, electric','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('svcD','Service, diesel','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('insEV','Insurance, electric','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('insD','Insurance, diesel','DKK/month','num','sample','No source yet',{pg:'costs',min0:1})]},
  rt:{one:'route',many:'routes',title:'Route',lead:'What one vehicle drives on a working day.',fields:[
    F('method','Where does the route come from?','','radio','','',{o:[['typed','Typed in','Distance, stops and time at each stop.'],['cycle','A VECTO standard cycle','The demo engine cannot run these.'],['gps','A GPS log','The demo engine cannot run these.'],['ai','Describe it in words','Planned.',1]]}),
    F('mission','Standard cycle','','sel','','',{when:o=>o.method==='cycle',o:[['lh','Long haul'],['rd','Regional delivery'],['ud','Urban delivery'],['mu','Municipal utility'],['co','Construction']]}),
    F('gpsFile','GPS log','','file','','',{when:o=>o.method==='gps'}),
    F('km','Distance per day','km','num','sample','',{when:typed}),
    F('stops','Stops per day','','num','sample','',{when:typed,min0:1}),
    F('stopTime','Time at each stop','s','num','sample','',{when:typed,min0:1}),
    F('road','Type of streets','','sel','sample','',{when:typed,o:[['deep','Dense city streets'],['urban','City'],['non','Outside the city']]}),
    F('speed','Driving speed between stops','km/h','num','assume','Tool default for the type of streets: 30, 50 or 80 km/h',{pop:'Speed and hills',when:typed}),
    F('grade','Slope','%','num','assume','Flat unless you say otherwise. The demo engine treats every route as flat',{pop:'Speed and hills',when:typed,min0:1,dec:1})]},
  load:{one:'payload profile',many:'payload profiles',title:'Payload',lead:'What the vehicle carries.',fields:[
    F('basis','Which payload?','','sel','','',{o:[['custom','My own figures'],['ref','VECTO reference payload'],['max','The most the vehicle may carry']]}),
    F('shape','How does it change during the day?','','radio','','',{o:[['const','Same all day','One weight for the whole route.'],['linear','Changes steadily along the route','A refuse truck filling up, or a delivery truck emptying.'],['stops','Set at each stop','Fill it in under Stops on the fleet row.']]}),
    F('start',o=>o.shape==='const'?'Payload':'Payload when leaving','t','num','std','EU standard low load for this type of work',{dec:1,min0:1}),
    F('end','Payload at the end of the route','t','num','std','EU standard reference load for this type of work',{dec:1,min0:1,when:o=>o.shape==='linear'})]},
  eq:{one:'PTO profile',many:'PTO profiles',title:'PTO',lead:'Powered equipment on the body: a bin lift, a crane, a mixer drum, a fridge unit.',fields:[
    F('type','When does the equipment work?','','radio','','',{o:[['none','No powered equipment',''],['stop','At each stop','A bin lift, a tail lift or a crane.'],['always','All the time','A fridge unit or a mixer drum.']]}),
    F('kwhStop','Energy per stop','kWh','num','assume','EU standard refuse profile. Not yet verified',{dec:3,when:isStop}),
    F('sStop','Working time per stop','s','num','assume','EU standard refuse profile. Not yet verified',{when:isStop,min0:1}),
    F('profFile','Power profile over time, instead of one figure','','file','','',{when:isStop}),
    F('wOn','Power while on shift','W','num','','',{when:o=>o.type==='always'}),
    F('driveW','Power while driving','W','num','','',{when:notNone,opt:1}),
    F('eff','Efficiency at stops','','num','assume','No source yet. 1.0 means no loss',{pop:'Efficiency and drive',dec:2,max:1,when:notNone}),
    F('effDrive','Efficiency while driving','','num','assume','No source yet. 1.0 means no loss',{pop:'Efficiency and drive',dec:2,max:1,when:notNone}),
    F('ownMotor','The body has its own electric motor','','tog','','',{pop:'Efficiency and drive',when:notNone}),
    F('effPtoMot','Efficiency of that motor','','num','','No source yet',{pop:'Efficiency and drive',opt:1,dec:2,max:1,when:o=>o.type!=='none'&&o.ownMotor==='yes'}),
    F('stopAsPto','Count the whole stop as working time','','tog','','Not a VECTO method',{pop:'Efficiency and drive',when:isStop})]},
  sch:{one:'schedule',many:'schedules',title:'Schedule',lead:'When the vehicles are away from the depot.',fields:[
    F('out','Leaves the depot','','time','sample',''),
    F('back','Back at the depot','','time','sample',''),
    F('days','Working days','','sel','sample','',{o:[['mf','Monday to Friday'],['ms','Monday to Saturday'],['all','Every day']]}),
    F('hol','Public holidays','','sel','std','Danish public holidays, 2026',{o:[['dk','Off on Danish public holidays'],['none','Works on public holidays']]}),
    F('opd','Operating days a year','','info','calc','Working days minus holidays, 2026 calendar',{v:o=>opDays(o)+' days'})]},
  depot:{title:'Depot and grid',fields:[
    F('name','Depot name','','txt','sample',''),
    F('addr','Address or town','','txt','sample',''),
    F('mode','Is there a grid connection today?','','radio','','',{o:[['existing','Yes, and I know its size','The tool checks whether charging fits.'],['new','No, or I want it sized','The tool works out the connection you need.']]}),
    F('limit','Connection size','kW','num','sample','',{when:o=>o.mode==='existing'}),
    F('dso','Grid company','','sel','sample','',{o:[['radius','Radius'],['cerius','Cerius'],['n1','N1'],['trefor','TREFOR El-net'],['other','Other']]}),
    F('access','Access to the grid','','sel','','',{o:[['full','Full access'],['lim','Limited access']]}),
    F('baseMode','Power the buildings already use','','radio','','',{o:[['fixed','One figure',''],['elo','Hourly meter data from Eloverblik','Not part of this demo.',1],['log','Upload from a logger','Not part of this demo.',1]]}),
    F('base','Building load','kW','num','sample','A steady value in the demo',{min0:1}),
    F('spaces','Parking spaces with room for a charger','','num','','',{pop:'Parking',opt:1}),
    F('pSpace','Power for each space','kW','num','','',{pop:'Parking',opt:1}),
    F('cut','Cut in power','%','num','','A what-if. Not a forecast',{pop:'Limited access what-if',opt:1,max:100}),
    F('cutFrom','From','','time','','',{pop:'Limited access what-if',opt:1}),
    F('cutTo','To','','time','','',{pop:'Limited access what-if',opt:1})]},
  chg:{title:'Charging',fields:[
    F('chgMode','Chargers','','radio','','',{o:[['auto','Size the chargers for me','The smallest size that has every vehicle full before it leaves.'],['set','I choose the size','']]}),
    F('kw','Charger power','','sel','','',{when:o=>o.chgMode==='set',o:SIZES.map(z=>[String(z),z+' kW'])}),
    F('points','Charge points','','info','calc','One for each vehicle in the demo',{v:()=>'One for each vehicle'}),
    F('plan','Charging plan','','radio','','',{o:[['cost','Lowest cost','Charge in the night hours, when power is cheapest.'],['grid','Grid-friendly','Spread charging over the whole stay to keep the peak low.'],['early','Ready earliest','Charge at full power as soon as vehicles are back.']]}),
    F('readyBy','Ready by','','time','','Empty means when the vehicle leaves',{opt:1}),
    F('loadF','Average charger load while charging','%','num','std','COWI truck cost sheet',{pop:'Charger load and losses',max:100}),
    F('loss','Charger losses','%','num','assume','4-leaf 2023 gives 3 to 4 %',{pop:'Charger load and losses',min0:1,max:50}),
    F('step','Time step','min','num','assume','Mock-up value. Must come from Energinet specifications',{pop:'Charger load and losses'}),
    F('flex','Offer flexibility to the power markets','','tog','','',{pop:'Flexibility'}),
    F('mkts','Markets','','multi','','',{pop:'Flexibility',o:[['fcrd','FCR-D'],['fcrn','FCR-N'],['mfrr','mFRR'],['afrr','aFRR']]})]},
  wx:{title:'Weather',fields:[
    F('year','Which year should the fleet be sized for?','','radio','','',{o:[['normal','A normal year',''],['cold','A cold winter','More energy in November to February.']]}),
    F('station','Weather station','','info','calc','The full tool takes the nearest DMI station with a full year of data',{v:()=>'Nearest to the depot'}),
    F('detail','Level of detail','','sel','','Not decided which is the default',{o:[['day','One value a day'],['drive','Driving hours'],['hour','Every hour']]}),
    F('shift','Shift every temperature by','K','num','std','No shift',{min0:1,neg:1,dec:1}),
    F('worst','Run the worst day as its own case','','tog','',''),
    F('wind','Reference wind at 10 m','m/s','num','std','HDEV decision. Replaces the 3 m/s at 4 m in VECTO',{pop:'Wind',dec:3}),
    F('hvacMode','Cab heating and cooling','','radio','','',{o:[['const','One fixed power','The EU standard value, or your own.'],['thermal','Worked out from the weather','Needs the cab data below. The demo engine still uses the fixed power.']]}),
    F('hvacW','Heating and cooling power','W','num','std','EU standard value',{min0:1}),
    F('persons','People in the cab','','num','','',{when:thermal}),
    F('heater','Heater','','sel','','',{when:thermal,o:[['hp','Heat pump'],['el','Electric heater'],['fuel','Fuel heater']]}),
    F('tHeat','Heat below','°C','num','std','VECTO',{pop:'Set-points',when:thermal,min0:1}),
    F('tCool','Cool above','°C','num','std','VECTO',{pop:'Set-points',when:thermal,min0:1}),
    F('tOff','Stop cooling below','°C','num','std','VECTO',{pop:'Set-points',when:thermal,min0:1}),
    F('aSurf','Cab surface','m²','num','','No sourced default exists',{pop:'Cab data',when:thermal,dec:1}),
    F('uVal','Heat loss through the cab','W/m²K','num','','No sourced default exists',{pop:'Cab data',when:thermal,dec:2}),
    F('aWin','Window area','m²','num','','No sourced default exists',{pop:'Cab data',when:thermal,dec:1}),
    F('vol','Cab volume','m³','num','','No sourced default exists',{pop:'Cab data',when:thermal,dec:1}),
    F('pHeat','Largest heating power','W','num','','No sourced default exists',{pop:'Cab data',when:thermal}),
    F('pCool','Largest cooling power','W','num','','No sourced default exists',{pop:'Cab data',when:thermal}),
    F('vent','Ventilation','m³/h','num','','No sourced default exists',{pop:'Cab data',when:thermal}),
    F('ventH','Ventilation while heating','m³/h','num','','No sourced default exists',{pop:'Cab data',when:thermal}),
    F('heatEff','Electric heater efficiency','','num','std','VECTO',{pop:'Climate constants',dec:2,max:1}),
    F('ventP','Power for ventilation','Wh/m³','num','std','VECTO',{pop:'Climate constants',dec:2}),
    F('tBound','Boundary temperature','°C','num','std','VECTO',{pop:'Climate constants'}),
    F('solG','Sun through the glass','','num','std','VECTO',{pop:'Climate constants',dec:2}),
    F('solF','Sun factor','','num','std','VECTO',{pop:'Climate constants',dec:2}),
    F('freshQ','Fresh air for two people','m³/h','num','assume','Dvorak preprint',{pop:'Climate constants'})]},
  pr:{title:'Prices',fields:[
    F('area','Price area','','sel','calc','Taken from the depot address',{o:[['dk2','DK2, east of the Great Belt'],['dk1','DK1, west of the Great Belt']]}),
    F('elPrice','Electricity price, all in','DKK/kWh','num','sample','Demo value. The full tool uses hourly prices, tariffs and taxes',{dec:2}),
    F('level','Electricity price level','','sel','assume','Tool default. Low is 20 % under, high is 25 % over',{o:[['low','Low'],['exp','Expected'],['high','High']]}),
    F('spotFile','Your own hourly prices','','file','',''),
    F('tariff','Grid tariff and taxes','DKK/kWh','num','','',{opt:1,dec:2}),
    F('dPrice','Diesel price','DKK/l','num','std','OK.dk, January to June 2024, plus 0.50 DKK duty. Refresh before use',{dec:2}),
    F('adblue','AdBlue','DKK/l','num','sample','Source to confirm',{pop:'Other fuels and public charging',dec:2}),
    F('hvo','HVO100','DKK/l','num','sample','Source to confirm',{pop:'Other fuels and public charging',dec:2}),
    F('pub','Public fast charging','DKK/kWh','num','std','FDM 2024',{pop:'Other fuels and public charging',dec:2})]},
  fin:{title:'Costs',fields:[
    F('years','Ownership period','','sel','assume','Tool default',{o:[['8','8 years'],['10','10 years'],['12','12 years']]}),
    F('how','Financing','','sel','','',{o:[['loan','Loan'],['lease','Lease'],['cash','Cash']]}),
    F('interest','Interest rate','%','num','sample','No source yet',{dec:2,min0:1}),
    F('wage','Driver wage','DKK/month','num','sample','No source yet. Same for electric and diesel',{min0:1}),
    F('resid','Value at the end','','info','sample','Depreciation table from the COWI truck cost sheet. No source given there',{v:o=>residPct(+o.years)+' % of the price'}),
    F('depYears','Years to write off the depot','','num','','Not decided',{opt:1})]},
  tax:{title:'Taxes and CO₂',fields:[
    F('e1','Road tax, electric, 2026 to 2027','DKK/km','num','std','Danish Ministry of Taxation rates, via the COWI truck cost sheet',{dec:4,min0:1}),
    F('d1','Road tax, diesel, 2026 to 2027','DKK/km','num','std','Danish Ministry of Taxation rates, via the COWI truck cost sheet',{dec:4,min0:1}),
    F('e2','Road tax, electric, 2028','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('d2','Road tax, diesel, 2028','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('e3','Road tax, electric, from 2029','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('d3','Road tax, diesel, from 2029','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('co2cls','CO₂ class of the diesel truck','','sel','','',{o:[['1','1'],['2','2'],['3','3'],['4','4'],['5','5']]}),
    F('subsidy','Subsidy scheme','','sel','','The Vejdirektoratet pool closed on 30 September 2026',{o:[['none','None'],['vd','Vejdirektoratet pool'],['bmv','German BMV scheme'],['own','Own amount']]}),
    F('grant','Grant or subsidy, paid once','DKK','num','assume','None applied',{min0:1})]},
  co2:{title:'Taxes and CO₂',fields:[
    F('gridMode','CO₂ from grid electricity','','radio','','',{o:[['path','Danish Energy Agency projection','19.35 g/kWh in 2026, falling to 8.26 g/kWh in 2034. Includes upstream.'],['fixed','My own value','One value for every year.']]}),
    F('gridEF','Grid electricity, every year','g/kWh','num','','',{dec:2,min0:1,when:o=>o.gridMode==='fixed'}),
    F('co2D','Diesel','kg/l','num','sample','Source pending',{dec:2}),
    F('hours','Count CO₂ at the hours the trucks really charge','','tog','','Planned')]}
};
/* what the demo engine reads. Everything else is kept with the project and listed, but does not change the result yet */
const USED={veh:'src cls curb bodyMass gvw dUse battMode battKwh cdxa crr effMot effInv effGb usable guar esW psW spW condW priceEV priceD svcEV svcD insEV insD',rt:'method road km stops stopTime speed',load:'shape start end',eq:'type kwhStop sStop wOn eff',sch:'out back days hol',depot:'mode limit dso base',chg:'chgMode kw plan loadF loss',wx:'year hvacW',pr:'elPrice level dPrice',fin:'years interest wage',tax:'e1 d1 e2 d2 e3 d3 grant',co2:'gridMode gridEF co2D',proj:'name scen mode brand'};
const used=(type,k)=>(' '+USED[type]+' ').includes(' '+k+' ');
const LIBS=['veh','rt','load','eq','sch'];
const SETS=['chg','wx','pr','fin','tax','co2'];
const SETPAGE={chg:'charging',wx:'weather',pr:'prices',fin:'costs',tax:'tax',co2:'tax'};

/* ---------- project data ---------- */
const mk=o=>{o._d=clone(o);if(o.id){delete o._d.id;delete o._d.name;}return o;};
const VEH_STD={src:'manual',pmax:'',trMass:'',mRed:'',thetaRed:'',height:4,cdFile:'',rdyn:'',loadIdx:'',kt:'',wet:'dry',effMethod:'eff',gear:'one',ratio:'',jrot:'',lossFile:'',vNoRegen:'',pRegen:'',effRegen:'',battMass:'',chem:'',dcMax:'',conn:'',cRate:0.9,ocv0:0.88,ocv10:0.94,ocv50:1,ocv90:1.06,ocv100:1.12,ri2:210,ri10:240,ri20:270,ri120:390,ptoOn:'',fES:0.7,fPS:1,fSP:0.7,fHV:1.25,fCo:1,hvacMode:'const',persons:'',heater:'hp',tHeat:18,tCool:23,tOff:17,aSurf:'',uVal:'',aWin:'',vol:'',pHeat:'',pCool:'',vent:'',ventH:'',heatEff:0.93,ventP:0.56,tBound:17,solG:0.95,solF:0.25,freshQ:100,cls:'4',cdxa:8.4,crr:6,effMot:0.95,effInv:0.95,effGb:0.98,esW:1000,psW:687,hvacW:375,spW:306,condW:550,usable:90,guar:70,priceEV:2050000,priceD:1150000,svcEV:7685,svcD:5000,insEV:1476,insD:768,battMode:'size',battKwh:''};
const EQ_STD={kwhStop:0.15,sStop:23,wOn:'',eff:1,profFile:'',driveW:'',effDrive:1,ownMotor:'no',effPtoMot:'',stopAsPto:'no'};
const BLANK={
  veh:()=>Object.assign({},VEH_STD,{curb:'',bodyMass:'',gvw:'',dUse:''}),
  rt:()=>({method:'typed',mission:'ud',gpsFile:'',km:'',stops:'',stopTime:'',road:'urban',speed:50,grade:0}),
  load:()=>({basis:'custom',shape:'const',start:'',end:''}),
  eq:()=>Object.assign({type:'none'},EQ_STD),
  sch:()=>({out:'',back:'',days:'mf',hol:'dk'})
};
function sampleProject(){return{
  proj:mk({name:'Sample project',scen:'Base case',mode:'sizing',brand:'no'}),
  lib:{
    veh:[mk(Object.assign({id:'v1',name:'Refuse truck'},VEH_STD,{curb:11500,bodyMass:6000,gvw:26000,dUse:55}))],
    rt:[mk({id:'r1',name:'City collection round',method:'typed',mission:'mu',gpsFile:'',km:120,stops:400,stopTime:20,road:'deep',speed:30,grade:0})],
    load:[mk({id:'l1',name:'Fills up along the route',basis:'custom',shape:'linear',start:0.6,end:3})],
    eq:[mk(Object.assign({id:'e1',name:'Bin lift',type:'stop'},EQ_STD)),mk(Object.assign({id:'e0',name:'None',type:'none'},EQ_STD))],
    sch:[mk({id:'s1',name:'Day shift',out:'06:00',back:'16:00',days:'mf',hol:'dk'}),mk({id:'s2',name:'Night shift',out:'19:00',back:'05:00',days:'mf',hol:'dk'})]},
  groups:[{id:1,name:'Refuse, day shift',n:4,n0:4,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s1'},{id:2,name:'Refuse, night shift',n:2,n0:2,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s2'}],
  depot:mk({name:'Main depot',addr:'Copenhagen',mode:'existing',limit:400,dso:'radius',access:'full',baseMode:'fixed',base:30,spaces:'',pSpace:'',cut:'',cutFrom:'',cutTo:''}),
  chg:mk({chgMode:'auto',kw:'50',plan:'cost',readyBy:'',loadF:85,loss:4,step:5,flex:'no',mkts:''}),
  wx:mk({year:'normal',detail:'hour',shift:0,worst:'no',wind:5.028,hvacMode:'const',hvacW:375,persons:'',heater:'hp',tHeat:18,tCool:23,tOff:17,aSurf:'',uVal:'',aWin:'',vol:'',pHeat:'',pCool:'',vent:'',ventH:'',heatEff:0.93,ventP:0.56,tBound:17,solG:0.95,solF:0.25,freshQ:100}),
  pr:mk({area:'dk2',elPrice:1.6,level:'exp',spotFile:'',tariff:'',dPrice:11.65,adblue:6.96,hvo:19.97,pub:3.25}),
  fin:mk({years:'10',how:'loan',interest:3.45,wage:30000,depYears:''}),
  tax:mk({e1:0.1008,d1:0.8525,e2:0.1864,d2:1.4324,e3:0.2613,d3:1.6181,co2cls:'5',subsidy:'none',grant:0}),
  co2:mk({gridMode:'path',gridEF:19.35,co2D:2.65,hours:'no'}),
  nid:10};}
let P=sampleProject();
const tpl=(lib,id)=>P.lib[lib].find(x=>x.id===id);
const visible=(type,o)=>DEFS[type].fields.filter(f=>!f.when||f.when(o));
function isMissing(f,o){if(f.t==='info'||f.t==='radio'||f.t==='tog'||f.t==='multi'||f.t==='file'||f.t==='sel')return false;const v=o[f.k];if(v===''||v==null)return !f.opt;
  if(f.t==='num')return !(typeof v==='number'&&isFinite(v)&&(f.neg||(f.min0?v>=0:v>0))&&(f.max==null||v<=f.max));
  if(f.t==='time')return isNaN(hrs(v));return false;}
function srcOf(f,o){if(f.t==='info')return f.s;if(isMissing(f,o))return'need';const d=o._d?o._d[f.k]:undefined;if(d!==undefined&&o[f.k]===d)return o[f.k]===''?'blank':(f.s||'plain');return o[f.k]===''||o[f.k]==null?'blank':'you';}
const labelOf=(f,o)=>typeof f.l==='function'?f.l(o):f.l;
function shown(f,o){const v=f.t==='info'?f.v(o):o[f.k];if(f.t==='file')return v||'No file';if(f.t==='multi')return f.o.filter(q=>(' '+v+' ').includes(' '+q[0]+' ')).map(q=>q[1]).join(', ')||'None';if(f.t==='tog')return v==='yes'?'Yes':'No';if(f.o){const x=f.o.find(q=>String(q[0])===String(v));return x?x[1]:String(v);}
  if(f.t==='num'&&typeof v==='number')return fmt(v,f.dec||0)+(f.u?' '+f.u:'');return v===''||v==null?'':String(v);}

/* every object that feeds the run, with a readable place name */
function parts(){const out=[],seen={};
  P.groups.forEach(g=>LIBS.forEach(l=>{const t=tpl(l,g[l]);if(t&&!seen[l+t.id]){seen[l+t.id]=1;out.push({type:l,o:t,where:DEFS[l].title+': '+t.name,open:{lib:l,tid:t.id}});}}));
  out.unshift({type:'proj',o:P.proj,where:'Project',open:{page:'project'}});
  out.push({type:'depot',o:P.depot,where:'Depot and grid',open:{page:'depot'}});
  SETS.forEach(s=>out.push({type:s,o:P[s],where:DEFS[s].title,open:{page:SETPAGE[s]}}));return out;}
function missing(){const m=[];
  P.groups.forEach(g=>{if(!(g.n>=1))m.push({where:'Fleet: '+g.name,label:'Number of vehicles',open:{page:'fleet'}});
    LIBS.forEach(l=>{if(!tpl(l,g[l]))m.push({where:'Fleet: '+g.name,label:DEFS[l].title+' not chosen',open:{page:'fleet'}});});});
  if(!P.groups.length)m.push({where:'Fleet',label:'Add at least one group of vehicles',open:{page:'fleet'}});
  parts().forEach(p=>visible(p.type,p.o).forEach(f=>{if(isMissing(f,p.o))m.push({where:p.where,label:labelOf(f,p.o),open:f.pg?{page:f.pg}:Object.assign({pop:f.pop},p.open)});
    if(p.type==='rt'&&f.k==='method'&&p.o.method!=='typed')m.push({where:p.where,label:'The demo engine can only run a typed route',open:p.open});}));
  P.groups.forEach(g=>{const s=tpl('sch',g.sch);if(s&&!isNaN(hrs(s.out))&&hrs(s.out)===hrs(s.back))m.push({where:'Schedule: '+s.name,label:'Leaving and return time are the same',open:{lib:'sch',tid:s.id}});});
  return m;}
function inputRows(){const rows=[];
  P.groups.forEach(g=>rows.push({where:'Fleet: '+g.name,label:'Vehicles',value:String(g.n),src:g.n===g.n0?'sample':'you',ref:''}));
  parts().forEach(p=>visible(p.type,p.o).forEach(f=>{const s=f.t==='radio'?'you':srcOf(f,p.o);if(s==='blank')return;rows.push({where:p.where,label:labelOf(f,p.o),value:shown(f,p.o),src:s,ref:s==='you'?'':(f.r||''),radio:f.t==='radio',used:used(p.type,f.k)});}));
  return rows;}
const snapshot=()=>JSON.stringify(P,(k,v)=>k==='_d'||k==='n0'||k==='nid'?undefined:v);

/* ---------- stop table: the day of one fleet row, stop by stop. Built from the route, the payload and the PTO; edits stay on that row ---------- */
function stopRows(gr){const rt=tpl('rt',gr.rt),l=tpl('load',gr.load),e=tpl('eq',gr.eq),n=rt&&rt.method==='typed'?Math.round(+rt.stops||0):0,ov=gr.ov||{},rows=[];
  for(let i=1;i<=n;i++){const o=ov[i]||{},p0=l?(l.shape==='linear'?l.start+(l.end-l.start)*i/n:l.start):0;
    rows.push({i,d:o.d!=null?o.d:rt.km*i/(n+1),t:o.t!=null?o.t:rt.stopTime,p:o.p!=null?o.p:p0,on:o.on!=null?o.on:!!(e&&e.type==='stop'),ed:!!ov[i]});}
  return rows;}
const hasOv=gr=>gr.ov&&Object.keys(gr.ov).length>0;

/* ---------- the stand-in model ---------- */
function chargeGroup(g,plan,D){const N=96,lf=D.loadF/100,loss=D.loss/100,st=Math.round(g.back*4)%N,nS=Math.max(0,Math.round(g.dwellH*4)),S=[];
  for(let k=0;k<nS;k++)S.push((st+k)%N);
  const need=g.worst/(1-loss);let order=S,winH=g.dwellH;
  if(plan==='cost'){const j=S.indexOf(88);if(j>=0&&(nS-j)/4>=3){winH=(nS-j)/4;order=S.slice(j).concat(S.slice(0,j).reverse());}else winH=Math.max(1,g.dwellH-1);}
  else if(plan==='grid'){winH=Math.max(1,g.dwellH-2);order=S.slice(2);}
  else winH=Math.max(1,Math.min(4,g.dwellH));
  const needKw=need/(lf*winH),kw=D.chgMode==='set'?+D.kw:(SIZES.find(z=>z>=needKw)||SIZES[SIZES.length-1]);
  let p=kw*lf;if(plan==='grid')p=Math.min(p,need/winH);
  const slot=new Array(N).fill(0);let rem=need;
  for(const i of order){if(rem<=1e-6)break;const e=Math.min(rem,p*0.25);slot[i]=e/0.25;rem-=e;}
  const on=S.map((i,k)=>slot[i]>0?k:-1).filter(k=>k>=0),a=on.length?on[0]:0,b=on.length?on[on.length-1]:0;
  const lastFrac=on.length?slot[S[b]]/p:0,end=nS?(S[b]/4+0.25*lastFrac):g.back;
  return{kw,p,slot,need,start:nS?S[a]/4:g.back,end,ready:rem<=0.5,short:rem*(1-loss),spare:Math.max(0,(nS-1-b)/4+0.25*(1-lastFrac)),hours:on.length/4};}

function compute(planOv){
  const D=Object.assign({},P.depot,P.chg,planOv?{plan:planOv}:{}),plan=D.plan,loss=D.loss/100,Y=+P.fin.years,r=P.fin.interest/100;
  const mf=MONTH_F.map((f,i)=>P.wx.year==='cold'&&(i<2||i>9)?f*DEMO.cold:f);
  const elP=P.pr.elPrice*PRICE_F[P.pr.level]*PLAN_F[plan];
  const rate=(yr,el)=>yr<=2027?(el?P.tax.e1:P.tax.d1):yr===2028?(el?P.tax.e2:P.tax.d2):(el?P.tax.e3:P.tax.d3);
  const G=P.groups.map(gr=>{const v=tpl('veh',gr.veh),rt=tpl('rt',gr.rt),l=tpl('load',gr.load),e=tpl('eq',gr.eq),s=tpl('sch',gr.sch),n=gr.n;
    const SR=hasOv(gr)?stopRows(gr):null,nOn=SR?SR.filter(x=>x.on).length:rt.stops;
    const vms=rt.speed/3.6,pay0=l.start,pay1=l.shape==='linear'?l.end:l.start,payAvg=SR?sum(SR.map(x=>x.p))/SR.length:(pay0+pay1)/2,mass=v.curb+v.bodyMass+payAvg*1000;
    const eta=v.effMot*v.effInv*v.effGb,d=rt.km*1000,J=3.6e6;
    const roll=mass*DEMO.g*v.crr/1000*d/J,air=0.5*DEMO.rho*v.cdxa*vms*vms*d/J,kin=rt.stops*0.5*mass*vms*vms/J;
    const wheel=roll+air+kin,regen=kin*DEMO.regen*eta,drive=wheel/eta-regen;
    const tA=vms/DEMO.acc,dA=vms*vms/(2*DEMO.acc),seg=rt.stops?d/rt.stops:d,cruise=Math.max(0,seg-2*dA);
    const tDrive=(rt.stops?rt.stops*(2*tA+cruise/vms):d/vms)/3600,tStop=(SR?sum(SR.map(x=>x.t)):rt.stops*rt.stopTime)/3600,tEq=e.type==='stop'?nOn*e.sStop/3600:0;
    const out=hrs(s.out),back=hrs(s.back),shiftH=((back-out+24)%24)||24,dwellH=24-shiftH;
    const hv=P.wx.hvacW,auxE=((v.esW+v.psW+hv+v.spW+v.condW)+(v.esW+v.psW+hv))/2000*shiftH;
    const eqE=e.type==='stop'?nOn*e.kwhStop/e.eff:e.type==='always'?e.wOn/1000*shiftH/e.eff:0;
    const avg=drive+auxE+eqE,months=mf.map(f=>avg*f),mean=sum(months)/12,worst=Math.max(...months)*DEMO.worstF;
    const us=v.usable/100,gu=v.guar/100,batt=v.battMode==='size'?Math.ceil(worst/(us*gu)/10)*10:v.battKwh;
    const g={gr,v,rt,l,e,s,n,name:gr.name,mass,eta,roll,air,kin,wheel,regen,drive,auxE,eqE,avg,months,mean,worst,batt,usable:batt*us,usableEol:batt*us*gu,
      tNeed:tDrive+tStop+tEq,tDrive,tStop,tEq,out,back,shiftH,dwellH,payMax:SR?Math.max(pay0,...SR.map(x=>x.p)):Math.max(pay0,pay1),payLimit:(v.gvw-v.curb-v.bodyMass)/1000,days:opDays(s)};
    g.kmYr=rt.km*g.days;g.kWhGrid=mean*g.days/(1-loss);g.c=chargeGroup(g,plan,D);
    const res=residPct(Y)/100,b=band(g.c.kw);
    g.cost={finE:pmt(r/12,Y*12,v.priceEV,v.priceEV*res)*12,finD:pmt(r/12,Y*12,v.priceD,v.priceD*res)*12,chg:b[1]+b[2],energyE:g.kWhGrid*elP,fuelD:g.kmYr*v.dUse/100*P.pr.dPrice,
      svcE:(v.svcEV+v.insEV)*12,svcD:(v.svcD+v.insD)*12,wage:P.fin.wage*12};
    g.dieselL=g.kmYr*v.dUse/100;return g;});
  const N=sum(G.map(g=>g.n)),load=new Array(96).fill(P.depot.base);
  G.forEach(g=>g.c.slot.forEach((x,i)=>{load[i]+=g.n*x;}));
  const peak=Math.max(...load),peakAt=load.indexOf(peak)/4,isNew=P.depot.mode==='new',limit=isNew?null:P.depot.limit,fee=FEE[P.depot.dso];
  const conn=isNew?(fee.base?fee.base+Math.max(0,amps(peak)-25)*fee.perA:0):Math.max(0,amps(peak)-amps(limit))*fee.perA;
  /* cost, whole fleet, year by year */
  const K=['fin','chg','energy','svc','tax','wage','grant'],KN={fin:'Financing the trucks',chg:'Chargers and grid connection',energy:'Electricity or diesel',svc:'Service and insurance',tax:'Road tax',wage:'Driver wages',grant:'Grant or subsidy'};
  const rowsE=[],rowsD=[];
  for(let y=1;y<=Y;y++){const yr=DEMO.elStart+y-1,E={yr,fin:0,chg:0,energy:0,svc:0,tax:0,wage:0,grant:0},Dd={yr,fin:0,chg:0,energy:0,svc:0,tax:0,wage:0,grant:0};
    G.forEach(g=>{const c=g.cost;E.fin+=g.n*c.finE;E.energy+=g.n*c.energyE;E.svc+=g.n*c.svcE;E.tax+=g.n*g.kmYr*rate(yr,true);E.wage+=g.n*c.wage;if(y===1)E.chg+=g.n*c.chg;
      Dd.fin+=g.n*c.finD;Dd.energy+=g.n*c.fuelD;Dd.svc+=g.n*c.svcD;Dd.tax+=g.n*g.kmYr*rate(yr,false);Dd.wage+=g.n*c.wage;});
    if(y===1){E.chg+=conn;E.grant=-P.tax.grant;}E.tot=sum(K.map(k=>E[k]));Dd.tot=sum(K.map(k=>Dd[k]));rowsE.push(E);rowsD.push(Dd);}
  const cumE=[0],cumD=[0];let be=null;rowsE.forEach((E,i)=>{cumE.push(cumE[i]+E.tot);cumD.push(cumD[i]+rowsD[i].tot);if(be===null&&cumE[i+1]<=cumD[i+1])be=i+1;});
  const totE=cumE[Y],totD=cumD[Y],kmTot=sum(G.map(g=>g.n*g.kmYr))*Y;
  const cats=K.map(k=>[KN[k],sum(rowsD.map(x=>x[k])),sum(rowsE.map(x=>x[k]))]).filter(c=>c[1]||c[2]);
  /* CO2 */
  const ef=yr=>P.co2.gridMode==='fixed'?P.co2.gridEF:(EF_PATH[yr]!=null?EF_PATH[yr]:EF_PATH[2034]);
  const co2D=sum(G.map(g=>g.n*g.dieselL))*P.co2.co2D/1000,kWhFleet=sum(G.map(g=>g.n*g.kWhGrid));
  const co2Rows=[];let co2Saved=0;for(let y=1;y<=Y;y++){const yr=DEMO.elStart+y-1,e=kWhFleet*ef(yr)/1e6;co2Saved+=co2D-e;co2Rows.push([yr,ef(yr),e,co2D,co2Saved]);}
  /* checks */
  const all=fn=>G.every(fn),bad=fn=>G.filter(g=>!fn(g)).map(g=>g.name).join(', ');
  const fNew=g=>g.worst<=g.usable,fEol=g=>g.worst<=g.usableEol,fRdy=g=>g.c.ready,fTime=g=>g.tNeed<=g.shiftH,fPay=g=>g.payMax<=g.payLimit;
  const minLeft=fn=>Math.min(...G.map(fn));
  const checks=[
    {k:'batt',t:'The battery covers the hardest day when new',ok:all(fNew),d:all(fNew)?fmt(minLeft(g=>100-g.worst/g.batt*100))+' % left at the lowest':'Too small for: '+bad(fNew),go:'bat'},
    {k:'eol',t:'The battery still covers the hardest day at year 8',ok:all(fEol),d:all(fEol)?'Within the guaranteed capacity':'Too small for: '+bad(fEol),go:'bat'},
    {k:'rdy',t:'Every vehicle is full before it leaves',ok:all(fRdy),d:all(fRdy)?fmt(minLeft(g=>g.c.spare),1)+' h to spare at the tightest':'Not full in time: '+bad(fRdy),go:'ch'},
    isNew?{k:'grid',t:'Grid connection needed',ok:true,d:fmt(peak)+' kW, about '+fmt(amps(peak))+' A',go:'gr'}
         :{k:'grid',t:'Charging fits the grid connection',ok:peak<=limit,d:peak<=limit?fmt(limit-peak)+' kW to spare at the peak':fmt(peak-limit)+' kW over at the peak',go:'gr'},
    {k:'time',t:'The route fits in the shift',ok:all(fTime),d:all(fTime)?fmt(minLeft(g=>g.shiftH-g.tNeed),1)+' h to spare at the tightest':'Too long for: '+bad(fTime),go:'en'},
    {k:'pay',t:'The load is within the weight limit',ok:all(fPay),d:all(fPay)?fmt(minLeft(g=>g.payLimit-g.payMax),1)+' t to spare. Battery weight is not counted yet':'Over the limit: '+bad(fPay),go:'bat'}];
  const feasible=checks.every(c=>c.ok),save=totD-totE,first=checks.find(c=>!c.ok);
  const title=feasible?(isNew?'All '+N+' vehicles can run electric with a '+fmt(Math.ceil(peak/10)*10)+' kW grid connection':'All '+N+' vehicles can run electric on today’s grid connection')
    :({batt:'The battery is too small for the hardest day',eol:'The battery is too small once it has aged',rdy:'The vehicles are not full before they leave',grid:'Charging goes over the grid connection',time:'The route does not fit in the shift',pay:'The load is over the weight limit'})[first.k];
  const text=(feasible?'Every vehicle has battery for its hardest day of the year, also at year 8, and is full again before it leaves. ':first.d+'. ')+
    'Over '+Y+' years electric '+(save>=0?'costs '+fmt(save/1e6,1)+' M DKK less':'costs '+fmt(-save/1e6,1)+' M DKK more')+' than diesel.';
  return{G,N,plan,D,load,peak,peakAt,limit,isNew,conn,fee,rowsE,rowsD,cumE,cumD,be,totE,totD,kmTot,cats,elP,co2D,co2E:co2Rows[0][2],co2Rows,co2Saved,kWhFleet,checks,feasible,save,title,text,Y};
}
