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
const MAIN=[['setup','Setup',['fleet','depot','assume','check']],['results','Results',['ov','en','ch','cost','src']],['cmp','Compare',['cmp']],['docs','Documents',['docs']]];
const TITLE={fleet:'Fleet',depot:'Depot',assume:'Assumptions',check:'Check and run',ov:'Overview',en:'Energy and battery',ch:'Charging and grid',cost:'Cost and CO₂',src:'Inputs and sources'};
const mainOf=t=>MAIN.find(m=>m[2].includes(t))[0];
const dirty=()=>S.snap!==null&&S.snap!==snapshot();
function drawNav(){
  const cur=mainOf(S.tab),miss=missing();
  $('nmain').innerHTML=MAIN.map(m=>`<button class="mtab" data-main="${m[0]}"${cur===m[0]?' aria-current="page"':''}${m[0]!=='setup'&&!S.run?' disabled title="Run the sample first"':''}>${ico(m[0],16)}<span>${m[1]}</span></button>`).join('');
  const subs=MAIN.find(m=>m[0]===cur)[2];
  $('nsub').innerHTML=subs.length>1?subs.map(t=>{
    const flag=(t==='fleet'&&miss.some(x=>x.open.lib||x.open.page==='fleet'))||(t==='depot'&&miss.some(x=>x.open.page==='depot'))||(t==='assume'&&miss.some(x=>x.open.set))||(S.run&&cur==='results'&&S.run.checks.some(c=>!c.ok&&c.go===t));
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
function srcHtml(f,o){
  if(f.t==='radio')return'';const s=srcOf(f,o),d=o._d?o._d[f.k]:undefined;
  let h=`<b class="${s==='you'?'you':s==='need'?'need':''}">${SRCN[s]}</b>`;
  if(s!=='you'&&s!=='need'&&f.r)h+=' · '+esc(f.r);
  if(s==='you'&&d!==undefined&&d!==''&&f.t!=='sel')h+=`<button class="lnk" data-reset="${f.k}">Reset to ${esc(typeof d==='number'?fmt(d,f.dec||0):d)}</button>`;
  return h;}
function fieldHtml(f,o,oid){
  const id='f'+oid+'_'+f.k,v=o[f.k],lab=labelOf(f,o),at=`id="${id}" data-o="${oid}" data-k="${f.k}"`;
  if(f.t==='radio')return`<fieldset class="choice"><legend>${lab}</legend>${f.o.map(q=>q[3]
    ?`<div class="opt off"><input type="radio" disabled aria-label="${esc(q[1])}"><span><b>${q[1]}</b><small>${q[2]}</small></span></div>`
    :`<label class="opt"><input type="radio" name="${id}" value="${q[0]}" data-o="${oid}" data-k="${f.k}"${v===q[0]?' checked':''}><span><b>${q[1]}</b>${q[2]?`<small>${q[2]}</small>`:''}</span></label>`).join('')}</fieldset>`;
  let c;const miss=isMissing(f,o);
  if(f.t==='info')c=`<span>${esc(f.v(o))}</span>`;
  else if(f.t==='sel')c=`<select class="in" ${at}>${f.o.map(q=>`<option value="${q[0]}"${String(v)===String(q[0])?' selected':''}>${q[1]}</option>`).join('')}</select>`;
  else c=`<input class="in${f.t==='num'?' n':''}${miss?' miss':''}" ${at} ${f.t==='num'?'inputmode="decimal"':f.t==='time'?'type="time"':''} value="${esc(v==null?'':v)}"${miss?' aria-invalid="true"':''} aria-describedby="s${id}">${f.u?`<span class="u">${f.u}</span>`:''}`;
  return`<div class="fr">${f.t==='info'?`<span>${lab}</span>`:`<label for="${id}">${lab}</label>`}<div class="fc">${c}</div><div class="fsrc" id="s${id}">${srcHtml(f,o)}</div></div>`;}
function formHtml(type,o,keys){
  const oid=reg(type,o);let fs=visible(type,o);if(keys)fs=fs.filter(f=>keys.includes(f.k));
  const secs=[...new Set(fs.filter(f=>f.sec).map(f=>f.sec))];
  return fs.filter(f=>!f.sec).map(f=>fieldHtml(f,o,oid)).join('')+secs.map(sn=>{
    const ff=fs.filter(f=>f.sec===sn),ed=ff.filter(f=>srcOf(f,o)==='you').length,ms=ff.filter(f=>isMissing(f,o)).length;
    return`<details class="fold" data-sec="${esc(sn)}"${OPEN.has(sn)||ms?' open':''}><summary>${sn}<small>${plural(ff.length,'value')}${ed?', '+ed+' changed':''}${ms?', '+ms+' needed':''}</small></summary><div>${ff.map(f=>fieldHtml(f,o,oid)).join('')}</div></details>`;}).join('');}
function setVal(oid,k,raw){
  const {type,o}=REG[oid],f=DEFS[type].fields.find(x=>x.k===k);let v=raw;
  if(f.t==='num'){const x=parseFloat(String(raw).replace(/\s/g,'').replace(',','.'));v=String(raw).trim()===''||isNaN(x)?'':x;}
  o[k]=v;
  if(type==='veh'&&k==='cls'){const c=CLS.find(q=>q[0]===o.cls)[2];if(o.cdxa===o._d.cdxa||o.cdxa==='')o.cdxa=c;o._d.cdxa=c;}
  if(type==='rt'&&k==='road'){const sp=ROAD_V[o.road];if(o.speed===o._d.speed||o.speed==='')o.speed=sp;o._d.speed=sp;}
  return f;}
function mix(type,o){const c={};visible(type,o).forEach(f=>{if(f.t==='radio'||f.t==='info')return;const s=srcOf(f,o);c[s]=(c[s]||0)+1;});
  return['need','you','std','sample','assume'].filter(s=>c[s]).map(s=>c[s]+' '+({need:'needed',you:'your own',std:'standard',sample:'sample',assume:'assumed'})[s]).join(', ');}

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
  $('dlgF').innerHTML=(c.foot?c.foot():'')+'<span class="sp"></span><button class="btn pri" data-close>Done</button>';
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
      h+=`<div class="fr"><label for="tplName">Name</label><div class="fc"><input class="in" id="tplName" data-name="${oid}" value="${esc(t.name)}"></div><div class="fsrc"></div></div>`;
      return h+formHtml(lib,t);},
    lib,gid});}
