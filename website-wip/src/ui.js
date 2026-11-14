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
const S={tl:'veh',tid:{},sel:{},bulkL:'rt',tab:'fleet',run:null,runNo:0,snap:null,runs:[],ai:false,enG:0,cmpA:1,cmpB:1,last:{setup:'fleet',results:'ov'}};
const SETUP=['project','fleet','templates','depot','charging','weather','prices','costs','tax','check'];
const MAIN=[['setup','Setup',SETUP],['results','Results',['ov','en','bat','ch','gr','cost','co2','src']],['cmp','Compare',['cmp']],['docs','Documents',['docs']]];
const TITLE={project:'Project',fleet:'Fleet',templates:'Templates',depot:'Depot and grid',charging:'Charging',weather:'Weather',prices:'Prices',costs:'Costs',tax:'Taxes and CO₂',check:'Check and run',
  ov:'Overview',en:'Energy',bat:'Battery',ch:'Charging',gr:'Grid',cost:'Cost',co2:'CO₂',src:'Inputs and sources'};
const mainOf=t=>MAIN.find(m=>m[2].includes(t))[0];
const dirty=()=>S.snap!==null&&S.snap!==snapshot();
function drawNav(){
  const cur=mainOf(S.tab),miss=missing();
  $('nmain').innerHTML=MAIN.map(m=>`<button class="mtab" data-main="${m[0]}"${cur===m[0]?' aria-current="page"':''}${m[0]!=='setup'&&!S.run?' disabled title="Run the sample first"':''}>${ico(m[0],16)}<span>${m[1]}</span></button>`).join('');
  const subs=MAIN.find(m=>m[0]===cur)[2];
  $('nsub').innerHTML=subs.length>1?subs.map(t=>{
    const flag=cur==='setup'?miss.some(x=>x.open.page===t||(t==='templates'&&x.open.lib)):(S.run&&S.run.checks.some(c=>!c.ok&&c.go===t));
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
  if(f.t==='tog')return`<label class="tog"><input type="checkbox" ${at}${v==='yes'?' checked':''}><i></i><span>${v==='yes'?'Yes':'No'}</span></label>`;
  if(f.t==='multi')return`<span class="multi">${f.o.map(q=>`<label><input type="checkbox" data-o="${oid}" data-k="${f.k}" data-mv="${q[0]}"${(' '+v+' ').includes(' '+q[0]+' ')?' checked':''}>${q[1]}</label>`).join('')}</span>`;
  if(f.t==='file')return`<label class="btn filebtn">Choose a file<input type="file" class="sr" ${at}></label><span class="u">${v?esc(v):'The demo keeps the file name only'}</span>`;
  return`<input class="in${f.t==='num'?' n':''}${miss?' miss':''}" ${at} ${f.t==='num'?'inputmode="decimal"':f.t==='time'?'type="time"':''} value="${esc(v==null?'':f.t==='num'&&typeof v==='number'?v.toLocaleString('en-GB',{maximumFractionDigits:6}):v)}"${miss?' aria-invalid="true"':''}>${f.u&&!noUnit?`<span class="u">${f.u}</span>`:''}`;}
function fieldHtml(f,o,oid){
  const id='f'+oid+'_'+f.k,v=o[f.k],lab=labelOf(f,o);
  if(f.t==='radio')return`<fieldset class="choice"><legend>${lab}</legend>${f.o.map(q=>q[3]
    ?`<div class="opt off"><input type="radio" disabled aria-label="${esc(q[1])}"><span><b>${q[1]}</b><small>${q[2]}</small></span></div>`
    :`<label class="opt"><input type="radio" name="${id}" value="${q[0]}" data-o="${oid}" data-k="${f.k}"${v===q[0]?' checked':''}><span><b>${q[1]}</b>${q[2]?`<small>${q[2]}</small>`:''}</span></label>`).join('')}</fieldset>`;
  const plain=f.t==='info'||f.t==='multi'||f.t==='file'||f.t==='tog';
  return`<div class="fr" data-s="${srcOf(f,o)}">${plain?`<span class="fl0">${lab}${ast(f)}</span>`:`<label for="${id}">${lab}${ast(f)}</label>`}<div class="fc">${ctl(f,o,oid)}${rst(f,o)}</div></div>`;}
/* main fields on the page; everything detailed sits behind a button named after what it holds */
const popsOf=(type,o)=>[...new Set(visible(type,o).filter(f=>f.pop).map(f=>f.pop))];
function popBtns(type,o,names){
  const oid=reg(type,o),all=popsOf(type,o),list=(names||all).filter(n=>all.includes(n));if(!list.length)return'';
  return`<div class="pops">${list.map(n=>{const ff=visible(type,o).filter(f=>f.pop===n),ed=ff.filter(f=>srcOf(f,o)==='you').length,ms=ff.filter(f=>isMissing(f,o)).length;
    return`<button class="btn popb${ms?' miss':''}" data-pop="${oid}|${esc(n)}" data-fk="pop-${oid}-${esc(n)}">${esc(n)}${ms?`<small class="no-t">${ms} needed</small>`:ed?`<small class="you-t">${ed} changed</small>`:''}</button>`;}).join('')}</div>`;}
function formHtml(type,o,keys,pops){
  const oid=reg(type,o);let fs=visible(type,o).filter(f=>!f.pop);fs=keys?fs.filter(f=>keys.includes(f.k)):fs.filter(f=>!f.pg);
  return fs.map(f=>fieldHtml(f,o,oid)).join('')+(keys&&!pops?'':popBtns(type,o,pops));}
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
  if(type==='veh'&&k==='cls'){const c=CLS.find(q=>q[0]===o.cls)[2],h=HEIGHT[o.cls];if(o.cdxa===o._d.cdxa||o.cdxa==='')o.cdxa=c;o._d.cdxa=c;if(o.height===o._d.height||o.height==='')o.height=h;o._d.height=h;}
  if(type==='rt'&&k==='road'){const sp=ROAD_V[o.road];if(o.speed===o._d.speed||o.speed==='')o.speed=sp;o._d.speed=sp;}
  return f;}

/* ---------- dialogs ---------- */
let DLG=null;
function openDlg(cfg){
  if(DLG)DLG.el.remove();OPEN.clear();
  const m=document.createElement('div');m.className='modal';
  m.innerHTML=`<div class="dlg${cfg.wide?' wide':''}" role="dialog" aria-modal="true" aria-labelledby="dlgT"><header><div><h2 id="dlgT" tabindex="-1"></h2><p id="dlgS"></p></div><button class="x" data-close aria-label="Close">${ico('x',18)}</button></header><div class="dbody" id="dlgB"></div><footer id="dlgF"></footer></div>`;
  document.body.appendChild(m);DLG={el:m,cfg};drawDlg();$('dlgT').focus();}
function drawDlg(){
  syncOpen(DLG.el);const c=DLG.cfg,a=document.activeElement,fid=a&&DLG.el.contains(a)?a.id:null,sc=$('dlgB').scrollTop;
  $('dlgT').textContent=c.title();$('dlgS').textContent=c.sub?c.sub():'';$('dlgB').innerHTML=c.body();
  $('dlgF').innerHTML='<p class="legend"><span><sup class="ast on">*</sup> Sample or assumed value</span><span><i class="sw"></i>Changed by you</span></p><span class="sp"></span><button class="btn pri" data-close>Done</button>';
  $('dlgB').scrollTop=sc;if(fid&&$(fid))$(fid).focus();}
function closeDlg(){if(!DLG)return;const fk=DLG.cfg.fk;DLG.el.remove();DLG=null;render();const b=fk&&document.querySelector('[data-fk="'+fk+'"]');if(b)b.focus();}
function openPop(oid,name){
  const {type,o}=REG[oid];
  openDlg({fk:'pop-'+oid+'-'+name,title:()=>name,sub:()=>DEFS[type].title+(o.name&&o.id?': '+o.name:'')+' · detailed settings',
    body:()=>{const id=reg(type,o);return visible(type,o).filter(f=>f.pop===name).map(f=>fieldHtml(f,o,id)).join('');}});}
function openStops(gid){
  const g=()=>P.groups.find(x=>x.id===gid);
  openDlg({fk:'stops-'+gid,wide:1,title:()=>'Stops',sub:()=>{const r=tpl('rt',g().rt);return'“'+g().name+'”'+(r?' on '+r.name:'')+' · one working day';},
    body:()=>{const gr=g(),rt=tpl('rt',gr.rt),rows=stopRows(gr);
      if(!rt||rt.method!=='typed')return'<p class="note">The stop table is built from a typed route. This row uses another kind of route.</p>';
      if(!rows.length)return'<p class="note">This route has no stops.</p>';
      return`<p class="note">Built from the route, the payload and the PTO of this row. Stops are spaced evenly until you change them.* Change any cell. Your changes stay on this fleet row.${hasOv(gr)?` <button class="lnk" data-streset="${gid}">Reset the table</button>`:''}</p>
      <div class="tw"><table class="t stops"><thead><tr><th scope="col">Stop</th><th scope="col" class="r">From the depot, km</th><th scope="col" class="r">Time at the stop, s</th><th scope="col" class="r">Payload after, t</th><th scope="col">PTO works</th></tr></thead><tbody>${rows.map(r=>`<tr${r.ed?' class="ed"':''}><td>${r.i}</td>
        <td class="r"><input class="in n" data-st="${gid}|${r.i}|d" value="${fmt(r.d,1)}" inputmode="decimal" aria-label="Stop ${r.i}, km from the depot"></td>
        <td class="r"><input class="in n" data-st="${gid}|${r.i}|t" value="${fmt(r.t)}" inputmode="decimal" aria-label="Stop ${r.i}, time at the stop"></td>
        <td class="r"><input class="in n" data-st="${gid}|${r.i}|p" value="${fmt(r.p,2)}" inputmode="decimal" aria-label="Stop ${r.i}, payload after the stop"></td>
        <td><input type="checkbox" data-st="${gid}|${r.i}|on"${r.on?' checked':''} aria-label="Stop ${r.i}, PTO works"></td></tr>`).join('')}</tbody></table></div>`;}});}
function openAt(o){if(o.lib){S.tl=o.lib;S.tid[o.lib]=o.tid;go('templates');}else go(o.page);if(o.pop){const t=o.lib?tpl(o.lib,o.tid):P[Object.keys(SETPAGE).find(k=>SETPAGE[k]===o.page&&popsOf(k,P[k]).includes(o.pop))||o.page];if(t)openPop(reg(o.lib||REG.find(r=>r.o===t).type,t),o.pop);}}

/* ---------- setup pages ---------- */
const DAYS={mf:'Monday to Friday',ms:'Monday to Saturday',all:'every day'};
const SUMM={
  veh:t=>'Group '+t.cls+', '+(t.battMode==='size'?'battery sized by the tool':(t.battKwh?fmt(t.battKwh)+' kWh battery':'battery size needed')),
  rt:t=>t.method==='cycle'?'VECTO standard cycle':t.method==='gps'?'GPS log':t.km===''?'Distance needed':fmt(t.km)+' km a day, '+fmt(t.stops||0)+' stops',
  load:t=>t.start===''?'Weight needed':t.shape==='stops'?'Set at each stop':t.shape==='linear'?fmt(t.start,1)+' t rising to '+fmt(t.end||0,1)+' t':fmt(t.start,1)+' t all day',
  eq:t=>t.type==='none'?'No powered equipment':t.type==='stop'?fmt(t.kwhStop||0,2)+' kWh at each stop':fmt(t.wOn||0)+' W all shift',
  sch:t=>(t.out&&t.back)?t.out+' to '+t.back+', '+DAYS[t.days]:'Times needed'};
function pageProject(){
  return`<h1>Project</h1><p class="lede">What the project is called and how it is run.</p>
  ${sect('Names','',formHtml('proj',P.proj,['name','scen']))}
  ${sect('Run','',formHtml('proj',P.proj,['mode','brand']))}
  ${nav('project')}`;}
function pageFleet(){
  const tot=sum(P.groups.map(g=>+g.n||0)),nsel=P.groups.filter(g=>S.sel[g.id]).length;
  const cell=(g,l)=>{const t=tpl(l,g[l]),bad=!t||visible(l,t).some(f=>isMissing(f,t));
    return`<td data-l="${DEFS[l].title}"><select class="in${bad?' miss':''}" data-gl="${l}|${g.id}" aria-label="${DEFS[l].title} for ${esc(g.name)}">${t?'':'<option value="" selected>Choose</option>'}${P.lib[l].map(x=>`<option value="${x.id}"${t&&x.id===t.id?' selected':''}>${esc(x.name)}</option>`).join('')}<option value="__new">New ${DEFS[l].one}…</option></select>
      <span class="csum">${t?SUMM[l](t)+` <button class="lnk" data-tedit="${l}|${t.id}">Edit</button>`:'Not chosen yet'}</span></td>`;};
  const runs={};P.groups.forEach(g=>{const k=g.veh+'|'+g.rt+'|'+g.eq;(runs[k]=runs[k]||[]).push(g);});const RK=Object.keys(runs);
  return`<h1>Fleet</h1><p class="lede">One row for each group of identical vehicles doing the same day. Each row picks a vehicle, a route, a payload, a PTO profile and a schedule from your templates.</p>
  <div class="tw" style="margin-top:22px"><table class="t fleet"><thead><tr><th scope="col"><input type="checkbox" id="selAll" aria-label="Select all rows"${nsel&&nsel===P.groups.length?' checked':''}></th><th scope="col">Group</th><th scope="col">Count</th>${LIBS.map(l=>`<th scope="col">${DEFS[l].title}</th>`).join('')}<th scope="col"><span class="sr">Actions</span></th></tr></thead><tbody>
  ${P.groups.map(g=>`<tr><td data-l=""><input type="checkbox" data-sel="${g.id}" aria-label="Select ${esc(g.name)}"${S.sel[g.id]?' checked':''}></td><td data-l="Group"><input class="in gname" data-g="name|${g.id}" value="${esc(g.name)}" aria-label="Group name"></td>
    <td data-l="Count"><input class="in n cnt${g.n>=1?'':' miss'}" data-g="n|${g.id}" inputmode="numeric" value="${g.n}" aria-label="Number of vehicles in ${esc(g.name)}"></td>
    ${LIBS.map(l=>cell(g,l)).join('')}
    <td class="rowact" data-l=""><span><button class="lnk" data-stops="${g.id}" data-fk="stops-${g.id}">Stops${hasOv(g)?'<i class="flag" title="Edited"></i>':''}</button><button class="lnk" data-gdup="${g.id}">Copy</button><button class="lnk" data-gdel="${g.id}"${P.groups.length<2?' hidden':''}>Remove</button></span></td></tr>`).join('')}
  </tbody></table></div>
  <div class="bulk"${nsel?'':' hidden'}><b>${plural(nsel,'row')} selected</b><label for="bulkL">Set</label><select class="in" id="bulkL">${LIBS.map(l=>`<option value="${l}"${S.bulkL===l?' selected':''}>${DEFS[l].title}</option>`).join('')}</select><label for="bulkT">to</label><select class="in" id="bulkT">${P.lib[S.bulkL].map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join('')}</select><button class="btn" data-bulk>Apply</button></div>
  <p style="margin-top:14px"><button class="lnk" data-gadd>Add a row</button><span class="mut" id="fleetTot" style="margin-left:18px">${plural(tot,'vehicle')} in ${plural(P.groups.length,'row')}</span></p>
  <h2>What will be driven</h2><p class="note">Rows that share vehicle, route and PTO are driven once. Payload, weather and schedule are applied afterwards.</p>
  ${tbl(['<Driver run','<Vehicle','<Route','<PTO','<Rows','Vehicles'],RK.map((k,i)=>{const gs=runs[k],g=gs[0],n=x=>{const t=tpl(x,g[x]);return t?esc(t.name):'Not chosen';};return[i+1,n('veh'),n('rt'),n('eq'),gs.map(x=>esc(x.name)).join(', '),sum(gs.map(x=>+x.n||0))];}))}
  ${nav('fleet')}`;}
function pageTemplates(){
  const l=S.tl,d=DEFS[l],list=P.lib[l],t=tpl(l,S.tid[l])||list[0],uses=x=>P.groups.filter(g=>g[l]===x.id);
  let ed='<p class="note">No '+d.one+' yet.</p>';
  if(t){const oid=reg(l,t),us=uses(t);
    ed=`<div class="fr"><label for="tplName">Name</label><div class="fc"><input class="in" id="tplName" data-name="${oid}" value="${esc(t.name)}"></div></div>
    ${formHtml(l,t)}
    ${l==='veh'?'<p class="note" style="margin-top:16px">Price, service and insurance are on the <button class="lnk" data-tab="costs">Costs page</button>.</p>':''}
    ${l==='rt'||l==='load'?'<p class="note" style="margin-top:16px">Stop by stop figures are under Stops on each fleet row.</p>':''}
    <p class="tact"><span class="mut">${us.length?'Used by '+us.map(x=>'“'+esc(x.name)+'”').join(' and ')+'. Changes apply there too.':'Not used by any fleet row.'}</span><button class="lnk" data-tdup="${t.id}">Make a copy</button>${us.length||list.length<2?'':`<button class="lnk" data-tdel="${t.id}">Delete</button>`}</p>${LEGEND}`;}
  return`<h1>Templates</h1><p class="lede">Your saved vehicles, routes, payloads, PTO profiles and schedules. Fleet rows pick from these.</p>
  <div class="ltabs" role="tablist">${LIBS.map(x=>`<button role="tab" data-tl="${x}"${x===l?' aria-selected="true"':''}>${DEFS[x].title}<small>${P.lib[x].length}</small></button>`).join('')}</div>
  <div class="tgrid"><div class="tlist">${list.map(x=>`<button data-tsel="${x.id}"${t&&x.id===t.id?' aria-current="true"':''}><b>${esc(x.name)}</b><span>${SUMM[l](x)}</span></button>`).join('')}<button class="lnk" data-tnew>New ${d.one}</button></div>
  <div class="ted"><p class="lead2">${d.lead}</p>${ed}</div></div>
  ${nav('templates')}`;}
const nav=t=>{const i=SETUP.indexOf(t),p=SETUP[i-1],n=SETUP[i+1];return`<div class="nextrow">${p?`<button class="btn" data-tab="${p}">Back: ${TITLE[p]}</button>`:'<span></span>'}${n?`<button class="btn" data-tab="${n}">Next: ${TITLE[n]}</button>`:'<span></span>'}</div>`;};
const sect=(t,note,body,hl)=>`<section class="sect${hl?' hl':''}"><h2>${t}</h2>${note?`<p class="note">${note}</p>`:''}${body}</section>`;
function pageDepot(){
  return`<h1>Depot and grid</h1><p class="lede">Where the vehicles park and charge, and what the grid connection allows.</p>
  ${sect('Site','',formHtml('depot',P.depot,['name','addr'],['Parking']))}
  ${sect('Grid connection','',formHtml('depot',P.depot,['mode','limit','dso','access'],P.depot.access==='lim'?['Limited access what-if']:[]))}
  ${sect('Buildings','',formHtml('depot',P.depot,['baseMode','base']),1)}
  ${LEGEND}${nav('depot')}`;}
function pageCharging(){
  return`<h1>Charging</h1><p class="lede">How big the chargers are and when the vehicles charge.</p>
  ${sect('Chargers','',formHtml('chg',P.chg,['chgMode','kw','points'],['Charger load and losses']),1)}
  ${sect('When to charge','',formHtml('chg',P.chg,['plan','readyBy'],['Flexibility']),1)}
  ${LEGEND}${nav('charging')}`;}
function pageWeather(){
  const mf=MONTH_F.map((f,i)=>P.wx.year==='cold'&&(i<2||i>9)?f*DEMO.cold:f);
  return`<h1>Weather</h1><p class="lede">Cold days take more energy. The fleet is sized for the hardest day of the year you choose here.</p>
  ${sect('Location','',`<div class="fr"><span class="fl0">Depot</span><div class="fc"><span class="fi">${esc(P.depot.addr||'Not set')}</span><button class="lnk" data-tab="depot">Change under Depot and grid</button></div></div>`+formHtml('wx',P.wx,['station']))}
  ${sect('Year to size for','',formHtml('wx',P.wx,['year']),1)}
  ${sect('How the weather is used','',formHtml('wx',P.wx,['detail','shift','worst'],['Wind']))}
  ${sect('What the year means month by month','Energy on a working day in each month, compared with April. Stand-in factors in this demo, the same for every location. They are not measured weather.',
    `<div class="tw"><table class="t months"><thead><tr>${MONTHS.map(m=>`<th scope="col" class="r">${m}</th>`).join('')}</tr></thead><tbody><tr>${mf.map(f=>`<td class="r">${signed((f-1)*100,0)} %</td>`).join('')}</tr></tbody></table></div>`)}
  ${LEGEND}${nav('weather')}`;}
function pagePrices(){
  return`<h1>Prices</h1><p class="lede">What a kilowatt-hour and a litre cost.</p>
  ${sect('Electricity','',formHtml('pr',P.pr,['area','elPrice','level','tariff','spotFile']))}
  ${sect('Diesel','',formHtml('pr',P.pr,['dPrice'],['Other fuels and public charging']))}
  ${LEGEND}${nav('prices')}`;}
function pageCosts(){
  const seen={},vs=[];P.groups.forEach(g=>{const v=tpl('veh',g.veh);if(v&&!seen[v.id]){seen[v.id]=1;vs.push(v);}});
  return`<h1>Costs</h1><p class="lede">What the vehicles and the depot cost to buy and to keep.</p>
  ${sect('Vehicles',vs.length>1?'One table for each vehicle used in the fleet.':'',vs.map(v=>(vs.length>1?`<h3>${esc(v.name)}</h3>`:'')+matrix('veh',v,['Electric','Diesel'],[['Purchase price','DKK','priceEV','priceD'],['Service','DKK a month','svcEV','svcD'],['Insurance','DKK a month','insEV','insD']])).join(''))}
  ${sect('Financing','',formHtml('fin',P.fin,['years','how','interest','resid']))}
  ${sect('Drivers','The same on both sides, so it does not change the difference.',formHtml('fin',P.fin,['wage']))}
  ${sect('Depot','Chargers and trenching are priced by size from the COWI truck cost sheet.* The connection fee follows the grid company.',`<div class="pops"><button class="btn popb" data-info="bands" data-fk="bands">Charger price list</button><button class="btn popb" data-info="fees" data-fk="fees">Connection fees</button></div>`+formHtml('fin',P.fin,['depYears']))}
  ${LEGEND}${nav('costs')}`;}
function pageTax(){
  return`<h1>Taxes and CO₂</h1><p class="lede">Road tax, subsidies and the CO₂ behind a kilowatt-hour and a litre.</p>
  ${sect('Road tax','Danish road tax per km, by period.',matrix('tax',P.tax,['Electric','Diesel'],[['2026 to 2027','DKK per km','e1','d1'],['2028','DKK per km','e2','d2'],['From 2029','DKK per km','e3','d3']])+formHtml('tax',P.tax,['co2cls']))}
  ${sect('Subsidy','',formHtml('tax',P.tax,['subsidy','grant']))}
  ${sect('CO₂ from grid electricity','',formHtml('co2',P.co2,['gridMode','gridEF','hours']),1)}
  ${sect('CO₂ from diesel','',formHtml('co2',P.co2,['co2D']))}
  ${LEGEND}${nav('tax')}`;}
function openInfo(k){
  if(k==='bands')openDlg({fk:'bands',title:()=>'Charger price list',sub:()=>'Costs · COWI truck cost sheet, 2024 operator prices. Operator not named, verify before use',
    body:()=>tbl(['<Charger','Amperes','Hardware, DKK','Trenching, DKK'],BANDS.map(b=>[b[0]+' kW',b[3]!=null?b[3]:'',fmt(b[1]),fmt(b[2])]))});
  else openDlg({fk:'fees',title:()=>'Connection fees',sub:()=>'Costs · by grid company',
    body:()=>tbl(['<Grid company','First 25 A, DKK','Each ampere more, DKK','<Source'],Object.keys(FEE).map(k=>{const f=FEE[k];return[({radius:'Radius',cerius:'Cerius',n1:'N1',trefor:'TREFOR El-net',other:'Other'})[k]||k,f.base?fmt(f.base):'Enter it yourself',f.perA?fmt(f.perA,2):'',esc(f.ref||'')];}))});}
function srcTable(rows){
  let last='';return`<div class="tw"><table class="t"><thead><tr><th scope="col">Value</th><th scope="col">Used</th><th scope="col">Where it comes from</th></tr></thead><tbody>${rows.map(r=>{
    const hd=r.where!==last?`<tr><td colspan="3" style="font-weight:600;padding-top:18px">${esc(r.where)}</td></tr>`:'';last=r.where;
    return hd+`<tr><td>${esc(r.label)}</td><td>${esc(r.value)}</td><td class="mut">${r.radio?'Your choice':`<span>${SRCN[r.src]}</span>${r.ref?' · '+esc(r.ref):''}`}${r.used===false?' · '+NB:''}</td></tr>`;}).join('')}</tbody></table></div>`;}
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
    <tr><th scope="row">Not used yet</th><td class="r">${rows.filter(r=>r.used===false).length}</td><td class="mut">Kept with the project. The demo engine does not read them yet.</td></tr>
  </tbody></table></div>
  <details class="more"><summary>Show every value and its source</summary>${srcTable(rows)}</details>
  ${nav('check')}`;}
