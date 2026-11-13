/* ---------- icons ---------- */
const IC={setup:'<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
  results:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',cmp:'<path d="M7 4v16M17 4v16M3 8h8M13 16h8"/>',
  docs:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
  ok:'<path d="m5 12 4.5 4.5L19 7"/>',no:'<path d="M6 6l12 12M18 6 6 18"/>',x:'<path d="M6 6l12 12M18 6 6 18"/>',play:'<path d="M7 5v14l11-7z" fill="currentColor" stroke="none"/>',
  chat:'<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>'};
const ico=(k,sz=16,sw=1.8)=>`<svg viewBox="0 0 24 24" width="${sz}" height="${sz}" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[k]}</svg>`;
const mark=ok=>`<span class="mark ${ok?'ok':'no'}">${ico(ok?'ok':'no',13,3)}</span>`;
const stat=(ok,yes,no)=>`<span class="st ${ok?'ok-t':'no-t'}">${ico(ok?'ok':'no',13,2.6)}${ok?yes:no}</span>`;

/* ---------- state and navigation ---------- */
const S={tab:'fleet',run:null,runNo:0,snap:null,runs:[],ai:false,enG:0,cmpA:1,cmpB:1,last:{setup:'fleet',results:'ov'}};
const SETUP=['fleet','depot','charging','weather','prices','costs','co2in','check'];
const MAIN=[['setup','Setup',SETUP],['results','Results',['ov','en','bat','ch','gr','cost','co2','src']],['cmp','Compare',['cmp']],['docs','Documents',['docs']]];
const TITLE={fleet:'Fleet',depot:'Depot',charging:'Charging',weather:'Weather',prices:'Energy prices',costs:'Costs',co2in:'CO₂',check:'Check and run',
  ov:'Overview',en:'Energy',bat:'Battery',ch:'Charging',gr:'Grid',cost:'Cost',co2:'CO₂',src:'Inputs and sources'};
const mainOf=t=>MAIN.find(m=>m[2].includes(t))[0];
const dirty=()=>S.snap!==null&&S.snap!==snapshot();
function drawNav(){
  const cur=mainOf(S.tab),miss=missing();
  $('nmain').innerHTML=MAIN.map(m=>`<button class="mtab" data-main="${m[0]}"${cur===m[0]?' aria-current="page"':''}${m[0]!=='setup'&&!S.run?' disabled title="Run the sample first"':''}>${ico(m[0],16)}<span>${m[1]}</span></button>`).join('');
  const subs=MAIN.find(m=>m[0]===cur)[2];
  $('nsub').innerHTML=subs.length>1?subs.map(t=>{
    const flag=cur==='setup'?miss.some(x=>x.open.page===t||(t==='fleet'&&x.open.lib)):(S.run&&S.run.checks.some(c=>!c.ok&&c.go===t));
    return `<button class="stab" data-tab="${t}"${S.tab===t?' aria-current="page"':''}>${TITLE[t]}${flag?'<i class="flag" title="Needs attention"></i>':''}</button>`;}).join(''):'';
  $('nsub').hidden=subs.length<2;
  const st=$('runState'),n=miss.length;
  st.className='rstate'+(n?' bad':dirty()||!S.run?' warn':'');
  st.textContent=n?plural(n,'value')+' needed before you can run':!S.run?'Sample project loaded. Not run yet':dirty()?'Inputs changed since run '+S.runNo:'Run '+S.runNo+' is up to date';
  $('bRun').disabled=!!n;
}
function go(t,keep){if(mainOf(t)!=='setup'&&!S.run)return;if(t!==S.tab)OPEN.clear();S.tab=t;const m=mainOf(t);if(S.last[m]!==undefined)S.last[m]=t;render();if(!keep){$('page').scrollTop=0;}}
function render(){
  const pg=PAGES[S.tab],R=S.run;if(!DLG)syncOpen($('content'));
  $('content').innerHTML=pg[0](R);if(pg[1])pg[1](R);drawNav();
}
const stale=()=>dirty()?`<p class="stale">These results are from run ${S.runNo}. The inputs have changed since. <button class="lnk" data-run>Run again</button></p>`:'';
function toast(msg){const d=document.createElement('div');d.className='toast';d.setAttribute('role','status');d.textContent=msg;document.body.appendChild(d);setTimeout(()=>d.remove(),2200);}
function doRun(){S.run=compute();S.run.alts=['cost','grid','early'].map(p=>p===S.run.plan?S.run:compute(p));S.runNo++;S.snap=snapshot();const t=new Date();
  S.runs.push({n:S.runNo,t:String(t.getHours()).padStart(2,'0')+':'+String(t.getMinutes()).padStart(2,'0'),R:S.run,rows:inputRows()});S.cmpB=S.runNo;S.cmpA=Math.max(1,S.runNo-1);}
