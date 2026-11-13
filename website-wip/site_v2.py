# Second pass on the landing page (13 Nov 2026, after Bob's feedback): what is sold is said plainly,
# every audience has its own part that can be reached in one click, the cursor tiles are gone,
# and the documents can be picked.
import json, pathlib
PK = json.loads(pathlib.Path('/home/claude/work/peek.json').read_text())
BATT = PK['fv'][0].replace('kWh', ''); PEAK = PK['fv'][2].replace('kW', ''); LIM = PK['fn'][2].split('the ')[1].split(' kW')[0]
WORST = PK['row'][4].replace(' kWh', ''); CHG = PK['row'][6].replace(' kW', '')

HERO_SUB = 'EV Scope works out the battery, the chargers and the grid connection your vehicles need, from your own routes. Before you order anything.'
EX_FLEET = 'Six refuse trucks on a 120 km city round with 400 stops. Each needs a %s kWh battery. The depot peaks at %s kW, inside the %s kW it already has.' % (BATT, PEAK, LIM)
EX_MUNI = 'From the tender annex of the sample case: usable battery at year 8 of at least %s kWh, and at least %s kW of charging at the depot.' % (WORST, CHG)
SAMPLE = 'Sample case with illustrative figures.'
NOTRES = 'An example of the question, not a result.'

AUD = [
 dict(id='fleet-owners', tab='Fleet owners', h='For fleet owners',
      hook='Buy the battery your routes need, not the one in the brochure',
      does='Too small and a truck does not finish a winter shift. Too big and you pay for weight you never use. EV Scope sizes the battery, the chargers and the grid connection from your own routes, before you order.',
      q=['How much battery do our vehicles actually need?', 'Will they finish a full winter shift?', 'Do we have to upgrade the grid connection?'],
      ex=EX_FLEET, note=SAMPLE, demo=True, docs=[(0, 'Feasibility report'), (3, 'Financial model')], img=(25, 26)),
 dict(id='housing', tab='Housing associations', h='For housing associations',
      hook='From 2026, residents have the right to charge',
      does='When everyone plugs in after work, the supply to the building sets the limit. EV Scope shows how much charging it can carry today, and what a larger connection would take.',
      q=['How much charging can our supply actually carry?', 'What happens when everyone plugs in after work?', 'Do we need a larger incoming connection?'],
      ex='A car park on one shared supply. You see how many charge points fit today, what the evening looks like when everyone is home, and the connection size the rest would need.', note=NOTRES, demo=False,
      docs=[(0, 'Feasibility report'), (1, 'Grid connection application')], img=(27, 28)),
 dict(id='municipalities', tab='Municipalities', h='For municipalities',
      hook='A tender that holds, inside a budget that is already fixed',
      does='You buy in fixed budget years and cannot favour a brand. EV Scope turns your routes into requirements that every bidder is measured against, and shows which vehicles can switch now and which should wait.',
      q=['Which vehicles can we electrify now, and which wait?', 'Can we spread the spend across budget years?', 'Will this hold up if a supplier complains?'],
      ex=EX_MUNI, note=SAMPLE, demo=True, docs=[(2, 'Tender annex'), (4, 'Grant application data')], img=(29, 30)),
 dict(id='suppliers', tab='Truck makers and charge operators', h='For truck makers and charge operators',
      hook='Show the buyer it works on their routes, not on a test cycle',
      does='Buyers ask whether your truck finishes their hardest winter day, and still does at year 8. EV Scope runs your spec on their routes, on the same case as every other bid. Charge operators get the load of the depot hour by hour, to size the site and its connection.',
      q=["Will our truck finish the buyer's hardest winter route?", 'Does our battery still meet the tender at year 8?', 'How much power does the depot need, and at what hours?'],
      ex='A tender asks for the hardest winter route at year 8. You run your truck on that route and hand over the result with every input shown.', note=NOTRES, demo=False,
      docs=[(2, 'Tender annex'), (5, 'Client presentation')], img=(31, 32)),
]

