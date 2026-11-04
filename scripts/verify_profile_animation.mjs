/** Check actual carousel playback in both motion preferences. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const server=await serve();const browser=await launch();const out=path.join(root,'assets/previews/profile');await fs.mkdir(out,{recursive:true});
const config=JSON.parse(await fs.readFile(path.join(root,'config/profile.json'),'utf8'));
const report={status:'passed',carousels:[]};
try{
 const page=await browser.newPage({deviceScaleFactor:1});
 for(const variant of ['projects-carousel','projects-carousel-mobile','projects-carousel-reduced','projects-carousel-mobile-reduced']){
  const mobile=variant.includes('mobile');const reduced=variant.endsWith('reduced');
  await page.setViewportSize({width:mobile?config.carousel.mobile_width:config.carousel.width,height:mobile?config.carousel.mobile_height:config.carousel.height});
  await page.goto(`${server.origin}/assets/profile/generated/${variant}.svg`);
  const width=page.viewportSize().width;const frames=[];
  for(const time of reduced?[0,2.9,3,3.2,5.9,6.1]:[0,2.9,3.2,3.5,6.3,7]){
   const state=await page.evaluate(time=>{const s=document.documentElement;s.pauseAnimations();s.setCurrentTime(time);return {time,x:document.querySelector('#track').transform.animVal.getItem(0).matrix.e,indicators:[...document.querySelectorAll('[id^="indicator-"]')].map(el=>Number(getComputedStyle(el).opacity))};},time);frames.push(state);
   if([0,3.2,3.5].includes(time))await page.screenshot({path:path.join(out,`${variant}-${time}.png`)});
  }
  if(Math.abs(frames[0].x)>0.01||Math.abs(frames[1].x)>0.01)throw new Error('First project is not held for three seconds');
  if(reduced){if(Math.abs(frames[2].x+width)>0.01)throw new Error('Reduced-motion view is static after three seconds');}
  else if(!(frames[2].x<0&&frames[2].x>-width))throw new Error('Carousel does not slide horizontally');
  if(Math.abs(frames[3].x+width)>0.01||Math.abs(frames[4].x+width)>0.01)throw new Error('Second project is not held');
  if(Math.abs(frames[5].x)>0.01)throw new Error('Carousel does not loop back to the first project');
  for(const [frame,active] of [[frames[0],0],[frames[3],1],[frames[5],0]]){
   if(frame.indicators.length!==config.projects.length||frame.indicators.some((opacity,i)=>opacity!==(i===active?1:0)))throw new Error('Footer indicators do not match the active project');
  }
  const centered=await page.locator('[id^="indicator-"]').evaluateAll(items=>{
   const start=Number(items[0].getAttribute('x'));const last=items.at(-1);
   return (start+Number(last.getAttribute('x'))+Number(last.getAttribute('width')))/2===Number(document.documentElement.getAttribute('width'))/2;
  });
  if(!centered)throw new Error('Footer indicators must be centered');
  report.carousels.push({variant,frames});
 }
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
 console.log('All four carousel variants hold each project for three seconds and repeat; embedded playback passes.');
}finally{await browser.close();await server.close();}
