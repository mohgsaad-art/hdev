# Second pass on the landing page (13 Nov 2026, after Bob's feedback): what is sold is said plainly,
# every audience has its own part that can be reached in one click, the cursor tiles are gone,
# and the documents can be picked.
import json, pathlib
PK = json.loads(pathlib.Path('/home/claude/work/peek.json').read_text())
BATT = PK['fv'][0].replace('kWh', ''); PEAK = PK['fv'][2].replace('kW', ''); LIM = PK['fn'][2].split('the ')[1].split(' kW')[0]
WORST = PK['row'][4].replace(' kWh', ''); CHG = PK['row'][6].replace(' kW', '')

HERO_SUB = 'Battery, charger and grid sizing for electric fleets, worked out from your own routes.'
EX_FLEET = 'Six refuse trucks on a 120 km city round with 400 stops. Each needs a %s kWh battery. The depot peaks at %s kW, inside the %s kW it already has.' % (BATT, PEAK, LIM)
EX_MUNI = 'From the tender annex of the sample case: usable battery at year 8 of at least %s kWh, and at least %s kW of charging at the depot.' % (WORST, CHG)
SAMPLE = 'Sample case with illustrative figures.'
NOTRES = 'An example of the question, not a result.'

AUD = [
 dict(id='fleet-owners', tab='Fleet owners', h='For fleet owners',
      does='EV Scope works out the battery size, the charger size and the grid connection for your vehicles, from the routes they drive.',
      q=['How much battery do our vehicles actually need?', 'Will they still finish a winter shift at year 8?', 'Do we have to upgrade the grid connection?'],
      ex=EX_FLEET, note=SAMPLE, demo=True, img=(25, 26)),
 dict(id='housing', tab='Housing associations', h='For housing associations',
      does='From 2026, residents have the right to charge. EV Scope works out how much charging the supply to the building can carry, and what a larger connection would take.',
      q=['How much charging can our supply actually carry?', 'What happens when everyone plugs in after work?', 'Do we need a larger incoming connection?'],
      ex='A car park on one shared supply. You see how many charge points fit today, what the evening looks like when everyone is home, and the connection size the rest would need.', note=NOTRES, demo=False, img=(27, 28)),
 dict(id='municipalities', tab='Municipalities', h='For municipalities',
      does='EV Scope turns your routes into requirements for a tender, the same for every bidder, and shows which vehicles can be electrified in which budget year.',
      q=['Which vehicles can we electrify now, and which wait?', 'Can we spread the spend across budget years?', 'Will this hold up if a supplier complains?'],
      ex=EX_MUNI, note=SAMPLE, demo=True, img=(29, 30)),
 dict(id='suppliers', tab='Truck makers and charge operators', h='For truck makers and charge operators',
      does="EV Scope runs your vehicle on the buyer's routes, so both sides look at the same case. Charge operators get the load of the depot hour by hour.",
      q=["Will our truck finish the buyer's hardest winter route?", 'Does our battery still meet the tender at year 8?', 'How much power does the depot need, and at what hours?'],
      ex='A tender asks for the hardest winter route at year 8. You run your truck on that route and hand over the result with every input shown.', note=NOTRES, demo=False, img=(31, 32)),
]

def who_section():
    tabs = ''.join('<button role="tab">%s<i></i></button>' % a['tab'] for a in AUD)
    pan = ''
    for i, a in enumerate(AUD):
        pan += '''
      <div class="apanel%s" id="%s" role="tabpanel">
        <div class="acopy">
          <h3>%s</h3>
          <p class="does">%s</p>
          <h4>Questions it answers</h4>
          <ul>%s</ul>
        </div>
        <div class="aside">
          <div class="aveh" aria-hidden="true"><img class="d" src="data:image/webp;base64,[[IMG%d]]" alt=""><img class="n" src="data:image/webp;base64,[[IMG%d]]" alt=""></div>
          <div class="aex"><h4>Example</h4><p>%s</p><p class="exn"><span>%s</span>%s</p></div>
        </div>
      </div>''' % (' on' if i == 0 else '', a['id'], a['h'], a['does'], ''.join('<li>%s</li>' % q for q in a['q']),
                   a['img'][0], a['img'][1], a['ex'], a['note'], ' <a href="#app">Open this case in the demo</a>' if a['demo'] else '')
    return '''
<section class="who" id="for">
  <div class="wrap">
    <div class="whotop rv">
      <h2>Who it is for</h2>
      <div class="switch c" data-switch="who"><div class="sw-track" role="tablist" aria-label="Who it's for">%s</div></div>
    </div>
    <div class="apanels">%s
    </div>
  </div>
</section>
''' % (tabs, pan)