function openSet(k){openDlg({fk:'set-'+k,title:()=>DEFS[k].title,sub:()=>k==='wx'?'Location: '+(P.depot.addr||'not set')+'. Change it on the Depot page.':'Standard and sample values are filled in. Change what you know better.',body:()=>formHtml(k,P[k])});}
function openAt(o){if(o.lib)openTpl(o.lib,o.gid);else if(o.set)openSet(o.set);else go(o.page);}

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
  return`<h1>Fleet</h1><p class="lede">One row for each group of identical vehicles doing the same day. Select any blue name to see or change what is behind it.</p>
  <div class="tw" style="margin-top:22px"><table class="t fleet"><thead><tr><th scope="col">Group</th><th scope="col">Vehicles</th><th scope="col">Vehicle</th><th scope="col">Route</th><th scope="col">Load</th><th scope="col">Body equipment</th><th scope="col">Shift</th><th scope="col"><span class="sr">Actions</span></th></tr></thead><tbody>
  ${P.groups.map(g=>`<tr><td data-l="Group"><input class="in gname" data-g="name|${g.id}" value="${esc(g.name)}" aria-label="Group name"></td>
    <td data-l="Vehicles"><input class="in n cnt${g.n>=1?'':' miss'}" data-g="n|${g.id}" inputmode="numeric" value="${g.n}" aria-label="Number of vehicles in ${esc(g.name)}"></td>
    ${LIBS.map(l=>cell(g,l)).join('')}
    <td class="rowact" data-l=""><span><button class="lnk" data-gdup="${g.id}">Copy</button><button class="lnk" data-gdel="${g.id}"${P.groups.length<2?' hidden':''}>Remove</button></span></td></tr>`).join('')}
  </tbody></table></div>
  <p style="margin-top:14px"><button class="lnk" data-gadd>Add a group</button><span class="mut" id="fleetTot" style="margin-left:18px">${plural(tot,'vehicle')} in ${plural(P.groups.length,'group')}</span></p>
  <div class="nextrow"><span></span><button class="btn" data-tab="depot">Next: Depot</button></div>`;}
function pageDepot(){
  const D=P.depot,sec=(t,note,keys)=>`<section class="sect"><h2>${t}</h2>${note?`<p class="note">${note}</p>`:''}${formHtml('depot',D,keys)}</section>`;
  return`<h1>Depot</h1><p class="lede">Where the vehicles park and charge, and what the grid connection allows.</p>
  ${sec('Site','',['name','addr'])}
  ${sec('Grid connection','',['mode','limit','dso','base'])}
  ${sec('Chargers and charging','One charger for each vehicle in this demo.',['chgMode','kw','plan','loadF','loss'])}
  <div class="nextrow"><button class="btn" data-tab="fleet">Back: Fleet</button><button class="btn" data-tab="assume">Next: Assumptions</button></div>`;}
const SETSUM={
  wx:()=>(P.depot.addr||'Location not set')+'. '+(P.wx.year==='cold'?'Sized for a cold winter.':'Sized for a normal year.'),
  pr:()=>'Electricity '+(P.pr.elPrice===''?'?':fmt(P.pr.elPrice,2))+' DKK/kWh at the '+({low:'low',exp:'expected',high:'high'})[P.pr.level]+' level. Diesel '+(P.pr.dPrice===''?'?':fmt(P.pr.dPrice,2))+' DKK/l.',
  fin:()=>P.fin.years+' years of ownership at '+(P.fin.interest===''?'?':fmt(P.fin.interest,2))+' % interest.',
  tax:()=>'Danish road tax per km. '+(P.tax.grant?'Grant of '+fmt(P.tax.grant)+' DKK.':'No grant applied.'),
  co2:()=>(P.co2.gridMode==='path'?'Grid electricity follows the Danish Energy Agency projection.':'Grid electricity at '+(P.co2.gridEF===''?'?':fmt(P.co2.gridEF,2))+' g/kWh.')+' Diesel '+(P.co2.co2D===''?'?':fmt(P.co2.co2D,2))+' kg/l.'};
function pageAssume(){
  return`<h1>Assumptions</h1><p class="lede">These are already filled in with standard and sample values. Change only what you know better.</p>
  <div style="margin-top:18px">${SETS.map(k=>`<div class="setrow"><b>${DEFS[k].title}</b><span>${esc(SETSUM[k]())}${mix(k,P[k])?`<small>${mix(k,P[k])}</small>`:''}</span><button class="btn" data-set="${k}" data-fk="set-${k}">Change</button></div>`).join('')}</div>
  <div class="nextrow"><button class="btn" data-tab="depot">Back: Depot</button><button class="btn" data-tab="check">Next: Check and run</button></div>`;}
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
  <div class="nextrow"><button class="btn" data-tab="assume">Back: Assumptions</button><span></span></div>`;}