function run(goto){
  if(missing().length){go('check');return;}
  const pr=$('prog'),pg=$('page');pg.classList.add('busy');pr.style.width='70%';
  setTimeout(()=>{doRun();pr.style.width='100%';pg.classList.remove('busy');setTimeout(()=>{pr.style.width='0';},200);
    go(goto||(mainOf(S.tab)==='results'?S.tab:'ov'));if(S.runNo>1)toast('Run '+S.runNo+' finished');aiGreet();},320);
}

/* ---------- forms ---------- */
const REG=[],OPEN=new Set();
const syncOpen=root=>root.querySelectorAll('details[data-sec]').forEach(d=>{d.open?OPEN.add(d.dataset.sec):OPEN.delete(d.dataset.sec);});
function reg(type,o){let i=REG.findIndex(r=>r.o===o);if(i<0){REG.push({type,o});i=REG.length-1;}return i;}
/* how a field is marked: blue when it is the user's own value, a small asterisk when it is a sample or an assumption, a red ring when it is missing */
const starred=f=>f.s==='sample'||f.s==='assume';
const ast=f=>starred(f)?`<sup class="ast" title="${esc(SRCN[f.s]+(f.r?'. '+f.r:''))}">*</sup>`:'';
function rst(f,o){const d=o._d?o._d[f.k]:undefined;if(d===undefined||d===''||f.t==='info')return'';
  const lab=f.o?(f.o.find(q=>String(q[0])===String(d))||[0,d])[1]:typeof d==='number'?fmt(d,f.dec||0):d;
  return`<button class="lnk rst" data-reset="${f.k}" title="Back to ${esc(lab)}">Reset</button>`;}
function ctl(f,o,oid,noUnit,aria){
  const id='f'+oid+'_'+f.k,v=o[f.k],at=`id="${id}" data-o="${oid}" data-k="${f.k}"${aria?` aria-label="${esc(aria)}"`:''}`,miss=isMissing(f,o);
  if(f.t==='info')return`<span class="fi">${esc(f.v(o))}</span>`;
  if(f.t==='sel')return`<select class="in" ${at}>${f.o.map(q=>`<option value="${q[0]}"${String(v)===String(q[0])?' selected':''}>${q[1]}</option>`).join('')}</select>`;
  return`<input class="in${f.t==='num'?' n':''}${miss?' miss':''}" ${at} ${f.t==='num'?'inputmode="decimal"':f.t==='time'?'type="time"':''} value="${esc(v==null?'':f.t==='num'&&typeof v==='number'?v.toLocaleString('en-GB',{maximumFractionDigits:6}):v)}"${miss?' aria-invalid="true"':''}>${f.u&&!noUnit?`<span class="u">${f.u}</span>`:''}`;}
function fieldHtml(f,o,oid){
  const id='f'+oid+'_'+f.k,v=o[f.k],lab=labelOf(f,o);
  if(f.t==='radio')return`<fieldset class="choice"><legend>${lab}</legend>${f.o.map(q=>q[3]
    ?`<div class="opt off"><input type="radio" disabled aria-label="${esc(q[1])}"><span><b>${q[1]}</b><small>${q[2]}</small></span></div>`
    :`<label class="opt"><input type="radio" name="${id}" value="${q[0]}" data-o="${oid}" data-k="${f.k}"${v===q[0]?' checked':''}><span><b>${q[1]}</b>${q[2]?`<small>${q[2]}</small>`:''}</span></label>`).join('')}</fieldset>`;
  return`<div class="fr" data-s="${srcOf(f,o)}">${f.t==='info'?`<span class="fl0">${lab}${ast(f)}</span>`:`<label for="${id}">${lab}${ast(f)}</label>`}<div class="fc">${ctl(f,o,oid)}${rst(f,o)}</div></div>`;}