def who_section():
    tabs = ''.join('<button role="tab">%s<i></i></button>' % a['tab'] for a in AUD)
    pan = ''
    for i, a in enumerate(AUD):
        pan += '''
      <div class="apanel%s" id="%s" role="tabpanel">
        <div class="acopy">
          <h3>%s</h3>
          <p class="hook">%s</p>
          <p class="does">%s</p>
          <h4>What you get answered</h4>
          <ul>%s</ul>
          <h4>Documents you can take away</h4>
          <div class="adocs">%s<a class="lnk" href="#documents">See all six</a></div>
        </div>
        <div class="aside">
          <div class="aveh" aria-hidden="true"><img class="d" src="data:image/webp;base64,[[IMG%d]]" alt=""><img class="n" src="data:image/webp;base64,[[IMG%d]]" alt=""></div>
          <div class="aex"><h4>Example</h4><p>%s</p><p class="exn"><span>%s</span>%s</p></div>
        </div>
      </div>''' % (' on' if i == 0 else '', a['id'], a['h'], a['hook'], a['does'], ''.join('<li>%s</li>' % q for q in a['q']),
                   ''.join('<button type="button" class="dbtn" data-doc="%d">%s</button>' % d for d in a['docs']),
                   a['img'][0], a['img'][1], a['ex'], a['note'], ' <a href="#app">Open this case in the demo</a>' if a['demo'] else '')
    return '''
<section class="who" id="for">
  <div class="wrap">
    <div class="whotop rv">
      <h2>What it does for you</h2>
      <div class="switch c" data-switch="who"><div class="sw-track" role="tablist" aria-label="Who it's for">%s</div></div>
    </div>
    <div class="apanels">%s
    </div>
  </div>
</section>
''' % (tabs, pan)

HERO_PICK = '<p class="pick in" style="animation-delay:.5s"><span>See what it does for</span>' + ''.join('<a href="#%s">%s</a>' % (a['id'], a['tab']) for a in AUD) + '</p>'

STORY = [  # (old h3, old p, new h3, new p)
 ('Every route, every stop, every&nbsp;day', 'Your real operation goes in first: routes, stops, payload and the hours trucks spend away from the depot.',
  'It starts with your routes, not a brochure&nbsp;range', 'Enter the routes, stops, loads and shift times your vehicles really drive. Everything else is worked out from them.'),
 ('While the city sleeps, the depot&nbsp;charges', 'Trucks plug in when the shift ends. EV Scope plans the night so every one is full by morning, under the grid limit.',
  'A truck that is not full by morning stays in the&nbsp;depot', 'EV Scope checks that every vehicle is full before its shift, with the depot kept under its grid limit.'),
 ('Will the battery last the&nbsp;route?', 'Every route checked against the battery, with charge to spare when the truck is back.',
  'Too small and the route fails. Too big and you pay for&nbsp;weight', 'EV Scope sizes the battery to your hardest route, so you compare offers on what you need.'),
 ('And on the coldest day, at year&nbsp;8?', 'Cold air, cabin heating and an aged battery, together. No optimistic averages.',
  'The coldest day at year 8 is the one that strands a&nbsp;truck', 'Cold air, cabin heating and an aged battery are tested together, so you see the worst day before you buy.'),
 ('How big do the chargers need to&nbsp;be?', 'Just big enough to have every truck full before the morning shift. Parked overnight, even the smallest one is enough.',
  'Bigger chargers cost more and can force a grid&nbsp;upgrade', 'EV Scope finds the smallest charger that still has every truck full before its shift. Parked overnight, a small one is often enough.'),
 ('How much can it still&nbsp;carry?', 'Batteries weigh. See the payload left on every route, before you order.',
  'A heavier battery can leave less room for&nbsp;cargo', 'Try light, full and changing loads on each route and see the payload left, before you order.'),
 ('When can the grid connect&nbsp;you?', 'Waits run from months to years. Apply early, with the numbers already done.',
  'A grid connection can take months or&nbsp;years', 'EV Scope gives you the power to apply for and the load hour by hour, so you can apply early with the numbers done.'),
]

