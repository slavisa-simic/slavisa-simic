/** Inspect the actual public profile, without replacing markup or intercepting media. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {root,launch} from './lib.mjs';
const config=JSON.parse(await fs.readFile(path.join(root,'config/profile.json'),'utf8'));
const out=path.join(root,'assets/previews/profile');await fs.mkdir(out,{recursive:true});
const browser=await launch();const report={url:`https://github.com/${config.owner}`,checked_at:new Date().toISOString(),checks:[]};
function check(value,message){if(!value)throw new Error(message);}
try{
 const context=await browser.newContext({colorScheme:'dark',reducedMotion:'no-preference'});const page=await context.newPage();
 async function capture(article,name){
  await page.evaluate(()=>scrollTo(0,0));
  const bounds=await article.boundingBox();const width=page.viewportSize().width;
  // Keep the whole article visible so GitHub's sticky tabs cannot cover the identity.
  await page.setViewportSize({width,height:Math.ceil(bounds.y+bounds.height+100)});
  await page.evaluate(()=>scrollTo(0,0));await article.screenshot({path:path.join(out,name)});
  await page.setViewportSize({width,height:1000});
 }
 for(const width of [1440,390,320]){
  await page.setViewportSize({width,height:1000});await page.goto(report.url,{waitUntil:'domcontentloaded'});
  const article=page.locator('.markdown-body').first();await article.waitFor();
  check((await article.locator('h2').allTextContents()).join('|')==='Projects|Toolkit|Recent work','Published profile has not updated');
  await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
  const state=await article.evaluate(a=>({width:innerWidth,images:[...a.querySelectorAll('img')].map(i=>({src:i.currentSrc,alt:i.alt,width:i.clientWidth,height:i.clientHeight,loaded:i.naturalWidth>0,href:i.closest('a')?.href})),tables:[...a.querySelectorAll('table')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth})),text:a.innerText}));
  check(state.images.length===4,'Unexpected published image count');
  check(state.tables.every(t=>t.scrollWidth<=t.width+1),'Published table overflows');
  for(const p of config.projects){const image=state.images.find(i=>i.alt.startsWith(p.name+':'));check(image?.href===p.readme,`Wrong destination for ${p.name}`);check(image.width>=44&&image.height>=44,'Project target too small');}
  check(state.images[0].src.includes(width<=600?'identity-mobile-dark.svg':'identity-dark.svg'),'Wrong identity variant');
  check(state.images[1].src.includes(width<=600?'vigil-mobile.gif':'vigil.gif'),'Wrong slideshow variant');
  await article.locator('details').last().locator('summary').click();check(await article.locator('details').last().evaluate(d=>d.open),'Published disclosure does not work');await article.locator('details').last().locator('summary').click();
  if(width===1440){await page.waitForTimeout(4400);await capture(article,'published-animated.png');}
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].slice(0,3).every(i=>i.currentSrc.includes('.png')&&i.complete&&i.naturalWidth>0));
  if(width===390||width===1440)await capture(article,`published-${width===390?'mobile':'desktop'}.png`);
  state.reducedMotion='PNG identity and project previews';report.checks.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.reload({waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
 const light=await page.locator('.markdown-body img').first().evaluate(i=>i.currentSrc);check(light.includes('identity-light.png'),'Light identity was not selected');
 await capture(page.locator('.markdown-body').first(),'published-light.png');
 report.status='passed';console.log('Public profile verified: native content, actual media, README links, disclosures, themes, responsive layouts, and reduced motion.');
}catch(error){report.status='failed';report.error=error.message;throw error;}
finally{await fs.writeFile(path.join(out,'published-report.json'),JSON.stringify(report,null,2));await browser.close();}
