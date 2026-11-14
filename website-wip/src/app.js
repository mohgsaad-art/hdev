/* ---------- assistant: fixed questions, answered from the current run ---------- */
const QA=[
  ['What happens in a cold winter?',/winter|cold|frost|snow/,R=>{const keep=P.wx.year;P.wx.year='cold';const C=compute();P.wx.year=keep;const a=Math.max(...R.G.map(g=>g.worst)),b=Math.max(...C.G.map(g=>g.worst));
    return keep==='cold'?'This run is already sized for a cold winter. The hardest day is <b>'+fmt(a)+' kWh</b> for one vehicle.':'In a cold winter the hardest day goes from <b>'+fmt(a)+'</b> to <b>'+fmt(b)+' kWh</b> for one vehicle. '+(C.feasible?'Every check still passes'+(C.G.some((g,i)=>g.batt!==R.G[i].batt)?', with a battery of '+fmt(Math.max(...C.G.map(g=>g.batt)))+' kWh.':'.'):'Then this fails: '+C.checks.find(c=>!c.ok).t.toLowerCase()+'.')+' Change it under Setup, Weather to run it.';}],
  ['Will the vehicles make it through the day?',/day|range|make it|batter|far|last/,R=>{const g=R.G.reduce((a,b)=>b.worst/b.usableEol>a.worst/a.usableEol?b:a);
    return(R.checks[0].ok&&R.checks[1].ok?'Yes. ':'Not all of them. ')+'The tightest group is “'+esc(g.name)+'”: <b>'+fmt(g.worst)+' kWh</b> on the hardest day against <b>'+fmt(g.usableEol)+' kWh</b> usable at year 8.';},'bat'],
  ['Do we need a bigger grid connection?',/grid|connection|upgrade|capacity|amp/,R=>R.isNew?'The depot needs a connection of about <b>'+fmt(Math.ceil(R.peak/10)*10)+' kW</b>, roughly '+fmt(amps(R.peak))+' A.':'The depot peaks at <b>'+fmt(R.peak)+' kW</b> against a connection of <b>'+fmt(R.limit)+' kW</b>. '+(R.peak<=R.limit?'No upgrade is needed.':'That is '+fmt(R.peak-R.limit)+' kW too much. Try another charging plan first.'),'gr'],
  ['How long does charging take?',/how long|charg|plug/,R=>'On the hardest day:<ul>'+R.G.map(g=>'<li>“'+esc(g.name)+'”: '+(g.c.ready?hm(g.c.start)+' to '+hm(g.c.end)+' on a '+g.c.kw+' kW charger':'not full before '+hm(g.out))+'</li>').join('')+'</ul>','ch'],
  ['Is electric cheaper than diesel?',/cheap|cost|diesel|sav|price|money|pay/,R=>'Over '+R.Y+' years electric costs <b>'+fmt(R.totE/1e6,1)+' M DKK</b> and diesel <b>'+fmt(R.totD/1e6,1)+' M DKK</b>. '+(R.be?'Electric is ahead from year '+R.be+'.':'Electric is not ahead within the period.'),'cost'],
  ['How much CO₂ does it save?',/co2|co₂|climate|emission|green/,R=>'About <b>'+fmt(R.co2D-R.co2E)+' t</b> in the first year and <b>'+fmt(R.co2Saved)+' t</b> over '+R.Y+' years. Production is not counted.','co2'],
  ['What have you assumed?',/assum|source|trust|sample|sure|where/,()=>{const c=srcCounts(S.runs[S.runs.length-1].rows);return'This run used <b>'+(c.sample||0)+' sample values</b> and <b>'+(c.assume||0)+' assumptions</b> next to '+(c.std||0)+' standard values. All of them are listed with their source.';},'src']];
function aiSay(cls,html){const d=document.createElement('div');d.className=cls;d.innerHTML=html;$('msgs').appendChild(d);$('msgs').scrollTop=1e6;}
function aiAsk(txt){
  aiSay('me',esc(txt));
  if(!S.run){aiSay('bot','Press <b>Run</b> first. Then I can answer from the results.');return;}
  const q=QA.find(x=>x[1].test(txt.toLowerCase()));
  if(!q){aiSay('bot','I can only answer the questions listed below in this demo.');return;}
  aiSay('bot',q[2](S.run)+(dirty()?' <span class="mut">The inputs have changed since this run.</span>':''));if(q[3])go(q[3]);}
function aiGreet(){if(S.runNo===1)aiSay('bot','<b>'+S.run.title+'.</b> '+S.run.text);}
function setAi(on){S.ai=on;$('ai').hidden=!on;$('bAi').setAttribute('aria-pressed',String(on));if(on)$('aiIn').focus();if(S.run)render();}

