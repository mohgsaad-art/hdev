import asyncio
from playwright.async_api import async_playwright
SET=['project','fleet','templates','depot','charging','weather','prices','costs','tax','check']; RES=['ov','en','bat','ch','gr','cost','co2','src']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1360,'height':900})
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('file:///home/claude/work/out/ev-scope-tool.html'); await pg.wait_for_timeout(300)
        T=lambda sel: pg.inner_text(sel)
        for t in SET:
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(120); await pg.screenshot(path=f's_{t}.png')
            print(t, '|', await T('h1'), '| popups:', await pg.locator('.popb').all_inner_texts())
        # templates: each library, popups
        await pg.click('.stab[data-tab="templates"]')
        for l in ['veh','rt','load','eq','sch']:
            await pg.click(f'[data-tl="{l}"]'); await pg.wait_for_timeout(80); print(' tpl',l, await pg.locator('.ted .fr').count(), await pg.locator('.popb').all_inner_texts())
        await pg.click('[data-tl="veh"]'); await pg.click('.popb:has-text("Cab heating")'); await pg.wait_for_timeout(150); await pg.screenshot(path='s_pop.png')
        await pg.click('.dlg input[value="thermal"]'); await pg.wait_for_timeout(150); print('thermal state:', await T('#runState')); await pg.screenshot(path='s_pop2.png')
        await pg.click('.dlg input[value="const"]'); await pg.click('[data-close]')
        await pg.click('.popb:has-text("Tyres")'); await pg.fill('.dlg input[data-k="crr"]','7'); await pg.click('[data-close]'); print('pop label:', await pg.inner_text('.popb:has-text("Tyres")'))
        # fleet: dropdown, bulk, stops
        await pg.click('.stab[data-tab="fleet"]'); await pg.select_option('[data-gl="sch|2"]','s1'); await pg.wait_for_timeout(100)
        await pg.check('[data-sel="1"]'); await pg.check('[data-sel="2"]'); await pg.select_option('#bulkL','eq'); await pg.select_option('#bulkT','e0'); await pg.screenshot(path='s_bulk.png'); await pg.click('[data-bulk]'); await pg.wait_for_timeout(100)
        print('after bulk:', await pg.eval_on_selector_all('[data-gl^="eq|"]','e=>e.map(x=>x.value)'))
        await pg.select_option('[data-gl="eq|1"]','e1'); await pg.select_option('[data-gl="eq|2"]','e1'); await pg.select_option('[data-gl="sch|2"]','s2')
        await pg.click('[data-stops="1"]'); await pg.wait_for_timeout(300); print('stop rows:', await pg.locator('.stops tbody tr').count())
        await pg.fill('[data-st="1|3|t"]','120'); await pg.screenshot(path='s_stops.png'); await pg.click('[data-close]')
        await pg.click('#bRun'); await pg.wait_for_timeout(700)
        for t in RES:
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(150); print(t, '|', (await T('.status')) if await pg.locator('.status').count() else await T('h1'))
        await pg.click('.stab[data-tab="src"]'); await pg.screenshot(path='s_src.png')
        await pg.click('[data-main="docs"]'); n = await pg.evaluate("(()=>{window.print=()=>{};document.querySelector('[data-doc=feas]').click();return document.getElementById('printRep').innerHTML.length})()"); print('doc',n)
        # missing → popup jump
        await pg.click('[data-main="setup"]'); await pg.click('.stab[data-tab="templates"]'); await pg.click('.popb:has-text("Drivetrain")'); await pg.fill('.dlg input[data-k="effMot"]',''); await pg.click('[data-close]')
        await pg.click('.stab[data-tab="check"]'); print('miss:', await T('.misslist')); await pg.click('[data-miss="0"]'); await pg.wait_for_timeout(200); print('opened:', await T('#dlgT'))
        await pg.click('[data-reset="effMot"]'); await pg.click('[data-close]')
        await pg.set_viewport_size({'width':390,'height':800})
        for t in ['fleet','templates']:
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(200); print('m overflow', t, await pg.evaluate("document.documentElement.scrollWidth>innerWidth+1")); await pg.screenshot(path=f's_m_{t}.png')
        print('ERRS', errs); await b.close()
asyncio.run(main())
