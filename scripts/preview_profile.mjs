/** Preview the actual README through GitHub's sanitizer and current styles. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {root,launch,serve} from './lib.mjs';
const config=JSON.parse(await fs.readFile(path.join(root,'config/profile.json'),'utf8'));
const out=path.join(root,'assets/previews/profile');const vendor=path.join(out,'vendor');await fs.mkdir(vendor,{recursive:true});
const readme=await fs.readFile(path.join(root,'README.md'),'utf8');const hash=crypto.createHash('sha256').update(readme).digest('hex');
const headers={'User-Agent':'slavisa-native-profile-preview',Accept:'text/html'};
async function request(url,options={}){const r=await fetch(url,{headers,...options,signal:AbortSignal.timeout(30000)});if(!r.ok)throw new Error(`${url}: HTTP ${r.status}`);return r.text();}
let cache,html;
try{cache=JSON.parse(await fs.readFile(path.join(out,'render-cache.json'),'utf8'));}catch{}
if(cache?.sha256===hash)html=await fs.readFile(path.join(out,'github-rendered.html'),'utf8');
else{
 html=await request('https://api.github.com/markdown',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({text:readme,mode:'gfm'})});
 cache={sha256:hash,endpoint:'https://api.github.com/markdown',time:new Date().toISOString()};
 await fs.writeFile(path.join(out,'render-cache.json'),JSON.stringify(cache,null,2));await fs.writeFile(path.join(out,'github-rendered.html'),html);
}
const shell=await request('https://github.com/slavisa-simic');const css=[],seen=new Set();
for(const tag of [...shell.matchAll(/<link\b[^>]*>/g)].map(m=>m[0]).filter(t=>/rel="stylesheet"/.test(t)&&/href="https:\/\/github\.githubassets\.com\//.test(t))){
 const url=tag.match(/href="([^"]+)"/)[1];if(seen.has(url))continue;seen.add(url);const name=path.basename(new URL(url).pathname);
 try{await fs.access(path.join(vendor,name));}catch{await fs.writeFile(path.join(vendor,name),await request(url));}
 css.push(tag.replace(url,`vendor/${name}`));
}
if(!css.length)throw new Error('GitHub styles were not found');
const content=html.replace(/\b(src|srcset)="assets\//g,'$1="../../../assets/');
for(const theme of ['dark','light'])await fs.writeFile(path.join(out,`${theme}.html`),`<!doctype html><html lang="en" data-color-mode="${theme}" data-light-theme="light" data-dark-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Slaviša Simić — profile preview</title>${css.join('\n')}<style>body{margin:0;background:var(--bgColor-default,#0d1117)}main{box-sizing:border-box;max-width:960px;margin:32px auto;padding:32px;border:1px solid var(--borderColor-default,#30363d);border-radius:10px}@media(max-width:600px){main{margin:0;padding:16px;border:0;border-radius:0}}</style></head><body><main><article class="markdown-body entry-content container-lg">${content}</article></main></body></html>`);
const browser=await launch();const server=await serve();
const report={readme_sha256:hash,checked_at:new Date().toISOString(),renderer:cache,viewports:[],images:{}};
for(const match of readme.matchAll(/\b(?:src|srcset)="(assets\/[^"]+)"/g))report.images[match[1]]=crypto.createHash('sha256').update(await fs.readFile(path.join(root,match[1]))).digest('hex');
function check(condition,message){if(!condition)throw new Error(message);}
try{
 const context=await browser.newContext({deviceScaleFactor:1,colorScheme:'dark',reducedMotion:'no-preference'});const page=await context.newPage();
 for(const width of [320,375,390,600,601,768,844,1024,1440]){
  await page.setViewportSize({width,height:width===844?390:1000});await page.goto(`${server.origin}/assets/previews/profile/dark.html`);
  await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>0));
  const state=await page.locator('article').evaluate(article=>({
   width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,
   tables:[...article.querySelectorAll('table')].map(t=>({scrollWidth:t.scrollWidth,width:t.clientWidth})),
   images:[...article.querySelectorAll('img')].map(i=>{const r=i.getBoundingClientRect();return{source:i.currentSrc,alt:i.alt,x:r.x,y:r.y,width:r.width,height:r.height,href:i.closest('a')?.href||null};}),
   headings:[...article.querySelectorAll('h2')].map(h=>h.textContent),
   visibleText:article.innerText
  }));
  check(!state.overflow,`Page overflow at ${width}`);
  check(state.tables.every(t=>t.scrollWidth<=t.width+1),`Table overflow at ${width}: ${JSON.stringify(state.tables)}`);
  check(state.images.length===3,'Expected one carousel, identity, and activity');
  const carousel=state.images.find(i=>i.alt.startsWith('Projects carousel:'));
  check(carousel?.href.endsWith(config.carousel.target),'Carousel must open the projects list');check(carousel.width>=44&&carousel.height>=44,'Carousel target is too small');
  check(carousel.source.endsWith(width<=600?'projects-carousel-mobile.svg':'projects-carousel.svg'),'Wrong carousel source');
  check(state.headings.join('|')==='Projects carousel|Toolkit|Recent work','Information hierarchy changed');
  check((await page.locator('article h3').allTextContents()).join('|')==='Projects list','Missing visible project list');
  for(const p of config.projects)check(await page.locator(`article a[href="${p.readme}"]`).count()===1,'Project README link missing or repeated');
  check(state.visibleText.split(config.intro).length===2,'Introduction is repeated');
  check(state.visibleText.split('AI Development Tools:').length===2,'AI tools label is repeated');
  const toolkit=state.visibleText.split('Toolkit')[1].split('Recent work')[0];check(!/Unity|C#/.test(toolkit),'Game technology is presented as personal expertise');
  await page.locator('details').first().locator('summary').click();check(await page.locator('details').first().evaluate(d=>d.open),'Disclosure does not open');await page.locator('details').first().locator('summary').click();
  await page.evaluate(()=>{window.projectClicks=[];document.querySelector('article').addEventListener('click',e=>{const a=e.target.closest('a');if(a){e.preventDefault();window.projectClicks.push(a.href);}});});
  const links=[page.locator('article a').filter({has:page.locator('img[alt^="Projects carousel:"]')}),...config.projects.map(p=>page.locator(`article a[href="${p.readme}"]`))];
  for(const link of links){await link.click();await link.focus();await page.keyboard.press('Enter');}
  const clicks=await page.evaluate(()=>window.projectClicks);check(clicks.slice(0,2).every(h=>h.endsWith(config.carousel.target))&&JSON.stringify(clicks.slice(2))===JSON.stringify(config.projects.flatMap(p=>[p.readme,p.readme])),'Pointer/keyboard carousel or README links failed');
  await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>[...document.querySelectorAll('article img')].slice(0,2).every(i=>i.currentSrc.endsWith('.png')));
  const identity=page.locator('article img').first();await page.waitForFunction(()=>document.querySelector('article img').currentSrc.endsWith('.png'));
  if(width===390||width===1440){await page.locator('article h2').first().click();await page.screenshot({path:path.join(out,width===390?'mobile.png':'desktop.png'),fullPage:true});}
  state.reducedMotion='Static identity and carousel PNGs';report.viewports.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.goto(`${server.origin}/assets/previews/profile/light.html`);await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>0));await page.screenshot({path:path.join(out,'light.png'),fullPage:true});
 const live=await context.newPage();await live.setViewportSize({width:1440,height:1100});
 await live.route('https://github.githubassets.com/assets/profile-local-review/**',async route=>{const relative=new URL(route.request().url()).pathname.split('/profile-local-review/')[1];const file=path.resolve(root,relative);if(!file.startsWith(root+path.sep))return route.abort();await route.fulfill({status:200,contentType:file.endsWith('.svg')?'image/svg+xml':file.endsWith('.gif')?'image/gif':'image/png',body:await fs.readFile(file)});});
 await live.goto('https://github.com/slavisa-simic',{waitUntil:'domcontentloaded'});await live.locator('.markdown-body').first().evaluate((article,html)=>{article.innerHTML=html;},html.replace(/\b(src|srcset)="assets\//g,'$1="https://github.githubassets.com/assets/profile-local-review/assets/'));
 await live.waitForFunction(()=>[...document.querySelectorAll('.markdown-body img')].every(i=>i.complete&&i.naturalWidth>0));await live.locator('.markdown-body').first().screenshot({path:path.join(out,'github-css.png')});
 report.liveCSS='Verified with actual GitHub styles; read-only DOM substitution, no publishing';
 await page.setViewportSize({width:375,height:800});await page.goto(`${server.origin}/assets/previews/profile/dark.html`);await page.locator('article').evaluate(a=>a.style.fontSize='24px');
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Enlarged text causes horizontal overflow');report.enlargedText='Native text checked at 24 px on 375 px viewport';
 report.status='passed';await context.close();console.log('Passed nine widths, native text, project links, disclosures, reduced motion, enlarged text, and GitHub rendering.');
}catch(error){report.status='failed';report.error=error.stack;throw error;}
finally{await fs.writeFile(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));await browser.close();await server.close();}
