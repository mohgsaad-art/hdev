/* ---------- charts: plain axes box, light grid, one accent ---------- */
const BLUE='#1F4E9E',PALE='#9DB5DC',GREY='#7C838E';
function ticks(lo,hi,count){const r=(hi-lo)||1,raw=r/count,p=Math.pow(10,Math.floor(Math.log10(raw))),k=raw/p,st=(k<=1?1:k<=2?2:k<=2.5?2.5:k<=5?5:10)*p;
  const a=Math.floor(lo/st+1e-9)*st,b=Math.ceil(hi/st-1e-9)*st,out=[];for(let v=a;v<=b+st*1e-6;v+=st)out.push(Math.round(v*1e6)/1e6);return out;}
const tf=v=>(v<0?'−':'')+fmt(Math.abs(v),(v%1)?1:0);
function chart(el,c){
  if(!el)return;const W=Math.max(300,Math.floor(el.clientWidth)),H=c.h||230,M={l:54,r:14,t:14,b:28},n=c.series[0].v.length,iw=W-M.l-M.r,ih=H-M.t-M.b;
  let all=[];c.series.forEach(s=>{all=all.concat(s.v);});(c.refs||[]).forEach(r=>all.push(r.v));
  const TK=ticks(Math.min(0,...all),Math.max(...all)*1.08,4),min=TK[0],max=TK[TK.length-1],span=c.step?n:n-1;
  const X=i=>M.l+iw*i/span,Y=v=>M.t+ih*(1-(v-min)/(max-min));let s='';
  TK.forEach(v=>{const y=Y(v);s+=`<line x1="${M.l}" x2="${W-M.r}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#EEF0F3"/><text x="${M.l-7}" y="${(y+4).toFixed(1)}" text-anchor="end">${tf(v)}</text>`;});
  c.x.forEach((l,i)=>{if(l==='')return;const x=X(i).toFixed(1);s+=`<line x1="${x}" x2="${x}" y1="${M.t+ih-4}" y2="${M.t+ih}" stroke="#9AA1AC"/><text x="${x}" y="${H-8}" text-anchor="middle">${l}</text>`;});
  if(c.unit)s+=`<text x="13" y="${M.t+ih/2}" text-anchor="middle" transform="rotate(-90 13 ${M.t+ih/2})">${c.unit}</text>`;
  c.series.forEach(se=>{let d='';se.v.forEach((v,i)=>{d+=`${i?'L':'M'}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`+(c.step?`H${X(i+1).toFixed(1)}`:'');});
    if(se.area)s+=`<path d="${d}V${Y(Math.max(0,min)).toFixed(1)}H${X(0).toFixed(1)}Z" fill="${se.color}" opacity=".1"/>`;
    s+=`<path d="${d}" fill="none" stroke="${se.color}" stroke-width="1.8" stroke-linejoin="round"/>`;});
  (c.refs||[]).forEach(r=>{const y=Y(r.v);s+=`<line x1="${M.l}" x2="${W-M.r}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#1D2026" stroke-dasharray="5 4"/><text x="${W-M.r-6}" y="${(y-6).toFixed(1)}" text-anchor="end" fill="#1D2026" stroke="#fff" stroke-width="4" stroke-linejoin="round" paint-order="stroke">${r.label}</text>`;});
  (c.marks||[]).forEach(m=>{const x=X(m.i),y=Y(m.v),rt=x<W*0.62;s+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.5" fill="#fff" stroke="#1D2026" stroke-width="1.6"/><text x="${(rt?x+9:x-9).toFixed(1)}" y="${(m.below?y+17:y-9).toFixed(1)}" text-anchor="${rt?'start':'end'}" fill="#1D2026" stroke="#fff" stroke-width="4" stroke-linejoin="round" paint-order="stroke">${m.label}</text>`;});
  if(c.zero&&min<0)s+=`<line x1="${M.l}" x2="${W-M.r}" y1="${Y(0).toFixed(1)}" y2="${Y(0).toFixed(1)}" stroke="#646B77"/>`;
  s+=`<rect x="${M.l}" y="${M.t}" width="${iw}" height="${ih}" fill="none" stroke="#9AA1AC" stroke-width=".8"/>`;
  if(c.tip)for(let i=0;i<n;i++){const w=iw/span,x0=c.step?X(i):X(i)-w/2;s+=`<rect x="${Math.max(M.l,x0).toFixed(1)}" y="${M.t}" width="${w.toFixed(1)}" height="${ih}" fill="transparent"><title>${esc(c.tip(i))}</title></rect>`;}
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(c.label)}" font-size="11.5" fill="#646B77">${s}</svg>`;}
function cols(el,c){
  if(!el)return;const W=Math.max(300,Math.floor(el.clientWidth)),H=c.h||200,M={l:54,r:14,t:20,b:28},n=c.v.length,iw=W-M.l-M.r,ih=H-M.t-M.b;
  const TK=ticks(0,Math.max(...c.v)*1.1,4),max=TK[TK.length-1],slot=iw/n,bw=Math.min(46,slot*0.62),Y=v=>M.t+ih*(1-v/max);let s='';
  TK.forEach(v=>{const y=Y(v);s+=`<line x1="${M.l}" x2="${W-M.r}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#EEF0F3"/><text x="${M.l-7}" y="${(y+4).toFixed(1)}" text-anchor="end">${tf(v)}</text>`;});
  if(c.unit)s+=`<text x="13" y="${M.t+ih/2}" text-anchor="middle" transform="rotate(-90 13 ${M.t+ih/2})">${c.unit}</text>`;
  c.v.forEach((v,i)=>{const cx=M.l+slot*i+slot/2,y=Y(v);s+=`<rect x="${(cx-bw/2).toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${(M.t+ih-y).toFixed(1)}" fill="${i===c.hi?BLUE:PALE}"><title>${esc(c.x[i]+': '+fmt(v)+' '+c.unit)}</title></rect><text x="${cx.toFixed(1)}" y="${H-8}" text-anchor="middle">${c.x[i]}</text>`;
    if(i===c.hi||i===c.lo)s+=`<text x="${cx.toFixed(1)}" y="${(y-6).toFixed(1)}" text-anchor="middle" fill="#1D2026">${fmt(v)}</text>`;});
  s+=`<line x1="${M.l}" x2="${W-M.r}" y1="${M.t+ih}" y2="${M.t+ih}" stroke="#9AA1AC"/>`;
  el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(c.label)}" font-size="11.5" fill="#646B77">${s}</svg>`;}
const segs=(a,b)=>{a=((a%24)+24)%24;b=((b%24)+24)%24;return Math.abs(a-b)<1e-6?[]:a<b?[[a,b]]:[[a,24],[0,b]];};
function gantt(R){
  const bar=(a,b,cls,tt)=>segs(a,b).map(q=>`<i class="${cls}" style="left:${(q[0]/24*100).toFixed(2)}%;width:${((q[1]-q[0])/24*100).toFixed(2)}%" title="${tt}"></i>`).join('');
  return`<div class="gantt" role="img" aria-label="When each group is on the road and when it charges">${R.G.map(g=>`<div class="grow"><span>${esc(g.name)}</span><div class="gtrack">${bar(g.out,g.back,'rd','On the road '+hm(g.out)+' to '+hm(g.back))}${bar(g.c.start,g.c.end,'ch','Charging '+hm(g.c.start)+' to '+hm(g.c.end))}</div></div>`).join('')}
  <div class="grow"><span></span><div class="gax">${[0,6,12,18,24].map(h=>`<span style="left:${h/24*100}%">${String(h).padStart(2,'0')}:00</span>`).join('')}</div></div></div>
  <div class="lgd"><span><i class="box" style="background:${PALE}"></i>On the road</span><span><i class="box" style="background:${BLUE}"></i>Charging</span><span><i class="box" style="background:#EEF0F3"></i>Parked</span></div>`;}

/* ---------- result pages ---------- */
const fig=(l,v,u,n,bad)=>`<div class="fig${bad?' bad':''}"><div class="fl">${l}</div><div class="fv">${v}${u?`<span>${u}</span>`:''}</div>${n?`<div class="fn">${n}</div>`:''}</div>`;
const figs=a=>`<div class="figs">${a.join('')}</div>`;
const kvt=rows=>`<div class="tw"><table class="t kvt"><tbody>${rows.map(r=>`<tr><th scope="row">${r[0]}</th><td class="v">${r[1]}</td><td class="mut">${r[2]||''}</td></tr>`).join('')}</tbody></table></div>`;
const tbl=(head,rows,foot,cls)=>`<div class="tw"><table class="t ${cls||''}"><thead><tr>${head.map((h,i)=>`<th scope="col"${i&&h[0]!=='<'?' class="r"':''}>${h[0]==='<'?h.slice(1):h}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr${r.cur?' class="cur"':''}>${(r.c||r).map((x,i)=>`<td${i&&head[i][0]!=='<'?' class="r"':''}>${x}</td>`).join('')}</tr>`).join('')}</tbody>${foot?`<tfoot><tr>${foot.map((x,i)=>`<td${i?' class="r"':''}>${x}</td>`).join('')}</tr></tfoot>`:''}</table></div>`;
/* every result page opens the same way: its name, one line that says how it went, then the figures */
const head=(name,ok,line)=>`<h1>${name}</h1><p class="status">${ok===null?'':mark(ok)}<span>${line}</span></p>${stale()}`;
const signed=(v,d,u)=>Math.abs(v)<Math.pow(10,-(d||0))/2?fmt(0,d):(v<0?'−':'+')+fmt(Math.abs(v),d)+(u?' '+u:'');
const chk=(R,k)=>R.checks.find(c=>c.k===k);
const pick=(R)=>R.G.length>1?`<p class="pickg"><label for="enG">Group</label><select class="in" id="enG">${R.G.map((x,i)=>`<option value="${i}"${i===(R.G[S.enG]?S.enG:0)?' selected':''}>${esc(x.name)}</option>`).join('')}</select></p>`:'';
function pageOv(R){
  const G=R.G,b=G.map(g=>g.batt),kws=[...new Set(G.map(g=>g.c.kw))],same=Math.min(...b)===Math.max(...b);
  return head('Overview',R.feasible,R.title)+figs([
    fig('Battery in each vehicle',fmt(Math.max(...b)),'kWh',same?(G.every(g=>g.v.battMode==='size')?'Sized for the hardest day at year 8':'From your datasheet'):'The largest. The smallest is '+fmt(Math.min(...b))+' kWh'),
    fig('Chargers',R.N,kws.length===1?'× '+kws[0]+' kW':'in '+kws.length+' sizes',kws.length===1?'One for each vehicle':G.map(g=>g.n+' × '+g.c.kw+' kW').join(', ')),
    fig('Depot peak',fmt(R.peak),'kW',R.isNew?'About '+fmt(amps(R.peak))+' A to apply for':'Of the '+fmt(R.limit)+' kW connected today',!R.isNew&&R.peak>R.limit),
    fig(R.save>=0?'Saved against diesel':'Extra cost against diesel',fmt(Math.abs(R.save)/1e6,1),'M DKK','Over '+R.Y+' years'+(R.be?', ahead from year '+R.be:''),R.save<0)])+
  `<h2>Checks</h2>
  <div class="tw"><table class="t checks"><tbody>${R.checks.map(c=>`<tr><td>${stat(c.ok,c.k==='grid'&&R.isNew?'Sized':'Passes','Fails')}</td><td class="ct">${c.t}</td><td class="mut">${esc(c.d)}</td><td class="r"><button class="lnk" data-tab="${c.go}">${TITLE[c.go]}</button></td></tr>`).join('')}</tbody></table></div>
  <h2>The fleet</h2><p class="note">What went in and what came out, one row for each group.</p>
  ${tbl(['<Group','Vehicles','<Route','<Load','Hardest day','Battery','Charger','Full again'],G.map(g=>[esc(g.name),g.n,fmt(g.rt.km)+' km, '+fmt(g.rt.stops)+' stops',SUMM.load(g.l),fmt(g.worst)+' kWh',fmt(g.batt)+' kWh',g.c.kw+' kW',g.c.ready?hm(g.c.end):'<span class="no-t">Not full</span>']))}`;}
function pageEn(R){
  const G=R.G,g=G[S.enG]||G[0],top=Math.max(...G.map(x=>x.worst)),parts=[['Driving',g.drive],['On-board systems',g.auxE],['Body equipment',g.eqE]].filter(p=>p[1]>0),mx=Math.max(...parts.map(p=>p[1])),okT=g.tNeed<=g.shiftH;
  return head('Energy',null,'Each vehicle uses up to '+fmt(top)+' kWh on its hardest day')+pick(R)+figs([
    fig('Average day',fmt(g.mean),'kWh','One vehicle, across the year'),
    fig('Hardest day',fmt(g.worst),'kWh',P.wx.year==='cold'?'In a cold winter':'In a normal year'),
    fig('Per km',fmt(g.mean/g.rt.km,2),'kWh','On an average day'),
    fig('From the grid each year',fmt(g.n*g.kWhGrid/1000),'MWh',plural(g.n,'vehicle')+', charger losses included')])+
  `<div class="cols2"><div><h2>Where the energy goes</h2><p class="note">One vehicle on a day in April.</p>
    <div class="hb">${parts.map((p,i)=>`<span>${p[0]}</span><div class="bar"><i${i?' class="alt"':''} style="width:${(p[1]/mx*100).toFixed(1)}%"></i></div><span class="num"><b>${fmt(p[1])} kWh</b> ${fmt(p[1]/g.avg*100)} %</span>`).join('')}</div>
    <p class="note" style="margin-top:14px">Braking gives back ${fmt(g.regen)} kWh a day. That is already taken off the driving figure.</p></div>
  <div><h2>Through the year</h2><p class="note">kWh for one vehicle on a working day, by month.</p><div class="viz" id="vMon"></div></div></div>
  <h2>Time on the route</h2>${kvt([
    ['The route needs',stat(okT,fmt(g.tNeed,1)+' h',fmt(g.tNeed,1)+' h'),'Against a shift of '+fmt(g.shiftH,1)+' h, '+hm(g.out)+' to '+hm(g.back)],
    ['Driving',fmt(g.tDrive,1)+' h','At '+fmt(g.rt.speed)+' km/h between stops'],
    ['At stops',fmt(g.tStop+g.tEq,1)+' h',fmt(g.rt.stops)+' stops'],
    ['Working days',fmt(g.days)+' a year',fmt(g.kmYr)+' km a year for each vehicle']])}`;}
function drawEn(R){const g=R.G[S.enG]||R.G[0],hi=g.months.indexOf(Math.max(...g.months)),lo=g.months.indexOf(Math.min(...g.months));
  cols($('vMon'),{v:g.months,x:MONTHS,unit:'kWh',hi,lo,h:210,label:'Energy per working day by month. Highest '+fmt(g.months[hi])+' kWh in '+MONTHS[hi]+', lowest '+fmt(g.months[lo])+' kWh in '+MONTHS[lo]});}
function pageBat(R){
  const G=R.G,t=G.reduce((a,b)=>b.worst/b.usableEol>a.worst/a.usableEol?b:a),bad=['batt','eol','pay'].map(k=>chk(R,k)).find(c=>!c.ok),okE=t.worst<=t.usableEol,who=G.length>1?'“'+esc(t.name)+'”, the tightest group':'';
  const pc=(a,b)=>a<=b?fmt((1-a/b)*100)+' %':'<span class="no-t">Short by '+fmt(a-b)+' kWh</span>';
  return head('Battery',!bad,bad?({batt:'The battery is too small for the hardest day',eol:'The battery is too small once it has aged',pay:'The load is over the weight limit'})[bad.k]:'The battery covers the hardest day, also at year 8')+figs([
    fig('Installed',fmt(t.batt),'kWh',t.v.battMode==='size'?'Sized by the tool, in steps of 10 kWh':'From your datasheet'),
    fig('Usable when new',fmt(t.usable),'kWh',fmt(t.v.usable)+' % of the installed size'),
    fig('Usable at year 8',fmt(t.usableEol),'kWh','At '+fmt(t.v.guar)+' % of the capacity'),
    okE?fig('Left after the hardest day',fmt((1-t.worst/t.usableEol)*100),'%','At year 8'+(who?'. '+who:'')):fig('Short on the hardest day',fmt(t.worst-t.usableEol),'kWh','At year 8'+(who?'. '+who:''),1)])+
  `<h2>The hardest day against the battery</h2><p class="note">Each bar is the full installed battery.</p>
  <div class="bul">${G.map(g=>`<span>${esc(g.name)}</span><div class="btrack" role="img" aria-label="${esc(g.name)}: hardest day ${fmt(g.worst)} kWh, usable ${fmt(g.usable)} kWh when new and ${fmt(g.usableEol)} kWh at year 8, of ${fmt(g.batt)} kWh installed"><i style="width:${Math.min(100,g.worst/g.batt*100).toFixed(1)}%"${g.worst>g.usableEol?' class="over"':''}></i><b style="left:${(g.usable/g.batt*100).toFixed(1)}%"></b><b class="eol" style="left:${(g.usableEol/g.batt*100).toFixed(1)}%"></b></div><span class="num">${fmt(g.worst)} of ${fmt(g.batt)} kWh</span>`).join('')}</div>
  <div class="lgd"><span><i class="box" style="background:${BLUE}"></i>Used on the hardest day</span><span><i class="tick"></i>Usable when new</span><span><i class="tick eol"></i>Usable at year 8</span></div>
  ${tbl(['<Group','Hardest day','Installed','Usable, new','Usable, year 8','Left, new','Left, year 8'],G.map(g=>[esc(g.name),fmt(g.worst)+' kWh',fmt(g.batt)+' kWh',fmt(g.usable)+' kWh',fmt(g.usableEol)+' kWh',pc(g.worst,g.usable),pc(g.worst,g.usableEol)]))}
  <h2>Weight</h2><p class="note">What the vehicle may carry against what the load asks for. The weight of the battery is not counted yet.</p>
  ${tbl(['<Group','Heaviest load','May carry','Room left','Average weight on the road'],G.map(g=>[esc(g.name),fmt(g.payMax,1)+' t',fmt(g.payLimit,1)+' t',g.payMax<=g.payLimit?fmt(g.payLimit-g.payMax,1)+' t':'<span class="no-t">Over by '+fmt(g.payMax-g.payLimit,1)+' t</span>',fmt(g.mass/1000,1)+' t']))}`;}
function pageCh(R){
  const G=R.G,rdy=G.every(g=>g.c.ready),kws=[...new Set(G.map(g=>g.c.kw))],minSp=Math.min(...G.map(g=>g.c.spare)),lg=G.reduce((a,b)=>b.c.hours>a.c.hours?b:a);
  return head('Charging',rdy,rdy?'Every vehicle is full before it leaves':'The vehicles are not full before they leave')+figs([
    fig('Chargers',R.N,kws.length===1?'× '+kws[0]+' kW':'in '+kws.length+' sizes',D_note(R)),
    fig('Longest charge',fmt(lg.c.hours,1),'h',hm(lg.c.start)+' to '+hm(lg.c.end)+(G.length>1?', “'+esc(lg.name)+'”':'')),
    rdy?fig('Time to spare',fmt(minSp,1),'h','Before the tightest group leaves'):fig('Time to spare','None','','A vehicle leaves before it is full',1),
    fig('Charged on the hardest day',fmt(sum(G.map(g=>g.n*g.c.need))),'kWh','Whole fleet, from the grid')])+
  `<h2>A day at the depot</h2><p class="note">The hardest day of the year, midnight to midnight.</p>${gantt(R)}
  <h2>Each group</h2>
  ${tbl(['<Group','Vehicles','Charger','Back','Charging','Leaves','Time to spare'],G.map(g=>[esc(g.name),g.n,g.c.kw+' kW',hm(g.back),g.c.ready?hm(g.c.start)+' to '+hm(g.c.end):'<span class="no-t">Short by '+fmt(g.c.short)+' kWh</span>',hm(g.out),g.c.ready?fmt(g.c.spare,1)+' h':'<span class="no-t">None</span>']))}
  <h2>The three charging plans</h2><p class="note">The same fleet, charged three ways. Choosing another plan runs the project again.</p>
  ${tbl(['<Plan','Chargers','Depot peak','<Fits the connection','<Full in time','Electricity a year','<'],R.alts.map(A=>{const k=[...new Set(A.G.map(g=>g.c.kw))],ok=A.isNew||A.peak<=A.limit,rd=A.G.every(g=>g.c.ready);
    return{cur:A.plan===R.plan,c:[PLAN_N[A.plan],k.join(' and ')+' kW',fmt(A.peak)+' kW',A.isNew?'New connection':stat(ok,'Yes','No'),stat(rd,'Yes','No'),fmt(A.rowsE[0].energy/1000)+' k DKK',A.plan===R.plan?'<span class="mut">In use</span>':`<button class="lnk" data-plan="${A.plan}">Use this plan</button>`]};}))}`;}
const D_note=R=>'Plan: '+PLAN_N[R.plan].toLowerCase();
function pageGr(R){
  const G=R.G,rdy=G.every(g=>g.c.ready),fits=R.isNew||R.peak<=R.limit,per=Math.max(...G.map(g=>g.c.p)),minSp=Math.min(...G.map(g=>g.c.spare)),ask=Math.ceil(R.peak/10)*10;
  return head('Grid',fits,R.isNew?'The depot needs a connection of about '+fmt(ask)+' kW':fits?'Charging fits the grid connection the depot has today':'Charging goes '+fmt(R.peak-R.limit)+' kW over the grid connection')+figs([
    fig('Depot peak',fmt(R.peak),'kW','At '+hm(R.peakAt)+', about '+fmt(amps(R.peak))+' A',!fits),
    R.isNew?fig('Connection to apply for',fmt(ask),'kW','Rounded up to the next 10 kW'):fig('Connection today',fmt(R.limit),'kW','About '+fmt(amps(R.limit))+' A at 400 V'),
    R.isNew?fig('Buildings',fmt(P.depot.base),'kW','Already in use, before charging'):fits?fig('Room at the peak',fmt(R.limit-R.peak),'kW','Enough for '+plural(Math.floor((R.limit-R.peak)/per),'more vehicle')):fig('Over at the peak',fmt(R.peak-R.limit),'kW','Try another charging plan first',1),
    fig('Cost of the connection',fmt(R.conn),'DKK',R.conn?(R.isNew?'New connection':'For the extra amperes'):R.isNew?'No price list for this grid company':'No upgrade needed')])+
  `<h2>Depot power over the hardest day</h2><p class="note">Buildings and charging together, in kW.</p><div class="viz" id="vLoad"></div>
  <h2>Behind the figures</h2>${kvt([
    ['Buildings',fmt(P.depot.base)+' kW','A steady value in the demo'],
    ['Charging at the peak',fmt(R.peak-P.depot.base)+' kW',R.N+' chargers, plan: '+PLAN_N[R.plan].toLowerCase()],
    ['Charging that could be paused',fmt(R.peak-P.depot.base)+' kW',rdy?'For up to '+fmt(minSp,1)+' h without a late start':'Not without a late start'],
    ['Price for each ampere',R.fee.perA?fmt(R.fee.perA,2)+' DKK':'Not in the demo',R.fee.ref],
    ['Voltage','400 V','Three-phase, used to turn kW into amperes']])}`;}
function drawGr(R){const x=[];for(let i=0;i<96;i++)x.push(i%12===0?String(i/4).padStart(2,'0')+':00':'');
  chart($('vLoad'),{h:260,step:1,x,unit:'kW',series:[{v:R.load,color:BLUE,area:1}],refs:R.isNew?[]:[{v:R.limit,label:'Grid connection '+fmt(R.limit)+' kW'}],
    marks:[{i:R.load.indexOf(R.peak)+0.5,v:R.peak,label:'Peak '+fmt(R.peak)+' kW'}],tip:i=>hm(i/4)+'  '+fmt(R.load[i])+' kW',
    label:'Depot power by time of day. Peak '+fmt(R.peak)+' kW at '+hm(R.peakAt)+(R.isNew?'':', connection '+fmt(R.limit)+' kW')});}
function pageCost(R){
  const Y=R.Y,s=R.save,M=v=>fmt(v/1e6,2),dif=(d,e)=>`<span class="${e-d<=0?'ok-t':'no-t'}">${signed((e-d)/1e6,2)}</span>`;
  return head('Cost',s>=0,s>=0?'Electric costs '+fmt(s/1e6,1)+' M DKK less than diesel over '+Y+' years':'Electric costs '+fmt(-s/1e6,1)+' M DKK more than diesel over '+Y+' years')+figs([
    fig('Electric',fmt(R.totE/1e6,1),'M DKK',fmt(R.totE/R.kmTot,2)+' DKK per km'),
    fig('Diesel',fmt(R.totD/1e6,1),'M DKK',fmt(R.totD/R.kmTot,2)+' DKK per km'),
    fig(s>=0?'Saved with electric':'Extra with electric',fmt(Math.abs(s)/1e6,1),'M DKK','Whole fleet, '+Y+' years',s<0),
    R.be?fig('Electric is ahead from','Year '+R.be,'','Counted from the first year'):fig('Electric is ahead from','Never','','Not within '+Y+' years',1)])+
  `<h2>How far electric is ahead, year by year</h2><p class="note">What the fleet has saved against diesel so far, in million DKK. Below zero means electric has cost more up to that year.</p><div class="viz" id="vCum"></div>
  <h2>Where the difference comes from</h2><p class="note">Whole fleet over ${Y} years, million DKK. Driver wages are the same on both sides.</p>
  ${tbl(['<Cost','Diesel','Electric','Electric against diesel'],R.cats.map(c=>[c[0],M(c[1]),M(c[2]),dif(c[1],c[2])]),['Total',M(R.totD),M(R.totE),dif(R.totD,R.totE)])}
  <h2>Year by year</h2><p class="note">Whole fleet, thousand DKK.</p>
  ${tbl(['<Year','Electric','Diesel','Difference','Saved so far'],R.rowsE.map((E,i)=>[E.yr,fmt(E.tot/1000),fmt(R.rowsD[i].tot/1000),signed((E.tot-R.rowsD[i].tot)/1000,0),fmt((R.cumD[i+1]-R.cumE[i+1])/1000)]))}`;}
function drawCost(R){const x=[],Y=R.Y,v=R.cumD.map((d,i)=>(d-R.cumE[i])/1e6);for(let y=0;y<=Y;y++)x.push(String(y));
  chart($('vCum'),{h:250,x,unit:'M DKK',zero:1,series:[{v,color:BLUE,area:1}],
    marks:R.be?[{i:R.be,v:v[R.be],below:1,label:'Ahead from year '+R.be}]:[],tip:i=>'Year '+i+'  '+signed(v[i],2)+' M DKK',
    label:'Saving against diesel building up over '+Y+' years, ending at '+signed(v[Y],1)+' million DKK'});}
function pageCo2(R){
  const Y=R.Y,first=R.co2D-R.co2E;
  return head('CO₂',R.co2Saved>=0,'Electric saves '+fmt(R.co2Saved)+' t of CO₂ over '+Y+' years')+figs([
    fig('Diesel fleet',fmt(R.co2D),'t a year','From the diesel burned'),
    fig('Electric fleet',fmt(R.co2E,1),'t a year','From grid electricity, '+DEMO.elStart),
    fig('Saved in the first year',fmt(first),'t',fmt(first/R.co2D*100)+' % less than diesel'),
    fig('Saved over '+Y+' years',fmt(R.co2Saved),'t',P.co2.gridMode==='path'?'The grid gets cleaner each year':'One grid value for every year')])+
  `<h2>Year by year</h2><p class="note">Whole fleet, tonnes of CO₂.</p>
  ${tbl(['<Year','Grid, g/kWh','Electric','Diesel','Saved so far'],R.co2Rows.map(r=>[r[0],fmt(r[1],2),fmt(r[2],1),fmt(r[3]),fmt(r[4])]))}
  <h2>What is counted</h2>${kvt([
    ['Counted','Diesel burned and electricity from the grid',fmt(sum(R.G.map(g=>g.n*g.dieselL)))+' l of diesel and '+fmt(R.kWhFleet/1000)+' MWh a year'],
    ['Not counted','Making the trucks, the batteries and the diesel','']])}`;}
function demoRows(R){return[
  ['Air density','1.2 kg/m³','Constant in the demo driving model'],
  ['Speeding up and braking','1.0 m/s²','Demo value'],
  ['Braking energy recovered','88 %','From the test harness. Not final'],
  ['Monthly weather factors','0.92 to 1.18','Demo values until daily weather is run'],
  ['Hardest day against the hardest month','15 % more','Demo value'],
  ['Cold winter','8 % more from November to February','Demo value'],
  ['Electricity price by charging plan','15 %, 8 % or 0 % off','Demo values until hourly prices are used'],
  ['Charger sizing','Full within the night hours, the whole stay less 2 h, or 4 h','Demo rule for the three plans'],
  ['Battery sizing','Usable energy at year 8 covers the hardest day','Demo rule'],
  ['Charger and installation prices','By charger size','COWI truck cost sheet, 2024 operator prices'],
  ['Grid connection fee',R.fee.perA?fmt(R.fee.perA,2)+' DKK per ampere':'Left out',R.fee.ref],
  ['Depot voltage','400 V, three-phase','To turn kW into amperes'],
  ['Routes','Flat','No hills in the demo']];}
function pageSrc(R){
  const run=S.runs[S.runs.length-1],c=srcCounts(run.rows),n=run.rows.filter(r=>!r.radio).length;
  return`<h1>Inputs and sources</h1><p class="lede">Run ${run.n} used ${n} values: ${c.std||0} standard, ${c.sample||0} sample, ${c.assume||0} assumed and ${c.you||0} of your own.</p>${stale()}
  <p class="note" style="margin-top:14px">This demo runs on a stand-in engine with simple formulas. The figures show how the tool works. They are not a study of a real fleet.</p>
  ${srcTable(run.rows)}
  <h2>Demo values behind the results</h2><p class="note">Fixed in the demo and not shown on the setup pages.</p>
  ${tbl(['<Value','<Used','<Basis'],demoRows(R))}`;}

/* ---------- compare ---------- */
const OUTS=[['Largest battery',R=>Math.max(...R.G.map(g=>g.batt)),'kWh',0,0],['Largest charger',R=>Math.max(...R.G.map(g=>g.c.kw)),'kW',0,0],['Depot peak',R=>R.peak,'kW',0,-1],
  ['Total cost, electric',R=>R.totE/1e6,'M DKK',1,-1],['Saving against diesel',R=>R.save/1e6,'M DKK',1,1],['CO₂ saved over the period',R=>R.co2Saved,'t',0,1]];
function diffRows(a,b){const m={};a.forEach(r=>{m[r.where+'|'+r.label]=r.value;});const out=[];
  b.forEach(r=>{const k=r.where+'|'+r.label;if(m[k]!==r.value)out.push([r.where+', '+r.label.toLowerCase(),m[k]===undefined?'':m[k],r.value]);delete m[k];});
  Object.keys(m).forEach(k=>{if(!b.some(r=>r.where+'|'+r.label===k))out.push([k.replace('|',', '),m[k],'']);});return out;}
function pageCmp(){
  const L=S.runs;let h=`<h1>Compare runs</h1><p class="lede">Every run keeps its inputs and results. Change something in Setup, run again, and see the difference here.</p>${stale()}`;
  if(L.length<2)h+=`<h2>Try a change</h2><p class="note">Each of these changes one input and runs the project again.</p>
    <ul class="misslist"><li><button class="lnk" data-whatif="cold">${P.wx.year==='cold'?'Size for a normal year':'Size for a cold winter'}</button></li>
    <li><button class="lnk" data-whatif="plan">${P.chg.plan==='grid'?'Charge at the lowest cost':'Charge grid-friendly'}</button></li>
    <li><button class="lnk" data-whatif="more">Add two vehicles to “${esc(P.groups[0].name)}”</button></li></ul>`;
  else{const A=L.find(r=>r.n===S.cmpA)||L[0],B=L.find(r=>r.n===S.cmpB)||L[L.length-1],d=diffRows(A.rows,B.rows),opt=s=>L.map(r=>`<option value="${r.n}"${r.n===s?' selected':''}>Run ${r.n}</option>`).join('');
    h+=`<p style="margin-top:22px"><label for="cmpA">Compare </label><select class="in" id="cmpA" style="width:auto">${opt(A.n)}</select><label for="cmpB"> with </label><select class="in" id="cmpB" style="width:auto">${opt(B.n)}</select></p>
    <div class="cols2"><div><h2>Inputs that differ</h2>${d.length?tbl(['<Input','<Run '+A.n,'<Run '+B.n],d.map(r=>r.map(esc))):'<p class="note">The two runs use the same inputs.</p>'}</div>
    <div><h2>Results</h2>${tbl(['<Result','Run '+A.n,'Run '+B.n,'Change'],OUTS.map(o=>{const a=o[1](A.R),b=o[1](B.R),dv=b-a,big=Math.abs(dv)>=Math.pow(10,-o[3])/2;
      return[o[0],fmt(a,o[3])+' '+o[2],fmt(b,o[3])+' '+o[2],big?`<span class="${o[4]?(dv*o[4]>0?'ok-t':'no-t'):''}">${signed(dv,o[3])}</span>`:'Same'];}).concat([['All checks pass',A.R.feasible?'Yes':'No',B.R.feasible?'Yes':'No','']]))}</div></div>`;}
  h+=`<h2>Runs so far</h2>${tbl(['<Run','<Time','<What changed','Depot peak','Saving against diesel','<Result'],L.slice().reverse().map(r=>{const pv=L[L.indexOf(r)-1],d=pv?diffRows(pv.rows,r.rows):null;
    return['Run '+r.n,r.t,pv?(d.length?d.slice(0,3).map(x=>esc(x[0])+': '+esc(x[1])+' to '+esc(x[2])).join('<br>')+(d.length>3?'<br><span class="mut">and '+(d.length-3)+' more</span>':''):'<span class="mut">Nothing</span>'):'<span class="mut">First run</span>',fmt(r.R.peak)+' kW',fmt(r.R.save/1e6,1)+' M DKK',stat(r.R.feasible,'All checks pass','A check fails')];}))}`;
  return h;}

/* ---------- documents ---------- */
const DOCS=[
  ['feas','Feasibility report','For the fleet owner and the board. The answer, every check, energy, charging, cost and all inputs with their sources.'],
  ['grid','Grid connection application','For the grid company. The figures it asks for at screening, with the load hour by hour.'],
  ['tender','Tender annex','For buyers and bidders. Requirements from your routes that every offer must meet.'],
  ['fin','Financial model','For the finance team. Electric against diesel, year by year, with every cost line.'],
  ['grant','Grant application data','For grant bodies. Vehicles, chargers and budget lines, ready to copy.'],
  ['deck','Client presentation','For management and politicians. The decision, the cost and the risks on one page.']];
function pageDocs(){
  return`<h1>Documents</h1><p class="lede">One run, six documents. Each opens ready to print or to save as a PDF, and uses run ${S.runNo}.</p>${stale()}
  <div class="doclist" style="margin-top:18px">${DOCS.map(d=>`<div class="setrow"><b>${d[1]}</b><span>${d[2]}</span><span><button class="btn" data-doc="${d[0]}">Open</button>${d[0]==='fin'?' <button class="lnk" data-csv style="margin-left:10px">Download CSV</button>':''}</span></div>`).join('')}</div>
  <p class="note" style="margin-top:18px">Every document is marked as a sample case with illustrative figures.</p>`;}
function buildDoc(k,R){
  const D=P.depot,run=S.runs[S.runs.length-1],today=new Date().toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'});
  const T=(h,rows)=>`<table><thead><tr>${h.map((x,i)=>`<th${i?' class="r"':''}>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map((x,i)=>`<td${i?' class="r"':''}>${x}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  const G=R.G,name=DOCS.find(d=>d[0]===k)[1];
  let h=`<h1>${name}</h1><div class="meta">${esc(D.name)}, ${esc(D.addr)} · ${R.N} vehicles · run ${run.n} · ${today} · EV Scope demo</div>`;
  const fleet=()=>T(['Group','Vehicles','Route','Hardest day','Battery','Charger'],G.map(g=>[esc(g.name),g.n,fmt(g.rt.km)+' km, '+fmt(g.rt.stops)+' stops',fmt(g.worst)+' kWh',fmt(g.batt)+' kWh',g.c.kw+' kW']));
  const checks=()=>T(['Check','Result','Detail'],R.checks.map(c=>[c.t,c.ok?'Passes':'Fails',esc(c.d)]));
  const cost=()=>T(['Cost, M DKK over '+R.Y+' years','Diesel','Electric'],R.cats.map(c=>[c[0],fmt(c[1]/1e6,2),fmt(c[2]/1e6,2)]).concat([['<b>Total</b>','<b>'+fmt(R.totD/1e6,1)+'</b>','<b>'+fmt(R.totE/1e6,1)+'</b>']]));
  if(k==='feas')h+=`<h2>1. Answer</h2><p><b>${R.title}.</b> ${R.text}</p><h2>2. Checks</h2>${checks()}<h2>3. Fleet</h2>${fleet()}
    <h2>4. Energy and battery</h2>${T(['Group','Average day','Hardest day','Per km','Usable at year 8'],G.map(g=>[esc(g.name),fmt(g.mean)+' kWh',fmt(g.worst)+' kWh',fmt(g.mean/g.rt.km,2)+' kWh',fmt(g.usableEol)+' kWh']))}
    <h2>5. Charging and grid</h2>${T(['Group','Charger','Charging','Leaves'],G.map(g=>[esc(g.name),g.n+' × '+g.c.kw+' kW',hm(g.c.start)+' to '+hm(g.c.end),hm(g.out)]))}<p>Depot peak ${fmt(R.peak)} kW${R.isNew?'':' against a connection of '+fmt(R.limit)+' kW'}. Charging plan: ${PLAN_N[R.plan].toLowerCase()}.</p>
    <h2>6. Cost</h2>${cost()}<p>${R.be?'Electric is ahead from year '+R.be+'.':'Electric is not ahead within the period.'}</p>
    <h2>7. CO₂</h2><p>Diesel fleet ${fmt(R.co2D)} t a year. Electric fleet ${fmt(R.co2E,1)} t in ${DEMO.elStart}. Saved over ${R.Y} years: ${fmt(R.co2Saved)} t. Production of trucks, batteries and diesel is not counted.</p>
    <h2>8. Inputs and sources</h2>${T(['Value','Used','Source'],run.rows.map(r=>[esc(r.where)+': '+esc(r.label),esc(r.value),r.radio?'Choice':SRCN[r.src]+(r.ref?'. '+esc(r.ref):'')]))}`;
  if(k==='grid'){const hr=[];for(let i=0;i<24;i++)hr.push([String(i).padStart(2,'0')+':00',fmt(Math.max(...R.load.slice(i*4,i*4+4)))+' kW']);
    h+=`<h2>Site</h2>${T(['Item','Value'],[['Depot',esc(D.name)],['Address',esc(D.addr)],['Grid company',({radius:'Radius',cerius:'Cerius',other:'Other'})[D.dso]],['Connection today',R.isNew?'None':fmt(R.limit)+' kW, about '+fmt(amps(R.limit))+' A'],['Power asked for',fmt(Math.ceil(R.peak/10)*10)+' kW, about '+fmt(amps(R.peak))+' A at 400 V'],['Load from buildings',fmt(D.base)+' kW']])}
    <h2>Chargers</h2>${T(['Group','Chargers','Power each','Charging hours'],G.map(g=>[esc(g.name),g.n,g.c.kw+' kW',hm(g.c.start)+' to '+hm(g.c.end)]))}
    <h2>Load on the hardest day</h2>${T(['Hour','Highest load'],hr)}<p>Full or limited grid access, the commissioning date and any grid services are agreed with the grid company and are not part of the demo.</p>`;}
  if(k==='tender')h+=`<h2>Requirements for each group</h2>${G.map(g=>`<p><b>${esc(g.name)}, ${g.n} vehicles</b></p>${T(['Requirement','Value'],[['Daily route',fmt(g.rt.km)+' km with '+fmt(g.rt.stops)+' stops'],['Away from the depot',hm(g.out)+' to '+hm(g.back)],['Energy on the hardest day',fmt(g.worst)+' kWh'],['Usable battery energy at year 8, at least',fmt(g.worst)+' kWh'],['Load to carry',fmt(g.payMax,1)+' t'],['Body equipment',SUMM.eq(g.e)],['Charging power at the depot, at least',g.c.kw+' kW'],['Time at the depot',fmt(g.dwellH,1)+' h']])}`).join('')}<p>Offers are compared on the same routes, the same weather year and the same battery age.</p>`;
  if(k==='fin')h+=`<h2>Totals</h2>${cost()}<h2>Year by year, thousand DKK</h2>${T(['Year','Financing','Chargers','Energy','Service','Road tax','Wages','Electric','Diesel'],R.rowsE.map((E,i)=>[E.yr,fmt(E.fin/1e3),fmt((E.chg+E.grant)/1e3),fmt(E.energy/1e3),fmt(E.svc/1e3),fmt(E.tax/1e3),fmt(E.wage/1e3),fmt(E.tot/1e3),fmt(R.rowsD[i].tot/1e3)]))}<p>Per km: electric ${fmt(R.totE/R.kmTot,2)} DKK, diesel ${fmt(R.totD/R.kmTot,2)} DKK. ${R.be?'Electric is ahead from year '+R.be+'.':''}</p>`;
  if(k==='grant'){const hw=sum(G.map(g=>g.n*band(g.c.kw)[1])),ins=sum(G.map(g=>g.n*band(g.c.kw)[2]));
    h+=`<h2>Vehicles and chargers</h2>${T(['Item','Value'],[['Vehicles charging each working day',R.N],['Chargers',G.map(g=>g.n+' × '+g.c.kw+' kW').join(', ')],['Charging site',esc(D.name)+', '+esc(D.addr)],['Ownership period',R.Y+' years']])}
    <h2>Budget lines, DKK</h2>${T(['Line','Amount'],[['Charger hardware',fmt(hw)],['Trenching and installation',fmt(ins)],['Grid connection',fmt(R.conn)],['Extra price of the electric trucks against diesel',fmt(sum(G.map(g=>g.n*(g.v.priceEV-g.v.priceD))))]])}<p>Check each amount against the supplier quotes before it goes into an application.</p>`;}
  if(k==='deck')h+=`<h2>The decision</h2><p><b>${R.title}.</b> ${R.text}</p>${fleet()}<h2>The cost</h2>${T(['Over '+R.Y+' years','M DKK'],[['Electric',fmt(R.totE/1e6,1)],['Diesel',fmt(R.totD/1e6,1)],['Difference',signed(-R.save/1e6,1)]])}<h2>The risks</h2>${checks()}`;
  return h+'<div class="foot">Sample case with illustrative figures from the EV Scope demo engine. Not a basis for decisions.</div>';}
function csv(R){const rows=[['Year','Financing','Chargers and connection','Electricity','Service and insurance','Road tax','Driver wages','Grant','Electric total','Diesel total','Saving']];
  R.rowsE.forEach((E,i)=>{const D=R.rowsD[i];rows.push([E.yr,E.fin,E.chg,E.energy,E.svc,E.tax,E.wage,E.grant,E.tot,D.tot,D.tot-E.tot].map(x=>Math.round(x)));});
  rows.push([]);rows.push(['Sample case with illustrative figures from the EV Scope demo engine. DKK, whole fleet.']);
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.map(r=>r.join(';')).join('\n')],{type:'text/csv'}));a.download='ev-scope-financial-model-run'+S.runNo+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);}

const PAGES={project:[pageProject],fleet:[pageFleet],templates:[pageTemplates],depot:[pageDepot],charging:[pageCharging],weather:[pageWeather],prices:[pagePrices],costs:[pageCosts],tax:[pageTax],check:[pageCheck],ov:[pageOv],en:[pageEn,drawEn],bat:[pageBat],ch:[pageCh],gr:[pageGr,drawGr],cost:[pageCost,drawCost],co2:[pageCo2],src:[pageSrc],cmp:[pageCmp],docs:[pageDocs]};
