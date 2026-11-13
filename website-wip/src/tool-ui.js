/* ================= state and navigation ================= */
const S = { tab:'fleet', runs:[], R:null, runSnap:null, cmpA:null, cmpB:null, gi:0, ai:false };
const NAV = [ ['setup','Setup',['fleet','depot','assume','check']], ['results','Results',['ov','en','ch','co','src']], ['compare','Compare',['compare']], ['docs','Documents',['docs']] ];
const TITLE = { fleet:'Fleet', depot:'Depot', assume:'Assumptions', check:'Check and run', ov:'Overview', en:'Energy and battery', ch:'Charging and grid', co:'Cost and CO₂', src:'Inputs and sources' };
const IC = {
  setup:'<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
  results:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>', compare:'<path d="M7 4v16M17 4v16M3 8h8M13 16h8"/>',
  docs:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
  ok:'<path d="m5 12 4.5 4.5L19 7"/>', no:'<path d="M6 6l12 12M18 6 6 18"/>', x:'<path d="M6 6l12 12M18 6 6 18"/>', play:'<path d="M7 5v14l11-7z" fill="currentColor" stroke="none"/>', up:'<path d="M12 19V5M5 12l7-7 7 7"/>' };
const ico = (k,sz=16,sw=1.8) => `<svg viewBox="0 0 24 24" width="${sz}" height="${sz}" fill="none" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[k]}</svg>`;
const mark = (ok,txt) => `<span class="mark ${ok?'ok':'no'}">${ico(ok?'ok':'no',15,2.4)}${txt||''}</span>`;
const mainOf = t => NAV.find(n => n[2].includes(t))[0];
const dirty = () => !!S.R && snapshot()!==S.runSnap;
function go(tab){ if(mainOf(tab)!=='setup' && !S.R) return; S.tab=tab; render(); const pg=$('page'); pg.scrollTop=0; pg.focus({preventScroll:true}); }
function drawNav(){
  const cur=mainOf(S.tab), miss=missing();
  $('nmain').innerHTML = NAV.map(n => { const lock=n[0]!=='setup' && !S.R;
    return `<button class="mtab" data-main="${n[0]}"${cur===n[0]?' aria-current="page"':''}${lock?' disabled title="Run the project first"':''}>${ico(n[0])}<span>${n[1]}</span></button>`; }).join('');
  const subs = NAV.find(n => n[0]===cur)[2];
  $('nsub').innerHTML = subs.length>1 ? subs.map(t => { const n = t==='check' ? miss.length : t==='fleet' ? miss.filter(m=>m.open[0]!=='page'&&m.open[0]!=='set').length : t==='depot' ? miss.filter(m=>m.open[0]==='page').length : t==='assume' ? miss.filter(m=>m.open[0]==='set').length : 0;
    return `<button class="stab" data-tab="${t}"${S.tab===t?' aria-current="page"':''}>${TITLE[t]}${n&&cur==='setup'?`<span class="need">${n} needed</span>`:''}</button>`; }).join('') : '';
  const rs=$('runState'), d=dirty(); rs.className='rstate'+(miss.length||d?' warn':'');
  rs.textContent = miss.length ? miss.length+' value'+(miss.length>1?'s':'')+' needed before you can run' : !S.R ? 'Ready to run' : d ? 'Inputs changed since run '+S.runs.length : 'Run '+S.runs.length+' is up to date';
  $('bRun').disabled = !!miss.length;
}
const PAGES = {};
function render(){ const w=$('content'); w.innerHTML = PAGES[S.tab](); drawNav(); if(PAGES[S.tab].after) PAGES[S.tab].after(); }
function toast(msg){ const d=document.createElement('div'); d.className='toast'; d.setAttribute('role','status'); d.textContent=msg; document.body.appendChild(d); setTimeout(()=>d.remove(),2200); }

/* ================= fields ================= */
const REG = {}; let rid=0;
function reg(o,key){ const id='o'+(++rid); REG[id]={o,key}; return id; }
function srcHtml(f,o,oid){ const s=srcOf(f,o);
  if(s==='need') return `<span class="need">Needed</span>${f.r?' · '+esc(f.r):''}`;
  if(s==='you') return `<span class="you">Your value</span>${o._d&&o._d[f.k]!==undefined&&o._d[f.k]!==''?`<button class="lnk" data-reset="${oid}|${f.k}">Reset to ${esc(showVal(f,o._d))}</button>`:''}`;
  return `<b>${SRC[s]}</b>${f.r?' · '+esc(f.r):''}`; }
