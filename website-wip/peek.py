import asyncio, json, re
from playwright.async_api import async_playwright
from PIL import Image
W,H=1200,720
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':W,'height':H}, device_scale_factor=1.5)
        await pg.goto('file:///home/claude/work/out/ev-scope-tool.html'); await pg.wait_for_timeout(400)
        async def c(sel):
            bb = await pg.locator(sel).first.bounding_box(); return [round((bb['x']+bb['width']/2)/W*100,2), round((bb['y']+bb['height']/2)/H*100,2)]
        pts=[]
        await pg.screenshot(path='peek0.png'); pts.append([await c('[data-tpl="rt|1"]'), await c('#bRun')])
        await pg.click('#bRun'); await pg.wait_for_timeout(900)
        fv=[re.sub(r'\s+',' ',t).strip() for t in await pg.locator('.fig .fv').all_inner_texts()]
        fn=[t.strip() for t in await pg.locator('.fig .fn').all_inner_texts()]
        row=[t.strip() for t in await pg.locator('.t:not(.checks) tbody tr').first.locator('td').all_inner_texts()]
        await pg.screenshot(path='peek1.png'); pts.append([await c('.fig:nth-child(4) .fv'), await c('.stab[data-tab="cost"]')])
        await pg.click('.stab[data-tab="cost"]'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='peek2.png'); pts.append([await c(".fig:nth-child(3) .fv"), await c('[data-main="setup"]')])
        out={'pts':pts,'fv':fv,'fn':fn,'row':row}; print(json.dumps(out,ensure_ascii=False)); open('peek.json','w').write(json.dumps(out,ensure_ascii=False)); await b.close()
    for i in range(3): Image.open(f'peek{i}.png').convert('RGB').save(f'peek{i}.webp',quality=82,method=6)
asyncio.run(main())
