# New and changed pieces of the landing page, kept apart from the build logic.

POLISH_CSS = r"""
/* ===== polish layer (13 Nov 2026) ===== */
:root{--faint:#667085}
[data-theme=night]{--faint:#8A93A5}
h1,h2,h3,.hero h1,.wm,.cols h3,.sheet h4,.docinfo b{letter-spacing:0}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.form input:focus-visible,.form select:focus-visible,.form textarea:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.ask form:focus-within{box-shadow:var(--sunk),0 0 0 2px var(--accent)}
.ask input:focus-visible{outline:0}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.hero p.sub,.close p{font-weight:400}
.btn{border-radius:10px}.btn.sm,.iconbtn,.langbtn{border-radius:8px}.ask form{border-radius:12px}.ask button{border-radius:8px}
.form input,.form select,.form textarea{border-radius:8px}.sw-track{border-radius:10px}.sw-track button{border-radius:7px}
.theme .sw-track{border-radius:8px}.theme .sw-track button{border-radius:6px}
.askpanel{border-radius:12px}.answer,.langmenu{border-radius:10px}.langmenu li{border-radius:7px}.skip{border-radius:6px}
/* plain labels where there were pills, tags and small caps */
.chip{font:400 13.5px/1.2 'IBM Plex Sans',system-ui,sans-serif;color:var(--slate);background:none;border-radius:0;padding:0;box-shadow:none;text-shadow:0 0 5px var(--bg),0 0 5px var(--bg),0 0 9px var(--bg),0 0 9px var(--bg)}
.chip::before{display:none}
.chips{gap:6px 26px}
.ask .hint{gap:6px 22px}
.ask .hint button{padding:2px 0;border-radius:0;box-shadow:none;font-size:14px;text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:4px}
.ask .hint button:hover{text-decoration-color:currentColor}
.hero-foot{font-size:14px;gap:8px 30px}.hero-foot span::before{display:none}
.answer small,.form .note,.snote,.loadbar .lb,.tl .t,.tl .ax,.sheet .sh-top span,.sheet .rw span,.sheet .foot{font-family:'IBM Plex Sans',system-ui,sans-serif}
.panel .get{border-top:0;padding-top:2px;display:block;color:var(--muted)}
.panel .get span{font:inherit;letter-spacing:0;text-transform:none;color:var(--faint);margin-right:8px}
.cols{border-top:0;margin-top:34px;gap:6px 44px}.cols>div{border-bottom:0;padding:14px 0}
.cols .lab{display:block;font-size:14px;color:var(--faint);margin-bottom:2px}
.cols .price{font-size:14px}
.note2{margin:22px 0 0;font-size:15px;color:var(--muted)}.note2 a,.legal a,.fine a{color:var(--accent);text-decoration:underline;text-underline-offset:3px}
/* pages */
body[class*="page-"] #home{display:none}
body.page-privacy #v-privacy,body.page-terms #v-terms{display:block}
.legal{max-width:720px}
.legal h2{font-size:20px;line-height:1.3;margin:34px 0 8px}
.legal p{margin:0 0 10px;color:var(--muted);font-size:16px}
.legal .org span{display:block}
/* the tool fills the window: one header, the tool's own */
#toolFrame{display:block;height:100%}
/* footer */
footer .wrap{display:block;padding-top:30px;padding-bottom:34px}
footer .frow{display:flex;justify-content:space-between;align-items:baseline;gap:10px 28px;flex-wrap:wrap}
footer nav{display:flex;gap:6px 22px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
footer nav a:hover{color:var(--ink)}
footer .fine{margin-top:14px;font-size:13px;color:var(--faint)}
/* tool preview */
.peek{padding:110px 0 30px}
.peek h2{font-size:clamp(26px,3vw,40px)}
.peekwin{position:relative;max-width:980px;margin:38px auto 0;border-radius:10px;overflow:hidden;background:#F5F6F8;box-shadow:0 0 0 1px var(--line),0 24px 60px rgba(18,24,43,.10)}
[data-theme=night] .peekwin{box-shadow:0 0 0 1px rgba(255,255,255,.12),0 24px 60px rgba(0,0,0,.8)}
.peekstage{position:relative;aspect-ratio:5/3}
.peekstage img{position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .55s ease}
.peekstage img.on{opacity:1}
[data-theme=night] .peekstage img{filter:brightness(.9)}
.pcur{position:absolute;left:60%;top:55%;width:20px;height:20px;margin:-2px 0 0 -3px;transition:left 1s var(--ease),top 1s var(--ease);pointer-events:none;z-index:3}
.pclick{position:absolute;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;border:2px solid var(--blue);opacity:0;pointer-events:none;z-index:2}
.pclick.go{animation:pclick .5s ease-out}
@keyframes pclick{from{opacity:.9;transform:scale(.3)}to{opacity:0;transform:scale(1.5)}}
.peek .switch{margin-top:22px}
.peek .cta{margin-top:26px;text-align:center}
@media (max-width:620px){.peek{padding-top:70px}.peekwin{margin-top:26px}.pcur{width:14px;height:14px}}
@media (prefers-reduced-motion:reduce){.pcur,.pclick{display:none}}
"""