function formHtml(type,o,keys){
  const oid=reg(type,o);let fs=visible(type,o);fs=keys?fs.filter(f=>keys.includes(f.k)):fs.filter(f=>!f.pg);
  const secs=[...new Set(fs.filter(f=>f.sec).map(f=>f.sec))];
  return fs.filter(f=>!f.sec).map(f=>fieldHtml(f,o,oid)).join('')+secs.map(sn=>{
    const ff=fs.filter(f=>f.sec===sn),ed=ff.filter(f=>srcOf(f,o)==='you').length,ms=ff.filter(f=>isMissing(f,o)).length;
    return`<details class="fold" data-sec="${esc(sn)}"${OPEN.has(sn)||ms?' open':''}><summary>${sn}<small>${plural(ff.length,'value')}${ed?', '+ed+' changed':''}${ms?', '+ms+' needed':''}</small></summary><div>${ff.map(f=>fieldHtml(f,o,oid)).join('')}</div></details>`;}).join('');}
/* a small grid of inputs: one row for each item, one column for each side */
function matrix(type,o,cols,rows){
  const oid=reg(type,o),fd=k=>DEFS[type].fields.find(f=>f.k===k);
  return`<div class="tw"><table class="mx"><thead><tr><th scope="col"><span class="sr">Item</span></th>${cols.map(c=>`<th scope="col">${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><th scope="row">${r[0]}<small>${r[1]}</small></th>${r.slice(2).map((k,i)=>{const f=fd(k);
    return`<td data-s="${srcOf(f,o)}"><div class="fc">${ctl(f,o,oid,1,r[0]+', '+cols[i].toLowerCase())}${ast(f)}${rst(f,o)}</div></td>`;}).join('')}</tr>`).join('')}</tbody></table></div>`;}
const LEGEND='<p class="legend"><span><sup class="ast on">*</sup> Sample or assumed value</span><span><i class="sw"></i>Changed by you</span><span>Every source is listed under Check and run and in the reports.</span></p>';
function setVal(oid,k,raw){
  const {type,o}=REG[oid],f=DEFS[type].fields.find(x=>x.k===k);let v=raw;
  if(f.t==='num'){let t=String(raw).replace(/\s/g,'');t=/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)?t.replace(/,/g,''):t.replace(',','.');const x=parseFloat(t);v=String(raw).trim()===''||isNaN(x)?'':x;}
  o[k]=v;
  if(type==='veh'&&k==='cls'){const c=CLS.find(q=>q[0]===o.cls)[2];if(o.cdxa===o._d.cdxa||o.cdxa==='')o.cdxa=c;o._d.cdxa=c;}
  if(type==='rt'&&k==='road'){const sp=ROAD_V[o.road];if(o.speed===o._d.speed||o.speed==='')o.speed=sp;o._d.speed=sp;}
  return f;}

/* ---------- dialogs ---------- */
let DLG=null;
function openDlg(cfg){
  if(DLG)DLG.el.remove();OPEN.clear();
  const m=document.createElement('div');m.className='modal';
  m.innerHTML=`<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="dlgT"><header><div><h2 id="dlgT" tabindex="-1"></h2><p id="dlgS"></p></div><button class="x" data-close aria-label="Close">${ico('x',18)}</button></header><div class="dbody" id="dlgB"></div><footer id="dlgF"></footer></div>`;
  document.body.appendChild(m);DLG={el:m,cfg};drawDlg();$('dlgT').focus();}
function drawDlg(){
  syncOpen(DLG.el);const c=DLG.cfg,a=document.activeElement,fid=a&&DLG.el.contains(a)?a.id:null,sc=$('dlgB').scrollTop;
  $('dlgT').textContent=c.title();$('dlgS').textContent=c.sub?c.sub():'';$('dlgB').innerHTML=c.body();
  $('dlgF').innerHTML='<p class="legend"><span><sup class="ast on">*</sup> Sample or assumed value</span><span><i class="sw"></i>Changed by you</span></p><span class="sp"></span><button class="btn pri" data-close>Done</button>';
  $('dlgB').scrollTop=sc;if(fid&&$(fid))$(fid).focus();}