PEEK_ALT2 = [
  "The fleet page of the demo: two groups of refuse trucks, each with a vehicle, a route, a load, body equipment and a shift",
  "The overview page of the demo: all six vehicles can run electric, with battery size, chargers, depot peak and cost against diesel",
  "The cost page of the demo: electric against diesel year by year and by cost line",
]
def peek_section2():
    imgs = ''.join('<img%s src="data:image/webp;base64,[[PEEK%d]]" alt="%s" width="1800" height="1080" decoding="async">' % (' class="on"' if i == 0 else '', i, a) for i, a in enumerate(PEEK_ALT2))
    return '''
<section class="peek" id="demo">
  <div class="wrap">
    <div class="center rv"><h2>See it on a sample&nbsp;depot</h2><p class="lead">Six refuse trucks, from the fleet table to the answer. Illustrative figures.</p></div>
    <div class="peekwin rv"><div class="peekstage" id="peekstage">''' + imgs + '''<span class="pclick" id="pclick" aria-hidden="true"></span><svg class="pcur" id="pcur" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 2l13 7.2-5.6 1.5L8 16.5z" fill="#12182B" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg></div></div>
    <div class="switch c rv" data-switch="peek">
      <div class="sw-track" role="tablist" aria-label="Tool preview"><button role="tab">Your fleet<i></i></button><button role="tab">The answer<i></i></button><button role="tab">The cost<i></i></button></div>
    </div>
    <p class="cta rv"><a class="btn" href="#app">Try the demo <span class="ar" aria-hidden="true">→</span></a></p>
  </div>
</section>
'''

PEEK_JS2 = r"""
  /* ---------- tool preview: three real screens from the demo. The cursor rests on the figure that matters, then clicks on ---------- */
  var PK=$('peekstage'), pimgs=[].slice.call(PK.querySelectorAll('img')), pcur=$('pcur'), pclk=$('pclick');
  var PTS=__PTS__, STEP=7200, pkOn=false, pkT=0, pkHold=0, pkPh=0, pkRaf=0;
  function pkPlace(p){ pcur.style.left=p[0]+'%'; pcur.style.top=p[1]+'%'; }
  var peek=Switch(document.querySelector('[data-switch="peek"]'),null,function(n,src){
    pimgs.forEach(function(im,k){ im.classList.toggle('on',k===n) }); pkPh=0; pkT=performance.now();
    if(src==='user') pkHold=pkT+9000;
  });
  peek.set(0); peek.progress(reduce?1:0); pkPlace([62,60]);
  function pkFrame(now){
    pkRaf=0; if(!pkOn) return;
    if(now<pkHold){ peek.progress(1); pkT=now; }
    else { var el=(now-pkT)/STEP; peek.progress(el);
      if(el>.12&&pkPh<1){ pkPh=1; pkPlace(PTS[peek.i][0]) }
      if(el>.6&&pkPh<2){ pkPh=2; pkPlace(PTS[peek.i][1]) }
      if(el>.82&&pkPh<3){ pkPh=3; pclk.style.left=PTS[peek.i][1][0]+'%'; pclk.style.top=PTS[peek.i][1][1]+'%'; pclk.classList.remove('go'); void pclk.offsetWidth; pclk.classList.add('go') }
      if(el>=.9) peek.set(peek.i+1,'auto');
    }
    pkRaf=requestAnimationFrame(pkFrame);
  }
  inView(PK,function(v){ pkOn=v&&!reduce; if(pkOn&&!pkRaf){ pkT=performance.now(); pkPh=0; pkRaf=requestAnimationFrame(pkFrame) } },.3);
"""

WHO_JS = r"""
  /* ---------- who it is for: one part for each kind of reader, reachable by tab, by link and by address ---------- */
  var apanels=[].slice.call(document.querySelectorAll('.apanel')), AIDS=apanels.map(function(p){ return p.id }), whoSec=$('for');
  var who=Switch(document.querySelector('[data-switch="who"]'),null,function(n,src){
    apanels.forEach(function(p,k){ p.classList.toggle('on',k===n) }); who.progress(1);
    if(src==='user'&&history.replaceState) history.replaceState(null,'','#'+AIDS[n]);
  },function(k){ who.set((k+4)%4,'user') });
  who.set(0);
  function goWho(id,jump){ var k=AIDS.indexOf(id); if(k<0) return false; who.set(k); who.progress(1);
    var y=whoSec.getBoundingClientRect().top+scrollY-(innerWidth<760?56:20); scrollTo({top:y,behavior:jump||reduce?'instant':'smooth'}); return true }
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[href^="#"]'); if(a&&AIDS.indexOf(a.getAttribute('href').slice(1))>=0&&!body.className.match(/page-/)){ e.preventDefault(); var id=a.getAttribute('href').slice(1); if(history.pushState) history.pushState(null,'','#'+id); setMenu(false); goWho(id) ; return }
    var d=e.target.closest('.dbtn'); if(d){ doc.set(+d.dataset.doc,'user'); var y=dsec.getBoundingClientRect().top+scrollY-10; scrollTo({top:y,behavior:reduce?'instant':'smooth'}) }
  });
"""

