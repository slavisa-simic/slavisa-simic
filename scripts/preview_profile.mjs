/** Preview the actual README through GitHub's sanitizer and current styles. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {root,launch,serve} from './lib.mjs';
const config=JSON.parse(await fs.readFile(path.join(root,'config/profile.json'),'utf8'));
const activityImageCount=2;
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
  check(!state.overflow,`Page overflow at ${width}`);
  if(width>=1024)check(state.tables.every(t=>t.scrollWidth<=t.width+1),`Desktop table overflow at ${width}`);
  const identity=state.images.find(i=>i.alt.startsWith(config.name+' — Software Engineer.'));
  check(identity&&!identity.alt.includes('Backend Developer'),'Incorrect responsive identity');
  check(state.images.length===7+config.projects.reduce((n,p)=>n+3+p.showcase.stack.length,0)+activityImageCount,'Unexpected profile image count');
  check(state.images[0]===identity,'Header must appear first');
  check(await page.locator('article img[alt="Projects"]').count()===1,'Missing original Projects title image');
  check(!state.visibleText.includes('All projects'),'Duplicate project heading must be removed');
  const carousel=state.images.find(i=>i.alt.startsWith('Projects carousel:'));check(carousel?.href.endsWith(config.carousel.target),'Carousel target is incorrect');check(carousel.width>=44&&carousel.height>=44,'Carousel target is too small');
  check(carousel.source.endsWith(width<=600?'projects-carousel-mobile.svg':'projects-carousel.svg'),'Wrong carousel variant');
  for(const p of config.projects){
   check(await page.locator(`article table a[href="https://github.com/${p.repository}"]`).count()===1,'Missing project repository link');
   const row=page.locator('article tbody tr').filter({has:page.getByRole('heading',{name:p.name,exact:true})});
   check(await row.count()===1,'Missing native project heading');
   check(await row.locator(':scope > td').count()===4,'Each project needs image, description, stack, and actions columns');
   check(await row.locator(':scope > td').nth(1).innerText().then(t=>t.includes(p.showcase.description)),'Description must be in the second column');
   check(await row.locator(':scope > td').nth(2).innerText().then(t=>t.includes('Tech stack')),'Technology stack must be in the third column');
   const imageCell=row.locator(':scope > td').first();
   const centered=await imageCell.evaluate(cell=>{const cellBox=cell.getBoundingClientRect();const photo=cell.querySelector('img').getBoundingClientRect();return {dx:Math.abs(photo.x+photo.width/2-cellBox.x-cellBox.width/2),dy:Math.abs(photo.y+photo.height/2-cellBox.y-cellBox.height/2)};});
   if(width>=1024)check(centered.dx<=1&&centered.dy<=1,'Project screenshot must be centered on both axes: '+JSON.stringify(centered));
   (state.imageAlignment??=[]).push({project:p.id,...centered});
   const actions=row.locator(':scope > td').nth(3);
   const repoBox=await actions.locator('a').boundingBox();
   const demoBox=await actions.locator('img[alt="Demo — not available yet"]').boundingBox();
   check(demoBox.y>=repoBox.y+repoBox.height,'Project actions must stack vertically in the fourth column');
   const copy=await row.innerText();
   check(copy.includes(p.showcase.kind)&&copy.includes(p.showcase.description),'Project descriptions must be real text');
   for(const technology of p.showcase.stack)check(await row.locator(`img[alt="${technology}"]`).count()===1,'Missing technology badge: '+technology);
   const selected=await row.evaluate((el,description)=>{const paragraph=[...el.querySelectorAll('p')].find(p=>p.textContent===description);const selection=window.getSelection();selection.selectAllChildren(paragraph);const value=selection.toString();selection.removeAllRanges();return value;},p.showcase.description);
   check(selected===p.showcase.description,'Project copy must be selectable');
  }
  check(await page.locator('article tbody tr').count()===config.projects.length,'Expected one table row per project');
  check(await page.locator('article details, article summary').count()===0,'Old disclosures must be removed');
  check(!state.visibleText.includes('hourly sync')&&!state.images.some(i=>['Projects list','Project notes','Recent changes','Hourly stats refresh'].includes(i.alt)),'Old profile footer must be removed');
  const demos=page.locator('article img[alt="Demo — not available yet"]');
  check(await demos.count()===config.projects.length,'Missing Demo placeholders');
  check(await demos.evaluateAll(images=>images.every(i=>!i.closest('a'))),'Demo placeholders must not navigate');
  check(await page.locator('article table').evaluate(t=>Math.abs(t.clientWidth-t.closest('article').clientWidth)<2),'Project table must fill the content width');
  const toolkit=identity;check(toolkit&&!/Unity/.test(toolkit.alt)&&toolkit.alt.includes('Python')&&toolkit.alt.includes('AI development tool'),'Technology list or Codex category is incorrect');
  check(!(await page.locator('img[alt="Tech stack"]').count()),'Standalone tech stack must be removed');
  check((width<=960?/profile-header-[0-9a-f]{16}-mobile\.svg$/:/profile-header-[0-9a-f]{16}\.svg$/).test(identity.source),'Wrong responsive header variant');
  for(const [label,href] of [['GitHub Repositories',`https://github.com/${config.owner}?tab=repositories`],['LinkedIn',config.linkedin]])check(await page.locator(`article a[href="${href}"] img[alt="${label}"]`).count()===1,`Missing independent ${label} link`);
  const contactsBox=await page.locator('article img[alt="GitHub Repositories"]').boundingBox();
  const identityBox=await page.locator('article img').first().boundingBox();
  const expectedContactX=identityBox.x+(width<=960?0:208);
  check(Math.abs(contactsBox.x-expectedContactX)<=1.1,'Contact links must align with the identity text column');
  check(state.images.some(i=>i.alt==='About Me. '+config.intro),'Missing simple About Me description');
  await page.evaluate(()=>{window.links=[];document.querySelector('article').addEventListener('click',e=>{const a=e.target.closest('a');if(a){e.preventDefault();window.links.push(a.href);}});});
  const contacts=[`https://github.com/${config.owner}?tab=repositories`,config.linkedin];
  const projectLinks=[page.locator('article a').filter({has:page.locator('img[alt^="Projects carousel:"]')}),...config.projects.map(p=>page.locator(`article table a[href="https://github.com/${p.repository}"]`)),...contacts.map(url=>page.locator(`article a[href="${url}"]`))];
  for(const link of projectLinks){await link.click();await link.focus();await page.keyboard.press('Enter');}
  const clicks=await page.evaluate(()=>window.links);check(clicks.slice(0,2).every(h=>h.endsWith(config.carousel.target))&&JSON.stringify(clicks.slice(2))===JSON.stringify([...config.projects.map(p=>`https://github.com/${p.repository}`),...contacts].flatMap(url=>[url,url])),'Keyboard or pointer navigation failed');
  await page.evaluate(()=>document.activeElement?.blur());
  if(width===390||width===1440){await page.evaluate(()=>window.scrollTo(0,0));const article=await page.locator('article').boundingBox();const projects=await page.locator('article img[alt="Projects"]').boundingBox();await page.screenshot({path:path.join(out,width===390?'header-mobile.png':'header-desktop.png'),clip:{x:article.x,y:article.y,width:article.width,height:projects.y-article.y-12}});}
  await page.emulateMedia({reducedMotion:'reduce'});await page.waitForFunction(()=>document.querySelector('img[alt^="Projects carousel:"]').currentSrc.endsWith('-reduced.svg'));
  await page.waitForFunction(()=>!document.querySelector('article img').currentSrc.endsWith('-reduced.svg'));
  if(width===390||width===1440){await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(out,width===390?'mobile.png':'desktop.png'),fullPage:true});const article=await page.locator('article').boundingBox();const projects=await page.locator('article img[alt="Projects"]').boundingBox();await page.screenshot({path:path.join(out,width===390?'header-mobile-reduced.png':'header-desktop-reduced.png'),clip:{x:article.x,y:article.y,width:article.width,height:projects.y-article.y-12}});}
  state.reducedMotion='Technology marquee keeps moving right per user preference; project carousel keeps its original non-sliding switches';report.viewports.push(state);await page.emulateMedia({reducedMotion:'no-preference'});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({colorScheme:'light',reducedMotion:'reduce'});await page.goto(`${server.origin}/assets/previews/profile/light.html`);await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth>0));await page.screenshot({path:path.join(out,'light.png'),fullPage:true});
 await page.setViewportSize({width:375,height:800});await page.goto(`${server.origin}/assets/previews/profile/dark.html`);await page.locator('article').evaluate(a=>a.style.fontSize='24px');check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Enlarged native text overflows');
 report.status='passed';console.log('Passed nine widths, identity-column contacts, responsive project table, repository links, inactive demos, themes, and animation.');
}catch(error){report.status='failed';report.error=error.stack;throw error;}
finally{await fs.writeFile(path.join(out,'browser-report.json'),JSON.stringify(report,null,2));await browser.close();await server.close();}
