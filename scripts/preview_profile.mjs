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
const data=JSON.parse(await fs.readFile(path.join(root,'assets/profile/activity.json'),'utf8'));
try{
 const context=await browser.newContext({deviceScaleFactor:1,colorScheme:'dark',reducedMotion:'no-preference'});const page=await context.newPage();
 for(const width of [320,375,390,600,601,768,844,1024,1440]){
  await page.setViewportSize({width,height:width===844?390:1000});await page.goto(`${server.origin}/assets/previews/profile/dark.html`);
  await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>0));
  const state=await page.locator('article').evaluate(a=>({width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,images:[...a.querySelectorAll('img')].map(i=>({source:i.currentSrc,alt:i.alt,width:i.clientWidth,height:i.clientHeight,href:i.closest('a')?.href})),tables:[...a.querySelectorAll('table')].map(t=>({width:t.clientWidth,scrollWidth:t.scrollWidth})),visibleText:a.innerText}));
  check(!state.overflow,`Page overflow at ${width}`);check(state.tables.every(t=>t.scrollWidth<=t.width+1),`Table overflow at ${width}`);
  check(await page.locator('article h1').innerText()===config.name,'Name must be selectable native text');
  check(state.visibleText.includes('Software Engineer')&&state.visibleText.includes('Backend Developer'),'Missing native role text');
  check(state.images.length===14,'Expected framed avatar, six image titles, carousel, badges, and workflow status');
  check(state.images[0].alt==='GitHub profile picture','Header needs the current framed GitHub avatar');
  for(const title of ['Projects','Projects list','Tech stack','AI Development Tools','Project notes','Recent changes'])check(await page.locator(`article img[alt="${title}"]`).count()===1,`Missing image title: ${title}`);
  const carousel=state.images.find(i=>i.alt.startsWith('Projects carousel:'));check(carousel?.href.endsWith(config.carousel.target),'Carousel target is incorrect');check(carousel.width>=44&&carousel.height>=44,'Carousel target is too small');
  check(carousel.source.endsWith(width<=600?'projects-carousel-mobile.svg':'projects-carousel.svg'),'Wrong carousel variant');
  for(const p of config.projects)check(await page.locator(`article a[href="${p.readme}"]`).count()===1,'Missing project README link');
  const rows=await page.locator('article tbody tr').evaluateAll(rows=>rows.map(r=>[...r.cells].map(c=>c.textContent.trim())));
  check(JSON.stringify(rows)===JSON.stringify(data.projects.map(p=>[p.name,String(p.commits_30d),String(p.stars)])),'Native stats differ from API data');
  check(state.visibleText.includes('hourly sync')&&state.visibleText.includes('UTC'),'Missing successful-sync timestamp');
  check(!state.images.some(i=>i.alt.includes('project commits across')),'Stats must not be a picture');
  const toolkit=await page.locator('article img[alt="Tech stack"]').evaluate(i=>{let s=i.closest('h2').nextElementSibling,text='';for(;s;s=s.nextElementSibling)text+=s.innerText;return text;});check(!/Unity|C#/.test(toolkit),'Project implementation is being claimed as expertise');check(await page.locator('img[alt="OpenAI Codex — AI Development Tool"]').count()===1,'Codex category is missing');
  await page.locator('details').first().locator('summary').click();check(await page.locator('details').first().evaluate(d=>d.open),'Disclosure does not open');await page.locator('details').first().locator('summary').click();
  await page.evaluate(()=>{window.links=[];document.querySelector('article').addEventListener('click',e=>{const a=e.target.closest('a');if(a){e.preventDefault();window.links.push(a.href);}});});
  const projectLinks=[page.locator('article a').filter({has:page.locator('img[alt^="Projects carousel:"]')}),...config.projects.map(p=>page.locator(`article a[href="${p.readme}"]`))];
  for(const link of projectLinks){await link.click();await link.focus();await page.keyboard.press('Enter');}
  const clicks=await page.evaluate(()=>window.links);check(clicks.slice(0,2).every(h=>h.endsWith(config.carousel.target))&&JSON.stringify(clicks.slice(2))===JSON.stringify(config.projects.flatMap(p=>[p.readme,p.readme])),'Keyboard or pointer navigation failed');
  await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('img[alt^="Projects carousel:"]').currentSrc.endsWith('-reduced.svg'));
  if(width===390||width===1440){await page.locator('article h1').click();await page.screenshot({path:path.join(out,width===390?'mobile.png':'desktop.png'),fullPage:true});}
  state.reducedMotion='Native text stays readable; carousel changes without sliding';report.viewports.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.goto(`${server.origin}/assets/previews/profile/light.html`);await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>0));await page.screenshot({path:path.join(out,'light.png'),fullPage:true});
 await page.setViewportSize({width:375,height:800});await page.goto(`${server.origin}/assets/previews/profile/dark.html`);await page.locator('article').evaluate(a=>a.style.fontSize='24px');check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Enlarged native text overflows');
 report.status='passed';console.log('Passed nine widths, native identity and stats, badges, links, disclosures, themes, and reduced motion.');
}catch(error){report.status='failed';report.error=error.stack;throw error;}
finally{await fs.writeFile(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));await browser.close();await server.close();}