function fieldHtml(f,o,oid){
  const id=oid+'_'+f.k, v=o[f.k]==null?'':o[f.k];
  if(f.t==='radio') return `<fieldset class="choice block"><legend>${f.l}</legend>${f.o.map(q => `<label class="opt${String(v)===q[0]?' on':''}${q[3]?' off':''}"><input type="radio" name="${id}" value="${q[0]}" data-o="${oid}" data-k="${f.k}"${String(v)===q[0]?' checked':''}${q[3]?' disabled':''}><span><b>${q[1]}</b>${q[2]?`<small>${q[2]}</small>`:''}</span></label>`).join('')}</fieldset>`;
  let c;
  if(f.t==='sel') c=`<select class="in" id="${id}" data-o="${oid}" data-k="${f.k}">${f.o.map(q => `<option value="${q[0]}"${String(v)===q[0]?' selected':''}>${q[1]}</option>`).join('')}</select>`;
  else c=`<input class="in${f.t==='num'?' n':''}${isMissing(f,o)?' miss':''}" id="${id}" data-o="${oid}" data-k="${f.k}" data-t="${f.t}" ${f.t==='time'?'type="time"':f.t==='num'?'inputmode="decimal" autocomplete="off"':'autocomplete="off"'} value="${esc(v)}"${isMissing(f,o)?' aria-invalid="true"':''}>`;
  return `<div class="fr"><label for="${id}">${f.l}</label><div class="fc">${c}${f.u?`<span class="u">${f.u}</span>`:''}</div><div class="fsrc" id="${id}_s">${srcHtml(f,o,oid)}</div></div>`;
}
/* main fields, then one named fold-out per group of rarely changed values */
function formHtml(key,o,openSecs){ const oid=reg(o,key), fs=fieldsOf(key,o), secs=[]; fs.forEach(f => { if(f.sec && !secs.includes(f.sec)) secs.push(f.sec); });
  let h=fs.filter(f=>!f.sec).map(f=>fieldHtml(f,o,oid)).join('');
  secs.forEach(sn => { const ff=fs.filter(f=>f.sec===sn), mine=ff.filter(f=>srcOf(f,o)==='you').length, need=ff.filter(f=>isMissing(f,o)).length;
    h+=`<details class="more" data-sec="${esc(sn)}"${need||(openSecs&&openSecs.includes(sn))?' open':''}><summary>${sn} <small>${ff.length} value${ff.length>1?'s':''}${need?', '+need+' needed':mine?', '+mine+' yours':', standard unless you change them'}</small></summary><div>${ff.map(f=>fieldHtml(f,o,oid)).join('')}</div></details>`; });
  const ft=DEFS[key].foot; if(ft) h+=`<p class="note">${typeof ft==='function'?ft(o):ft}</p>`;
  return h; }
function parseIn(el){ const t=el.dataset.t, v=el.value.trim(); if(t==='num'){ if(v==='') return ''; const x=+v.replace(/\s/g,'').replace(',','.'); return isNaN(x)?v:x; } return v; }
function applyEdit(el){ const r=REG[el.dataset.o]; if(!r) return null; const o=r.o, k=el.dataset.k, f=fieldsOf(r.key,o).find(x=>x.k===k)||DEFS[r.key].fields.find(x=>x.k===k);
  o[k] = el.type==='radio'||el.tagName==='SELECT' ? el.value : parseIn(el);
  if(r.key==='veh'&&k==='cls'&&o.cdxa===o._d.cdxa){ o.cdxa=o._d.cdxa=CLS[o.cls][1]; }
  if(r.key==='rt'&&k==='road'&&o.speed===o._d.speed){ o.speed=o._d.speed=ROAD[o.road][1]; }
  return {r,o,k,f}; }
document.addEventListener('input', e => { const el=e.target; if(!el.dataset||!el.dataset.o||el.type==='radio'||el.tagName==='SELECT') return;
  const x=applyEdit(el); if(!x) return; const bad=isMissing(x.f,x.o); el.classList.toggle('miss',bad); el.toggleAttribute('aria-invalid',bad);
  const s=$(el.id+'_s'); if(s) s.innerHTML=srcHtml(x.f,x.o,el.dataset.o); drawNav(); });