PEEK_ALT = [
  "The fleet page of the demo: two groups of refuse trucks, each with a vehicle, a route, a load, body equipment and a shift",
  "The overview page of the demo: all six vehicles can run electric, with battery size, chargers, depot peak and cost against diesel",
  "The charging page of the demo: depot power over the hardest day stays under the grid connection",
  "The cost page of the demo: electric against diesel year by year and by cost line",
]

def peek_section(alts):
    imgs = ''.join('<img%s src="data:image/webp;base64,[[PEEK%d]]" alt="%s" width="1800" height="1080" decoding="async">' % (' class="on"' if i == 0 else '', i, a) for i, a in enumerate(alts))
    return '''
<section class="peek" id="demo">
  <div class="wrap">
    <div class="center rv"><h2>See the tool at&nbsp;work</h2><p class="lead">The same sample depot, from the fleet table to the answer.</p></div>
    <div class="peekwin rv"><div class="peekstage" id="peekstage">''' + imgs + '''<span class="pclick" id="pclick" aria-hidden="true"></span><svg class="pcur" id="pcur" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 2l13 7.2-5.6 1.5L8 16.5z" fill="#12182B" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg></div></div>
    <div class="switch c rv" data-switch="peek">
      <button class="sw-arrow" data-dir="-1" aria-label="Previous">←</button>
      <div class="sw-track" role="tablist" aria-label="Tool preview"><button role="tab">Fleet<i></i></button><button role="tab">Answer<i></i></button><button role="tab">Charging<i></i></button><button role="tab">Cost<i></i></button></div>
      <button class="sw-arrow" data-dir="1" aria-label="Next">→</button>
    </div>
    <p class="cta rv"><a class="btn" href="#app">Try the demo <span class="ar" aria-hidden="true">→</span></a></p>
  </div>
</section>
'''

TOOL_VIEW = '''<section class="view" id="v-tool"><div class="wrap">
  <div class="split">
    <div>
      <h1>Try EV Scope on a sample fleet</h1>
      <p class="lead">Six refuse trucks and one depot, with illustrative figures. No account is needed, and nothing you type leaves your browser.</p>
      <div style="margin-top:30px"><a class="btn" href="#app">Open the demo <span class="ar" aria-hidden="true">→</span></a></div>
      <p class="note2">Want it run on your own fleet? <a href="#contact">Get early access</a></p>
    </div>
    <div class="cols" style="grid-template-columns:1fr;margin-top:0">
      <div><h3>Dashboard</h3><p>See your study and keep your fleet data up to date for the next tender.</p><p class="price">Price on request</p></div>
      <div><h3>Full tool</h3><p>Every input, every result and all six documents.</p><p class="price">Price on request</p></div>
      <div><h3>Project</h3><p>Send your data. We deliver the study and the documents you need.</p><p class="price">Price on request</p></div>
    </div>
  </div>
</div></section>'''