HERO_PICK = ''
_UNUSED = '<p class="pick in" style="animation-delay:.5s"><span>See what it does for</span>' + ''.join('<a href="#%s">%s</a>' % (a['id'], a['tab']) for a in AUD) + '</p>'

STORY = [  # (old h3, old p, new h3, new p)
 ('Every route, every stop, every&nbsp;day', 'Your real operation goes in first: routes, stops, payload and the hours trucks spend away from the depot.',
  'Your routes go in&nbsp;first', 'Routes, stops, payload and shift times. Everything else is worked out from them.'),
 ('While the city sleeps, the depot&nbsp;charges', 'Trucks plug in when the shift ends. EV Scope plans the night so every one is full by morning, under the grid limit.',
  'Charging overnight', 'Each vehicle is checked to be full before its shift, with the depot inside its grid limit.'),
 ('Will the battery last the&nbsp;route?', 'Every route checked against the battery, with charge to spare when the truck is back.',
  'Battery size', 'Each route is checked against the battery when new and at year 8, when it holds less.'),
 ('And on the coldest day, at year&nbsp;8?', 'Cold air, cabin heating and an aged battery, together. No optimistic averages.',
  'Winter at year 8', 'The coldest day, with cabin heating and the battery at its year-8 capacity, checked together.'),
 ('How big do the chargers need to&nbsp;be?', 'Just big enough to have every truck full before the morning shift. Parked overnight, even the smallest one is enough.',
  'Charger size', 'The smallest charger that has every vehicle full before its shift.'),
 ('How much can it still&nbsp;carry?', 'Batteries weigh. See the payload left on every route, before you order.',
  'Payload', 'A heavier battery can leave less payload. Different loads can be tested on each route.'),
 ('When can the grid connect&nbsp;you?', 'Waits run from months to years. Apply early, with the numbers already done.',
  'Grid connection', 'The power to apply for and the load hour by hour. Waits run from months to years.'),
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
  });