/* ---------- events ---------- */
const EMB=window.parent!==window;
document.addEventListener('click',e=>{
  const t=e.target,c=s=>t.closest(s);let el;
  if((el=c('[data-close]'))||(DLG&&t===DLG.el)){closeDlg();return;}
  if((el=c('[data-reset]'))){const inp=el.closest('[data-s]').querySelector('[data-o]'),r=REG[+inp.dataset.o];r.o[el.dataset.reset]=r.o._d[el.dataset.reset];DLG?drawDlg():render();return;}
  if(DLG&&(el=c('[data-streset]'))){delete P.groups.find(x=>x.id===+el.dataset.streset).ov;drawDlg();return;}
  if(DLG)return;
  if((el=c('[data-main]'))){if(!el.disabled){const m=el.dataset.main;go(S.last[m]||m);}return;}
  if((el=c('[data-tab]'))){go(el.dataset.tab);return;}
  if(c('[data-run]')||c('#bRun')){run();return;}
  if((el=c('[data-pop]'))){const a=el.dataset.pop.split('|');openPop(+a[0],a[1]);return;}
  if((el=c('[data-info]'))){openInfo(el.dataset.info);return;}
  if((el=c('[data-stops]'))){openStops(+el.dataset.stops);return;}
  if((el=c('[data-tedit]'))){const a=el.dataset.tedit.split('|');S.tl=a[0];S.tid[a[0]]=a[1];go('templates');return;}
  if((el=c('[data-tl]'))){S.tl=el.dataset.tl;render();return;}
  if((el=c('[data-tsel]'))){S.tid[S.tl]=el.dataset.tsel;render();return;}
  if(c('[data-tnew]')||(el=c('[data-tdup]'))){const l=S.tl,src=el?tpl(l,el.dataset.tdup):null,o=newTpl(l,src);S.tid[l]=o.id;render();$('tplName').focus();$('tplName').select();return;}
  if((el=c('[data-tdel]'))){const l=S.tl;P.lib[l]=P.lib[l].filter(x=>x.id!==el.dataset.tdel);delete S.tid[l];render();return;}
  if(c('[data-bulk]')){const l=$('bulkL').value,v=$('bulkT').value;P.groups.forEach(g=>{if(S.sel[g.id])g[l]=v;});S.sel={};render();toast('Applied');return;}
  if((el=c('[data-miss]'))){openAt(missing()[+el.dataset.miss].open);return;}
  if(c('[data-gadd]')){const g0=P.groups[P.groups.length-1];P.groups.push({id:P.nid++,name:'New group',n:1,veh:g0?g0.veh:'',rt:g0?g0.rt:'',load:g0?g0.load:'',eq:g0?g0.eq:'',sch:g0?g0.sch:''});render();const i=document.querySelectorAll('.gname');i[i.length-1].focus();i[i.length-1].select();return;}
  if((el=c('[data-gdup]'))){const g=P.groups.find(x=>x.id===+el.dataset.gdup);P.groups.splice(P.groups.indexOf(g)+1,0,Object.assign({},g,{id:P.nid++,name:g.name+' (copy)'}));render();return;}
  if((el=c('[data-gdel]'))){P.groups=P.groups.filter(x=>x.id!==+el.dataset.gdel);render();return;}
  if((el=c('[data-plan]'))){P.chg.plan=el.dataset.plan;run('ch');return;}
  if((el=c('[data-whatif]'))){const w=el.dataset.whatif;if(w==='cold')P.wx.year=P.wx.year==='cold'?'normal':'cold';if(w==='plan')P.chg.plan=P.chg.plan==='grid'?'cost':'grid';if(w==='more')P.groups[0].n+=2;run('cmp');return;}
  if((el=c('[data-doc]'))){$('printRep').innerHTML=buildDoc(el.dataset.doc,S.run);setTimeout(()=>window.print(),80);return;}
  if(c('[data-csv]')){csv(S.run);return;}
  if(c('#bAi')){setAi(!S.ai);return;}
  if(c('#aiClose')){setAi(false);$('bAi').focus();return;}
  if((el=c('[data-q]'))){aiAsk(el.textContent);return;}
  if(c('#bExit')||(EMB&&c('#brand'))){e.preventDefault();window.parent.postMessage({evs:'exit'},'*');return;}
  if(c('.skip')){e.preventDefault();$('page').focus();}
});
function newTpl(l,src){const o=src?clone(src):BLANK[l]();o.id=l+(P.nid++);o.name=src?src.name+' (copy)':'New '+DEFS[l].one;if(!src){o._d=clone(o);delete o._d.id;delete o._d.name;}P.lib[l].push(o);return o;}
function liveField(inp){const r=REG[+inp.dataset.o],f=setVal(+inp.dataset.o,inp.dataset.k,inp.value),w=inp.closest('[data-s]'),m=isMissing(f,r.o);
  if(w)w.dataset.s=srcOf(f,r.o);inp.classList.toggle('miss',m);if(m)inp.setAttribute('aria-invalid','true');else inp.removeAttribute('aria-invalid');drawNav();}
