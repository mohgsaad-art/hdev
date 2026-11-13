/* ================= helpers ================= */
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt = (n,d=0) => Number(n).toLocaleString('en-GB',{maximumFractionDigits:d,minimumFractionDigits:d});
const sum = a => a.reduce((x,y)=>x+y,0);
const clone = o => JSON.parse(JSON.stringify(o));
const hrs = t => { const m=/^(\d{1,2}):(\d{2})$/.exec(t||''); return m ? (+m[1])+(+m[2])/60 : NaN; };
const hm = h => { h=((h%24)+24)%24; let H=Math.floor(h), M=Math.round((h-H)*60); if(M===60){H=(H+1)%24;M=0;} return String(H).padStart(2,'0')+':'+String(M).padStart(2,'0'); };

/* ================= demo engine constants =================
   Stand-in formulas, not the validated engine. Every constant here is listed on Results > Sources. */
const DEMO = { rho:1.2, g:9.81, acc:1.0, regen:0.88, elBase:1.6, worstF:1.15, sizeF:1.1, startYear:2026 };
const MONTH_F = [1.18,1.16,1.08,1.0,0.95,0.92,0.92,0.93,0.96,1.02,1.1,1.16];
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const SIZES = [22,40,50,60,90,120,150];
const PRICE_F = { low:0.8, exp:1, high:1.25 }, PLAN_F = { cost:0.85, grid:0.92, early:1.0 };
const PLAN = { cost:['Lowest cost','Charge in the night hours, when power is usually cheapest'], grid:['Grid-friendly','Spread charging over the whole stay to keep the peak low'], early:['Ready earliest','Charge at full power as soon as the vehicles are back'] };
/* charger price bands: kW, hardware, trenching and installation (DKK). Charge-point operator prices 2024, via the COWI sheet */
const BANDS = [[22,12500,10000],[43.5,120000,16000],[50,150000,50000],[80,200000,150000],[150,400000,250000],[400,700000,500000]];
const band = kw => BANDS.find(b => b[0]>=kw) || BANDS[BANDS.length-1];
/* grid connection fees: first 25 A, then per extra ampere (DKK) */
const DSO = { Radius:{base:17950,perA:1280,ref:'Radius connection charge, via the COWI sheet. May be out of date'}, Cerius:{base:23500,perA:1812.5,ref:'Cerius price list 2026, category C, incl. VAT'}, Other:{base:0,perA:0,ref:'No fee calculated'} };
const amps = kw => kw*1000/(Math.sqrt(3)*400);
const residPct = y => y<=6?15:y===7?12.5:y===8?10:y===9?7.5:y===10?5:0;   /* COWI sheet, unsourced there */
const EF_PATH = {2026:19.35,2027:16.64,2028:14.75,2029:11.92,2030:10.27,2031:9.09,2032:8.85,2033:8.61,2034:8.26}; /* g/kWh, Danish Energy Agency incl. upstream, via COWI */
const pmt = (r,n,pv,fv) => { if(!r) return (pv-fv)/n; const f=Math.pow(1+r,n); return (r*(pv*f-fv))/((1+r)*(f-1)); };
/* standard air-drag area by vehicle class (VECTO segment table) */
const CLS = { '1':['Rigid 4×2, 7.5 to 10 t',7.1], '2':['Rigid 4×2, 10 to 12 t',7.2], '3':['Rigid 4×2, 12 to 16 t',7.4], '4':['Rigid 4×2, over 16 t',8.4], '9':['Rigid 6×2',8.5], '11':['Rigid 6×4',8.5], '16':['Rigid 8×4',9.0], '5':['Tractor 4×2',8.7], '10':['Tractor 6×2',8.8], '12':['Tractor 6×4',8.8] };
const ROAD = { deep:['Dense city streets',30], urban:['City and suburb',50], non:['Country roads and motorway',80] };
/* Danish public holidays 2026 that fall on a weekday or Saturday (month-day) */
const HOL = ['1-1','4-2','4-3','4-6','5-14','5-25','12-25','12-26'];
function opDays(sch){ let c=0; for(let m=0;m<12;m++){ const dn=new Date(2026,m+1,0).getDate(); for(let d=1;d<=dn;d++){ const w=new Date(2026,m,d).getDay();
  const works = sch.days==='all' || (sch.days==='ms' ? w!==0 : (w>0&&w<6)); if(works && !(sch.hol==='dk' && HOL.includes((m+1)+'-'+d))) c++; } } return c; }