document.addEventListener('change', e => { const el=e.target; if(!el.dataset) return;
  if(el.dataset.o && (el.type==='radio'||el.tagName==='SELECT')){ applyEdit(el); refresh(el); return; }
  if(el.dataset.g){ const g=P.groups.find(x=>x.id===+el.dataset.g); if(el.dataset.gk==='n'){ const n=parseInt(el.value,10); g.n = n>0?Math.min(500,n):''; el.classList.toggle('miss',!g.n); } else g.name=el.value; drawNav(); return; }
  if(el.id==='tplPick'){ const g=P.groups.find(x=>x.id===DLG.gid); g[DLG.lib]=el.value; refresh(el); return; }
  if(el.id==='tplName'){ tpl(DLG.lib, P.groups.find(x=>x.id===DLG.gid)[DLG.lib]).name=el.value.trim()||'Untitled'; return; }
  if(el.id==='cmpA'||el.id==='cmpB'){ S[el.id]=+el.value; render(); } });
function refresh(el){ const keep=el&&el.id, open=[...document.querySelectorAll('details.more[open]')].map(d=>d.dataset.sec);
  if(DLG) drawDlg(open); else { render(); } const n=keep&&$(keep); if(n) n.focus(); else if(el&&el.name){ const c=document.querySelector(`input[name="${el.name}"]:checked`); if(c) c.focus(); } drawNav(); }

/* ================= dialogs ================= */
let DLG=null, lastFocus=null;
function openDlg(d){ lastFocus=document.activeElement&&document.activeElement.dataset?document.activeElement.dataset.focus:null; DLG=d;
  const m=document.createElement('div'); m.className='modal'; m.id='modal'; m.innerHTML='<div class="dlg" role="dialog" aria-modal="true" aria-labelledby="dlgT"></div>'; document.body.appendChild(m); drawDlg();
  const f=m.querySelector('.dbody input:not([type=radio]),.dbody select,.dbody input:checked'); (f||m.querySelector('.x')).focus(); }
function drawDlg(openSecs){ const d=DLG, box=document.querySelector('#modal .dlg'), sc=box.querySelector('.dbody'), top=sc?sc.scrollTop:0;
  box.innerHTML=`<header><div><h2 id="dlgT">${d.title()}</h2><p class="dsub">${d.sub()}</p></div><button class="x" data-close aria-label="Close">${ico('x',16,2)}</button></header><div class="dbody">${d.body(openSecs)}</div><footer>${d.foot?d.foot():''}<span class="sp"></span><button class="btn pri" data-close>Done</button></footer>`;
  box.querySelector('.dbody').scrollTop=top; }
function closeDlg(){ const m=$('modal'); if(!m) return; m.remove(); DLG=null; render(); const b=lastFocus&&document.querySelector(`[data-focus="${lastFocus}"]`); if(b) b.focus(); }
document.addEventListener('keydown', e => { if(!DLG) return;
  if(e.key==='Escape'){ e.preventDefault(); closeDlg(); return; }
  if(e.key==='Tab'){ const f=[...document.querySelectorAll('#modal button:not([disabled]),#modal input:not([disabled]),#modal select,#modal summary,#modal a[href]')].filter(x=>x.offsetParent!==null); if(!f.length) return;
    const a=f[0], z=f[f.length-1]; if(e.shiftKey&&document.activeElement===a){ e.preventDefault(); z.focus(); } else if(!e.shiftKey&&document.activeElement===z){ e.preventDefault(); a.focus(); } } });
/* one popup per part of a group: pick a saved one, or change it */
function openTpl(lib,gid){ const D=DEFS[lib], g=()=>P.groups.find(x=>x.id===gid), t=()=>tpl(lib,g()[lib]);
  openDlg({ lib, gid, title:()=>D.title, sub:()=>D.sub,
    body:(open)=>{ const cur=t(), others=cur?P.groups.filter(x=>x.id!==gid&&x[lib]===cur.id):[];
      let h=`<div class="pick"><label for="tplPick">Saved ${D.many}</label><select class="in" id="tplPick">${cur?'':'<option value="">Choose…</option>'}${P.lib[lib].map(x=>`<option value="${x.id}"${cur&&x.id===cur.id?' selected':''}>${esc(x.name)}</option>`).join('')}</select><button class="lnk" data-tnew="blank">New</button>${cur?'<button class="lnk" data-tnew="copy">Copy this one</button>':''}</div>`;
      if(!cur) return h+`<p class="hint">Pick a saved ${D.one} for ${esc(g().name)}, or make a new one.</p>`;
      if(others.length) h+=`<p class="shared">Also used by ${others.map(x=>esc(x.name)).join(', ')}. Changes here apply there too. Use “Copy this one” to change it for ${esc(g().name)} only.</p>`;
      h+=`<div class="fr"><label for="tplName">Name</label><div class="fc"><input class="in" id="tplName" value="${esc(cur.name)}" autocomplete="off"></div><div class="fsrc"></div></div>`;
      return h+formHtml(lib,cur,open); },
    foot:()=>{ const cur=t(); return cur&&P.lib[lib].length>1&&!P.groups.some(x=>x[lib]===cur.id&&x.id!==gid)?'<button class="lnk q" data-tdel>Delete this '+D.one+'</button>':''; } }); }