LEGAL_VIEWS = '''
<section class="view" id="v-privacy"><div class="wrap"><div class="legal">
  <h1>Privacy</h1>
  <p class="lead">What happens to your data when you use this website and the demo.</p>
  <h2>Who is responsible</h2>
  <p class="org"><span data-org="legal"></span><span data-org="cvr" data-pre="CVR "></span><span data-org="address"></span><a data-org="email"></a></p>
  <h2>What this website collects</h2>
  <p>Nothing on its own. The site sets no cookies, has no analytics and loads nothing from other companies. Fonts and images are part of the page.</p>
  <p>The company that hosts the site keeps ordinary server logs, such as your IP address and the time of your visit, to run it securely.</p>
  <h2>What stays in your browser</h2>
  <p>If you choose a language or switch between day and night, that choice is saved in your browser so the site remembers it. It is not sent to us. Clearing your browser data removes it.</p>
  <h2>The demo</h2>
  <p>The demo runs entirely in your browser. What you type into it is not sent anywhere and is gone when you close the page.</p>
  <h2>When you contact us</h2>
  <p>The contact form opens your own email app. Nothing reaches us until you send that email. We use what you write to answer you and to follow up, and we keep it only as long as that takes.</p>
  <h2>Your rights</h2>
  <p>You can ask to see, correct or delete what we hold about you, or object to how we use it. Write to the email address above.</p>
  <p>You can also complain to the Danish Data Protection Agency, Datatilsynet, at datatilsynet.dk.</p>
  <p class="note2">Last updated 13 November 2026.</p>
</div></div></section>

<section class="view" id="v-terms"><div class="wrap"><div class="legal">
  <h1>Terms of use</h1>
  <p class="lead">These terms cover this website and the demo.</p>
  <h2>The demo is an illustration</h2>
  <p>The demo uses a sample fleet and a simplified engine. Its figures show how EV Scope works. They are not advice, and they must not be used to buy vehicles, write a tender or apply for a grid connection.</p>
  <h2>The website</h2>
  <p>We keep the content correct as far as we can, but we do not guarantee that it is complete or up to date. Sample figures are marked as illustrative.</p>
  <h2>Work for customers</h2>
  <p>Studies and access to the full tool are covered by a separate written agreement.</p>
  <h2>Rights</h2>
  <p>The text, images and software on this site belong to the company named below unless stated otherwise. The IBM Plex typeface is used under the SIL Open Font License.</p>
  <h2>Law</h2>
  <p>Danish law applies to these terms.</p>
  <h2>Who we are</h2>
  <p class="org"><span data-org="legal"></span><span data-org="cvr" data-pre="CVR "></span><span data-org="address"></span><a data-org="email"></a></p>
  <p class="note2">Last updated 13 November 2026.</p>
</div></div></section>
'''

FOOTER = '''<footer id="siteFoot"><div class="wrap">
  <div class="frow"><span class="wm" style="font-size:15px"><b>EV</b> Scope</span><nav aria-label="Footer"><a href="#about">About</a><a href="#contact">Contact</a><a href="#tool">Try the demo</a><a href="#privacy">Privacy</a><a href="#terms">Terms</a></nav></div>
  <div class="frow fine"><span id="orgLine"></span><span>Sample figures are illustrative. Grid lead times: Radius.</span></div>
</div></footer>'''

PEEK_JS = r"""
  /* ---------- tool preview: real screens from the demo, a cursor clicks through them ---------- */
  var PK=$('peekstage'), pimgs=[].slice.call(PK.querySelectorAll('img')), pcur=$('pcur'), pclk=$('pclick');
  var PTS=__PTS__, REST=[[58,56],[60,44],[64,50],[52,58]], STEP=5600, pkOn=false, pkT=0, pkHold=0, pkMoved=false, pkClicked=false, pkRaf=0;
  function pkPlace(p){ pcur.style.left=p[0]+'%'; pcur.style.top=p[1]+'%'; }
  var peek=Switch(document.querySelector('[data-switch="peek"]'),null,function(n,src){
    pimgs.forEach(function(im,k){ im.classList.toggle('on',k===n) }); pkPlace(REST[n]); pkMoved=pkClicked=false; pkT=performance.now();
    if(src==='user') pkHold=pkT+9000;
  });
  peek.set(0); peek.progress(reduce?1:0);
  function pkFrame(now){
    pkRaf=0; if(!pkOn) return;
    if(now<pkHold){ peek.progress(1); pkT=now; }
    else { var el=now-pkT; peek.progress(el/STEP);
      if(el>STEP*.5&&!pkMoved){ pkMoved=true; pkPlace(PTS[peek.i]) }
      if(el>STEP*.74&&!pkClicked){ pkClicked=true; pclk.style.left=PTS[peek.i][0]+'%'; pclk.style.top=PTS[peek.i][1]+'%'; pclk.classList.remove('go'); void pclk.offsetWidth; pclk.classList.add('go') }
      if(el>=STEP*.82) peek.set(peek.i+1,'auto');
    }
    pkRaf=requestAnimationFrame(pkFrame);
  }
  inView(PK,function(v){ pkOn=v&&!reduce; if(pkOn&&!pkRaf){ pkT=performance.now(); pkMoved=pkClicked=false; pkRaf=requestAnimationFrame(pkFrame) } },.3);
"""