function closeDlg(){if(!DLG)return;const fk=DLG.cfg.fk;DLG.el.remove();DLG=null;render();const b=fk&&document.querySelector('[data-fk="'+fk+'"]');if(b)b.focus();}
function openTpl(lib,gid){
  const d=DEFS[lib],g=()=>P.groups.find(x=>x.id===gid);
  openDlg({fk:lib+'-'+gid,title:()=>d.title,sub:()=>d.lead+' For the group “'+g().name+'”.',
    body:()=>{const t=tpl(lib,g()[lib]);
      let h=`<div class="pick"><label class="sr" for="tplSel">Saved ${d.many}</label><select class="in" id="tplSel" data-tplsel>${t?'':'<option value="" selected>Choose a saved '+d.one+'</option>'}${P.lib[lib].map(x=>`<option value="${x.id}"${t&&x.id===t.id?' selected':''}>${esc(x.name)}</option>`).join('')}</select><button class="lnk" data-tplnew>New ${d.one}</button>${t?'<button class="lnk" data-tpldup>Copy this one</button>':''}</div>`;
      if(!t)return h+`<p class="note">Choose a saved ${d.one} or make a new one.</p>`;
      const oth=P.groups.filter(x=>x.id!==gid&&x[lib]===t.id),oid=reg(lib,t);
      if(oth.length)h+=`<p class="used">Also used by ${oth.map(x=>'“'+esc(x.name)+'”').join(' and ')}. Changes here apply there too. Copy it first to change only this group.</p>`;
      h+=`<div class="fr"><label for="tplName">Name</label><div class="fc"><input class="in" id="tplName" data-name="${oid}" value="${esc(t.name)}"></div></div>`;
      return h+formHtml(lib,t)+(lib==='veh'?'<p class="note" style="margin-top:14px">Price, service and insurance are on the <button class="lnk" data-goto="costs">Costs page</button>.</p>':'');},
    lib,gid});}
function openAt(o){if(o.lib)openTpl(o.lib,o.gid);else go(o.page);}

/* ---------- setup pages ---------- */
const DAYS={mf:'Monday to Friday',ms:'Monday to Saturday',all:'every day'};
const SUMM={
  veh:t=>CLS.find(c=>c[0]===t.cls)[1]+', '+(t.battMode==='size'?'battery sized by the tool':(t.battKwh?fmt(t.battKwh)+' kWh battery':'battery size needed')),
  rt:t=>t.km===''?'Distance needed':fmt(t.km)+' km a day, '+fmt(t.stops||0)+' stops',
  load:t=>t.start===''?'Weight needed':t.shape==='linear'?fmt(t.start,1)+' t rising to '+fmt(t.end||0,1)+' t':fmt(t.start,1)+' t all day',
  eq:t=>t.type==='none'?'No powered equipment':t.type==='stop'?fmt(t.kwhStop||0,2)+' kWh at each stop':fmt(t.wOn||0)+' W all shift',
  sch:t=>(t.out&&t.back)?t.out+' to '+t.back+', '+DAYS[t.days]:'Times needed'};
function pageFleet(){
  const tot=sum(P.groups.map(g=>+g.n||0));
  const cell=(g,l)=>{const t=tpl(l,g[l]),bad=!t||visible(l,t).some(f=>isMissing(f,t));
    return`<td data-l="${DEFS[l].title}"><button class="cellbtn${bad?' miss':''}" data-tpl="${l}|${g.id}" data-fk="${l}-${g.id}"><b>${t?esc(t.name):'Choose'}</b><span>${t?SUMM[l](t):'Not chosen yet'}</span></button></td>`;};
  return`<h1>Fleet</h1><p class="lede">One row for each group of identical vehicles doing the same day. Select a blue name to see or change the vehicle, the route, the load, the equipment or the shift.</p>
  <div class="tw" style="margin-top:22px"><table class="t fleet"><thead><tr><th scope="col">Group</th><th scope="col">Vehicles</th><th scope="col">Vehicle</th><th scope="col">Route</th><th scope="col">Load</th><th scope="col">Body equipment</th><th scope="col">Shift</th><th scope="col"><span class="sr">Actions</span></th></tr></thead><tbody>
  ${P.groups.map(g=>`<tr><td data-l="Group"><input class="in gname" data-g="name|${g.id}" value="${esc(g.name)}" aria-label="Group name"></td>
    <td data-l="Vehicles"><input class="in n cnt${g.n>=1?'':' miss'}" data-g="n|${g.id}" inputmode="numeric" value="${g.n}" aria-label="Number of vehicles in ${esc(g.name)}"></td>
    ${LIBS.map(l=>cell(g,l)).join('')}
    <td class="rowact" data-l=""><span><button class="lnk" data-gdup="${g.id}">Copy</button><button class="lnk" data-gdel="${g.id}"${P.groups.length<2?' hidden':''}>Remove</button></span></td></tr>`).join('')}
  </tbody></table></div>
  <p style="margin-top:14px"><button class="lnk" data-gadd>Add a group</button><span class="mut" id="fleetTot" style="margin-left:18px">${plural(tot,'vehicle')} in ${plural(P.groups.length,'group')}</span></p>
  ${nav('fleet')}`;}