function openSet(k){ const D=DEFS[k]; openDlg({ title:()=>D.title, sub:()=>'Filled in with standard and sample values. Change only what you know better.', body:(open)=>formHtml(k,P[k],open) }); }

/* ================= setup pages ================= */
const pnav = (prev,next,run) => `<div class="pnav">${prev?`<button class="btn" data-tab="${prev}">Back: ${TITLE[prev]}</button>`:'<span></span>'}${next?`<button class="btn pri" data-tab="${next}">Next: ${TITLE[next]}</button>`:''}</div>`;
PAGES.fleet = () => { const nV=sum(P.groups.map(g=>+g.n||0));
  const cell=(g,lib)=>{ const t=tpl(lib,g[lib]), need=!t||fieldsOf(lib,t).some(f=>isMissing(f,t));
    return `<td data-l="${DEFS[lib].title}"><button class="cell${need?' need':''}" data-tpl="${lib}|${g.id}" data-focus="${lib}${g.id}"><b>${t?esc(t.name):'Choose…'}</b><small>${t?(need?'Values needed':esc(DEFS[lib].sum(t))):'Not set'}</small></button></td>`; };
  return `<h1>Fleet</h1><p class="lede">One row for each group of identical vehicles that do the same round. Click any blue name to see or change what is behind it.</p>
  <div class="tw" style="margin-top:22px"><table class="t fleet"><thead><tr><th>Group</th><th>Vehicles</th>${LIBS.map(l=>`<th>${DEFS[l].title}</th>`).join('')}<th><span class="sr">Actions</span></th></tr></thead><tbody>
  ${P.groups.map(g=>`<tr><td data-l="Group"><input class="in nm" aria-label="Group name" data-g="${g.id}" data-gk="name" value="${esc(g.name)}"></td><td data-l="Vehicles"><input class="in n ct${g.n?'':' miss'}" aria-label="Number of vehicles in ${esc(g.name)}" inputmode="numeric" data-g="${g.id}" data-gk="n" value="${g.n}"></td>${LIBS.map(l=>cell(g,l)).join('')}<td class="rowact"><button class="lnk" data-gdup="${g.id}">Copy</button>${P.groups.length>1?`<button class="lnk q" data-gdel="${g.id}" aria-label="Remove ${esc(g.name)}">Remove</button>`:''}</td></tr>`).join('')}
  </tbody></table></div>
  <div class="addrow"><button class="btn" id="addGroup">Add a group</button></div>
  <p class="note">${nV} vehicle${nV===1?'':'s'} in ${P.groups.length} group${P.groups.length===1?'':'s'}. A saved vehicle, route, load, equipment or shift can be reused in several groups.</p>${pnav(null,'depot')}`; };
PAGES.depot = () => { const d=P.depot, oid=reg(d,'depot'), F1=k=>{ const f=fieldsOf('depot',d).find(x=>x.k===k); return f?fieldHtml(f,d,oid):''; };
  const secs=formHtml('depot',{...d,_only:1}).match(/<details[\s\S]*<\/details>/); /* fold-out rebuilt below against the live object */
  const adv=fieldsOf('depot',d).filter(f=>f.sec), mine=adv.filter(f=>srcOf(f,d)==='you').length;
  return `<h1>Depot</h1><p class="lede">Where the vehicles park and charge, and what the grid connection can give.</p>
  <div class="block"><h2>Site</h2>${F1('name')}${F1('addr')}</div>
  ${F1('mode')}<div class="sub2">${F1('limit')}${F1('dso')}${F1('base')}</div>
  ${F1('chg')}<div class="sub2">${F1('kw')}</div>
  ${F1('plan')}
  <details class="more" data-sec="Charger behaviour"${adv.some(f=>isMissing(f,d))?' open':''}><summary>Charger behaviour <small>${adv.length} values${mine?', '+mine+' yours':', standard unless you change them'}</small></summary><div>${adv.map(f=>fieldHtml(f,d,oid)).join('')}</div></details>
  ${pnav('fleet','assume')}`; };
