import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1360,'height':860})
        errs=[]; reqs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        pg.on('request', lambda r: reqs.append(r.url) if not r.url.startswith(('file:','data:','about:','blob:')) else None)
        await pg.goto('file:///home/claude/work/out/ev-scope-site.html'); await pg.wait_for_timeout(1500)
        async def to(sel, off=0):
            await pg.evaluate("([s,o])=>{const e=document.querySelector(s);scrollTo({top:e.getBoundingClientRect().top+scrollY+o,behavior:'instant'})}", [sel, off]); await pg.wait_for_timeout(900)
        await pg.screenshot(path='w_hero.png')
        await pg.click('.hero .pick a[href="#municipalities"]'); await pg.wait_for_timeout(1300)
        print('picked:', await pg.inner_text('.apanel.on h3'), '| hash', await pg.evaluate('location.hash')); await pg.screenshot(path='w_who_muni.png')
        await pg.click('[data-switch="who"] button:nth-child(1)'); await pg.wait_for_timeout(500); await pg.screenshot(path='w_who_fleet.png')
        await pg.click('[data-switch="who"] button:nth-child(4)'); await pg.wait_for_timeout(500); await pg.screenshot(path='w_who_sup.png')
        await pg.click('.apanel.on .dbtn:nth-of-type(2)'); await pg.wait_for_timeout(1400); print('doc picked:', await pg.inner_text('#docinfo .on b')); await pg.screenshot(path='w_docs.png')
        await to('#depot', 500); await pg.screenshot(path='w_story1.png')
        await to('#depot', 2600); await pg.screenshot(path='w_story2.png')
        await to('#demo'); await pg.wait_for_timeout(5200); await pg.screenshot(path='w_peek.png')
        await pg.wait_for_timeout(3000); await pg.screenshot(path='w_peek2.png')
        # deep link
        await pg.goto('file:///home/claude/work/out/ev-scope-site.html#housing'); await pg.wait_for_timeout(1500); print('deep link:', await pg.inner_text('.apanel.on h3'), await pg.evaluate('Math.round(scrollY)'))
        # danish + night
        await pg.click('#langBtn'); await pg.click('[data-lang="da"]'); await pg.wait_for_timeout(500); print('da:', await pg.inner_text('.apanel.on h3'), '|', await pg.inner_text('.apanel.on .hook'))
        await pg.click('[data-switch="theme"] button:nth-child(2)'); await pg.wait_for_timeout(700); await pg.screenshot(path='w_night.png')
        await pg.click('#langBtn'); await pg.click('[data-lang="en"]')
        # tool
        await pg.evaluate("location.hash='app'"); await pg.wait_for_timeout(1500); fr=pg.frame_locator('#toolFrame'); print('tool h1:', await fr.locator('h1').inner_text()); await pg.screenshot(path='w_tool.png')
        await fr.locator('#bExit').click(); await pg.wait_for_timeout(500); print('after exit hash:', await pg.evaluate('location.hash'))
        # mobile
        await pg.set_viewport_size({'width':390,'height':800}); await pg.goto('file:///home/claude/work/out/ev-scope-site.html'); await pg.wait_for_timeout(1500)
        print('m overflow:', await pg.evaluate("document.documentElement.scrollWidth>innerWidth")); await pg.screenshot(path='w_m_hero.png')
        await pg.click('.hero .pick a[href="#fleet-owners"]'); await pg.wait_for_timeout(1300); await pg.screenshot(path='w_m_who.png')
        await to('#documents'); await pg.screenshot(path='w_m_docs.png'); print('m overflow2:', await pg.evaluate("document.documentElement.scrollWidth>innerWidth"))
        print('REQS', reqs); print('ERRS', errs); await b.close()
asyncio.run(main())
