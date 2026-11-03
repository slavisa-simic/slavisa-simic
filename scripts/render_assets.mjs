/** Rasterize the approved authoring canvas. The README itself executes no code. */
import fs from 'node:fs/promises';
import path from 'node:path';
import { root, config, launch, serve } from './lib.mjs';
const server = await serve();
const browser = await launch();
const out = path.join(root,'assets/blueprint');
const geometry = {};
try {
  const context = await browser.newContext({deviceScaleFactor:2,colorScheme:'dark',reducedMotion:'reduce'});
  const page = await context.newPage();
  for(const variant of ['desktop','mobile']) {
    await page.setViewportSize({width:config.exports[variant].width,height:1200});
    await page.goto(`${server.origin}/src/blueprint.html`);
    await page.waitForFunction(()=>window.blueprintReady);
    await page.evaluate(()=>document.fonts.ready);
    await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth));
    geometry[variant] = {};
    for(const row of ['masthead','identity','network','legend','practice','footer']) {
      const locator=page.locator(`[data-row="${row}"]`);
      geometry[variant][row]=await locator.evaluate(el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height}});
      await locator.screenshot({path:path.join(out,'build',`${variant}-${row}.png`)});
    }
    await page.locator('main.hero').screenshot({path:path.join(out,'build',`${variant}-approved-canvas.png`)});
    await page.evaluate(()=>document.body.classList.add('base'));
    await page.locator('[data-row="network"]').screenshot({path:path.join(out,'build',`${variant}-network-base.png`)});
    console.log(`Rendered ${variant} blueprint rows.`);
  }
  await fs.writeFile(path.join(out,'build/row-geometry.json'),JSON.stringify(geometry,null,2));
  await context.close();
} finally {await browser.close();await server.close();}
