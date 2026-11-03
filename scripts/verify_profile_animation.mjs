/** Check actual SMIL playback in Chromium and record progressive typing evidence. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const server=await serve();const browser=await launch();const out=path.join(root,'assets/previews/profile');await fs.mkdir(out,{recursive:true});
const report={status:'passed',identities:[]};
try{
 const page=await browser.newPage({viewport:{width:720,height:126},deviceScaleFactor:2});
 for(const variant of ['dark','light','mobile-dark','mobile-light']){
  await page.goto(`${server.origin}/assets/profile/generated/identity-${variant}.svg`);
  const frames=[];
  for(const time of [0,.5,2,4.3,8]){
   const frame=await page.evaluate(time=>{
    const svg=document.documentElement;svg.pauseAnimations();svg.setCurrentTime(time);
    return {time,widths:[...document.querySelectorAll('clipPath rect')].map(r=>r.width.animVal.value),cursors:[...document.querySelectorAll('g>rect')].map(r=>Number(getComputedStyle(r).opacity))};
   },time);
   frames.push(frame);
   if(variant==='dark'&&[.5,2,4.3].includes(time))await page.screenshot({path:path.join(out,`typing-${time}.png`)});
  }
  if(!frames[0].widths.every(w=>w===0))throw new Error('Identity starts fully visible');
  if(!(frames[1].widths[0]>0&&frames[1].widths[0]<frames[3].widths[0]))throw new Error('Name does not type progressively');
  if(!frames[3].widths.every(w=>w>0)||frames[3].cursors.some(Boolean))throw new Error('Identity does not settle');
  if(JSON.stringify(frames[3].widths)!==JSON.stringify(frames[4].widths))throw new Error('Typing repeats');
  report.identities.push({variant,frames});
 }
 // SVG loaded as an image must also animate; GitHub embeds it in this context.
 await page.route('**/typing-test.html',route=>route.fulfill({contentType:'text/html',body:`<body style="margin:0;background:#0d1117"><img src="${server.origin}/assets/profile/generated/identity-dark.svg?image-playback" width="720"></body>`}));
 await page.goto(`${server.origin}/typing-test.html`);
 await page.waitForFunction(()=>document.images[0].complete&&document.images[0].naturalWidth>0);
 await page.locator('img').screenshot({path:path.join(out,'typing-image-start.png')});
 await page.waitForTimeout(4400);
 await page.locator('img').screenshot({path:path.join(out,'typing-image-complete.png')});
 const initial=await fs.readFile(path.join(out,'typing-image-start.png'));const final=await fs.readFile(path.join(out,'typing-image-complete.png'));
 if(initial.equals(final))throw new Error('Typing is static when embedded as an image');
 report.embeddedImage='Progressive playback and complete resting state recorded';
 await fs.writeFile(path.join(out,'animation-report.json'),JSON.stringify(report,null,2));
 console.log('Typing progresses once, settles before 4.3 seconds, and stays complete in all four variants.');
}finally{await browser.close();await server.close();}
