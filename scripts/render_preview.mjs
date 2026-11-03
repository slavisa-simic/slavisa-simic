/** Render with GitHub's real sanitizer and styles, then verify the local and live layouts. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { root, config, launch, serve } from './lib.mjs';
const preview=path.join(root,'assets/previews/blueprint');
const vendor=path.join(preview,'vendor');
await fs.mkdir(vendor,{recursive:true});
const readme=await fs.readFile(path.join(root,'README.md'),'utf8');
const hash=crypto.createHash('sha256').update(readme).digest('hex');
const headers={'User-Agent':'engineering-blueprint-local-verification',Accept:'text/html'};
async function get(url,options={}) {
  const response=await fetch(url,{headers,...options,signal:AbortSignal.timeout(30000)});
  if(!response.ok) throw new Error(`${url}: HTTP ${response.status}`);
  return response.text();
}
let rendered,cache;
try{cache=JSON.parse(await fs.readFile(path.join(preview,'render-cache.json'),'utf8'));}catch{}
if(cache?.sha256===hash&&!process.argv.includes('--refresh')) rendered=await fs.readFile(path.join(preview,'github-rendered.html'),'utf8');
else {
  rendered=await get('https://api.github.com/markdown',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({text:readme,mode:'gfm'})});
  cache={sha256:hash,rendered_at:new Date().toISOString(),endpoint:'https://api.github.com/markdown'};
  await fs.writeFile(path.join(preview,'github-rendered.html'),rendered);
  await fs.writeFile(path.join(preview,'render-cache.json'),JSON.stringify(cache,null,2));
}
const shell=await get('https://github.com/slavisa-simic/vigil');
const links=[...shell.matchAll(/<link\b[^>]*>/g)].map(m=>m[0]).filter(s=>/rel="stylesheet"/.test(s)&&/href="https:\/\/github\.githubassets\.com\//.test(s));
if(!links.length)throw new Error('GitHub CSS not found');
const localLinks=[],seen=new Set(),cssEvidence=[];
for(const link of links) {
  const url=link.match(/href="([^"]+)"/)[1];
  if(seen.has(url))continue; seen.add(url);
  const filename=path.basename(new URL(url).pathname);
  let css;try{css=await fs.readFile(path.join(vendor,filename),'utf8');}catch{css=await get(url);await fs.writeFile(path.join(vendor,filename),css);}
  localLinks.push(link.replace(url,`vendor/${filename}`));
  cssEvidence.push({url,sha256:crypto.createHash('sha256').update(css).digest('hex')});
}
function document(content,theme='dark') {
  return `<!doctype html><html lang="en" data-color-mode="${theme}" data-light-theme="light" data-dark-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Slaviša Simić — Engineering Blueprint profile</title>${localLinks.join('\n')}<style>body{margin:0;background:var(--bgColor-default,#0d1117)}main{box-sizing:border-box;max-width:960px;margin:32px auto;padding:32px;border:1px solid var(--borderColor-default,#30363d);border-radius:10px}@media(max-width:600px){main{margin:0;padding:16px;border:0;border-radius:0}}</style></head><body><main><article class="markdown-body entry-content container-lg">${content}</article></main></body></html>`;
}
const local=rendered.replace(/\b(src|srcset|href)="assets\//g,'$1="../../../assets/');
await fs.writeFile(path.join(preview,'profile.html'),document(local));
await fs.writeFile(path.join(preview,'profile-light.html'),document(local,'light'));
const server=await serve();const browser=await launch();
const assetHashes={};
for(const relative of new Set([...readme.matchAll(/\b(?:src|srcset)="(assets\/[^"]+)"/g)].map(m=>m[1]))) {
  assetHashes[relative]=crypto.createHash('sha256').update(await fs.readFile(path.join(root,relative))).digest('hex');
}
const report={checked_at:new Date().toISOString(),readme_sha256:hash,assets_sha256:assetHashes,renderer:cache,browser:browser.version(),stylesheets:cssEvidence,viewports:[],publication:'Read-only rendering. No repository, commit, push, or publication.'};
function assert(condition,message){if(!condition)throw new Error(message);}
async function ready(page){await page.waitForFunction(()=>[...document.querySelectorAll('article img')].every(i=>i.complete&&i.naturalWidth));await page.evaluate(()=>document.fonts.ready);}
async function measure(page){return page.evaluate(()=>{
  const p=document.querySelector('article p[align="center"]');
  const imgs=[...p.querySelectorAll('img')];
  const box=el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
  return{width:innerWidth,strip:box(p),overflow:document.documentElement.scrollWidth>innerWidth,images:imgs.map(img=>({...box(img),name:img.getAttribute('src').split('/').at(-1),source:img.currentSrc,href:img.closest('a')?.href||null,alt:img.alt,verticalAlign:getComputedStyle(img).verticalAlign}))};
});}
function validate(m){
  const n=config.panels.length;
  assert(!m.overflow,`Overflow at ${m.width}`);assert(m.images.length===n+6,'Unexpected hero image count');
  const groups=[[0,1,2],[3],Array.from({length:n},(_,i)=>4+i),[4+n],[5+n]];let previous=null;
  for(const group of groups){
    const rows=group.map(i=>m.images[i]);
    for(let j=0;j<rows.length;j++){
      assert(rows[j].verticalAlign==='top','GitHub changed top alignment');
      assert(rows[j].alt.length>3,'An image lacks alt text');
      assert(Math.abs(rows[j].y-rows[0].y)<.1,'A panel wrapped');
      assert(Math.abs(rows[j].height-rows[0].height)<.1,'Panel heights differ');
      if(j)assert(Math.abs(rows[j].x-rows[j-1].right)<.1,'Horizontal seam');
    }
    if(previous!==null)assert(Math.abs(rows[0].y-previous)<.1,`Vertical seam ${rows[0].y-previous}px`);
    previous=Math.max(...rows.map(r=>r.bottom));
  }
  const expected=[config.identity.github,config.identity.github,config.identity.linkedin,null,...config.panels.map(p=>p.url),null,config.identity.github+'?tab=repositories'];
  m.images.forEach((i,index)=>assert(i.href===expected[index],`Wrong hero link ${index}: ${i.href}`));
}
try{
  const context=await browser.newContext({deviceScaleFactor:1,colorScheme:'dark',reducedMotion:'no-preference'});
  const page=await context.newPage();
  for(const width of [320,390,600,601,768,1024,1280]){
    await page.setViewportSize({width,height:1000});await page.goto(`${server.origin}/assets/previews/blueprint/profile.html`);await ready(page);
    const m=await measure(page);validate(m);
    assert(m.images.every(i=>i.source.includes(width<=600?'/mobile/':'/desktop/')),'Wrong responsive source');
    assert(m.images.filter(i=>i.source.endsWith('.gif')).length===config.panels.length,'Missing animation');
    await page.evaluate(()=>{window.heroClicks=[];document.querySelector('article p[align="center"]').addEventListener('click',e=>{const a=e.target.closest('a');if(a){e.preventDefault();window.heroClicks.push(a.href);}});});
    const anchors=page.locator('article p[align="center"] a');
    const expected=m.images.filter(i=>i.href).map(i=>i.href);
    for(let i=0;i<expected.length;i++)await anchors.nth(i).click();
    for(let i=0;i<expected.length;i++){await anchors.nth(i).focus();await page.keyboard.press('Enter');}
    assert(JSON.stringify(await page.evaluate(()=>window.heroClicks))===JSON.stringify([...expected,...expected]),'Pointer or keyboard activation failed');
    m.links=`All ${expected.length} hero links passed pointer and keyboard activation`;report.viewports.push(m);
    if(width===390||width===1280){await page.locator('article h2').first().click();await page.screenshot({path:path.join(preview,width===390?'profile-mobile.png':'profile-desktop.png'),fullPage:true});}
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(()=>[...document.querySelectorAll('article p[align="center"] img')].every(i=>i.currentSrc.endsWith('.png')));
    await ready(page);
    const reduced=await measure(page);validate(reduced);assert(reduced.images.every(i=>i.source.endsWith('.png')),'Reduced-motion fallback failed');
    report.viewports.at(-1).reduced_motion='All PNG; geometry and links unchanged';
    await page.emulateMedia({reducedMotion:'no-preference'});
  }
  await page.setViewportSize({width:1280,height:1000});await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto(`${server.origin}/assets/previews/blueprint/profile.html`);await ready(page);
  await page.locator('article p[align="center"]').first().screenshot({path:path.join(preview,'hero-desktop.png')});
  await page.screenshot({path:path.join(preview,'profile-reduced-motion.png'),fullPage:true});
  await page.goto(`${server.origin}/assets/previews/blueprint/profile-light.html`);await ready(page);validate(await measure(page));
  await page.screenshot({path:path.join(preview,'profile-light.png'),fullPage:true});
  // Live GitHub styles and custom elements; local images intercepted before any upload.
  const live=await context.newPage();await live.setViewportSize({width:1280,height:1000});
  await live.route('https://github.githubassets.com/assets/blueprint-local-preview/**',async route=>{
    const relative=new URL(route.request().url()).pathname.split('/blueprint-local-preview/')[1];const file=path.resolve(root,relative);
    if(!file.startsWith(root+path.sep))return route.abort();
    await route.fulfill({status:200,contentType:file.endsWith('.gif')?'image/gif':'image/png',body:await fs.readFile(file)});
  });
  await live.goto('https://github.com/slavisa-simic/vigil',{waitUntil:'domcontentloaded'});await live.locator('article.markdown-body').waitFor();
  const liveHTML=rendered.replace(/\b(src|srcset)="assets\//g,'$1="https://github.githubassets.com/assets/blueprint-local-preview/assets/');
  await live.locator('article.markdown-body').evaluate((article,html)=>{article.innerHTML=html;},liveHTML);await ready(live);
  const actual=await measure(live);validate(actual);report.live_github={mode:'Read-only DOM injection using GitHub CSS and custom elements; locally intercepted images',url:live.url(),...actual};
  await live.locator('article p[align="center"]').first().screenshot({path:path.join(preview,'github-live-hero.png')});
  const skills=await page.locator('h2').filter({hasText:'Personal skills'}).evaluate(h=>h.nextElementSibling.textContent);
  assert(!/Unity|C#/.test(skills),'Personal skills incorrectly claim game technologies');
  report.content={personal_skills_exclude_unity_and_csharp:true,potamorph_focus:'AI development case study',ai_tool:'OpenAI Codex'};
  report.status='passed';await context.close();
  console.log('Passed seven widths, light/dark, reduced motion, linked regions, row seams, and live GitHub CSS.');
}catch(error){report.status='failed';report.error=error.stack;throw error;}
finally{await fs.writeFile(path.join(preview,'browser-report.json'),JSON.stringify(report,null,2));await browser.close();await server.close();}
