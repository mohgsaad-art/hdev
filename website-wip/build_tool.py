import base64, pathlib
W = pathlib.Path('/home/claude/work'); F = pathlib.Path('/home/claude/fonts')
def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
SANS = F/'x/package/fonts/split/woff2'; MONO = F/'m/package/fonts/split/woff2'
L1 = 'U+0000,U+000D,U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2018-201A,U+201C-201E,U+2020-2022,U+2026,U+2030,U+2039-203A,U+2044,U+2074,U+20AC,U+2122,U+2212,U+FB01-FB02'
PI = 'U+0E3F,U+2032-2033,U+2070,U+2075-2079,U+2080-2081,U+2083,U+2085-2089,U+2113,U+2116,U+2126,U+212E,U+2150-2151,U+2153-215E,U+2190-2199,U+21A9-21AA,U+21B0-21B3,U+21B6-21B7,U+21BA-21BB,U+21C4,U+21C6,U+2202,U+2206,U+220F,U+2211,U+221A,U+221E,U+222B,U+2248,U+2260,U+2264-2265,U+25CA,U+2713,U+274C,U+2B0E-2B11'
ML1 = 'U+0020-007E,U+00A0-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2013-2014,U+2018-201A,U+201C-201E,U+2020-2022,U+2026,U+2030,U+2039-203A,U+2044,U+20AC,U+2122,U+2212,U+FB01-FB02'
def face(fam, w, path, rng):
    return "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}" % (fam, w, b64(path), rng)
def fonts_css(mono=False):
    out = ['/* IBM Plex Sans. Copyright (c) 2017 IBM Corp. with Reserved Font Name "Plex". SIL Open Font License 1.1, full text in the comment at the top of this file. Unmodified files from IBM\'s @ibm/plex-sans package. */']
    for w, n in [(400, 'Regular'), (500, 'Medium'), (600, 'SemiBold')]:
        out.append(face('IBM Plex Sans', w, SANS/f'IBMPlexSans-{n}-Latin1.woff2', L1))
    out.append(face('IBM Plex Sans', 400, SANS/'IBMPlexSans-Regular-Pi.woff2', PI))
    if mono:
        for w, n in [(400, 'Regular'), (500, 'Medium')]:
            out.append(face('IBM Plex Mono', w, MONO/f'IBMPlexMono-{n}-Latin1.woff2', ML1))
    return '\n'.join(out)
LICENSE = '<!--\nFont: IBM Plex Sans, embedded below.\n' + (F/'x/package/LICENSE.txt').read_text().replace('--', '- -') + '\n-->\n'
def tool_html(embed_fonts):
    src = W/'src'
    js = '\n'.join((src/n).read_text() for n in ['model.js', 'ui.js', 'results.js', 'app.js'])
    h = (src/'tool.html').read_text().replace('/*TOOL_CSS*/', (src/'tool.css').read_text()).replace('/*TOOL_JS*/', js)
    if embed_fonts:
        h = h.replace('/*EVS_FONTS*/', fonts_css()).replace('<!doctype html>\n', '<!doctype html>\n' + LICENSE, 1)
    return h
if __name__ == '__main__':
    (W/'out').mkdir(exist_ok=True)
    t = tool_html(True); (W/'out/ev-scope-tool.html').write_text(t); print('tool', len(t))