CSS2 = r"""
/* ===== second pass: clearer hierarchy, a part for each reader ===== */
.glyphs{display:none}
.hero{padding-top:calc(var(--hh) + 84px)}
.hero p.sub{margin:24px auto 30px;max-width:640px;font-size:clamp(18px,1.6vw,21px);color:var(--slate)}
.hero .cta-row{margin-top:0}
.hero .pick{margin:34px auto 0;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:10px;font-size:15px;color:var(--muted)}
.hero .pick span{margin-right:6px}
.hero .pick a{padding:9px 15px;border-radius:9px;background:var(--bg);box-shadow:inset 0 0 0 1px var(--line);color:var(--ink);font-weight:500;transition:box-shadow .2s,color .2s}
.hero .pick a:hover{box-shadow:inset 0 0 0 1.5px var(--accent);color:var(--accent)}
.hero-depot{margin-top:40px}
.who{padding:96px 0 110px;scroll-margin-top:20px}
.whotop{display:flex;flex-direction:column;align-items:center;gap:20px}
.whotop h2{font-size:17px;line-height:1.3;font-weight:500;color:var(--muted)}
.who .switch{margin:0;max-width:100%}
.apanels{margin-top:64px}
.apanel{display:none;grid-template-columns:minmax(0,6fr) minmax(0,5fr);gap:72px;align-items:start}
.apanel.on{display:grid;animation:afade .5s ease both}
@keyframes afade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.apanel h3{font-size:clamp(30px,3.5vw,48px);line-height:1.06;font-weight:600;margin:0 0 20px;text-wrap:balance}
.apanel .hook{font-size:clamp(19px,1.7vw,23px);line-height:1.3;font-weight:500;color:var(--ink);margin:0 0 14px;max-width:30em;text-wrap:balance}
.apanel .does{font-size:17px;line-height:1.55;color:var(--muted);margin:0 0 36px;max-width:56ch}
.apanel h4{font-size:14px;font-weight:600;color:var(--ink);margin:0 0 12px}
.apanel ul{list-style:none;padding:0;margin:0 0 34px}
.apanel li{position:relative;padding-left:24px;margin-bottom:9px;font-size:16.5px}
.apanel li::before{content:"";position:absolute;left:0;top:.72em;width:12px;height:1.5px;background:var(--accent)}
.adocs{display:flex;flex-wrap:wrap;gap:10px 12px;align-items:center}
.dbtn{font:500 15px/1 'IBM Plex Sans',system-ui,sans-serif;color:var(--ink);padding:12px 16px;border:0;border-radius:9px;background:var(--bg);box-shadow:inset 0 0 0 1px var(--line);cursor:pointer;transition:box-shadow .2s,color .2s}
.dbtn::after{content:"→";margin-left:9px;color:var(--accent)}
.dbtn:hover{box-shadow:inset 0 0 0 1.5px var(--accent);color:var(--accent)}
.adocs .lnk{margin-left:8px;font-size:15px;color:var(--accent);text-decoration:underline;text-underline-offset:4px;text-decoration-color:var(--line)}
.aveh{position:relative;height:clamp(180px,24vw,280px);display:flex;align-items:center;justify-content:center}
.aveh img{max-width:100%;max-height:100%;width:auto;height:auto}
.aveh .n{position:absolute;inset:0;margin:auto;display:none}
[data-theme=night] .aveh .d{display:none}[data-theme=night] .aveh .n{display:block;position:static}
.aex{margin-top:26px;padding:22px 24px 20px;background:var(--tint);border-radius:12px}
.aex h4{margin-bottom:8px}
.aex p{margin:0;font-size:16.5px;line-height:1.5;color:var(--ink)}
.aex .exn{margin-top:12px;font-size:13.5px;color:var(--faint)}
.aex .exn a{color:var(--accent);text-decoration:underline;text-underline-offset:3px;margin-left:6px;white-space:nowrap}
/* the story: the hook is the headline, what the tool does sits under it */
.ch h3{font-size:clamp(25px,2.7vw,38px);line-height:1.1;margin-bottom:16px}
.ch p{font-size:17.5px;line-height:1.5}
/* documents: no longer pinned, pick any */
.docs{height:auto;padding:104px 0 96px;overflow:hidden}
.docs .pin{position:static;height:auto;padding:0;display:block;overflow:visible}
.docs .fanbox{margin-top:34px}
.peek{padding:110px 0 100px}
.pcur{transition:left 1.5s cubic-bezier(.45,.05,.2,1),top 1.5s cubic-bezier(.45,.05,.2,1)}
.peek .switch{margin-top:24px}
@media (max-width:900px){
  .apanel{grid-template-columns:1fr;gap:34px}
  .aveh{display:none}.aex{margin-top:0}
  .apanel h3{margin-bottom:14px}
  .who .sw-track{display:grid;grid-template-columns:1fr 1fr;width:100%}
  .who .sw-track button{white-space:normal;line-height:1.2;padding:10px 8px;min-height:44px}
  .apanels{margin-top:40px}
  .who{padding:70px 0 80px}
  .hero .pick a{padding:8px 12px;font-size:14px}
}
"""

