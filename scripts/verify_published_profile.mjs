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
  check(await article.locator(`img[alt^="${config.name} — Software Engineer."]`).count()===1,'Published responsive identity is missing');
  await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
  const state=await article.evaluate(a=>({width:innerWidth,images:[...a.querySelectorAll('img')].map(i=>({src:i.currentSrc,alt:i.alt,width:i.clientWidth,height:i.clientHeight,loaded:i.naturalWidth>0,href:i.closest('a')?.href})),tables:[...a.querySelectorAll('table')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth})),text:a.innerText}));
  check(state.images.length===10,'Missing header, contact link, footer decoration, title, carousel, or workflow status');
  check(state.images[0].alt.startsWith(config.name+' — Software Engineer.'),'Missing responsive profile header');
  check(state.images[0].alt.includes('Python')&&!state.images[0].alt.includes('Unity'),'Incorrect personal technology stack');
  for(const [label,url] of [['GitHub Repositories',`https://github.com/${config.owner}?tab=repositories`],['LinkedIn',config.linkedin]])check(await article.locator(`a[href="${url}"] img[alt="${label}"]`).count()===1,`Missing ${label} link`);
  for(const title of ['Projects','Projects list','Project notes','Recent changes'])check(await article.locator(`img[alt="${title}"]`).count()===1,`Missing image title: ${title}`);
  check(state.text.includes('hourly sync')&&state.text.includes('UTC'),'Native statistics sync time is missing');
  const rows=await article.locator('tbody tr').evaluateAll(rows=>rows.map(r=>[...r.cells].map(c=>c.textContent.trim())));
  const data=JSON.parse(await fs.readFile(path.join(root,'assets/profile/activity.json'),'utf8'));
  check(JSON.stringify(rows)===JSON.stringify(data.projects.map(p=>[p.name,String(p.commits_30d),String(p.stars)])),'Native statistics differ from the API snapshot');
  state.nativeStats=rows;
  check(state.tables.every(t=>t.scrollWidth<=t.width+1),'Published table overflows');
  const carousel=state.images.find(i=>i.alt.startsWith('Projects carousel:'));check(carousel.href.endsWith(config.carousel.target),'Carousel does not open the project list');check(carousel.width>=44&&carousel.height>=44,'Carousel target too small');
  for(const p of config.projects)check(await article.locator(`a[href="${p.readme}"]`).count()===1,`Wrong README link for ${p.name}`);
  check(carousel.src.includes(width<=600?'projects-carousel-mobile.svg':'projects-carousel.svg'),'Wrong carousel variant');
  const carouselImage=article.locator('img[alt^="Projects carousel:"]');
  if(width===1440){await carouselImage.screenshot({path:path.join(out,'published-carousel-first.png')});await page.waitForTimeout(3600);await carouselImage.screenshot({path:path.join(out,'published-carousel-second.png')});}
  await carouselImage.click();await page.waitForFunction(()=>location.hash.includes('projects-list'));
  await page.waitForFunction(()=>{const h=document.querySelector('.markdown-body img[alt="Projects list"]')?.closest('h3');return h&&h.getBoundingClientRect().top>=0&&h.getBoundingClientRect().top<innerHeight;});
  state.carouselNavigation='Click scrolls to the visible projects list';
  await article.locator('details').last().locator('summary').click();check(await article.locator('details').last().evaluate(d=>d.open),'Published disclosure does not work');await article.locator('details').last().locator('summary').click();
  if(width===1440)await capture(article,'published-animated.png');
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(()=>document.querySelector('img[alt^="Projects carousel:"]').currentSrc.includes('-reduced.svg')&&[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
  if(width===1440){const first=await carouselImage.screenshot({path:path.join(out,'published-reduced-first.png')});await page.waitForTimeout(1600);const middle=await carouselImage.screenshot({path:path.join(out,'published-reduced-middle.png')});await page.waitForTimeout(1600);const last=await carouselImage.screenshot({path:path.join(out,'published-reduced-last.png')});check(!first.equals(middle)||!middle.equals(last),'Reduced-motion view is still a static image');}
  if(width===390||width===1440)await capture(article,`published-${width===390?'mobile':'desktop'}.png`);
  const headerImage=article.locator('img[alt^="'+config.name+' — Software Engineer."]');
  check(!(await headerImage.evaluate(i=>i.currentSrc)).includes('-reduced.svg'),'Published header selects a static reduced-motion source');
  const headerBefore=await headerImage.screenshot();await page.waitForTimeout(1100);const headerAfter=await headerImage.screenshot();check(!headerBefore.equals(headerAfter),'Published technology marquee does not move with reduced motion enabled');
  state.reducedMotion='Technology marquee keeps moving right; project carousel retains three-second switches';report.checks.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.reload({waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));
 check(await page.locator(`.markdown-body img[alt^="${config.name} — Software Engineer."]`).count()===1,'Light-theme identity is missing');
 await capture(page.locator('.markdown-body').first(),'published-light.png');
 const first=await fs.readFile(path.join(out,'published-carousel-first.png'));const second=await fs.readFile(path.join(out,'published-carousel-second.png'));check(!first.equals(second),'Published carousel is static');
 report.status='passed';console.log('Public profile verified: responsive header, technology stack, four image titles, API stats, links, mobile, and both motion preferences.');
}catch(error){report.status='failed';report.error=error.message;throw error;}
finally{await fs.writeFile(path.join(out,'published-report.json'),JSON.stringify(report,null,2));await browser.close();}
