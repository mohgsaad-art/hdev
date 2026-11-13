import re, json, base64, pathlib
from build_tool import tool_html, fonts_css, LICENSE, W
from site_parts import *

s = (W/'site_stripped.html').read_text(encoding='utf-8')
orig = (W/'site.html').read_text(encoding='utf-8')
imgs = re.findall(r'data:image/webp;base64,([A-Za-z0-9+/=]+)', orig)
assert len(imgs) == 45

def sub(a, b, count=1):
    global s
    assert a in s, 'missing: ' + a[:90]
    s = s.replace(a, b) if count == 0 else s.replace(a, b, count)
def rsub(pat, rep, expect=None):
    global s
    s, n = re.subn(pat, rep, s)
    assert n > 0 and (expect is None or n == expect), (pat, n)

# ---------- head ----------
sub('<!doctype html>\n', '<!doctype html>\n' + LICENSE)
sub('<title>EV Scope · Scope before you sign.</title>', '<title>EV Scope · Scope before you sign</title>')
sub('''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap">
''', '''<meta name="theme-color" content="#1F4E9E">
<meta property="og:type" content="website">
<meta property="og:title" content="EV Scope · Scope before you sign">
<meta property="og:description" content="EV Scope sizes vehicle electrification before anyone signs: the vehicles, chargers and grid connection a depot really needs.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Crect x='1' y='1' width='46' height='46' rx='9' fill='%231F4E9E'/%3E%3Crect x='4.5' y='4.5' width='39' height='39' rx='6.5' fill='none' stroke='%23fff' stroke-width='1.8'/%3E%3Ctext x='24' y='31.5' text-anchor='middle' font-family='Arial,Helvetica,sans-serif' font-weight='800' font-size='19' fill='%23fff' letter-spacing='-.5'%3EEV%3C/text%3E%3C/svg%3E">
<script>
/* ===== FILL IN BEFORE PUBLISHING =====
   These four values appear in the footer, on the Contact, Privacy and Terms pages, and in the contact form.
   Leave a value as '' to leave it out. */
window.EVS_ORG = {
  legal:   '[COMPANY LEGAL NAME]',
  cvr:     '[CVR NUMBER]',
  address: '[STREET, POSTCODE AND CITY]',
  email:   '[YOUR EMAIL]'
};
</script>
<style id="evs-fonts">[[FONTS]]</style>
''')

# ---------- css ----------
sub(".mono{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}\n", '')
sub("'IBM Plex Mono',monospace", "'IBM Plex Sans',system-ui,sans-serif", 0)
assert 'Plex Mono' not in s.split('</style>\n</head>')[0].split('[[FONTS]]')[1]
rsub(r"\.kicker\{[^\n]*\n\.kicker::before\{[^\n]*\n", '', 1)
sub(".cols .mono{font-size:12px;color:var(--accent);display:block;margin-bottom:12px}\n", '')
sub(".appbar{flex:none;height:52px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 20px;border-bottom:1px solid var(--line)}\n", '')
sub('</style>\n</head>', POLISH_CSS + '</style>\n</head>')

