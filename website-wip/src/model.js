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
const BANDS=[[22,12500,10000],[43.5,120000,16000],[50,150000,50000],[80,200000,150000],[150,400000,250000],[400,700000,500000]];
const EF_PATH={2026:19.35,2027:16.64,2028:14.75,2029:11.92,2030:10.27,2031:9.09,2032:8.85,2033:8.61,2034:8.26};
const FEE={radius:{base:17950,perA:1280,ref:'Radius connection charge, as listed in the COWI truck cost sheet. May be out of date'},cerius:{base:23500,perA:1812.5,ref:'Cerius price list 2026, category C, incl. VAT'},other:{base:0,perA:0,ref:'No price list in the demo. Fee left out'}};
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
const SRCN={std:'Standard',sample:'Sample value',assume:'Assumption',calc:'Calculated',you:'Your value',need:'Needed'};
const F=(k,l,u,t,s,r,x)=>Object.assign({k,l,u,t,s,r},x||{});
const isStop=o=>o.type==='stop', notNone=o=>o.type!=='none';
const DEFS={
  veh:{one:'vehicle',many:'vehicles',title:'Vehicle',lead:'The truck: its weight, its battery and what it replaces.',fields:[
    F('cls','Vehicle class','','sel','sample','',{o:CLS.map(c=>[c[0],c[1]])}),
    F('curb','Chassis weight, empty','kg','num','sample','No datasheet'),
    F('bodyMass','Body weight','kg','num','std','EU standard value for a refuse body'),
    F('gvw','Gross vehicle weight','kg','num','sample',''),
    F('dUse','Diesel the truck uses today','l/100 km','num','sample','',{dec:1}),
    F('battMode','Battery','','radio','','',{o:[['size','Let the tool size it','The smallest battery that still covers the hardest day at year 8.'],['sheet','I have a battery size','From a datasheet or a supplier offer.']]}),
    F('battKwh','Installed battery','kWh','num','','',{when:o=>o.battMode==='sheet'}),
    F('cdxa','Air drag area','m²','num','std','EU standard value for the vehicle class. Verify before use',{sec:'Air drag and tyres',dec:1}),
    F('crr','Tyre rolling resistance','N/kN','num','sample','Placeholder, no source yet',{sec:'Air drag and tyres',dec:1}),
    F('effMot','Motor efficiency','','num','assume','Placeholder until measured loss maps are used',{sec:'Drivetrain efficiency',dec:2,max:1}),
    F('effInv','Inverter efficiency','','num','assume','Placeholder until measured loss maps are used',{sec:'Drivetrain efficiency',dec:2,max:1}),
    F('effGb','Gearbox efficiency','','num','assume','Placeholder until measured loss maps are used',{sec:'Drivetrain efficiency',dec:2,max:1}),
    F('esW','Electrical system','W','num','std','EU standard value',{sec:'On-board systems',min0:1}),
    F('psW','Air system for brakes and suspension','W','num','std','EU standard value',{sec:'On-board systems',min0:1}),
    F('hvacW','Cab heating and cooling','W','num','std','EU standard value',{sec:'On-board systems',min0:1}),
    F('spW','Power steering','W','num','std','EU standard method',{sec:'On-board systems',min0:1}),
    F('condW','Battery and motor cooling','W','num','std','EU standard value',{sec:'On-board systems',min0:1}),
    F('usable','Usable share of the battery','%','num','sample','',{sec:'Battery ageing',max:100}),
    F('guar','Capacity guaranteed at year 8','%','num','assume','Rambøll 2023: warranties often go down to 70 %. Use the value in the offer',{sec:'Battery ageing',max:100}),
    F('priceEV','Electric truck price','DKK','num','sample','No source yet',{pg:'costs'}),
    F('priceD','Diesel truck price','DKK','num','sample','No source yet',{pg:'costs'}),
    F('svcEV','Service, electric','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('svcD','Service, diesel','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('insEV','Insurance, electric','DKK/month','num','sample','No source yet',{pg:'costs',min0:1}),
    F('insD','Insurance, diesel','DKK/month','num','sample','No source yet',{pg:'costs',min0:1})]},
  rt:{one:'route',many:'routes',title:'Route',lead:'What one vehicle drives on a working day.',fields:[
    F('method','How do you want to describe the route?','','radio','','',{o:[['typed','Type in distance and stops','Enough for a first answer.'],['cycle','Use a standard EU test route','Not part of this demo.',1],['gps','Upload a GPS log','Not part of this demo.',1]]}),
    F('km','Distance per day','km','num','sample',''),
    F('stops','Stops per day','','num','sample','',{min0:1}),
    F('stopTime','Time at each stop','s','num','sample','',{min0:1}),
    F('road','Type of streets','','sel','sample','',{o:[['deep','Dense city streets'],['urban','City'],['non','Outside the city']]}),
    F('speed','Driving speed between stops','km/h','num','assume','Tool default for the type of streets: 30, 50 or 80 km/h',{sec:'Speed and hills'}),
    F('flat','Hills','','info','assume','The demo treats every route as flat',{sec:'Speed and hills',v:()=>'Flat'})]},
  load:{one:'load profile',many:'load profiles',title:'Load',lead:'What the vehicle carries.',fields:[
    F('shape','How does the load change during the day?','','radio','','',{o:[['const','Same all day','One weight for the whole route.'],['linear','Changes steadily along the route','A refuse truck filling up, or a delivery truck emptying.'],['stops','Set at each stop','Not part of this demo.',1]]}),
    F('start',o=>o.shape==='linear'?'Load when leaving':'Load','t','num','std','EU standard low load for this type of work',{dec:1,min0:1}),
    F('end','Load at the end of the route','t','num','std','EU standard reference load for this type of work',{dec:1,min0:1,when:o=>o.shape==='linear'})]},
  eq:{one:'equipment set',many:'equipment sets',title:'Body equipment',lead:'Powered equipment on the body, if any.',fields:[
    F('type','What does the equipment do?','','radio','','',{o:[['none','No powered equipment',''],['stop','Works at each stop','A bin lift, a tail lift or a crane.'],['always','Runs all the time','A fridge unit or a mixer drum.']]}),
    F('kwhStop','Energy per stop','kWh','num','assume','EU standard refuse profile. Not yet verified',{dec:3,when:isStop}),
    F('sStop','Working time per stop','s','num','assume','EU standard refuse profile. Not yet verified',{when:isStop,min0:1}),
    F('wOn','Power while on shift','W','num','','',{when:o=>o.type==='always'}),
    F('eff','Efficiency of the electric drive','','num','assume','No source yet. 1.0 means no loss',{sec:'Efficiency',dec:2,max:1,when:notNone})]},
  sch:{one:'shift',many:'shifts',title:'Shift',lead:'When the vehicles are away from the depot.',fields:[
    F('out','Leaves the depot','','time','sample',''),
    F('back','Back at the depot','','time','sample',''),
    F('days','Working days','','sel','sample','',{o:[['mf','Monday to Friday'],['ms','Monday to Saturday'],['all','Every day']]}),
    F('hol','Public holidays','','sel','std','Danish public holidays, 2026',{o:[['dk','Off on Danish public holidays'],['none','Works on public holidays']]}),
    F('opd','Operating days a year','','info','calc','Working days minus holidays, 2026 calendar',{v:o=>opDays(o)+' days'})]},
  depot:{title:'Depot',fields:[
    F('name','Depot name','','txt','sample',''),
    F('addr','Address or town','','txt','sample',''),
    F('mode','Is there a grid connection today?','','radio','','',{o:[['existing','Yes, and I know its size','The tool checks whether charging fits.'],['new','No, or I want it sized','The tool works out the connection you need.']]}),
    F('limit','Connection size','kW','num','sample','',{when:o=>o.mode==='existing'}),
    F('dso','Grid company','','sel','sample','',{o:[['radius','Radius'],['cerius','Cerius'],['other','Other']]}),
    F('base','Power the buildings already use','kW','num','sample','A steady value in the demo',{min0:1})]},
  chg:{title:'Charging',fields:[
    F('chgMode','Chargers','','radio','','',{o:[['auto','Size the chargers for me','The smallest size that has every vehicle full before it leaves.'],['set','I choose the size','']]}),
    F('kw','Charger power','','sel','','',{when:o=>o.chgMode==='set',o:SIZES.map(z=>[String(z),z+' kW'])}),
    F('plan','Charging plan','','radio','','',{o:[['cost','Lowest cost','Charge in the night hours, when power is cheapest.'],['grid','Grid-friendly','Spread charging over the whole stay to keep the peak low.'],['early','Ready earliest','Charge at full power as soon as vehicles are back.']]}),
    F('loadF','Average charger load while charging','%','num','std','COWI truck cost sheet',{sec:'Fine tuning: charger losses and load',max:100}),
    F('loss','Charger losses','%','num','assume','4-leaf 2023 gives 3 to 4 %',{sec:'Fine tuning: charger losses and load',min0:1,max:50})]},
  wx:{title:'Weather',fields:[
    F('year','Which year should the fleet be sized for?','','radio','','',{o:[['normal','A normal year',''],['cold','A cold winter','More energy in November to February.']]})]},
  pr:{title:'Energy prices',fields:[
    F('elPrice','Electricity price, all in','DKK/kWh','num','sample','Demo value. The full tool uses hourly prices, tariffs and taxes',{dec:2}),
    F('level','Electricity price level','','sel','assume','Tool default. Low is 20 % under, high is 25 % over',{o:[['low','Low'],['exp','Expected'],['high','High']]}),
    F('dPrice','Diesel price','DKK/l','num','std','OK.dk, January to June 2024, plus 0.50 DKK duty. Refresh before use',{dec:2})]},
  fin:{title:'Costs',fields:[
    F('years','Ownership period','','sel','assume','Tool default',{o:[['8','8 years'],['10','10 years'],['12','12 years']]}),
    F('interest','Interest rate','%','num','sample','No source yet',{dec:2,min0:1}),
    F('wage','Driver wage','DKK/month','num','sample','No source yet. Same for electric and diesel',{min0:1}),
    F('resid','Value at the end','','info','sample','Depreciation table from the COWI truck cost sheet. No source given there',{v:o=>residPct(+o.years)+' % of the price'})]},
  tax:{title:'Costs',fields:[
    F('e1','Road tax, electric, 2026 to 2027','DKK/km','num','std','Danish Ministry of Taxation rates, via the COWI truck cost sheet',{dec:4,min0:1}),
    F('d1','Road tax, diesel, 2026 to 2027','DKK/km','num','std','Danish Ministry of Taxation rates, via the COWI truck cost sheet',{dec:4,min0:1}),
    F('e2','Road tax, electric, 2028','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('d2','Road tax, diesel, 2028','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('e3','Road tax, electric, from 2029','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('d3','Road tax, diesel, from 2029','DKK/km','num','std','As above',{dec:4,min0:1}),
    F('grant','Grant or subsidy, paid once','DKK','num','assume','None applied',{min0:1})]},
  co2:{title:'CO₂',fields:[
    F('gridMode','CO₂ from grid electricity','','radio','','',{o:[['path','Danish Energy Agency projection','19.35 g/kWh in 2026, falling to 8.26 g/kWh in 2034. Includes upstream.'],['fixed','My own value','One value for every year.']]}),
    F('gridEF','Grid electricity, every year','g/kWh','num','','',{dec:2,min0:1,when:o=>o.gridMode==='fixed'}),
    F('co2D','Diesel','kg/l','num','sample','Source pending',{dec:2})]}
};
const LIBS=['veh','rt','load','eq','sch'];
const SETS=['chg','wx','pr','fin','tax','co2'];
const SETPAGE={chg:'charging',wx:'weather',pr:'prices',fin:'costs',tax:'costs',co2:'co2in'};

/* ---------- project data ---------- */
const mk=o=>{o._d=clone(o);if(o.id){delete o._d.id;delete o._d.name;}return o;};
const VEH_STD={cls:'4',cdxa:8.4,crr:6,effMot:0.95,effInv:0.95,effGb:0.98,esW:1000,psW:687,hvacW:375,spW:306,condW:550,usable:90,guar:70,priceEV:2050000,priceD:1150000,svcEV:7685,svcD:5000,insEV:1476,insD:768,battMode:'size',battKwh:''};
const BLANK={
  veh:()=>Object.assign({},VEH_STD,{curb:'',bodyMass:'',gvw:'',dUse:''}),
  rt:()=>({method:'typed',km:'',stops:'',stopTime:'',road:'urban',speed:50}),
  load:()=>({shape:'const',start:'',end:''}),
  eq:()=>({type:'none',kwhStop:0.15,sStop:23,wOn:'',eff:1}),
  sch:()=>({out:'',back:'',days:'mf',hol:'dk'})
};
function sampleProject(){return{
  name:'Sample project',
  lib:{
    veh:[mk(Object.assign({id:'v1',name:'Refuse truck'},VEH_STD,{curb:11500,bodyMass:6000,gvw:26000,dUse:55}))],
    rt:[mk({id:'r1',name:'City collection round',method:'typed',km:120,stops:400,stopTime:20,road:'deep',speed:30})],
    load:[mk({id:'l1',name:'Fills up along the route',shape:'linear',start:0.6,end:3})],
    eq:[mk({id:'e1',name:'Bin lift',type:'stop',kwhStop:0.15,sStop:23,wOn:'',eff:1}),mk({id:'e0',name:'None',type:'none',kwhStop:0.15,sStop:23,wOn:'',eff:1})],
    sch:[mk({id:'s1',name:'Day shift',out:'06:00',back:'16:00',days:'mf',hol:'dk'}),mk({id:'s2',name:'Night shift',out:'19:00',back:'05:00',days:'mf',hol:'dk'})]},
  groups:[{id:1,name:'Refuse, day shift',n:4,n0:4,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s1'},{id:2,name:'Refuse, night shift',n:2,n0:2,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s2'}],
  depot:mk({name:'Main depot',addr:'Copenhagen',mode:'existing',limit:400,dso:'radius',base:30}),
  chg:mk({chgMode:'auto',kw:'50',plan:'cost',loadF:85,loss:4}),
  wx:mk({year:'normal'}),
  pr:mk({elPrice:1.6,level:'exp',dPrice:11.65}),
  fin:mk({years:'10',interest:3.45,wage:30000}),
  tax:mk({e1:0.1008,d1:0.8525,e2:0.1864,d2:1.4324,e3:0.2613,d3:1.6181,grant:0}),
  co2:mk({gridMode:'path',gridEF:19.35,co2D:2.65}),
  nid:10};}
let P=sampleProject();
const tpl=(lib,id)=>P.lib[lib].find(x=>x.id===id);
const visible=(type,o)=>DEFS[type].fields.filter(f=>!f.when||f.when(o));
function isMissing(f,o){if(f.t==='info'||f.t==='radio')return false;const v=o[f.k];if(v===''||v==null)return true;
  if(f.t==='num')return !(typeof v==='number'&&isFinite(v)&&(f.min0?v>=0:v>0)&&(f.max==null||v<=f.max));
  if(f.t==='time')return isNaN(hrs(v));return false;}
function srcOf(f,o){if(f.t==='info')return f.s;if(isMissing(f,o))return'need';const d=o._d?o._d[f.k]:undefined;return(d!==undefined&&d!==''&&o[f.k]===d&&f.s)?f.s:'you';}
const labelOf=(f,o)=>typeof f.l==='function'?f.l(o):f.l;
function shown(f,o){const v=f.t==='info'?f.v(o):o[f.k];if(f.o){const x=f.o.find(q=>String(q[0])===String(v));return x?x[1]:String(v);}
  if(f.t==='num'&&typeof v==='number')return fmt(v,f.dec||0)+(f.u?' '+f.u:'');return v===''||v==null?'':String(v);}

/* every object that feeds the run, with a readable place name */
function parts(){const out=[],seen={};
  P.groups.forEach(g=>LIBS.forEach(l=>{const t=tpl(l,g[l]);if(t&&!seen[l+t.id]){seen[l+t.id]=1;out.push({type:l,o:t,where:DEFS[l].title+': '+t.name,open:{lib:l,gid:g.id}});}}));
  out.push({type:'depot',o:P.depot,where:'Depot',open:{page:'depot'}});
  SETS.forEach(s=>out.push({type:s,o:P[s],where:DEFS[s].title,open:{page:SETPAGE[s]}}));return out;}
function missing(){const m=[];
  P.groups.forEach(g=>{if(!(g.n>=1))m.push({where:'Fleet: '+g.name,label:'Number of vehicles',open:{page:'fleet'}});
    LIBS.forEach(l=>{if(!tpl(l,g[l]))m.push({where:'Fleet: '+g.name,label:DEFS[l].title+' not chosen',open:{lib:l,gid:g.id}});});});
  if(!P.groups.length)m.push({where:'Fleet',label:'Add at least one group of vehicles',open:{page:'fleet'}});
  parts().forEach(p=>visible(p.type,p.o).forEach(f=>{if(isMissing(f,p.o))m.push({where:p.where,label:labelOf(f,p.o),open:f.pg?{page:f.pg}:p.open});}));
  P.groups.forEach(g=>{const s=tpl('sch',g.sch);if(s&&!isNaN(hrs(s.out))&&hrs(s.out)===hrs(s.back))m.push({where:'Shift: '+s.name,label:'Leaving and return time are the same',open:{lib:'sch',gid:g.id}});});
  return m;}
function inputRows(){const rows=[];
  P.groups.forEach(g=>rows.push({where:'Fleet: '+g.name,label:'Vehicles',value:String(g.n),src:g.n===g.n0?'sample':'you',ref:''}));
  parts().forEach(p=>visible(p.type,p.o).forEach(f=>{const s=f.t==='radio'?'you':srcOf(f,p.o);rows.push({where:p.where,label:labelOf(f,p.o),value:shown(f,p.o),src:s,ref:s==='you'?'':(f.r||''),radio:f.t==='radio'});}));
  return rows;}
const snapshot=()=>JSON.stringify(P,(k,v)=>k==='_d'||k==='n0'||k==='nid'?undefined:v);

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
    const vms=rt.speed/3.6,pay0=l.start,pay1=l.shape==='linear'?l.end:l.start,mass=v.curb+v.bodyMass+(pay0+pay1)/2*1000;
    const eta=v.effMot*v.effInv*v.effGb,d=rt.km*1000,J=3.6e6;
    const roll=mass*DEMO.g*v.crr/1000*d/J,air=0.5*DEMO.rho*v.cdxa*vms*vms*d/J,kin=rt.stops*0.5*mass*vms*vms/J;
    const wheel=roll+air+kin,regen=kin*DEMO.regen*eta,drive=wheel/eta-regen;
    const tA=vms/DEMO.acc,dA=vms*vms/(2*DEMO.acc),seg=rt.stops?d/rt.stops:d,cruise=Math.max(0,seg-2*dA);
    const tDrive=(rt.stops?rt.stops*(2*tA+cruise/vms):d/vms)/3600,tStop=rt.stops*rt.stopTime/3600,tEq=e.type==='stop'?rt.stops*e.sStop/3600:0;
    const out=hrs(s.out),back=hrs(s.back),shiftH=((back-out+24)%24)||24,dwellH=24-shiftH;
    const auxE=((v.esW+v.psW+v.hvacW+v.spW+v.condW)+(v.esW+v.psW+v.hvacW))/2000*shiftH;
    const eqE=e.type==='stop'?rt.stops*e.kwhStop/e.eff:e.type==='always'?e.wOn/1000*shiftH/e.eff:0;
    const avg=drive+auxE+eqE,months=mf.map(f=>avg*f),mean=sum(months)/12,worst=Math.max(...months)*DEMO.worstF;
    const us=v.usable/100,gu=v.guar/100,batt=v.battMode==='size'?Math.ceil(worst/(us*gu)/10)*10:v.battKwh;
    const g={gr,v,rt,l,e,s,n,name:gr.name,mass,eta,roll,air,kin,wheel,regen,drive,auxE,eqE,avg,months,mean,worst,batt,usable:batt*us,usableEol:batt*us*gu,
      tNeed:tDrive+tStop+tEq,tDrive,tStop,tEq,out,back,shiftH,dwellH,payMax:Math.max(pay0,pay1),payLimit:(v.gvw-v.curb-v.bodyMass)/1000,days:opDays(s)};
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