"""

CSS2 = r"""
/* ===== second pass: clearer hierarchy, a part for each reader ===== */
.glyphs{display:none}
.hero{padding-top:calc(var(--hh) + 84px)}
.hero p.sub{margin:22px auto 30px;max-width:560px;font-size:clamp(18px,1.6vw,21px);color:var(--slate)}
.hero .cta-row{margin-top:0}
.hero .pick{margin:34px auto 0;display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:10px;font-size:15px;color:var(--muted)}
.hero .pick span{margin-right:6px}
.hero .pick a{padding:9px 15px;border-radius:9px;background:var(--bg);box-shadow:inset 0 0 0 1px var(--line);color:var(--ink);font-weight:500;transition:box-shadow .2s,color .2s}
.hero .pick a:hover{box-shadow:inset 0 0 0 1.5px var(--accent);color:var(--accent)}
.hero-depot{margin-top:40px}
.who{padding:72px 0 100px;scroll-margin-top:20px}
.whotop{display:flex;flex-direction:column;align-items:center;gap:20px}
.whotop h2{font-size:clamp(26px,3vw,38px);line-height:1.15;font-weight:600;color:var(--ink)}
.who .switch{margin:0;max-width:100%}
.apanels{margin-top:64px}
.apanel{display:none;grid-template-columns:minmax(0,6fr) minmax(0,5fr);gap:72px;align-items:start}
.apanel.on{display:grid;animation:afade .5s ease both}
@keyframes afade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.apanel h3{font-size:clamp(22px,2.2vw,28px);line-height:1.15;font-weight:600;margin:0 0 14px;text-wrap:balance}
.apanel .hook{font-size:clamp(19px,1.7vw,23px);line-height:1.3;font-weight:500;color:var(--ink);margin:0 0 14px;max-width:30em;text-wrap:balance}
.apanel .does{font-size:clamp(18px,1.5vw,20px);line-height:1.5;color:var(--slate);margin:0 0 36px;max-width:52ch}
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
 HERO_SUB: {'da':'Dimensionering af batteri, ladere og nettilslutning til elektriske flåder, beregnet ud fra dine egne ruter.','de':'Auslegung von Batterie, Ladestationen und Netzanschluss für elektrische Flotten, berechnet aus Ihren eigenen Routen.','nl':'Dimensionering van batterij, laders en netaansluiting voor elektrische vloten, berekend op basis van je eigen routes.'},
 'Truck makers and charge operators': {'da':'Lastbilproducenter og ladeoperatører','de':'Lkw-Hersteller und Ladebetreiber','nl':'Truckfabrikanten en laadexploitanten'},
 'Who it is for': {'da':'Hvem det er for','de':'Für wen es ist','nl':'Voor wie het is'},
 'Questions it answers': {'da':'Spørgsmål, det besvarer','de':'Fragen, die es beantwortet','nl':'Vragen die het beantwoordt'},
 'Example': {'da':'Eksempel','de':'Beispiel','nl':'Voorbeeld'},
 'Open this case in the demo': {'da':'Åbn eksemplet i demoen','de':'Diesen Fall in der Demo öffnen','nl':'Open dit voorbeeld in de demo'},
 SAMPLE: {'da':'Eksempel med illustrative tal.','de':'Beispielfall mit illustrativen Zahlen.','nl':'Voorbeeldcase met illustratieve cijfers.'},
 NOTRES: {'da':'Et eksempel på spørgsmålet, ikke et resultat.','de':'Ein Beispiel für die Frage, kein Ergebnis.','nl':'Een voorbeeld van de vraag, geen resultaat.'},
 'For fleet owners': {'da':'For flådeejere','de':'Für Flottenbetreiber','nl':'Voor vlooteigenaren'},
 'For housing associations': {'da':'For boligforeninger','de':'Für Wohnungsgesellschaften','nl':'Voor woningcorporaties'},
 'For municipalities': {'da':'For kommuner','de':'Für Kommunen','nl':'Voor gemeenten'},
 'For truck makers and charge operators': {'da':'For lastbilproducenter og ladeoperatører','de':'Für Lkw-Hersteller und Ladebetreiber','nl':'Voor truckfabrikanten en laadexploitanten'},
 AUD[0]['does']: {'da':'EV Scope beregner batteristørrelse, laderstørrelse og nettilslutning til dine køretøjer ud fra de ruter, de kører.','de':'EV Scope ermittelt Batteriegröße, Ladeleistung und Netzanschluss für Ihre Fahrzeuge aus den Routen, die sie fahren.','nl':'EV Scope berekent de batterijgrootte, het laadvermogen en de netaansluiting voor je voertuigen, op basis van de routes die ze rijden.'},
 EX_FLEET: {'da':'Seks renovationsbiler på en byrute på 120 km med 400 stop. Hver har brug for et batteri på %s kWh. Depotet topper ved %s kW, inden for de %s kW, det allerede har.' % (BATT, PEAK, LIM),'de':'Sechs Müllfahrzeuge auf einer 120-km-Stadtrunde mit 400 Stopps. Jedes braucht eine Batterie mit %s kWh. Das Depot erreicht in der Spitze %s kW, innerhalb der %s kW, die es bereits hat.' % (BATT, PEAK, LIM),'nl':'Zes vuilniswagens op een stadsronde van 120 km met 400 stops. Elk heeft een batterij van %s kWh nodig. Het depot piekt op %s kW, binnen de %s kW die het al heeft.' % (BATT, PEAK, LIM)},
 AUD[1]['does']: {'da':'Fra 2026 har beboere ret til at lade. EV Scope beregner, hvor meget ladning bygningens forsyning kan bære, og hvad en større tilslutning vil kræve.','de':'Ab 2026 haben Bewohner ein Recht auf Laden. EV Scope ermittelt, wie viel Laden die Versorgung des Gebäudes trägt und was ein größerer Anschluss erfordern würde.','nl':'Vanaf 2026 hebben bewoners het recht om te laden. EV Scope berekent hoeveel laden de aansluiting van het gebouw aankan, en wat een grotere aansluiting zou vragen.'},
 AUD[1]['ex']: {'da':'En parkeringsplads på én fælles forsyning. Du ser, hvor mange ladepunkter der er plads til i dag, hvordan aftenen ser ud, når alle er hjemme, og hvilken tilslutning resten vil kræve.','de':'Ein Parkplatz an einer gemeinsamen Versorgung. Sie sehen, wie viele Ladepunkte heute passen, wie der Abend aussieht, wenn alle zu Hause sind, und welche Anschlussgröße der Rest bräuchte.','nl':'Een parkeerterrein op één gedeelde aansluiting. Je ziet hoeveel laadpunten er vandaag passen, hoe de avond eruitziet als iedereen thuis is, en welke aansluiting de rest nodig zou hebben.'},
 AUD[2]['does']: {'da':'EV Scope omsætter jeres ruter til krav i et udbud, ens for alle tilbudsgivere, og viser, hvilke køretøjer der kan elektrificeres i hvilket budgetår.','de':'EV Scope macht aus Ihren Routen Anforderungen für eine Ausschreibung, gleich für jeden Bieter, und zeigt, welche Fahrzeuge in welchem Haushaltsjahr elektrifiziert werden können.','nl':'EV Scope zet je routes om in eisen voor een aanbesteding, gelijk voor elke inschrijver, en laat zien welke voertuigen in welk begrotingsjaar elektrisch kunnen worden.'},
 EX_MUNI: {'da':'Fra eksemplets udbudsbilag: brugbart batteri i år 8 på mindst %s kWh og mindst %s kW ladeeffekt på depotet.' % (WORST, CHG),'de':'Aus der Ausschreibungsanlage des Beispielfalls: nutzbare Batterie im Jahr 8 von mindestens %s kWh und mindestens %s kW Ladeleistung im Depot.' % (WORST, CHG),'nl':'Uit de aanbestedingsbijlage van de voorbeeldcase: bruikbare batterij in jaar 8 van minstens %s kWh, en minstens %s kW laadvermogen op het depot.' % (WORST, CHG)},
 AUD[3]['does']: {'da':'EV Scope kører jeres køretøj på køberens ruter, så begge parter ser på samme case. Ladeoperatører får depotets belastning time for time.','de':'EV Scope rechnet Ihr Fahrzeug auf den Routen des Käufers, sodass beide Seiten denselben Fall betrachten. Ladebetreiber erhalten die Last des Depots Stunde für Stunde.','nl':'EV Scope rekent je voertuig door op de routes van de koper, zodat beide partijen naar dezelfde case kijken. Laadexploitanten krijgen de belasting van het depot van uur tot uur.'},
 'How much power does the depot need, and at what hours?': {'da':'Hvor meget effekt har depotet brug for, og på hvilke tidspunkter?','de':'Wie viel Leistung braucht das Depot, und zu welchen Stunden?','nl':'Hoeveel vermogen heeft het depot nodig, en op welke uren?'},
 AUD[3]['ex']: {'da':'Et udbud beder om den hårdeste vinterrute i år 8. I kører jeres lastbil på den rute og afleverer resultatet med alle input vist.','de':'Eine Ausschreibung verlangt die härteste Winterroute im Jahr 8. Sie rechnen Ihren Lkw auf dieser Route und übergeben das Ergebnis mit allen Eingaben.','nl':'Een aanbesteding vraagt om de zwaarste winterroute in jaar 8. Je rekent je truck door op die route en levert het resultaat met alle invoer erbij.'},
 'Your routes go in first': {'da':'Dine ruter kommer først','de':'Ihre Routen kommen zuerst','nl':'Je routes gaan er eerst in'},
 STORY[0][3]: {'da':'Ruter, stop, nyttelast og vagttider. Alt andet beregnes ud fra dem.','de':'Routen, Stopps, Nutzlast und Schichtzeiten. Alles andere wird daraus berechnet.','nl':'Routes, stops, lading en diensttijden. Al het andere wordt daaruit berekend.'},
 'Charging overnight': {'da':'Opladning om natten','de':'Laden über Nacht','nl':'’s Nachts laden'},
 STORY[1][3]: {'da':'Hvert køretøj tjekkes for at være fuldt opladet før sin vagt, med depotet inden for sin netgrænse.','de':'Für jedes Fahrzeug wird geprüft, dass es vor seiner Schicht voll ist und das Depot innerhalb seiner Netzgrenze bleibt.','nl':'Voor elk voertuig wordt gecontroleerd dat het vol is vóór zijn dienst, met het depot binnen zijn netlimiet.'},
 'Battery size': {'da':'Batteristørrelse','de':'Batteriegröße','nl':'Batterijgrootte'},
 STORY[2][3]: {'da':'Hver rute tjekkes mod batteriet som nyt og i år 8, hvor det rummer mindre.','de':'Jede Route wird gegen die Batterie geprüft, neu und im Jahr 8, wenn sie weniger speichert.','nl':'Elke route wordt getoetst aan de batterij, nieuw en in jaar 8, als die minder opslaat.'},
 'Winter at year 8': {'da':'Vinter i år 8','de':'Winter im Jahr 8','nl':'Winter in jaar 8'},
 'Will they still finish a winter shift at year 8?': {'da':'Klarer de stadig en vintervagt i år 8?','de':'Schaffen sie im Jahr 8 noch eine Winterschicht?','nl':'Halen ze in jaar 8 nog een winterdienst?'},
 STORY[3][3]: {'da':'Den koldeste dag, med kabinevarme og batteriet ved sin kapacitet i år 8, tjekket samlet.','de':'Der kälteste Tag, mit Kabinenheizung und der Batterie bei ihrer Kapazität im Jahr 8, zusammen geprüft.','nl':'De koudste dag, met cabineverwarming en de batterij op haar capaciteit in jaar 8, samen getoetst.'},
 'Charger size': {'da':'Laderstørrelse','de':'Ladeleistung','nl':'Laadvermogen'},
 STORY[4][3]: {'da':'Den mindste lader, der har hvert køretøj fuldt opladet før sin vagt.','de':'Die kleinste Ladestation, mit der jedes Fahrzeug vor seiner Schicht voll ist.','nl':'De kleinste lader waarmee elk voertuig vol is vóór zijn dienst.'},
 STORY[5][3]: {'da':'Et tungere batteri kan give mindre nyttelast. Forskellige laster kan testes på hver rute.','de':'Eine schwerere Batterie kann weniger Nutzlast lassen. Auf jeder Route lassen sich verschiedene Ladungen testen.','nl':'Een zwaardere batterij kan minder laadvermogen overlaten. Op elke route kunnen verschillende ladingen worden getest.'},
 'Grid connection': {'da':'Nettilslutning','de':'Netzanschluss','nl':'Netaansluiting'},
 STORY[6][3]: {'da':'Den effekt, der skal søges om, og belastningen time for time. Ventetiden er fra måneder til år.','de':'Die zu beantragende Leistung und die Last Stunde für Stunde. Wartezeiten reichen von Monaten bis Jahren.','nl':'Het aan te vragen vermogen en de belasting van uur tot uur. Wachttijden lopen van maanden tot jaren.'},
 'Six documents from one run': {'da':'Seks dokumenter fra én kørsel','de':'Sechs Dokumente aus einem Durchlauf','nl':'Zes documenten uit één run'},
 'Pick one to see what is in it.': {'da':'Vælg et for at se, hvad det indeholder.','de':'Wählen Sie eines, um den Inhalt zu sehen.','nl':'Kies er één om te zien wat erin staat.'},
 'See it on a sample depot': {'da':'Se det på et eksempeldepot','de':'Sehen Sie es an einem Beispieldepot','nl':'Bekijk het op een voorbeelddepot'},
 'Six refuse trucks, from the fleet table to the answer. Illustrative figures.': {'da':'Seks renovationsbiler, fra flådetabel til svar. Illustrative tal.','de':'Sechs Müllfahrzeuge, von der Flottentabelle bis zur Antwort. Illustrative Zahlen.','nl':'Zes vuilniswagens, van vloottabel tot antwoord. Illustratieve cijfers.'},
 'Your fleet': {'da':'Din flåde','de':'Ihre Flotte','nl':'Je vloot'},
 'The answer': {'da':'Svaret','de':'Die Antwort','nl':'Het antwoord'},
 'The cost': {'da':'Økonomien','de':'Die Kosten','nl':'De kosten'},
}