# ---------- markup ----------
sub('<a class="skip" href="#depot">Skip to content</a>', '<a class="skip" href="#depot" id="skip">Skip to content</a>')
sub('<a class="btn sm tool-btn" href="#tool">Open the tool</a>', '<a class="btn sm tool-btn" href="#tool">Try the demo</a>')
sub('<a class="btn" href="#tool">Open the tool</a>', '<a class="btn" href="#tool">Try the demo</a>')
sub('<p class="kicker">Inside one depot</p>', '<h2 class="vh">How it works</h2>')
rsub(r'<span class="n2">[^<]*</span>', '', 7)
sub('Different assets. The same&nbsp;question.', 'Different assets, the same&nbsp;question')
sub('Fixed budget years. Brand-agnostic&nbsp;procurement.', 'Fixed budget years, brand-agnostic&nbsp;procurement')
rsub(r'<p class="kicker"[^>]*>[^<]*</p>', '')
rsub(r'<span class="mono">0\d</span>', '', 4)
sub('<div><span class="mono">Email</span><p>[YOUR EMAIL]</p></div>', '<div><span class="lab">Email</span><p><a data-org="email" style="color:var(--accent)"></a></p></div>')
sub('<div><span class="mono">Based in</span><p>Copenhagen, Denmark</p></div>', '<div><span class="lab">Based in</span><p>Copenhagen, Denmark</p></div>')
sub('<p class="note">Sending opens your email app with the message filled in.</p>', '<p class="note">Sending opens your email app with the message filled in. Nothing reaches us before you send it.</p>')
a = s.index('<section class="view" id="v-tool">'); b = s.index('<section class="appview" id="v-app"')
s = s[:a] + TOOL_VIEW + '\n' + LEGAL_VIEWS + '\n' + s[b:]
sub('''  <div class="appbar">
    <a href="#top" class="brand" aria-label="EV Scope home"><span class="logo" aria-hidden="true"><i>EV</i></span><span class="wm"><b>EV</b> Scope</span></a>
    <a class="lnk" href="#tool"><span aria-hidden="true">←</span> Back to site</a>
  </div>
''', '')
a = s.index('<footer id="siteFoot">'); b = s.index('</footer>', a) + len('</footer>')
s = s[:a] + FOOTER + s[b:]
sub('<section class="close">', peek_section(PEEK_ALT) + '\n<section class="close">')
rsub(r'\.(</h[123]>)', r'\1')
assert not re.search(r'[a-z]\.</h[1-4]>', s)

# ---------- script ----------
sub("  var hdr=$('hdr'), body=document.body;\n", "  var hdr=$('hdr'), body=document.body;\n" + ORG_JS)
sub("var fan=$('fan'), fanbox=$('fanbox'),", "$('fan').setAttribute('aria-hidden','true');\n  var fan=$('fan'), fanbox=$('fanbox'),")
pts = json.loads((W/'peek.json').read_text())
sub("  /* ---------- smooth scroll engine ---------- */", PEEK_JS.replace('__PTS__', json.dumps([pts[str(i)] for i in range(4)])) + "\n  /* ---------- smooth scroll engine ---------- */")
sub("var PAGES=['about','contact','tool','app'], toolLoaded=false, signedIn=false, hadPage=false;\n  try{ signedIn=sessionStorage.getItem('evs-in')==='1' }catch(e){}\n",
    "var PAGES=['about','contact','tool','app','privacy','terms'], toolLoaded=false, hadPage=false;\n")
sub("fr.srcdoc=new TextDecoder('utf-8').decode(by) }", "fr.srcdoc=new TextDecoder('utf-8').decode(by).replace('/*EVS_FONTS*/',function(){ return $('evs-fonts').textContent }) }")
sub("    if(pg==='tool'&&signedIn){ location.hash='app'; return }\n", '')
sub("  addEventListener('hashchange',route);\n", "  addEventListener('hashchange',route);\n  addEventListener('message',function(e){ if(e.data&&e.data.evs==='exit'&&e.source===$('toolFrame').contentWindow) location.hash='tool' });\n  $('skip').addEventListener('click',function(e){ var v=[].slice.call(document.querySelectorAll('.view')).filter(function(x){ return getComputedStyle(x).display!=='none' })[0]; if(v){ e.preventDefault(); var h=v.querySelector('h1'); h.tabIndex=-1; h.focus() } });\n")
sub("location.href='mailto:[YOUR EMAIL]?subject='", "location.href='mailto:'+(ORG.email||'')+'?subject='")
sub("  $('signinForm').addEventListener('submit',function(e){ e.preventDefault(); signedIn=true; try{sessionStorage.setItem('evs-in','1')}catch(x){} location.hash='app' });\n", '')
sub("$('askClose').addEventListener('click',function(){ askPanel.classList.remove('on') });", "$('askClose').addEventListener('click',function(){ askPanel.classList.remove('on'); $('askOpen').focus() });")
sub("document.querySelectorAll('[placeholder],[aria-label],[title]')).forEach(function(el){ ['placeholder','aria-label','title'].forEach(", "document.querySelectorAll('[placeholder],[aria-label],[title],img[alt]')).forEach(function(el){ ['placeholder','aria-label','title','alt'].forEach(")
sub("document.title='EV Scope · '+(D&&D['Scope before you sign.']||'Scope before you sign.');\n    try{localStorage.setItem('evs-lang',lang)}catch(e){}\n", "document.title='EV Scope · '+(D&&D['Scope before you sign']||'Scope before you sign');\n")
sub("function pickLang(l){ translate(l); openLang(false); langBtn.focus() }", "function pickLang(l){ translate(l); try{localStorage.setItem('evs-lang',l)}catch(e){} openLang(false); langBtn.focus() }")

