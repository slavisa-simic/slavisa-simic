import path from 'node:path';
import {root,launch,serve} from './lib.mjs';
const server=await serve();const browser=await launch();
try{
 const page=await browser.newPage({viewport:{width:1280,height:350},deviceScaleFactor:1});
 await page.setContent(`<style>html,body{margin:0}img{display:block}</style><img src="${server.origin}/assets/profile/source/potamorph-hero.svg" width="1280" height="350">`);
 await page.waitForFunction(()=>document.images[0].complete&&document.images[0].naturalWidth>0);
 await page.locator('img').screenshot({path:path.join(root,'assets/profile/source/potamorph-hero.png')});
 console.log('Rasterized the original game header for the project preview.');
}finally{await browser.close();await server.close();}
