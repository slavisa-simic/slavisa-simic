/** Offline SVG rasterization only; no JavaScript is used by the published README. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const browser=await launch(), server=await serve();
try {
  const page=await browser.newPage({deviceScaleFactor:1});
  for(const variant of ['activity-commits','activity-commits-mobile']) {
    const out=path.join(root,'assets/profile/build',variant);
    await fs.mkdir(out,{recursive:true});
    await page.goto(`${server.origin}/assets/profile/generated/${variant}.svg`);
    const size=await page.evaluate(()=>({width:document.documentElement.viewBox.baseVal.width,height:document.documentElement.viewBox.baseVal.height}));
    await page.setViewportSize(size);
    await page.evaluate(()=>document.documentElement.pauseAnimations());
    for(let frame=0;frame<48;frame++) {
      await page.evaluate(t=>document.documentElement.setCurrentTime(t),frame/8);
      await page.locator('svg').screenshot({path:path.join(out,`${String(frame).padStart(3,'0')}.png`)});
    }
  }
} finally {await browser.close();await server.close();}
