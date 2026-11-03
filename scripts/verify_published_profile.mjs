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
  check((await article.locator('h3').allTextContents()).join('|')==='Selected work|Toolkit|Activity','Published profile has not updated');
  await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
  const state=await article.evaluate(a=>({width:innerWidth,images:[...a.querySelectorAll('img')].map(i=>({src:i.currentSrc,alt:i.alt,width:i.clientWidth,height:i.clientHeight,loaded:i.naturalWidth>0,href:i.closest('a')?.href})),tables:[...a.querySelectorAll('table')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth})),text:a.innerText}));
  check(state.images.length===3,'Expected one public carousel');
  check(state.tables.every(t=>t.scrollWidth<=t.width+1),'Published table overflows');
  const carousel=state.images[1];check(carousel.href.endsWith(config.carousel.target),'Carousel does not open the project list');check(carousel.width>=44&&carousel.height>=44,'Carousel target too small');
  for(const p of config.projects)check(await article.locator(`a[href="${p.readme}"]`).count()===1,`Wrong README link for ${p.name}`);
  check(state.images[0].src.includes(width<=600?'identity-mobile-dark.svg':'identity-dark.svg'),'Wrong identity variant');
  check(carousel.src.includes(width<=600?'projects-carousel-mobile.svg':'projects-carousel.svg'),'Wrong carousel variant');
  const carouselImage=article.locator('img').nth(1);
  if(width===1440){await carouselImage.screenshot({path:path.join(out,'published-carousel-first.png')});await page.waitForTimeout(3600);await carouselImage.screenshot({path:path.join(out,'published-carousel-second.png')});}
  await carouselImage.click();await page.waitForFunction(()=>location.hash.includes('projects-list'));
  await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body h4')].some(h=>h.textContent==='Projects list'&&h.getBoundingClientRect().top>=0&&h.getBoundingClientRect().top<innerHeight));
  state.carouselNavigation='Click scrolls to the visible projects list';
  await article.locator('details').last().locator('summary').click();check(await article.locator('details').last().evaluate(d=>d.open),'Published disclosure does not work');await article.locator('details').last().locator('summary').click();
  if(width===1440)await capture(article,'published-animated.png');
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(()=>document.querySelector('.markdown-body img').currentSrc.includes('.png')&&document.querySelectorAll('.markdown-body img')[1].currentSrc.includes('-reduced.svg')&&[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
  if(width===1440){const first=await carouselImage.screenshot({path:path.join(out,'published-reduced-first.png')});await page.waitForTimeout(1600);const middle=await carouselImage.screenshot({path:path.join(out,'published-reduced-middle.png')});await page.waitForTimeout(1600);const last=await carouselImage.screenshot({path:path.join(out,'published-reduced-last.png')});check(!first.equals(middle)||!middle.equals(last),'Reduced-motion view is still a static image');}
  if(width===390||width===1440)await capture(article,`published-${width===390?'mobile':'desktop'}.png`);
  state.reducedMotion='Static identity; projects alternate every three seconds without sliding';report.checks.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.reload({waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
 const light=await page.locator('.markdown-body img').first().evaluate(i=>i.currentSrc);check(light.includes('identity-light.png'),'Light identity was not selected');
 await capture(page.locator('.markdown-body').first(),'published-light.png');
 const first=await fs.readFile(path.join(out,'published-carousel-first.png'));const second=await fs.readFile(path.join(out,'published-carousel-second.png'));check(!first.equals(second),'Published carousel is static');
 report.status='passed';console.log('Public profile verified: one moving carousel, project-list navigation, README links, disclosures, themes, mobile layouts, and reduced motion.');
}catch(error){report.status='failed';report.error=error.message;throw error;}
finally{await fs.writeFile(path.join(out,'published-report.json'),JSON.stringify(report,null,2));await browser.close();}