PAGES.assume = () => `<h1>Assumptions</h1><p class="lede">Everything here is already filled in with standard or sample values, so you can run straight away. Change only what you know better.</p>
  <div class="sets">${SETS.map(k=>{ const o=P[k], fs=fieldsOf(k,o), c={std:0,sample:0,assume:0,you:0,need:0}; fs.forEach(f=>c[srcOf(f,o)]++);
    const mix=['need','you','std','assume','sample'].filter(x=>c[x]).map(x=>c[x]+' '+({need:'needed',you:'yours',std:'standard',assume:'assumed',sample:'sample'})[x]).join(', ');
    return `<div class="set"><h3>${DEFS[k].title}</h3><p>${esc(DEFS[k].sum(o,P))}<small>${mix}</small></p><button class="btn" data-set="${k}" data-focus="set${k}">Change</button></div>`; }).join('')}</div>${pnav('depot','check')}`;
PAGES.check = () => { const all=allInputs(), miss=all.filter(x=>isMissing(x.f,x.o)), c={std:0,sample:0,assume:0,you:0};
  all.forEach(x=>{ const s=srcOf(x.f,x.o); if(c[s]!=null) c[s]++; });
  const samp=all.filter(x=>srcOf(x.f,x.o)==='sample'), d=dirty();
  let h=`<h1 class="h1mark">${mark(!miss.length)}<span>${miss.length?miss.length+' value'+(miss.length>1?'s are':' is')+' needed before you can run':'Ready to run'}</span></h1>`;
  if(miss.length) h+=`<ul class="todo">${miss.map((x,i)=>`<li><button class="lnk" data-open="${i}">${esc(x.where)}: ${esc(x.f.l)}</button></li>`).join('')}</ul>`;
  else h+=`<p class="lede">${all.length} values go into this run. ${c.you} are yours, ${c.std} are standard values, ${c.assume} are assumptions and ${c.sample} are sample values.</p>`;
  h+=`<div class="runrow"><button class="btn pri big" data-run${miss.length?' disabled':''}>${ico('play',13)}${S.R&&!d?'Run again':'Run the project'}</button><span class="mut">${S.R?(d?'Inputs have changed since run '+S.runs.length+'.':'Run '+S.runs.length+' is up to date.'):'A full year for every group, the depot and the costs.'}</span></div>`;
  if(samp.length&&!miss.length) h+=`<h2>Sample values to replace with your own</h2><p class="hint">The result is only as good as these. Each one opens where it is set.</p>
    <div class="tw"><table class="t"><thead><tr><th>Where</th><th>Value</th><th class="r">Now</th><th>Note</th></tr></thead><tbody>${all.map((x,i)=>srcOf(x.f,x.o)==='sample'?`<tr><td>${esc(x.where)}</td><td><button class="lnk" data-open="${i}">${esc(x.f.l)}</button></td><td class="r">${esc(showVal(x.f,x.o))}</td><td class="mut">${esc(x.f.r||'')}</td></tr>`:'').join('')}</tbody></table></div>`;
  S.openList=all; return h+pnav('assume',null); };
function openInput(x){ const o=x.open; if(o[0]==='tpl') openTpl(o[1],o[2]); else if(o[0]==='set') openSet(o[1]); else if(o[0]==='page') go('depot'); else go('fleet'); }

/* ================= run ================= */
function run(then){ if(missing().length){ go('check'); return; }
  const pr=$('prog'), pg=$('page'); let p=0; pg.classList.add('busy'); $('bRun').disabled=true;
  const t=setInterval(()=>{ p+=25; pr.style.width=p+'%'; if(p<100) return; clearInterval(t); setTimeout(()=>{ pr.style.width='0'; },200);
    S.R=compute(P); S.runSnap=snapshot(); const now=new Date();
    S.runs.push({n:S.runs.length+1, t:String(now.getHours()).padStart(2,'0')+':'+String(now.getMinutes()).padStart(2,'0'), R:S.R, flat:flat()});
    S.cmpB=S.runs.length; S.cmpA=Math.max(1,S.runs.length-1); pg.classList.remove('busy'); $('live').textContent='Run '+S.runs.length+' finished. '+S.R.title+'.';
    if(then) then(); else go(mainOf(S.tab)==='setup'?'ov':S.tab); },60); }
