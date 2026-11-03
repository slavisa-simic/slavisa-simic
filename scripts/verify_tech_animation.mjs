/** Verify SMIL direction, periodic pixels, alpha, and real image playback. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const manifest=JSON.parse(await fs.readFile(path.join(root,'assets/profile/generated/tech-manifest.json'),'utf8'));
const server=await serve(),browser=await launch();
const out=path.join(root,'assets/previews/profile');await fs.mkdir(out,{recursive:true});
const report={status:'passed',variants:[]};
function check(value,message){if(!value)throw new Error(message);}
try{
 const page=await browser.newPage({deviceScaleFactor:1});
 for(const [name,spec] of Object.entries(manifest)){
  await page.setViewportSize({width:spec.width,height:spec.height});
  await page.goto(`${server.origin}/assets/profile/generated/${name}.svg`);
  await page.waitForFunction(()=>[...document.querySelectorAll('image')].every(i=>!!i.href.baseVal));
  if(spec.static){check(await page.locator('animateTransform').count()===0,'Reduced-motion variant must be static');continue;}
  const samples=[];const pixels=[];
  for(const time of [0,1,spec.duration_seconds-0.001,spec.duration_seconds,spec.duration_seconds+1]){
   const x=await page.evaluate(t=>{const s=document.documentElement;s.pauseAnimations();s.setCurrentTime(t);return document.querySelector('#tech-track').transform.animVal.getItem(0).matrix.e;},time);
   samples.push({time,x});pixels.push(await page.screenshot({omitBackground:true}));
  }
  check(samples[1].x>samples[0].x,'Track must move LEFT to RIGHT');
  check(Math.abs(samples[1].x-samples[0].x-spec.period/spec.duration_seconds)<0.01,'Speed must be constant');
  check(Math.abs(samples[2].x)<0.1,'End of cycle must approach zero without a pause');
  check(pixels[0].equals(pixels[3])&&pixels[1].equals(pixels[4]),'Repeating frames must be pixel-identical across the loop');
  if(name==='tech-carousel')await fs.writeFile(path.join(out,'tech-transparent.png'),pixels[0]);
  report.variants.push({name,samples,seam:'Pixel-identical period boundaries'});
 }
 // Verify nested animation in the actual composed header as an <img>, with
 // the same image security restrictions as a GitHub README.
 for(const [variant,width] of [['profile-header',808],['profile-header-mobile',288]]){
  await page.setViewportSize({width,height:340});
  await page.route(`**/${variant}-playback.html`,route=>route.fulfill({contentType:'text/html',body:`<body style="margin:0;background:#0d1117"><img src="${server.origin}/assets/profile/generated/${variant}.svg?playback"></body>`}));
  await page.goto(`${server.origin}/${variant}-playback.html`);
  await page.waitForFunction(()=>document.images[0].complete&&document.images[0].naturalWidth>0);
  const alpha=await page.evaluate(()=>{const img=document.images[0],c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;const ctx=c.getContext('2d');ctx.drawImage(img,0,0);const data=ctx.getImageData(0,0,c.width,c.height).data;let transparent=0,partial=0;for(let i=3;i<data.length;i+=4){if(data[i]===0)transparent++;else if(data[i]<255)partial++;}return {transparent,partial};});
  check(alpha.transparent>0&&alpha.partial>0,'Header must preserve real alpha transparency and fading');
  const before=await page.locator('img').screenshot();await page.waitForTimeout(1100);const after=await page.locator('img').screenshot();
  check(!before.equals(after),`${variant} does not animate inside an image`);
  await page.locator('img').screenshot({path:path.join(out,`${variant}-animated-preview.png`)});
 }
 report.embeddedPlayback='Desktop and mobile headers move as image resources';
 await fs.writeFile(path.join(out,'tech-animation-report.json'),JSON.stringify(report,null,2));
 console.log('Technology carousel: rightward constant motion, exact seamless loops, static reduced-motion alternatives, and embedded header playback passed.');
}finally{await browser.close();await server.close();}