const nav=t=>{const i=SETUP.indexOf(t),p=SETUP[i-1],n=SETUP[i+1];return`<div class="nextrow">${p?`<button class="btn" data-tab="${p}">Back: ${TITLE[p]}</button>`:'<span></span>'}${n?`<button class="btn" data-tab="${n}">Next: ${TITLE[n]}</button>`:'<span></span>'}</div>`;};
const sect=(t,note,body,hl)=>`<section class="sect${hl?' hl':''}"><h2>${t}</h2>${note?`<p class="note">${note}</p>`:''}${body}</section>`;
function pageDepot(){
  return`<h1>Depot</h1><p class="lede">Where the vehicles park and charge, and what the grid connection allows.</p>
  ${sect('Site','',formHtml('depot',P.depot,['name','addr']))}
  ${sect('Grid connection','',formHtml('depot',P.depot,['mode','limit','dso','base']))}
  ${LEGEND}${nav('depot')}`;}
function pageCharging(){
  return`<h1>Charging</h1><p class="lede">How big the chargers are and when the vehicles charge. This demo gives every vehicle its own charger.</p>
  ${sect('Chargers','',formHtml('chg',P.chg,['chgMode','kw']),1)}
  ${sect('When to charge','',formHtml('chg',P.chg,['plan']),1)}
  <div class="sect">${formHtml('chg',P.chg,['loadF','loss'])}</div>
  ${LEGEND}${nav('charging')}`;}
function pageWeather(){
  const mf=MONTH_F.map((f,i)=>P.wx.year==='cold'&&(i<2||i>9)?f*DEMO.cold:f);
  return`<h1>Weather</h1><p class="lede">Cold days take more energy. The fleet is sized for the hardest day of the year you choose here.</p>
  ${sect('Location','',`<div class="fr"><span class="fl0">Depot</span><div class="fc"><span class="fi">${esc(P.depot.addr||'Not set')}</span><button class="lnk" data-tab="depot">Change on the Depot page</button></div></div>`)}
  ${sect('Year to size for','',formHtml('wx',P.wx),1)}
  ${sect('What that means month by month','Energy on a working day in each month, compared with April. Stand-in factors in this demo, the same for every location. They are not measured weather.',
    `<div class="tw"><table class="t months"><thead><tr>${MONTHS.map(m=>`<th scope="col" class="r">${m}</th>`).join('')}</tr></thead><tbody><tr>${mf.map(f=>`<td class="r">${signed((f-1)*100,0)} %</td>`).join('')}</tr></tbody></table></div>`)}
  ${nav('weather')}`;}
function pagePrices(){
  return`<h1>Energy prices</h1><p class="lede">What a kilowatt-hour and a litre cost. They decide the running cost on both sides of the comparison.</p>
  ${sect('Electricity','',formHtml('pr',P.pr,['elPrice','level']))}
  ${sect('Diesel','',formHtml('pr',P.pr,['dPrice']))}
  ${LEGEND}${nav('prices')}`;}