NEW2 = {
 'The tool': {'da':'Værktøjet','de':'Das Tool','nl':'De tool'},
 HERO_SUB: {'da':'EV Scope beregner det batteri, de ladere og den nettilslutning, dine køretøjer har brug for, ud fra dine egne ruter. Før du bestiller noget.','de':'EV Scope ermittelt die Batterie, die Ladestationen und den Netzanschluss, die Ihre Fahrzeuge brauchen, aus Ihren eigenen Routen. Bevor Sie etwas bestellen.','nl':'EV Scope berekent de batterij, de laders en de netaansluiting die je voertuigen nodig hebben, op basis van je eigen routes. Voordat je iets bestelt.'},
 'See what it does for': {'da':'Se, hvad det gør for','de':'Sehen Sie, was es bringt für','nl':'Bekijk wat het doet voor'},
 'Truck makers and charge operators': {'da':'Lastbilproducenter og ladeoperatører','de':'Lkw-Hersteller und Ladebetreiber','nl':'Truckfabrikanten en laadexploitanten'},
 'What it does for you': {'da':'Hvad det gør for dig','de':'Was es für Sie tut','nl':'Wat het voor jou doet'},
 'What you get answered': {'da':'Det får du svar på','de':'Darauf erhalten Sie Antworten','nl':'Hierop krijg je antwoord'},
 'Documents you can take away': {'da':'Dokumenter, du kan tage med','de':'Dokumente zum Mitnehmen','nl':'Documenten die je kunt meenemen'},
 'See all six': {'da':'Se alle seks','de':'Alle sechs ansehen','nl':'Bekijk alle zes'},
 'Example': {'da':'Eksempel','de':'Beispiel','nl':'Voorbeeld'},
 'Open this case in the demo': {'da':'Åbn eksemplet i demoen','de':'Diesen Fall in der Demo öffnen','nl':'Open dit voorbeeld in de demo'},
 SAMPLE: {'da':'Eksempel med illustrative tal.','de':'Beispielfall mit illustrativen Zahlen.','nl':'Voorbeeldcase met illustratieve cijfers.'},
 NOTRES: {'da':'Et eksempel på spørgsmålet, ikke et resultat.','de':'Ein Beispiel für die Frage, kein Ergebnis.','nl':'Een voorbeeld van de vraag, geen resultaat.'},
 'For fleet owners': {'da':'For flådeejere','de':'Für Flottenbetreiber','nl':'Voor vlooteigenaren'},
 'For housing associations': {'da':'For boligforeninger','de':'Für Wohnungsgesellschaften','nl':'Voor woningcorporaties'},
 'For municipalities': {'da':'For kommuner','de':'Für Kommunen','nl':'Voor gemeenten'},
 'For truck makers and charge operators': {'da':'For lastbilproducenter og ladeoperatører','de':'Für Lkw-Hersteller und Ladebetreiber','nl':'Voor truckfabrikanten en laadexploitanten'},
 AUD[0]['hook']: {'da':'Køb det batteri, dine ruter kræver, ikke det fra brochuren','de':'Kaufen Sie die Batterie, die Ihre Routen brauchen, nicht die aus dem Prospekt','nl':'Koop de batterij die je routes nodig hebben, niet die uit de brochure'},
 AUD[0]['does']: {'da':'For lille, og en lastbil gennemfører ikke en vintervagt. For stor, og du betaler for vægt, du aldrig bruger. EV Scope dimensionerer batteri, ladere og nettilslutning ud fra dine egne ruter, før du bestiller.','de':'Zu klein, und ein Lkw schafft die Winterschicht nicht. Zu groß, und Sie zahlen für Gewicht, das Sie nie nutzen. EV Scope legt Batterie, Ladestationen und Netzanschluss anhand Ihrer eigenen Routen aus, bevor Sie bestellen.','nl':'Te klein en een truck haalt een winterdienst niet. Te groot en je betaalt voor gewicht dat je nooit gebruikt. EV Scope bepaalt batterij, laders en netaansluiting op basis van je eigen routes, voordat je bestelt.'},
 EX_FLEET: {'da':'Seks renovationsbiler på en byrute på 120 km med 400 stop. Hver har brug for et batteri på %s kWh. Depotet topper ved %s kW, inden for de %s kW, det allerede har.' % (BATT, PEAK, LIM),'de':'Sechs Müllfahrzeuge auf einer 120-km-Stadtrunde mit 400 Stopps. Jedes braucht eine Batterie mit %s kWh. Das Depot erreicht in der Spitze %s kW, innerhalb der %s kW, die es bereits hat.' % (BATT, PEAK, LIM),'nl':'Zes vuilniswagens op een stadsronde van 120 km met 400 stops. Elk heeft een batterij van %s kWh nodig. Het depot piekt op %s kW, binnen de %s kW die het al heeft.' % (BATT, PEAK, LIM)},
 AUD[1]['does']: {'da':'Når alle sætter stikket i efter arbejde, er det bygningens forsyning, der sætter grænsen. EV Scope viser, hvor meget ladning den kan bære i dag, og hvad en større tilslutning vil kræve.','de':'Wenn alle nach der Arbeit laden, setzt die Versorgung des Gebäudes die Grenze. EV Scope zeigt, wie viel Laden sie heute trägt und was ein größerer Anschluss erfordern würde.','nl':'Als iedereen na het werk inplugt, bepaalt de aansluiting van het gebouw de grens. EV Scope laat zien hoeveel laden die vandaag aankan, en wat een grotere aansluiting zou vragen.'},
 AUD[1]['ex']: {'da':'En parkeringsplads på én fælles forsyning. Du ser, hvor mange ladepunkter der er plads til i dag, hvordan aftenen ser ud, når alle er hjemme, og hvilken tilslutning resten vil kræve.','de':'Ein Parkplatz an einer gemeinsamen Versorgung. Sie sehen, wie viele Ladepunkte heute passen, wie der Abend aussieht, wenn alle zu Hause sind, und welche Anschlussgröße der Rest bräuchte.','nl':'Een parkeerterrein op één gedeelde aansluiting. Je ziet hoeveel laadpunten er vandaag passen, hoe de avond eruitziet als iedereen thuis is, en welke aansluiting de rest nodig zou hebben.'},
 AUD[2]['hook']: {'da':'Et udbud, der holder, inden for et budget, der allerede ligger fast','de':'Eine Ausschreibung, die hält, in einem Haushalt, der schon feststeht','nl':'Een aanbesteding die standhoudt, binnen een begroting die al vastligt'},
 AUD[2]['does']: {'da':'I køber ind i faste budgetår og må ikke favorisere et mærke. EV Scope omsætter jeres ruter til krav, som alle tilbudsgivere måles på, og viser, hvilke køretøjer der kan skifte nu, og hvilke der bør vente.','de':'Sie beschaffen in festen Haushaltsjahren und dürfen keine Marke bevorzugen. EV Scope macht aus Ihren Routen Anforderungen, an denen jeder Bieter gemessen wird, und zeigt, welche Fahrzeuge jetzt umsteigen können und welche warten sollten.','nl':'Je koopt in vaste begrotingsjaren en mag geen merk bevoordelen. EV Scope zet je routes om in eisen waaraan elke inschrijver wordt getoetst, en laat zien welke voertuigen nu kunnen overstappen en welke beter wachten.'},
 EX_MUNI: {'da':'Fra eksemplets udbudsbilag: brugbart batteri i år 8 på mindst %s kWh og mindst %s kW ladeeffekt på depotet.' % (WORST, CHG),'de':'Aus der Ausschreibungsanlage des Beispielfalls: nutzbare Batterie im Jahr 8 von mindestens %s kWh und mindestens %s kW Ladeleistung im Depot.' % (WORST, CHG),'nl':'Uit de aanbestedingsbijlage van de voorbeeldcase: bruikbare batterij in jaar 8 van minstens %s kWh, en minstens %s kW laadvermogen op het depot.' % (WORST, CHG)},
 AUD[3]['hook']: {'da':'Vis køberen, at det virker på deres ruter, ikke på en testcyklus','de':'Zeigen Sie dem Käufer, dass es auf seinen Routen funktioniert, nicht auf einem Testzyklus','nl':'Laat de koper zien dat het werkt op zijn routes, niet op een testcyclus'},
 AUD[3]['does']: {'da':'Købere spørger, om jeres lastbil klarer deres hårdeste vinterdag, og stadig gør det i år 8. EV Scope kører jeres specifikation på deres ruter, på samme case som alle andre tilbud. Ladeoperatører får depotets belastning time for time til at dimensionere anlægget og tilslutningen.','de':'Käufer fragen, ob Ihr Lkw ihren härtesten Wintertag schafft, und das auch im Jahr 8. EV Scope rechnet Ihre Spezifikation auf deren Routen, im selben Fall wie jedes andere Angebot. Ladebetreiber erhalten die Last des Depots Stunde für Stunde, um Standort und Anschluss auszulegen.','nl':'Kopers vragen of je truck hun zwaarste winterdag haalt, en dat in jaar 8 nog steeds doet. EV Scope rekent jouw specificatie door op hun routes, op dezelfde case als elke andere inschrijving. Laadexploitanten krijgen de belasting van het depot van uur tot uur, om de locatie en de aansluiting te bepalen.'},
 'How much power does the depot need, and at what hours?': {'da':'Hvor meget effekt har depotet brug for, og på hvilke tidspunkter?','de':'Wie viel Leistung braucht das Depot, und zu welchen Stunden?','nl':'Hoeveel vermogen heeft het depot nodig, en op welke uren?'},
 AUD[3]['ex']: {'da':'Et udbud beder om den hårdeste vinterrute i år 8. I kører jeres lastbil på den rute og afleverer resultatet med alle input vist.','de':'Eine Ausschreibung verlangt die härteste Winterroute im Jahr 8. Sie rechnen Ihren Lkw auf dieser Route und übergeben das Ergebnis mit allen Eingaben.','nl':'Een aanbesteding vraagt om de zwaarste winterroute in jaar 8. Je rekent je truck door op die route en levert het resultaat met alle invoer erbij.'},
 'It starts with your routes, not a brochure range': {'da':'Det begynder med dine ruter, ikke en rækkevidde fra brochuren','de':'Es beginnt mit Ihren Routen, nicht mit einer Prospektreichweite','nl':'Het begint bij je routes, niet bij een actieradius uit de brochure'},
 STORY[0][3]: {'da':'Indtast de ruter, stop, laster og vagttider, dine køretøjer faktisk kører. Alt andet beregnes ud fra dem.','de':'Geben Sie die Routen, Stopps, Ladungen und Schichtzeiten ein, die Ihre Fahrzeuge wirklich fahren. Alles andere wird daraus berechnet.','nl':'Voer de routes, stops, ladingen en diensttijden in die je voertuigen echt rijden. Al het andere wordt daaruit berekend.'},
 'A truck that is not full by morning stays in the depot': {'da':'En lastbil, der ikke er fuldt opladet om morgenen, bliver på depotet','de':'Ein Lkw, der morgens nicht voll ist, bleibt im Depot','nl':'Een truck die ’s ochtends niet vol is, blijft op het depot'},
 STORY[1][3]: {'da':'EV Scope tjekker, at hvert køretøj er fuldt opladet før sin vagt, mens depotet holdes under sin netgrænse.','de':'EV Scope prüft, dass jedes Fahrzeug vor seiner Schicht voll ist und das Depot unter seiner Netzgrenze bleibt.','nl':'EV Scope controleert dat elk voertuig vol is vóór zijn dienst, terwijl het depot onder zijn netlimiet blijft.'},
 'Too small and the route fails. Too big and you pay for weight': {'da':'For lille, og ruten fejler. For stor, og du betaler for vægt','de':'Zu klein, und die Route scheitert. Zu groß, und Sie zahlen für Gewicht','nl':'Te klein en de route mislukt. Te groot en je betaalt voor gewicht'},
 STORY[2][3]: {'da':'EV Scope dimensionerer batteriet efter din hårdeste rute, så du sammenligner tilbud ud fra det, du har brug for.','de':'EV Scope legt die Batterie nach Ihrer härtesten Route aus, damit Sie Angebote an Ihrem Bedarf messen.','nl':'EV Scope bepaalt de batterij op je zwaarste route, zodat je offertes vergelijkt op wat je nodig hebt.'},
 'The coldest day at year 8 is the one that strands a truck': {'da':'Den koldeste dag i år 8 er den, der efterlader en lastbil på ruten','de':'Der kälteste Tag im Jahr 8 ist der, an dem ein Lkw liegen bleibt','nl':'De koudste dag in jaar 8 is de dag waarop een truck strandt'},
 STORY[3][3]: {'da':'Kold luft, kabinevarme og et ældet batteri testes sammen, så du ser den værste dag, før du køber.','de':'Kalte Luft, Kabinenheizung und eine gealterte Batterie werden zusammen geprüft, damit Sie den schlimmsten Tag vor dem Kauf sehen.','nl':'Koude lucht, cabineverwarming en een verouderde batterij worden samen getest, zodat je de zwaarste dag ziet voordat je koopt.'},
 'Bigger chargers cost more and can force a grid upgrade': {'da':'Større ladere koster mere og kan fremtvinge en netudvidelse','de':'Größere Ladestationen kosten mehr und können einen Netzausbau erzwingen','nl':'Grotere laders kosten meer en kunnen een netverzwaring afdwingen'},
 STORY[4][3]: {'da':'EV Scope finder den mindste lader, der stadig har hver lastbil fuldt opladet før vagten. Parkeret natten over er en lille ofte nok.','de':'EV Scope findet die kleinste Ladestation, mit der jeder Lkw vor seiner Schicht noch voll ist. Über Nacht geparkt reicht oft eine kleine.','nl':'EV Scope vindt de kleinste lader waarmee elke truck nog vol is vóór zijn dienst. Als hij ’s nachts geparkeerd staat, is een kleine vaak genoeg.'},
 'A heavier battery can leave less room for cargo': {'da':'Et tungere batteri kan give mindre plads til last','de':'Eine schwerere Batterie kann weniger Platz für Ladung lassen','nl':'Een zwaardere batterij kan minder ruimte voor lading laten'},
 STORY[5][3]: {'da':'Prøv let, fuld og skiftende last på hver rute, og se den resterende nyttelast, før du bestiller.','de':'Testen Sie leichte, volle und wechselnde Ladungen auf jeder Route und sehen Sie die verbleibende Nutzlast, bevor Sie bestellen.','nl':'Probeer lichte, volle en wisselende lading op elke route en zie het resterende laadvermogen, voordat je bestelt.'},
 'A grid connection can take months or years': {'da':'En nettilslutning kan tage måneder eller år','de':'Ein Netzanschluss kann Monate oder Jahre dauern','nl':'Een netaansluiting kan maanden of jaren duren'},
 STORY[6][3]: {'da':'EV Scope giver dig den effekt, du skal søge om, og belastningen time for time, så du kan søge tidligt med tallene klar.','de':'EV Scope liefert die zu beantragende Leistung und die Last Stunde für Stunde, damit Sie früh und mit fertigen Zahlen beantragen können.','nl':'EV Scope geeft je het aan te vragen vermogen en de belasting van uur tot uur, zodat je vroeg kunt aanvragen met de cijfers klaar.'},
 'Pick the document you need': {'da':'Vælg det dokument, du har brug for','de':'Wählen Sie das Dokument, das Sie brauchen','nl':'Kies het document dat je nodig hebt'},
 'One run gives all six. Choose the one your reader signs.': {'da':'Én kørsel giver alle seks. Vælg det, din modtager skriver under på.','de':'Ein Durchlauf liefert alle sechs. Wählen Sie das, das Ihr Leser unterschreibt.','nl':'Eén run levert alle zes. Kies het document dat je lezer ondertekent.'},
 'See it on a sample depot': {'da':'Se det på et eksempeldepot','de':'Sehen Sie es an einem Beispieldepot','nl':'Bekijk het op een voorbeelddepot'},
 'Six refuse trucks, from the fleet table to the answer. Illustrative figures.': {'da':'Seks renovationsbiler, fra flådetabel til svar. Illustrative tal.','de':'Sechs Müllfahrzeuge, von der Flottentabelle bis zur Antwort. Illustrative Zahlen.','nl':'Zes vuilniswagens, van vloottabel tot antwoord. Illustratieve cijfers.'},
 'Your fleet': {'da':'Din flåde','de':'Ihre Flotte','nl':'Je vloot'},
 'The answer': {'da':'Svaret','de':'Die Antwort','nl':'Het antwoord'},
 'The cost': {'da':'Økonomien','de':'Die Kosten','nl':'De kosten'},
}