ORG_JS = r"""
  /* ---------- business details: one place to fill in, at the top of this file ---------- */
  var ORG=window.EVS_ORG||{};
  [].slice.call(document.querySelectorAll('[data-org]')).forEach(function(el){ var v=ORG[el.dataset.org]||''; if(!v){ el.hidden=true; return }
    el.textContent=(el.dataset.pre||'')+v; if(el.tagName==='A') el.href='mailto:'+v });
  $('orgLine').textContent=[ORG.legal,ORG.cvr&&('CVR '+ORG.cvr),ORG.address,ORG.email].filter(Boolean).join(' · ');
"""

# ---- translations: changed titles (old key -> new key and new values) ----
RENAME = {
 'Scope before you sign.': ('Scope before you sign', {'da':'Scope, før du skriver under','de':'Scope, bevor Sie unterschreiben','nl':'Scope, voordat je tekent'}),
 'Every route, every stop, every day.': ('Every route, every stop, every day', None),
 'While the city sleeps, the depot charges.': ('While the city sleeps, the depot charges', None),
 'Different assets. The same question.': ('Different assets, the same question', {'da':'Forskellige aktiver, samme spørgsmål','de':'Verschiedene Anlagen, dieselbe Frage','nl':'Verschillende assets, dezelfde vraag'}),
 'Battery, chargers and connection, sized before capital is committed.': ('Battery, chargers and connection, sized before capital is committed', None),
 'From 2026, residents have the right to charge.': ('From 2026, residents have the right to charge', None),
 'Fixed budget years. Brand-agnostic procurement.': ('Fixed budget years, brand-agnostic procurement', {'da':'Faste budgetår, brandneutrale indkøb','de':'Feste Haushaltsjahre, herstellerneutrale Beschaffung','nl':'Vaste begrotingsjaren, merkonafhankelijke inkoop'}),
 "Your spec sheet, tested on the buyer's own routes.": ("Your spec sheet, tested on the buyer's own routes", None),
 'Get the document you need.': ('Get the document you need', None),
 'Start with one depot.': ('Start with one depot', None),
 'Advice before the money is spent.': ('Advice before the money is spent', None),
}
NEW = {
 'Try the demo': {'da':'Prøv demoen','de':'Demo ausprobieren','nl':'Probeer de demo'},
 'Open the demo': {'da':'Åbn demoen','de':'Demo öffnen','nl':'Open de demo'},
 'Try EV Scope on a sample fleet': {'da':'Prøv EV Scope på en eksempelflåde','de':'EV Scope an einer Beispielflotte ausprobieren','nl':'Probeer EV Scope op een voorbeeldvloot'},
 'Six refuse trucks and one depot, with illustrative figures. No account is needed, and nothing you type leaves your browser.': {'da':'Seks renovationsbiler og ét depot, med illustrative tal. Du behøver ingen konto, og intet af det, du skriver, forlader din browser.','de':'Sechs Müllfahrzeuge und ein Depot, mit illustrativen Zahlen. Kein Konto nötig, und nichts, was Sie eingeben, verlässt Ihren Browser.','nl':'Zes vuilniswagens en één depot, met illustratieve cijfers. Je hebt geen account nodig, en niets van wat je intypt verlaat je browser.'},
 'Want it run on your own fleet?': {'da':'Vil du have det kørt på din egen flåde?','de':'Soll es für Ihre eigene Flotte gerechnet werden?','nl':'Wil je het voor je eigen vloot laten doorrekenen?'},
 'See the tool at work': {'da':'Se værktøjet i brug','de':'Das Tool im Einsatz','nl':'Zie de tool aan het werk'},
 'The same sample depot, from the fleet table to the answer.': {'da':'Det samme eksempeldepot, fra flådetabel til svar.','de':'Dasselbe Beispieldepot, von der Flottentabelle bis zur Antwort.','nl':'Hetzelfde voorbeelddepot, van vloottabel tot antwoord.'},
 'Fleet': {'da':'Flåde','de':'Flotte','nl':'Vloot'},
 'Answer': {'da':'Svar','de':'Antwort','nl':'Antwoord'},
 'Cost': {'da':'Økonomi','de':'Kosten','nl':'Kosten'},
 'Tool preview': {'da':'Forhåndsvisning af værktøjet','de':'Vorschau des Tools','nl':'Voorbeeld van de tool'},
 'Footer': {'da':'Sidefod','de':'Fußzeile','nl':'Voettekst'},
 'Privacy': {'da':'Privatliv','de':'Datenschutz','nl':'Privacy'},
 'Terms': {'da':'Vilkår','de':'Bedingungen','nl':'Voorwaarden'},
 'Terms of use': {'da':'Vilkår for brug','de':'Nutzungsbedingungen','nl':'Gebruiksvoorwaarden'},
 'What happens to your data when you use this website and the demo.': {'da':'Hvad der sker med dine data, når du bruger dette websted og demoen.','de':'Was mit Ihren Daten geschieht, wenn Sie diese Website und die Demo nutzen.','nl':'Wat er met je gegevens gebeurt als je deze website en de demo gebruikt.'},
 'Who is responsible': {'da':'Hvem er ansvarlig','de':'Wer verantwortlich ist','nl':'Wie verantwoordelijk is'},
 'What this website collects': {'da':'Hvad webstedet indsamler','de':'Was diese Website erhebt','nl':'Wat deze website verzamelt'},
 'Nothing on its own. The site sets no cookies, has no analytics and loads nothing from other companies. Fonts and images are part of the page.': {'da':'Ingenting af sig selv. Webstedet sætter ingen cookies, har ingen statistik og henter intet fra andre virksomheder. Skrifttyper og billeder er en del af siden.','de':'Von sich aus nichts. Die Website setzt keine Cookies, nutzt keine Analyse und lädt nichts von anderen Unternehmen. Schriften und Bilder sind Teil der Seite.','nl':'Uit zichzelf niets. De site plaatst geen cookies, heeft geen analytics en laadt niets van andere bedrijven. Lettertypen en afbeeldingen zijn onderdeel van de pagina.'},
 'The company that hosts the site keeps ordinary server logs, such as your IP address and the time of your visit, to run it securely.': {'da':'Den virksomhed, der hoster webstedet, fører almindelige serverlogs, f.eks. din IP-adresse og tidspunktet for dit besøg, for at drive det sikkert.','de':'Das Unternehmen, das die Website hostet, führt übliche Serverprotokolle, etwa Ihre IP-Adresse und den Zeitpunkt Ihres Besuchs, um sie sicher zu betreiben.','nl':'Het bedrijf dat de site host, houdt gewone serverlogs bij, zoals je IP-adres en het tijdstip van je bezoek, om de site veilig te laten draaien.'},
 'What stays in your browser': {'da':'Hvad der bliver i din browser','de':'Was in Ihrem Browser bleibt','nl':'Wat in je browser blijft'},
 'If you choose a language or switch between day and night, that choice is saved in your browser so the site remembers it. It is not sent to us. Clearing your browser data removes it.': {'da':'Hvis du vælger et sprog eller skifter mellem dag og nat, gemmes valget i din browser, så webstedet husker det. Det sendes ikke til os. Det forsvinder, når du rydder dine browserdata.','de':'Wenn Sie eine Sprache wählen oder zwischen Tag und Nacht wechseln, wird diese Wahl in Ihrem Browser gespeichert, damit die Website sie behält. Sie wird nicht an uns gesendet. Beim Löschen Ihrer Browserdaten verschwindet sie.','nl':'Als je een taal kiest of wisselt tussen dag en nacht, wordt die keuze in je browser opgeslagen zodat de site haar onthoudt. Ze wordt niet naar ons verzonden. Als je je browsergegevens wist, is ze weg.'},
 'The demo': {'da':'Demoen','de':'Die Demo','nl':'De demo'},
 'The demo runs entirely in your browser. What you type into it is not sent anywhere and is gone when you close the page.': {'da':'Demoen kører udelukkende i din browser. Det, du skriver i den, sendes ingen steder hen og er væk, når du lukker siden.','de':'Die Demo läuft vollständig in Ihrem Browser. Was Sie eingeben, wird nirgendwohin gesendet und ist weg, wenn Sie die Seite schließen.','nl':'De demo draait volledig in je browser. Wat je erin typt, wordt nergens heen gestuurd en is weg als je de pagina sluit.'},
 'When you contact us': {'da':'Når du kontakter os','de':'Wenn Sie uns kontaktieren','nl':'Als je contact met ons opneemt'},
 'The contact form opens your own email app. Nothing reaches us until you send that email. We use what you write to answer you and to follow up, and we keep it only as long as that takes.': {'da':'Kontaktformularen åbner din egen mailapp. Intet når frem til os, før du sender mailen. Vi bruger det, du skriver, til at svare dig og følge op, og vi gemmer det kun, så længe det kræver.','de':'Das Kontaktformular öffnet Ihre eigene E-Mail-App. Nichts erreicht uns, bevor Sie diese E-Mail senden. Wir nutzen, was Sie schreiben, um Ihnen zu antworten und nachzufassen, und bewahren es nur so lange auf, wie das dauert.','nl':'Het contactformulier opent je eigen e-mailapp. Niets bereikt ons voordat je die e-mail verstuurt. We gebruiken wat je schrijft om je te antwoorden en op te volgen, en we bewaren het alleen zolang dat nodig is.'},
 'Your rights': {'da':'Dine rettigheder','de':'Ihre Rechte','nl':'Je rechten'},
 'You can ask to see, correct or delete what we hold about you, or object to how we use it. Write to the email address above.': {'da':'Du kan bede om at se, rette eller slette det, vi har om dig, eller gøre indsigelse mod, hvordan vi bruger det. Skriv til mailadressen ovenfor.','de':'Sie können verlangen, einzusehen, zu berichtigen oder zu löschen, was wir über Sie gespeichert haben, oder der Nutzung widersprechen. Schreiben Sie an die oben genannte E-Mail-Adresse.','nl':'Je kunt vragen om in te zien, te corrigeren of te verwijderen wat we over je bewaren, of bezwaar maken tegen het gebruik ervan. Schrijf naar het e-mailadres hierboven.'},
 'You can also complain to the Danish Data Protection Agency, Datatilsynet, at datatilsynet.dk.': {'da':'Du kan også klage til Datatilsynet på datatilsynet.dk.','de':'Sie können sich auch bei der dänischen Datenschutzbehörde Datatilsynet unter datatilsynet.dk beschweren.','nl':'Je kunt ook een klacht indienen bij de Deense privacytoezichthouder, Datatilsynet, via datatilsynet.dk.'},
 'Last updated 13 November 2026.': {'da':'Senest opdateret 13. november 2026.','de':'Zuletzt aktualisiert am 13. November 2026.','nl':'Laatst bijgewerkt op 13 november 2026.'},
 'These terms cover this website and the demo.': {'da':'Disse vilkår gælder for dette websted og demoen.','de':'Diese Bedingungen gelten für diese Website und die Demo.','nl':'Deze voorwaarden gelden voor deze website en de demo.'},
 'The demo is an illustration': {'da':'Demoen er en illustration','de':'Die Demo ist eine Veranschaulichung','nl':'De demo is een illustratie'},
 'The demo uses a sample fleet and a simplified engine. Its figures show how EV Scope works. They are not advice, and they must not be used to buy vehicles, write a tender or apply for a grid connection.': {'da':'Demoen bruger en eksempelflåde og en forenklet beregningsmotor. Tallene viser, hvordan EV Scope virker. De er ikke rådgivning og må ikke bruges til at købe køretøjer, skrive et udbud eller søge om nettilslutning.','de':'Die Demo nutzt eine Beispielflotte und ein vereinfachtes Rechenmodell. Die Zahlen zeigen, wie EV Scope funktioniert. Sie sind keine Beratung und dürfen nicht verwendet werden, um Fahrzeuge zu kaufen, eine Ausschreibung zu verfassen oder einen Netzanschluss zu beantragen.','nl':'De demo gebruikt een voorbeeldvloot en een vereenvoudigd rekenmodel. De cijfers laten zien hoe EV Scope werkt. Ze zijn geen advies en mogen niet worden gebruikt om voertuigen te kopen, een aanbesteding te schrijven of een netaansluiting aan te vragen.'},
 'The website': {'da':'Webstedet','de':'Die Website','nl':'De website'},
 'We keep the content correct as far as we can, but we do not guarantee that it is complete or up to date. Sample figures are marked as illustrative.': {'da':'Vi holder indholdet korrekt, så godt vi kan, men vi garanterer ikke, at det er fuldstændigt eller opdateret. Eksempeltal er markeret som illustrative.','de':'Wir halten die Inhalte so korrekt wie möglich, garantieren aber nicht, dass sie vollständig oder aktuell sind. Beispielzahlen sind als illustrativ gekennzeichnet.','nl':'We houden de inhoud zo goed mogelijk juist, maar we garanderen niet dat ze volledig of actueel is. Voorbeeldcijfers zijn als illustratief gemarkeerd.'},
 'Work for customers': {'da':'Arbejde for kunder','de':'Arbeit für Kunden','nl':'Werk voor klanten'},
 'Studies and access to the full tool are covered by a separate written agreement.': {'da':'Undersøgelser og adgang til det fulde værktøj er dækket af en særskilt skriftlig aftale.','de':'Studien und der Zugang zum vollständigen Tool werden durch eine gesonderte schriftliche Vereinbarung geregelt.','nl':'Studies en toegang tot de volledige tool vallen onder een aparte schriftelijke overeenkomst.'},
 'Rights': {'da':'Rettigheder','de':'Rechte','nl':'Rechten'},
 'The text, images and software on this site belong to the company named below unless stated otherwise. The IBM Plex typeface is used under the SIL Open Font License.': {'da':'Tekst, billeder og software på dette websted tilhører virksomheden nævnt nedenfor, medmindre andet er angivet. Skrifttypen IBM Plex bruges under SIL Open Font License.','de':'Texte, Bilder und Software auf dieser Website gehören dem unten genannten Unternehmen, sofern nicht anders angegeben. Die Schrift IBM Plex wird unter der SIL Open Font License verwendet.','nl':'De tekst, afbeeldingen en software op deze site zijn eigendom van het hieronder genoemde bedrijf, tenzij anders vermeld. Het lettertype IBM Plex wordt gebruikt onder de SIL Open Font License.'},
 'Law': {'da':'Lovvalg','de':'Recht','nl':'Recht'},
 'Danish law applies to these terms.': {'da':'Dansk ret gælder for disse vilkår.','de':'Für diese Bedingungen gilt dänisches Recht.','nl':'Op deze voorwaarden is Deens recht van toepassing.'},
 'Who we are': {'da':'Hvem vi er','de':'Wer wir sind','nl':'Wie wij zijn'},
}
ALT_TR = {
 0: {'da':'Demoens flådeside: to grupper af renovationsbiler, hver med køretøj, rute, last, udstyr og vagt','de':'Die Flottenseite der Demo: zwei Gruppen von Müllfahrzeugen, jeweils mit Fahrzeug, Route, Ladung, Aufbau und Schicht','nl':'De vlootpagina van de demo: twee groepen vuilniswagens, elk met voertuig, route, lading, opbouw en dienst'},
 1: {'da':'Demoens overblik: alle seks køretøjer kan køre på el, med batteristørrelse, ladere, spidslast og økonomi mod diesel','de':'Die Übersicht der Demo: alle sechs Fahrzeuge können elektrisch fahren, mit Batteriegröße, Ladestationen, Spitzenlast und Kosten gegenüber Diesel','nl':'Het overzicht van de demo: alle zes voertuigen kunnen elektrisch rijden, met batterijgrootte, laders, piekvermogen en kosten tegenover diesel'},
 2: {'da':'Demoens ladeside: depotets effekt over den hårdeste dag holder sig under nettilslutningen','de':'Die Ladeseite der Demo: die Leistung des Depots bleibt am härtesten Tag unter dem Netzanschluss','nl':'De laadpagina van de demo: het vermogen van het depot blijft op de zwaarste dag onder de netaansluiting'},
 3: {'da':'Demoens økonomiside: el mod diesel år for år og pr. omkostningspost','de':'Die Kostenseite der Demo: Elektro gegenüber Diesel, Jahr für Jahr und nach Kostenposten','nl':'De kostenpagina van de demo: elektrisch tegenover diesel, jaar na jaar en per kostenpost'},
}