# ---------- translations ----------
m = re.search(r'window\.__I18N=(\{.*\});</script>', s)
D = json.loads(m.group(1))
NEW['Sending opens your email app with the message filled in. Nothing reaches us before you send it.'] = {
  'da': 'Når du sender, åbnes din mailapp med beskeden udfyldt. Intet når frem til os, før du sender den.',
  'de': 'Beim Senden öffnet sich Ihre E-Mail-App mit ausgefüllter Nachricht. Nichts erreicht uns, bevor Sie sie senden.',
  'nl': 'Bij verzenden opent je e-mailapp met het bericht al ingevuld. Niets bereikt ons voordat je het verstuurt.'}
for L in D:
    for old, (new, vals) in RENAME.items():
        v = D[L].pop(old)
        D[L][new] = vals[L] if vals else v.rstrip('.')
    for k, v in NEW.items(): D[L][k] = v[L]
    for i, a in enumerate(PEEK_ALT): D[L][a] = ALT_TR[i][L]
    for k in [k for k in D[L] if re.match(r'0\d · ', k)] + ['Open the tool', 'Sign in to EV Scope.', 'Password', 'Sign in', 'No account yet? Ask for early access.', 'Early-access customers sign in here.', 'The tool', 'Inside one depot', 'Questions we get', 'Every vehicle, one method', 'Scope · Denmark & EU', 'Your results, kept current', 'Run your own studies', 'We run it for you', 'Sending opens your email app with the message filled in.']:
        D[L].pop(k, None)
s = s[:m.start(1)] + json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + s[m.end(1):]

# every visible English string in the new markup must have a translation
import html as _h
body = s[s.index('<body>'):s.index('<script id="toolsrc"')]
body = re.sub(r'<svg.*?</svg>|<script.*?</script>', '', body, flags=re.S)
texts = set(re.sub(r'\s+', ' ', _h.unescape(t)).strip() for t in re.findall(r'>([^<>]+)<', body))
skip = {'EV', 'Scope', 'English', 'Dansk', 'Deutsch', 'Nederlands', '←', '→', '↓', '×', '0'}
miss = sorted(t for t in texts if t and t not in D['da'] and t not in skip and not t.startswith('[['))
print('untranslated text nodes:', miss)

# ---------- put the heavy parts back ----------
for i, b64 in enumerate(imgs): s = s.replace('data:image/webp;base64,[[IMG%d]]' % i, 'data:image/webp;base64,' + b64)
for i in range(4): s = s.replace('[[PEEK%d]]' % i, base64.b64encode((W/('peek%d.webp' % i)).read_bytes()).decode())
tool = tool_html(False)
s = s.replace('[[TOOL_B64]]', base64.b64encode(tool.encode('utf-8')).decode())
s = s.replace('[[FONTS]]', fonts_css())
assert '[[' not in s.replace('[[', '', 0) or not re.search(r'\[\[(IMG|PEEK|TOOL|FONTS)', s)
assert 'fonts.googleapis' not in s and 'gstatic' not in s
(W/'out').mkdir(exist_ok=True)
(W/'out/ev-scope-site.html').write_text(s, encoding='utf-8')
print('site bytes', len(s.encode('utf-8')))