const flat = () => { const o={}; allInputs().forEach(x => { o[x.where+' · '+x.f.l]=showVal(x.f,x.o); }); o['Depot · Charging plan']=PLAN[P.depot.plan][0]; o['Depot · Chargers']=P.depot.chg==='auto'?'Sized by the tool':'Chosen'; o['Depot · Grid connection known']=P.depot.mode==='existing'?'Yes':'No'; return o; };

/* ================= clicks ================= */
document.addEventListener('click', e => { const t=e.target, c=s=>t.closest(s); let el;
  if((el=c('[data-close]'))||(t.id==='modal')){ closeDlg(); return; }
  if((el=c('[data-main]'))){ if(!el.disabled){ const n=NAV.find(x=>x[0]===el.dataset.main); go(n[0]==='results'&&S.lastRes?S.lastRes:n[2][0]); } return; }
  if((el=c('[data-tab]'))){ go(el.dataset.tab); return; }
  if((el=c('[data-run]'))||c('#bRun')){ run(); return; }
  if((el=c('[data-tpl]'))){ const a=el.dataset.tpl.split('|'); openTpl(a[0],+a[1]); return; }
  if((el=c('[data-set]'))){ openSet(el.dataset.set); return; }
  if((el=c('[data-open]'))){ openInput(S.openList[+el.dataset.open]); return; }
  if((el=c('[data-reset]'))){ const a=el.dataset.reset.split('|'), r=REG[a[0]]; r.o[a[1]]=r.o._d[a[1]]; refresh(); return; }
  if((el=c('[data-tnew]'))){ const lib=DLG.lib, g=P.groups.find(x=>x.id===DLG.gid), cur=tpl(lib,g[lib]), id=lib+(P.nid++);
    const n = el.dataset.tnew==='copy'&&cur ? Object.assign(clone(cur),{id,name:cur.name+' (copy)'}) : mk(lib,id,'New '+DEFS[lib].one,{});
    P.lib[lib].push(n); g[lib]=id; drawDlg(); const nm=$('tplName'); if(nm){ nm.focus(); nm.select(); } drawNav(); return; }
  if(c('[data-tdel]')){ const lib=DLG.lib, g=P.groups.find(x=>x.id===DLG.gid), i=P.lib[lib].findIndex(x=>x.id===g[lib]); P.lib[lib].splice(i,1); g[lib]=P.lib[lib][0].id; drawDlg(); drawNav(); return; }
  if(c('#addGroup')){ const l=P.groups[P.groups.length-1]; P.groups.push({id:P.nid++,name:'New group',n:1,veh:l.veh,rt:'',load:'',eq:(P.lib.eq.find(x=>x.type==='none')||{}).id||'',sch:''}); render(); const r=document.querySelectorAll('.fleet .nm'); r[r.length-1].focus(); r[r.length-1].select(); return; }
  if((el=c('[data-gdup]'))){ const g=P.groups.find(x=>x.id===+el.dataset.gdup); P.groups.splice(P.groups.indexOf(g)+1,0,Object.assign({},g,{id:P.nid++,name:g.name+' (copy)'})); render(); return; }
  if((el=c('[data-gdel]'))){ P.groups=P.groups.filter(x=>x.id!==+el.dataset.gdel); render(); toast('Group removed'); return; }
  if((el=c('[data-gi]'))){ S.gi=+el.dataset.gi; render(); return; }
  if((el=c('[data-plan]'))){ P.depot.plan=el.dataset.plan; run(()=>{ go('ch'); toast('Now charging with: '+PLAN[P.depot.plan][0]); }); return; }
  if((el=c('[data-try]'))){ TRY[+el.dataset.try][1](); run(()=>go('compare')); return; }
  if((el=c('[data-doc]'))){ openDoc(el.dataset.doc); return; }
  if(c('[data-csv]')){ csv(); return; }
  if(c('#bAi')||c('#aiClose')){ S.ai=!S.ai; $('ai').hidden=!S.ai; $('bAi').setAttribute('aria-pressed',String(S.ai)); if(S.ai){ drawQs(); $('prompt').focus(); } else $('bAi').focus(); return; }
  if((el=c('[data-q]'))){ ask(el.dataset.q); return; }
  if(c('#bExit')||c('.brand.go')){ e.preventDefault(); parent.postMessage({evs:'exit'},'*'); return; }
  if(c('.skip')){ e.preventDefault(); $('page').focus(); }
});
document.addEventListener('keydown', e => { if((e.ctrlKey||e.metaKey)&&e.key==='Enter'&&!DLG){ e.preventDefault(); run(); } });