/* ================= input definitions =================
   F(key, label, unit, type, source, reference, extra)
   source: std = standard value, sample = sample value to replace, assume = assumption. sec = named fold-out it sits in. */
const F = (k,l,u,t,s,r,x) => Object.assign({k,l,u,t,s,r,req:t==='num'},x||{});
const SRC = { std:'Standard', sample:'Sample', assume:'Assumption', you:'Your value', need:'Needed' };
const DEFS = {
  veh:{ one:'vehicle', many:'vehicles', title:'Vehicle', sub:'The truck: its weight, its battery and what it replaces.', fields:[
    F('cls','Vehicle class','','sel','assume','Assumed from the vehicle type',{o:Object.keys(CLS).map(k=>[k,CLS[k][0]])}),
    F('curb','Chassis weight, empty','kg','num','sample','Sample value. Take it from the registration papers'),
    F('body','Body weight','kg','num','std','Standard body table (refuse body)'),
    F('gvw','Gross vehicle weight','kg','num','sample','Sample value. Take it from the registration papers'),
    F('batt','Battery','','radio','assume','Tool default',{o:[['size','Size it for me','The smallest battery that still covers the hardest day at year 8'],['sheet','I have a datasheet','Enter the installed battery size']]}),
    F('battKwh','Installed battery','kWh','num','sample','From the datasheet',{when:o=>o.batt==='sheet'}),
    F('dUse','Diesel the same truck uses today','l/100 km','num','sample','Sample value. Take it from your fuel log'),
    F('usable','Usable share of the battery','%','num','sample','Sample value',{sec:'Battery ageing',min:10,max:100}),
    F('guar','Capacity guaranteed at year 8','%','num','assume','Rambøll 2023: warranties often go down to 70 %. Use the offer’s value',{sec:'Battery ageing',min:10,max:100}),
    F('cdxa','Air drag area','m²','num','std','Standard value for the vehicle class (VECTO segment table)',{sec:'Air drag and tyres'}),
    F('crr','Tyre rolling resistance','N/kN','num','sample','Placeholder, no source. Take it from the tyre label',{sec:'Air drag and tyres'}),
    F('effMot','Motor efficiency','','num','assume','Placeholder until loss maps are in',{sec:'Drivetrain efficiency',max:1}),
    F('effInv','Inverter efficiency','','num','assume','Placeholder until loss maps are in',{sec:'Drivetrain efficiency',max:1}),
    F('effGb','Gearbox efficiency','','num','assume','Placeholder until loss maps are in',{sec:'Drivetrain efficiency',max:1}),
    F('esW','Electrical system','W','num','std','EU standard value, electrical-system table',{sec:'On-board systems',min:0}),
    F('psW','Air system (brakes, suspension)','W','num','std','EU standard value, air-system table',{sec:'On-board systems',min:0}),
    F('hvacW','Cab heating and cooling','W','num','std','EU standard value, climate table',{sec:'On-board systems',min:0}),
    F('spW','Power steering','W','num','std','EU standard method, one steered axle',{sec:'On-board systems',min:0}),
    F('condW','Battery and motor cooling','W','num','std','EU standard value, conditioning table',{sec:'On-board systems',min:0}),
    F('priceEV','Electric truck price','DKK','num','sample','Sample value, no source',{sec:'Price and service'}),
    F('priceD','Diesel truck price','DKK','num','sample','Sample value, no source',{sec:'Price and service'}),
    F('svcEV','Service, electric','DKK/month','num','sample','Sample value, no source',{sec:'Price and service',min:0}),
    F('svcD','Service, diesel','DKK/month','num','sample','Sample value, no source',{sec:'Price and service',min:0}),
    F('insEV','Insurance, electric','DKK/month','num','sample','Sample value, no source',{sec:'Price and service',min:0}),
    F('insD','Insurance, diesel','DKK/month','num','sample','Sample value, no source',{sec:'Price and service',min:0}) ],
    blank:{cls:'4',curb:'',body:'',gvw:'',batt:'size',battKwh:'',dUse:'',usable:90,guar:70,cdxa:8.4,crr:'',effMot:0.95,effInv:0.95,effGb:0.98,esW:1000,psW:687,hvacW:375,spW:306,condW:550,priceEV:'',priceD:'',svcEV:'',svcD:'',insEV:'',insD:''},
    sum:o=>fmt((+o.gvw||0)/1000,0)+' t gross · '+(o.batt==='size'?'battery sized by the tool':(o.battKwh?fmt(o.battKwh)+' kWh battery':'battery size needed')) },
  rt:{ one:'route', many:'routes', title:'Route', sub:'What one vehicle drives on a working day.', fields:[
    F('how','How do you want to describe the route?','','radio','','',{o:[['typed','Type in distance and stops','Enough for a first answer'],['cycle','Use a standard EU test cycle','In the full tool',1],['gps','Upload a GPS log','In the full tool',1]]}),
    F('km','Distance per day','km','num','sample','Sample value'),
    F('stops','Stops per day','','num','sample','Sample value',{min:0}),
    F('stopT','Time at each stop','s','num','sample','Sample value',{min:0,when:o=>+o.stops>0}),
    F('road','Mostly driven on','','sel','sample','Sample value',{o:Object.keys(ROAD).map(k=>[k,ROAD[k][0]])}),
    F('speed','Speed between stops','km/h','num','assume','Tool default for the street type: 30, 50 or 80 km/h',{sec:'Speed and hills'}) ],
    blank:{how:'typed',km:'',stops:'',stopT:'',road:'urban',speed:50},
    sum:o=>fmt(+o.km||0)+' km · '+fmt(+o.stops||0)+' stops',
    foot:'Hills are not in the demo: the route is treated as flat.' },
  load:{ one:'load', many:'loads', title:'Load', sub:'What the vehicle carries through the day.', fields:[
    F('shape','How does the load change?','','radio','','',{o:[['const','The same all day',''],['linear','It changes steadily along the route','For example a refuse truck that fills up, or a delivery van that empties'],['stops','Set it stop by stop','In the full tool',1]]}),
    F('a','Load','t','num','std','Standard reference load for this class and type of work',{min:0,when:o=>o.shape==='const'}),
    F('a','Load at the start','t','num','std','Standard low load for this class and type of work',{min:0,when:o=>o.shape!=='const'}),
    F('b','Load at the end','t','num','std','Standard reference load for this class and type of work',{min:0,when:o=>o.shape!=='const'}) ],
    blank:{shape:'const',a:'',b:''},
    sum:o=>o.shape==='const'?fmt(+o.a||0,1)+' t all day':fmt(+o.a||0,1)+' → '+fmt(+o.b||0,1)+' t' },
  eq:{ one:'equipment', many:'equipment', title:'Body equipment', sub:'Anything on the truck that uses power besides driving: a bin lift, a crane, a fridge.', fields:[
    F('type','When does it use power?','','radio','','',{o:[['none','No equipment',''],['stop','At each stop','For example a bin lift or a crane'],['always','All the time','For example a fridge or a mixer drum']]}),
    F('kwh','Energy per stop','kWh','num','assume','EU standard refuse profile. Not yet checked against the source data',{min:0,when:o=>o.type==='stop'}),
    F('sec','Working time per stop','s','num','assume','EU standard refuse profile. Not yet checked against the source data',{min:0,when:o=>o.type==='stop'}),
    F('w','Power while the vehicle is out','W','num','sample','From the equipment datasheet',{min:0,when:o=>o.type==='always'}),
    F('eff','Efficiency of the equipment drive','','num','assume','Tool default: no extra loss',{sec:'Efficiency',max:1,when:o=>o.type!=='none'}) ],
    blank:{type:'none',kwh:'',sec:'',w:'',eff:1},
    sum:o=>o.type==='none'?'no extra power':o.type==='stop'?fmt(+o.kwh||0,2)+' kWh per stop':fmt(+o.w||0)+' W all the time' },
  sch:{ one:'shift', many:'shifts', title:'Shift', sub:'When the vehicles are away from the depot. They can charge the rest of the time.', fields:[
    F('out','Leaves the depot','','time','sample','Sample value'),
    F('back','Back at the depot','','time','sample','Sample value'),
    F('days','Working days','','sel','sample','Sample value',{o:[['mf','Monday to Friday'],['ms','Monday to Saturday'],['all','Every day']]}),
    F('hol','Holidays','','sel','std','Danish public holidays 2026',{o:[['dk','Off on Danish public holidays'],['none','No days off']]}) ],
    blank:{out:'',back:'',days:'mf',hol:'dk'},
    sum:o=>(o.out||'?')+' to '+(o.back||'?')+' · '+({mf:'Mon to Fri',ms:'Mon to Sat',all:'every day'})[o.days],
    foot:o=>'That is '+opDays(o)+' working days in 2026.' },
  depot:{ title:'Depot', fields:[
    F('name','Depot name','','txt','sample','Sample value'),
    F('addr','Address or town','','txt','sample','Sample value. Used in the documents'),
    F('mode','What do you know about the grid connection?','','radio','','',{o:[['existing','The depot has a connection and I know its size','The tool checks whether charging fits inside it'],['new','New site, or I do not know','The tool tells you what size to apply for']]}),
    F('limit','Grid connection','kW','num','sample','Sample value. It is on your grid company’s bill or agreement',{when:o=>o.mode==='existing'}),
    F('dso','Grid company','','sel','sample','Sample value',{o:Object.keys(DSO).map(k=>[k,k])}),
    F('base','Power the buildings already use','kW','num','sample','Sample value. A single figure in the demo; hourly meter data in the full tool',{min:0}),
    F('chg','Chargers','','radio','','',{o:[['auto','Size them for me','The smallest standard charger that has every vehicle full in time'],['set','I choose the size','']]}),
    F('kw','Charger power','','sel','you','Your choice',{o:SIZES.map(k=>[String(k),k+' kW']),when:o=>o.chg==='set'}),
    F('plan','How should the vehicles charge?','','radio','assume','Tool default',{o:Object.keys(PLAN).map(k=>[k,PLAN[k][0],PLAN[k][1]])}),
    F('loadF','Average charger load while charging','%','num','std','COWI reference sheet',{sec:'Charger behaviour',min:10,max:100}),
    F('loss','Charger losses','%','num','assume','4-leaf 2023 gives 3 to 4 %',{sec:'Charger behaviour',min:0,max:30}) ] },
  wx:{ title:'Weather', fields:[
    F('year','Weather year','','sel','assume','Tool default',{o:[['normal','A normal year'],['cold','A year with a cold winter']]}) ],
    sum:(o,P)=>(P.depot.addr||'Location not set')+' · '+(o.year==='cold'?'a cold winter':'a normal year'),
    foot:'The demo uses monthly weather factors. The full tool uses measured hourly weather from the nearest station.' },
  pr:{ title:'Energy prices', fields:[
    F('el','Electricity, all in','DKK/kWh','num','sample','Demo value until hourly prices and tariffs are in'),
    F('level','Price level to test','','sel','assume','Tool default',{o:[['low','Low (20 % under)'],['exp','Expected'],['high','High (25 % over)']]}),
    F('diesel','Diesel','DKK/l','num','std','OK.dk, January to June 2024, plus 0.50 DKK duty. Dated: refresh before use') ],
    sum:o=>'Electricity '+fmt(o.el,2)+' DKK/kWh, '+({low:'low',exp:'expected',high:'high'})[o.level]+' level · diesel '+fmt(o.diesel,2)+' DKK/l' },
  fin:{ title:'Ownership and financing', fields:[
    F('years','Ownership period','','sel','assume','Tool default',{o:[['8','8 years'],['10','10 years'],['12','12 years']]}),
    F('rate','Interest rate','%','num','sample','Sample value, no source',{min:0}),
    F('wage','Driver wage','DKK/month','num','sample','Sample value, no source. The same for electric and diesel',{min:0}) ],
    sum:o=>o.years+' years · '+fmt(o.rate,2)+' % interest · value left at the end '+fmt(residPct(+o.years),1)+' %',
    foot:o=>'Value left at the end of '+o.years+' years: '+fmt(residPct(+o.years),1)+' % of the price (sample table, no source).' },
  tax:{ title:'Road tax and grants', fields:[
    F('e1','Road tax, electric, to 2027','DKK/km','num','std','Danish km-based road tax, via the COWI sheet. Check the weight class',{min:0}),
    F('d1','Road tax, diesel, to 2027','DKK/km','num','std','Danish km-based road tax, via the COWI sheet. Check the weight class',{min:0}),
    F('e2','Electric, 2028','DKK/km','num','std','As above',{sec:'Later years',min:0}), F('d2','Diesel, 2028','DKK/km','num','std','As above',{sec:'Later years',min:0}),
    F('e3','Electric, from 2029','DKK/km','num','std','As above',{sec:'Later years',min:0}), F('d3','Diesel, from 2029','DKK/km','num','std','As above',{sec:'Later years',min:0}),
    F('grant','Grant for the electric fleet, once','DKK','num','assume','None assumed',{min:0}) ],
    sum:o=>'Electric '+fmt(o.e1,2)+' and diesel '+fmt(o.d1,2)+' DKK/km to 2027, rising after · '+(+o.grant?'grant '+fmt(o.grant)+' DKK':'no grant') },
  co2:{ title:'CO₂ factors', fields:[
    F('grid','Grid electricity','','sel','std','Danish Energy Agency projection incl. upstream, via the COWI sheet',{o:[['path','Official projection, falling each year'],['fixed','One fixed value']]}),
    F('ef','Fixed value','g/kWh','num','you','Your value',{min:0,when:o=>o.grid==='fixed'}),
    F('diesel','Diesel','kg/l','num','sample','Sample value, source pending') ],
    sum:o=>(o.grid==='path'?'Grid '+fmt(EF_PATH[2026],1)+' g/kWh in 2026, falling to '+fmt(EF_PATH[2034],1)+' by 2034':'Grid fixed at '+fmt(o.ef||0,1)+' g/kWh')+' · diesel '+fmt(o.diesel,2)+' kg/l' }
};
const LIBS = ['veh','rt','load','eq','sch'];
const SETS = ['wx','pr','fin','tax','co2'];

