/** Check actual SMIL playback in Chromium and record progressive typing evidence. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const server=await serve();const browser=await launch();const out=path.join(root,'assets/previews/profile');await fs.mkdir(out,{recursive:true});
const config=JSON.parse(await fs.readFile(path.join(root,'config/profile.json'),'utf8'));
const report={status:'passed',identities:[],carousels:[]};
try{
 const page=await browser.newPage({viewport:{width:720,height:126},deviceScaleFactor:2});
 for(const variant of ['dark','light','mobile-dark','mobile-light']){
  await page.goto(`${server.origin}/assets/profile/generated/identity-${variant}.svg`);
  const frames=[];
  for(const time of [0,.5,1.5,2.8,8]){
   const frame=await page.evaluate(time=>{
    const svg=document.documentElement;svg.pauseAnimations();svg.setCurrentTime(time);
    return {time,widths:[...document.querySelectorAll('clipPath rect')].map(r=>r.width.animVal.value),cursors:[...document.querySelectorAll('g>rect')].map(r=>Number(getComputedStyle(r).opacity))};
   },time);
   frames.push(frame);
   if(variant==='dark'&&[.5,1.5,2.8].includes(time))await page.screenshot({path:path.join(out,`typing-${time}.png`)});
  }
  if(!frames[0].widths.every(w=>w===0))throw new Error('Identity starts fully visible');
  if(!(frames[1].widths[0]>0&&frames[1].widths[0]<frames[3].widths[0]))throw new Error('Name does not type progressively');
  if(!frames[3].widths.every(w=>w>0)||frames[3].cursors.some(Boolean))throw new Error('Identity does not settle');
  if(JSON.stringify(frames[3].widths)!==JSON.stringify(frames[4].widths))throw new Error('Typing repeats');
  report.identities.push({variant,frames});
 }
 for(const variant of ['projects-carousel','projects-carousel-mobile','projects-carousel-reduced','projects-carousel-mobile-reduced']){
  const mobile=variant.includes('mobile');const reduced=variant.endsWith('reduced');
  await page.setViewportSize({width:mobile?config.carousel.mobile_width:config.carousel.width,height:mobile?config.carousel.mobile_height:config.carousel.height});
  await page.goto(`${server.origin}/assets/profile/generated/${variant}.svg`);
  const width=page.viewportSize().width;const frames=[];
  for(const time of reduced?[0,2.9,3,3.2,5.9,6.1]:[0,2.9,3.2,3.5,6.3,7]){
   const state=await page.evaluate(time=>{const s=document.documentElement;s.pauseAnimations();s.setCurrentTime(time);return {time,x:document.querySelector('#track').transform.animVal.getItem(0).matrix.e};},time);frames.push(state);
   if([0,3.2,3.5].includes(time))await page.screenshot({path:path.join(out,`${variant}-${time}.png`)});
  }
  if(Math.abs(frames[0].x)>0.01||Math.abs(frames[1].x)>0.01)throw new Error('First project is not held for three seconds');
  if(reduced){if(Math.abs(frames[2].x+width)>0.01)throw new Error('Reduced-motion view is static after three seconds');}
  else if(!(frames[2].x<0&&frames[2].x>-width))throw new Error('Carousel does not slide horizontally');
  if(Math.abs(frames[3].x+width)>0.01||Math.abs(frames[4].x+width)>0.01)throw new Error('Second project is not held');
  if(Math.abs(frames[5].x)>0.01)throw new Error('Carousel does not loop back to the first project');
  report.carousels.push({variant,frames});
 }
 await page.setViewportSize({width:720,height:126});
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
 await page.route('**/carousel-test.html',route=>route.fulfill({contentType:'text/html',body:`<body style="margin:0"><img src="${server.origin}/assets/profile/generated/projects-carousel.svg?embedded-playback" width="1000"></body>`}));
 await page.setViewportSize({width:1000,height:config.carousel.height});await page.goto(`${server.origin}/carousel-test.html`);
 await page.waitForFunction(()=>document.images[0].complete&&document.images[0].naturalWidth>0);
 const carouselImage=page.locator('img');const first=await carouselImage.screenshot({path:path.join(out,'carousel-image-first.png')});
 await page.waitForTimeout(3700);const second=await carouselImage.screenshot({path:path.join(out,'carousel-image-second.png')});
 if(first.equals(second))throw new Error('Carousel is static when embedded as an image');
 report.embeddedCarousel='Both project images recorded in the same image element';
 await page.route('**/reduced-carousel-test.html',route=>route.fulfill({contentType:'text/html',body:`<body style="margin:0"><img src="${server.origin}/assets/profile/generated/projects-carousel-reduced.svg?actual-reduced-playback" width="1000"></body>`}));
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto(`${server.origin}/reduced-carousel-test.html`);await page.waitForFunction(()=>document.images[0].complete&&document.images[0].naturalWidth>0);
 const reducedFirst=await page.locator('img').screenshot({path:path.join(out,'carousel-reduced-first.png')});await page.waitForTimeout(3200);
 const reducedSecond=await page.locator('img').screenshot({path:path.join(out,'carousel-reduced-second.png')});if(reducedFirst.equals(reducedSecond))throw new Error('Reduced-motion default does not change project automatically');
 report.reducedPlayback='Automatic three-second switch confirmed with reduced motion enabled';
 await fs.writeFile(path.join(out,'animation-report.json'),JSON.stringify(report,null,2));
 console.log('Typing settles once. Both carousel variants hold, slide horizontally, show the second project, and loop smoothly.');
}finally{await browser.close();await server.close();}
