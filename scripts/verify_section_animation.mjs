/** Verify section-heading animation in the actual sanitized README, plus exact loop seams. */
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root,launch,serve} from './lib.mjs';
const browser=await launch(),server=await serve();
const out=path.join(root,'assets/previews/profile');
const report={status:'pending',playback:[],loops:[]};
try {
 const page=await browser.newPage({deviceScaleFactor:1});
 const selectors=['img[alt="Projects"]','img[alt="GitHub Activity"]','img[alt^="About Me."]'];
 for(const width of [390,1440])for(const theme of ['dark','light'])for(const motion of ['no-preference','reduce']){
  await page.setViewportSize({width,height:1100});
  await page.emulateMedia({colorScheme:theme,reducedMotion:motion});
  await page.goto(`${server.origin}/assets/previews/profile/${theme}.html`);
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
  const before=[];
  for(const selector of selectors){
   const image=page.locator(selector);
   assert((await image.evaluate(i=>i.currentSrc)).includes('animated'));
   before.push(await image.screenshot());
  }
  await page.waitForTimeout(900);
  for(let i=0;i<selectors.length;i++){
   assert(!before[i].equals(await page.locator(selectors[i]).screenshot()),`${selectors[i]} is static at ${width}/${theme}/${motion}`);
  }
  report.playback.push({width,theme,motion,animatedSections:3});
 }
 const names=['title-projects-animated','title-projects-animated-mobile',
              'title-github-activity-animated','title-github-activity-animated-mobile',
              'about-me-animated','about-me-animated-mobile','about-me-animated-light','about-me-animated-mobile-light'];
 for(const name of names){
  await page.goto(`${server.origin}/assets/profile/generated/${name}.svg`);
  await page.evaluate(()=>{document.documentElement.pauseAnimations();document.documentElement.setCurrentTime(0);});
  const first=await page.locator('svg').screenshot();
  await page.evaluate(()=>document.documentElement.setCurrentTime(6));
  assert(first.equals(await page.locator('svg').screenshot()),`${name} has a loop jump`);
  await page.evaluate(()=>document.documentElement.setCurrentTime(3));
  assert(!first.equals(await page.locator('svg').screenshot()),`${name} has no changing pixels`);
  report.loops.push({name,seamless:true});
 }
 await page.setViewportSize({width:1440,height:1100});
 await page.emulateMedia({colorScheme:'dark',reducedMotion:'no-preference'});
 await page.goto(`${server.origin}/assets/previews/profile/dark.html`);
 await page.locator('article table').screenshot({path:path.join(out,'centered-table.png')});
 report.status='passed';
 console.log('All three section headers animate in both sizes, themes, and motion settings. Eight SVG loops are seamless.');
}finally{
 await fs.writeFile(path.join(out,'section-animation-report.json'),JSON.stringify(report,null,2));
 await browser.close();await server.close();
}