function pageCosts(){
  const seen={},vs=[];P.groups.forEach(g=>{const v=tpl('veh',g.veh);if(v&&!seen[v.id]){seen[v.id]=1;vs.push(v);}});
  return`<h1>Costs</h1><p class="lede">What the vehicles cost to buy and to keep, on the electric side and on the diesel side.</p>
  ${sect('Vehicles',vs.length>1?'One table for each vehicle used in the fleet.':'',vs.map(v=>(vs.length>1?`<h3>${esc(v.name)}</h3>`:'')+matrix('veh',v,['Electric','Diesel'],[['Purchase price','DKK','priceEV','priceD'],['Service','DKK a month','svcEV','svcD'],['Insurance','DKK a month','insEV','insD']])).join(''))}
  ${sect('Financing','',formHtml('fin',P.fin,['years','interest','resid']))}
  ${sect('Drivers','The same on both sides, so it does not change the difference.',formHtml('fin',P.fin,['wage']))}
  ${sect('Road tax','Danish road tax per km, by period.',matrix('tax',P.tax,['Electric','Diesel'],[['2026 to 2027','DKK per km','e1','d1'],['2028','DKK per km','e2','d2'],['From 2029','DKK per km','e3','d3']]))}
  ${sect('Grants','',formHtml('tax',P.tax,['grant']))}
  ${LEGEND}${nav('costs')}`;}
function pageCo2in(){
  return`<h1>CO₂</h1><p class="lede">How much CO₂ a kilowatt-hour and a litre of diesel stand for.</p>
  ${sect('Grid electricity','',formHtml('co2',P.co2,['gridMode','gridEF']),1)}
  ${sect('Diesel','',formHtml('co2',P.co2,['co2D']))}
  ${LEGEND}${nav('co2in')}`;}
function srcTable(rows){
  let last='';return`<div class="tw"><table class="t"><thead><tr><th scope="col">Value</th><th scope="col">Used</th><th scope="col">Where it comes from</th></tr></thead><tbody>${rows.map(r=>{
    const hd=r.where!==last?`<tr><td colspan="3" style="font-weight:600;padding-top:18px">${esc(r.where)}</td></tr>`:'';last=r.where;
    return hd+`<tr><td>${esc(r.label)}</td><td>${esc(r.value)}</td><td class="mut">${r.radio?'Your choice':`<span class="${r.src==='you'?'':''}">${SRCN[r.src]}</span>${r.ref?' · '+esc(r.ref):''}`}</td></tr>`;}).join('')}</tbody></table></div>`;}
function srcCounts(rows){const c={};rows.forEach(r=>{if(!r.radio)c[r.src]=(c[r.src]||0)+1;});return c;}
function pageCheck(){
  const m=missing(),rows=inputRows(),c=srcCounts(rows),n=rows.filter(r=>!r.radio).length;
  return`<div class="verd">${mark(!m.length)}<div><h1>${m.length?plural(m.length,'value')+' needed before you can run':'Everything is filled in'}</h1>
  <p class="lede">${m.length?'Select a line to go to it.':(S.run&&!dirty()?'Run '+S.runNo+' already uses these inputs.':'The run takes the fleet through a full year, hardest day included.')}</p></div></div>
  ${m.length?`<ul class="misslist">${m.map((x,i)=>`<li><button class="lnk" data-miss="${i}">${esc(x.where)}</button> · ${esc(x.label)}</li>`).join('')}</ul>`:''}
  <p style="margin-top:22px"><button class="btn pri big" data-run${m.length?' disabled':''}>${ico('play',14)}Run</button></p>
  <h2>Where the ${n} values come from</h2>
  <div class="tw"><table class="t kvt"><tbody>
    <tr><th scope="row">Your own values</th><td class="r">${c.you||0}</td><td class="mut">Entered or changed by you.</td></tr>
    <tr><th scope="row">Standard values</th><td class="r">${c.std||0}</td><td class="mut">From EU and Danish standard data.</td></tr>
    <tr><th scope="row">Sample values</th><td class="r">${c.sample||0}</td><td class="mut">Stand-ins. Replace them with your own data.</td></tr>
    <tr><th scope="row">Assumptions</th><td class="r">${c.assume||0}</td><td class="mut">Choices made where no data exists. Check them.</td></tr>
  </tbody></table></div>
  <details class="more"><summary>Show every value and its source</summary>${srcTable(rows)}</details>
  ${nav('check')}`;}