document.addEventListener('input',e=>{const t=e.target;
  if(t.dataset.name!==undefined){REG[+t.dataset.name].o.name=t.value||'Untitled';const o=document.querySelector('.tlist [aria-current] b');if(o)o.textContent=t.value||'Untitled';return;}
  if(t.dataset.st&&t.type!=='checkbox'){const a=t.dataset.st.split('|'),g=P.groups.find(x=>x.id===+a[0]),x=parseFloat(t.value.replace(',','.'));if(!isNaN(x)&&x>=0){g.ov=g.ov||{};(g.ov[a[1]]=g.ov[a[1]]||{})[a[2]]=x;t.closest('tr').classList.add('ed');}return;}
  if(t.dataset.g){const a=t.dataset.g.split('|'),g=P.groups.find(x=>x.id===+a[1]);if(a[0]==='name')g.name=t.value||'Group';else{const n=parseInt(t.value,10);g.n=n>=1&&n<=500?n:0;t.classList.toggle('miss',!g.n);
      $('fleetTot').textContent=plural(sum(P.groups.map(x=>x.n)),'vehicle')+' in '+plural(P.groups.length,'row');}drawNav();return;}
  if(t.dataset.o!==undefined&&t.tagName==='INPUT'&&t.type!=='radio'&&t.type!=='checkbox'&&t.type!=='file')liveField(t);});
document.addEventListener('change',e=>{const t=e.target;
  if(t.dataset.gl){const a=t.dataset.gl.split('|'),g=P.groups.find(x=>x.id===+a[1]);if(t.value==='__new'){const o=newTpl(a[0]);g[a[0]]=o.id;S.tl=a[0];S.tid[a[0]]=o.id;go('templates');$('tplName').focus();$('tplName').select();}else{g[a[0]]=t.value;render();}return;}
  if(t.dataset.sel){S.sel[t.dataset.sel]=t.checked;render();return;}
  if(t.id==='selAll'){P.groups.forEach(g=>{S.sel[g.id]=t.checked;});render();return;}
  if(t.id==='bulkL'){S.bulkL=t.value;render();$('bulkL').focus();return;}
  if(t.dataset.st){const a=t.dataset.st.split('|'),g=P.groups.find(x=>x.id===+a[0]);g.ov=g.ov||{};(g.ov[a[1]]=g.ov[a[1]]||{}).on=t.checked;t.closest('tr').classList.add('ed');return;}
  if(t.dataset.o!==undefined&&t.type==='file'){setVal(+t.dataset.o,t.dataset.k,t.files[0]?t.files[0].name:'');DLG?drawDlg():render();return;}
  if(t.dataset.o!==undefined&&t.type==='checkbox'){const r=REG[+t.dataset.o];if(t.dataset.mv){const w=t.closest('.multi');setVal(+t.dataset.o,t.dataset.k,[...w.querySelectorAll('input:checked')].map(x=>x.dataset.mv).join(' '));}else setVal(+t.dataset.o,t.dataset.k,t.checked?'yes':'no');const id=t.id;DLG?drawDlg():render();if(id&&$(id))$(id).focus();drawNav();return;}
  if(t.id==='enG'){S.enG=+t.value;render();$('enG').focus();return;}
  if(t.id==='cmpA'||t.id==='cmpB'){S[t.id]=+t.value;render();$(t.id).focus();return;}
  if(t.dataset.o!==undefined&&(t.tagName==='SELECT'||t.type==='radio')){setVal(+t.dataset.o,t.dataset.k,t.value);const nm=t.name,v=t.value,id=t.id;
    DLG?drawDlg():render();const f=id?$(id):document.querySelector('input[name="'+nm+'"][value="'+v+'"]');if(f)f.focus();drawNav();}});
document.addEventListener('toggle',e=>{const d=e.target;if(d.dataset&&d.dataset.sec){d.open?OPEN.add(d.dataset.sec):OPEN.delete(d.dataset.sec);}},true);
document.addEventListener('keydown',e=>{
  if(DLG){if(e.key==='Escape'){e.preventDefault();closeDlg();return;}
    if(e.key==='Tab'){const f=[...DLG.el.querySelectorAll('button,[href],input:not([disabled]),select,summary,[tabindex="0"]')].filter(x=>x.offsetParent!==null);if(!f.length)return;
      const a=document.activeElement;if(e.shiftKey&&(a===f[0]||!DLG.el.contains(a))){e.preventDefault();f[f.length-1].focus();}else if(!e.shiftKey&&(a===f[f.length-1]||!DLG.el.contains(a))){e.preventDefault();f[0].focus();}}
    return;}
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();run();}
  if(e.key==='Escape'&&S.ai&&$('ai').contains(document.activeElement)){setAi(false);$('bAi').focus();}});
$('aiForm').addEventListener('submit',e=>{e.preventDefault();const v=$('aiIn').value.trim();if(v){$('aiIn').value='';aiAsk(v);}});
let rz;window.addEventListener('resize',()=>{clearTimeout(rz);rz=setTimeout(()=>{if(!DLG&&PAGES[S.tab][1]&&S.run)PAGES[S.tab][1](S.run);},150);});
window.addEventListener('afterprint',()=>{$('printRep').innerHTML='';});

/* ---------- start ---------- */
if(EMB){$('bExit').hidden=false;$('brand').dataset.link='1';$('brand').setAttribute('aria-label','EV Scope, back to the site');}
$('sugs').innerHTML=QA.map(q=>`<button class="lnk" data-q>${q[0]}</button>`).join('');
aiSay('bot','This demo assistant answers a fixed set of questions about the current run. Pick one below.');
render();
