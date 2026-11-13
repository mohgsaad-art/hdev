import asyncio
from playwright.async_api import async_playwright
SET=['fleet','depot','charging','weather','prices','costs','co2in','check']; RES=['ov','en','bat','ch','gr','cost','co2','src']
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
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(120); await pg.screenshot(path=f's_{t}.png', full_page=False)
            print(t, '|', await T('h1'))
        # field marks
        await pg.click('.stab[data-tab="prices"]'); await pg.fill('input[data-k="dPrice"]','13')
        print('mark after edit:', await pg.evaluate("document.querySelector('input[data-k=dPrice]').closest('[data-s]').dataset.s"), '| reset visible:', await pg.is_visible('[data-reset="dPrice"]'))
        await pg.click('[data-reset="dPrice"]'); print('after reset:', await pg.input_value('input[data-k="dPrice"]'))
        await pg.click('.stab[data-tab="costs"]'); await pg.fill('input[data-k="priceEV"]',''); print('state:', await T('#runState'))
        await pg.click('.stab[data-tab="check"]'); print('miss:', await T('.misslist')); await pg.click('[data-miss="0"]'); await pg.wait_for_timeout(100); print('went to:', await T('h1'))
        await pg.fill('input[data-k="priceEV"]','2050000')
        await pg.click('.stab[data-tab="fleet"]'); await pg.click('[data-tpl="veh|1"]'); await pg.wait_for_timeout(150); await pg.screenshot(path='s_dlg.png')
        await pg.click('summary:has-text("On-board systems")'); await pg.wait_for_timeout(100); await pg.screenshot(path='s_dlg2.png')
        await pg.click('[data-goto="costs"]'); await pg.wait_for_timeout(100); print('goto from dialog:', await T('h1'))
        await pg.click('#bRun'); await pg.wait_for_timeout(700)
        for t in RES:
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(150); await pg.screenshot(path=f's_{t}.png', full_page=False)
            print(t, '|', await T('h1'), '|', (await T('.status')) if await pg.locator('.status').count() else '')
        await pg.click('.stab[data-tab="ch"]'); await pg.click('[data-plan="early"]'); await pg.wait_for_timeout(700); print('plan switch:', await T('#runState'))
        await pg.click('.stab[data-tab="gr"]'); await pg.wait_for_timeout(150); print('grid:', await T('.status'))
        await pg.click('[data-main="cmp"]'); await pg.wait_for_timeout(150); await pg.screenshot(path='s_cmp.png')
        await pg.click('[data-main="docs"]'); await pg.wait_for_timeout(100)
        for k in ['feas','grid','tender','fin','grant','deck']:
            n = await pg.evaluate(f"(()=>{{window.print=()=>{{}};document.querySelector('[data-doc={k}]').click();return document.getElementById('printRep').innerHTML.length}})()")
            print('doc',k,n)
        await pg.click('#bAi'); await pg.fill('#aiIn','what about a cold winter?'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(150); print('ai:', (await T('#msgs'))[-200:].replace('\n',' | ')); await pg.click('#aiClose')
        # failing case
        await pg.click('[data-main="setup"]'); await pg.click('.stab[data-tab="depot"]'); await pg.fill('input[data-k="limit"]','150'); await pg.click('#bRun'); await pg.wait_for_timeout(700)
        await pg.screenshot(path='s_fail_ov.png'); await pg.click('.stab[data-tab="gr"]'); await pg.wait_for_timeout(150); await pg.screenshot(path='s_fail_gr.png'); print('fail:', await T('.status'))
        await pg.set_viewport_size({'width':390,'height':800})
        for t in ['ov','bat']:
            await pg.click(f'.stab[data-tab="{t}"]'); await pg.wait_for_timeout(200); print('m overflow', t, await pg.evaluate("document.documentElement.scrollWidth>innerWidth")); await pg.screenshot(path=f's_m_{t}.png')
        await pg.click('[data-main="setup"]'); await pg.click('.stab[data-tab="costs"]'); await pg.wait_for_timeout(200); await pg.screenshot(path='s_m_costs.png', full_page=False)
        print('ERRS', errs); await b.close()
asyncio.run(main())