/* ================= sample project ================= */
function mk(lib, id, name, vals){ const o=Object.assign({id, name}, DEFS[lib].blank, vals); o._d=Object.assign({}, DEFS[lib].blank, vals); return o; }
function sampleProject(){ const P = {
  name:'Sample project', lib:{
    veh:[ mk('veh','v1','Refuse truck',{cls:'4',curb:11500,body:6000,gvw:26000,dUse:55,crr:6,priceEV:2050000,priceD:1150000,svcEV:7685,svcD:5000,insEV:1476,insD:768}) ],
    rt:[ mk('rt','r1','City collection round',{km:120,stops:400,stopT:20,road:'deep',speed:30}) ],
    load:[ mk('load','l1','Fills up along the route',{shape:'linear',a:0.6,b:3.0}) ],
    eq:[ mk('eq','e1','Bin lift',{type:'stop',kwh:0.15,sec:23}), mk('eq','e0','None',{}) ],
    sch:[ mk('sch','s1','Day shift',{out:'06:00',back:'16:00'}), mk('sch','s2','Night shift',{out:'20:00',back:'05:00'}) ] },
  groups:[ {id:1,name:'Refuse, day shift',n:4,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s1'}, {id:2,name:'Refuse, night shift',n:2,veh:'v1',rt:'r1',load:'l1',eq:'e1',sch:'s2'} ],
  depot:{name:'Main depot',addr:'Copenhagen',mode:'existing',limit:400,dso:'Radius',base:30,chg:'auto',kw:'50',plan:'cost',loadF:85,loss:4},
  wx:{year:'normal'}, pr:{el:1.6,level:'exp',diesel:11.65}, fin:{years:'10',rate:3.45,wage:30000},
  tax:{e1:0.1008,d1:0.8525,e2:0.1864,d2:1.4324,e3:0.2613,d3:1.6181,grant:0}, co2:{grid:'path',ef:'',diesel:2.65}, nid:10 };
  ['depot'].concat(SETS).forEach(k => { P[k]._d = Object.assign({}, P[k]); });
  return P; }
let P = sampleProject();
const tpl = (lib,id) => P.lib[lib].find(x => x.id===id);
const fieldsOf = (key,o) => DEFS[key].fields.filter(f => !f.when || f.when(o));
const isMissing = (f,o) => f.t!=='radio' && f.t!=='sel' && (o[f.k]===''||o[f.k]==null||(f.t==='num'&&(isNaN(+o[f.k])||+o[f.k]<(f.min!=null?f.min:1e-9)||(f.max!=null&&+o[f.k]>f.max)))||(f.t==='time'&&isNaN(hrs(o[f.k]))));
const srcOf = (f,o) => isMissing(f,o) ? 'need' : (o._d && o._d[f.k]!==undefined && o._d[f.k]!=='' && String(o._d[f.k])===String(o[f.k])) ? (f.s||'assume') : 'you';
const showVal = (f,o) => { const v=o[f.k]; if(f.o){ const x=f.o.find(q=>q[0]===String(v)); return x?x[1]:String(v); } if(f.t==='num') return (v===''||v==null?'':fmt(+v, Math.min(4,(String(v).split('.')[1]||'').length)))+(f.u?' '+f.u:''); return String(v||''); };
/* everything the run needs, as a flat list: where it lives, value, source */
function allInputs(){ const out=[];
  P.groups.forEach(g => { out.push({where:'Fleet · '+g.name, f:{k:'n',l:'Vehicles',t:'num',s:'sample',r:'Sample value',u:''}, o:g, open:['group',g.id]});
    LIBS.forEach(lib => { if(!tpl(lib,g[lib])) out.push({where:'Fleet · '+g.name, f:{k:lib,l:DEFS[lib].title,t:'txt',s:'sample',r:''}, o:{[lib]:''}, open:['tpl',lib,g.id]}); }); });
  LIBS.forEach(lib => P.lib[lib].filter(t => P.groups.some(g => g[lib]===t.id)).forEach(t => fieldsOf(lib,t).forEach(f => { if(f.t!=='radio'||f.s) out.push({where:DEFS[lib].title+' · '+t.name, f, o:t, open:['tpl',lib,P.groups.find(g=>g[lib]===t.id).id]}); })));
  fieldsOf('depot',P.depot).forEach(f => { if(f.t!=='radio'||f.s) out.push({where:'Depot', f, o:P.depot, open:['page','depot']}); });
  SETS.forEach(k => fieldsOf(k,P[k]).forEach(f => out.push({where:DEFS[k].title, f, o:P[k], open:['set',k]})));
  return out; }
const missing = () => allInputs().filter(x => isMissing(x.f,x.o));
const snapshot = () => JSON.stringify(P, (k,v) => k==='_d'?undefined:v);

/* ================= demo model ================= */
function physics(v, r, l){
  const sp=(+r.speed||ROAD[r.road][1])/3.6, pay=(l.shape==='const'?+l.a:(+l.a + +l.b)/2)*1000, mass=+v.curb + +v.body + pay, d=r.km*1000, st=+r.stops||0;
  const eta=v.effMot*v.effInv*v.effGb, J=3.6e6;
  const roll=mass*DEMO.g*(v.crr/1000)*d/J, air=0.5*DEMO.rho*v.cdxa*sp*sp*d/J, kin=st*0.5*mass*sp*sp/J;
  const wheel=roll+air+kin, batt=wheel/eta, back=kin*DEMO.regen*eta, net=batt-back;
  const tA=sp/DEMO.acc, dA=sp*sp/(2*DEMO.acc), seg=st?d/st:d, cruise=Math.max(0,seg-2*dA);
  const tDrive=(st?st*(2*tA+cruise/sp):d/sp)/3600, tStop=st*(+r.stopT||0)/3600;
  return { mass, eta, roll, air, kin, wheel, back, net, loss:batt-wheel, tDrive, tStop, seg, sp };
}
function chargePlan(G, plan, kwSet, dep){
  const lossF=1-dep.loss/100, need=G.worst/lossF, S=[]; let i=Math.round(G.back*4)%96; const end=Math.round(G.out*4)%96;
  do { S.push(i); i=(i+1)%96; } while(i!==end && S.length<96);
  const dwell=S.length/4; let win, order=S, j=S.indexOf(88);
  if(plan==='cost'){ if(j>=0 && (S.length-j)/4>=3){ win=(S.length-j)/4; order=S.slice(j).concat(S.slice(0,j).reverse()); } else win=Math.max(1,dwell-1); }
  else if(plan==='grid'){ win=Math.max(1,dwell-2); order=S.slice(2).concat(S.slice(0,2)); }
  else win=Math.min(4,dwell);
  const kw = kwSet || SIZES.find(z => z>=G.worst*DEMO.sizeF/win) || SIZES[SIZES.length-1];
  let p=kw*dep.loadF/100; if(plan==='grid') p=Math.min(p, need/win);
  const slot=new Array(96).fill(0); let rem=need;
  for(const s of order){ const e=Math.min(rem,p*0.25); slot[s]=e/0.25; rem-=e; if(rem<=1e-6) break; }
  const used=S.filter(s => slot[s]>0), first=S.indexOf(used[0]), last=S.indexOf(used[used.length-1]);
  return { kw, slot, dwell, ready:rem<=0.5, short:Math.max(0,rem*lossF), start:G.back+first/4, end:G.back+(last+1)/4, spare:(S.length-last-1)/4, busy:used.length/4 };
}
function compute(Q, over){ over=over||{};
  const dep=Object.assign({}, Q.depot, over.depot||{}), plan=dep.plan, Y=+Q.fin.years, lossF=1-dep.loss/100;
  const monthF=MONTH_F.map((f,i) => Q.wx.year==='cold'&&(i<2||i>9) ? f*1.08 : f);
  const lib=(k,id)=>Q.lib[k].find(x=>x.id===id);
  const groups=Q.groups.map(g => { const v=lib('veh',g.veh), r=lib('rt',g.rt), l=lib('load',g.load), e=lib('eq',g.eq), s=lib('sch',g.sch), n=+g.n;
    const ph=physics(v,r,l), out=hrs(s.out), back=hrs(s.back), shift=((back-out+24)%24)||24, st=+r.stops||0;
    const auxE=((v.esW+v.psW+v.hvacW)+(v.esW+v.psW+v.hvacW+v.spW+v.condW))/2000*shift;
    const eqE=e.type==='stop'?st*e.kwh/e.eff:e.type==='always'?e.w/1000*shift/e.eff:0, tEq=e.type==='stop'?st*e.sec/3600:0;
    const avg=ph.net+auxE+eqE, months=monthF.map(f=>avg*f), mean=sum(months)/12, worst=Math.max(...months)*DEMO.worstF;
    const us=v.usable/100, gu=v.guar/100, batt=v.batt==='size'?Math.ceil(worst/(us*gu)/10)*10:+v.battKwh;
    const G={ g, v, r, l, e, s, n, ph, out, back, shift, auxE, eqE, tEq, avg, months, mean, worst, batt, usable:batt*us, usable8:batt*us*gu, km:+r.km, stops:st,
      need:ph.tDrive+ph.tStop+tEq, payMax:(v.gvw-v.curb-v.body)/1000, payTop:l.shape==='const'?+l.a:Math.max(+l.a,+l.b), days:opDays(s) };
    G.c=chargePlan(G, plan, dep.chg==='set'?+dep.kw:null, dep); G.kmYr=G.km*G.days; G.gridYr=mean*G.days/lossF; return G; });
  const load=new Array(96).fill(+dep.base); groups.forEach(G => G.c.slot.forEach((p,i) => load[i]+=p*G.n));
  const peak=Math.max(...load), nVeh=sum(groups.map(G=>G.n)), isNew=dep.mode==='new', limit=isNew?null:+dep.limit, A=amps(peak), fee=DSO[dep.dso];
  const conn = isNew ? (fee.base ? fee.base+Math.max(0,A-25)*fee.perA : 0) : Math.max(0,A-amps(limit))*fee.perA;
  /* cost: electric against diesel, year by year */
  const r=Q.fin.rate/100, res=residPct(Y)/100, elP=Q.pr.el*PRICE_F[Q.pr.level]*PLAN_F[plan], K=['fin','chg','energy','svc','tax','wage'], NM={fin:'Financing the vehicles',chg:'Chargers and grid connection',energy:'Energy',svc:'Service and insurance',tax:'Road tax',wage:'Driver wages'};
  const rate=(yr,el)=>yr<=2027?(el?Q.tax.e1:Q.tax.d1):yr===2028?(el?Q.tax.e2:Q.tax.d2):(el?Q.tax.e3:Q.tax.d3);
  const rowsE=[], rowsD=[]; let chgCap=0; groups.forEach(G => { const b=band(G.c.kw); chgCap+=G.n*(b[1]+b[2]); });
  for(let y=1;y<=Y;y++){ const yr=DEMO.startYear+y-1, E={yr,fin:0,chg:y===1?chgCap+conn-(+Q.tax.grant||0):0,energy:0,svc:0,tax:0,wage:0}, D={yr,fin:0,chg:0,energy:0,svc:0,tax:0,wage:0};
    groups.forEach(G => { const v=G.v, n=G.n;
      E.fin+=n*pmt(r/12,Y*12,v.priceEV,v.priceEV*res)*12; D.fin+=n*pmt(r/12,Y*12,v.priceD,v.priceD*res)*12;
      E.energy+=n*G.gridYr*elP; D.energy+=n*G.kmYr*v.dUse/100*Q.pr.diesel;
      E.svc+=n*(v.svcEV+v.insEV)*12; D.svc+=n*(v.svcD+v.insD)*12; E.tax+=n*G.kmYr*rate(yr,1); D.tax+=n*G.kmYr*rate(yr,0); E.wage+=n*Q.fin.wage*12; D.wage+=n*Q.fin.wage*12; });
    rowsE.push(E); rowsD.push(D); }
  const tot=x=>K.reduce((a,k)=>a+x[k],0), cumE=[0], cumD=[0]; let be=null;
  rowsE.forEach((E,i) => { cumE.push(cumE[i]+tot(E)); cumD.push(cumD[i]+tot(rowsD[i])); if(be===null && cumE[i+1]<=cumD[i+1]) be=i+1; });
  const cats=K.map(k=>[NM[k], sum(rowsD.map(x=>x[k])), sum(rowsE.map(x=>x[k]))]), totE=cumE[Y], totD=cumD[Y], kmAll=sum(groups.map(G=>G.n*G.kmYr))*Y;
  /* CO2 */
  const ef=yr=>Q.co2.grid==='fixed'?+Q.co2.ef:(EF_PATH[yr]!=null?EF_PATH[yr]:EF_PATH[2034]);
  const co2D=sum(groups.map(G=>G.n*G.kmYr*G.v.dUse/100))*Q.co2.diesel/1000, gridAll=sum(groups.map(G=>G.n*G.gridYr));
  const co2Rows=[]; let saved=0; for(let y=1;y<=Y;y++){ const yr=DEMO.startYear+y-1, e=gridAll*ef(yr)/1e6; saved+=co2D-e; co2Rows.push([yr,ef(yr),e,co2D,co2D-e,saved]); }
  /* checks */
  const worstOf=(fn)=>groups.reduce((a,G)=>fn(G)<fn(a)?G:a, groups[0]);
  const gN=worstOf(G=>1-G.worst/G.usable), g8=worstOf(G=>1-G.worst/G.usable8), gR=worstOf(G=>G.c.ready?G.c.spare:-G.c.short), gT=worstOf(G=>G.shift-G.need), gP=worstOf(G=>G.payMax-G.payTop);
  const many=groups.length>1, nm=G=>many?' ('+G.g.name+')':'';
  const checks=[
    {k:'batt', t:'The battery covers the hardest day when new', ok:gN.worst<=gN.usable, res:fmt(100-gN.worst/gN.usable*100)+' % of the usable battery left'+nm(gN), go:'en'},
    {k:'age', t:'It still covers the hardest day at year 8', ok:g8.worst<=g8.usable8, res:(g8.worst<=g8.usable8?fmt(100-g8.worst/g8.usable8*100)+' % left':'short by '+fmt(g8.worst-g8.usable8)+' kWh')+' at '+fmt(g8.v.guar)+' % capacity'+nm(g8), go:'en'},
    {k:'ready', t:'Every vehicle is full before it leaves', ok:groups.every(G=>G.c.ready), res:(gR.c.ready?'full at '+hm(gR.c.end)+', '+fmt(gR.c.spare,1)+' h to spare':'short by '+fmt(gR.c.short)+' kWh at '+hm(gR.out))+nm(gR), go:'ch'},
    isNew ? {k:'grid', t:'Grid connection to apply for', ok:true, res:fmt(Math.ceil(peak/10)*10)+' kW, about '+fmt(A)+' A', go:'ch'}
          : {k:'grid', t:'Charging stays inside the grid connection', ok:peak<=limit, res:'peak '+fmt(peak)+' kW of '+fmt(limit)+' kW', go:'ch'},
    {k:'time', t:'The round fits in the shift', ok:gT.need<=gT.shift, res:fmt(gT.need,1)+' h needed of '+fmt(gT.shift,1)+' h'+nm(gT), go:'ov'},
    {k:'pay', t:'The load stays under the weight limit', ok:gP.payTop<=gP.payMax, res:fmt(gP.payTop,1)+' t of '+fmt(gP.payMax,1)+' t allowed, battery weight not yet counted'+nm(gP), go:'ov'} ];
  const ok=checks.every(c=>c.ok), save=totD-totE, fail=checks.find(c=>!c.ok);
  const title = ok ? (nVeh===1?'The vehicle':'All '+nVeh+' vehicles')+' can run on electricity'+(isNew?'':' with today’s grid connection')
    : ({batt:'The battery is too small for the hardest day', age:'The battery will be too small for the hardest day by year 8', ready:'The vehicles are not full again before they leave', grid:'Charging needs more power than the grid connection gives', time:'The round does not fit in the shift', pay:'The load is over the weight limit'})[fail.k];
  return { Q, dep, plan, groups, load, peak, peakAt:load.indexOf(peak)/4, limit, isNew, A, conn, nVeh, rowsE, rowsD, tot, cumE, cumD, be, cats, totE, totD, save, kmAll, elP, chgCap, co2D, co2E:co2Rows[0][2], co2Rows, co2Saved:saved, gridAll, checks, ok, title, Y };
}
