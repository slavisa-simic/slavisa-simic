/** Verify the actual README images, mobile/static selection, SMIL loop, and SVG bounds. */
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {root, launch, serve} from './lib.mjs';

const config = JSON.parse(await fs.readFile(path.join(root, 'config/activity.json'), 'utf8'));
const snapshot = JSON.parse(await fs.readFile(path.join(root, 'assets/profile/activity/commits.json'), 'utf8'));
const readme = await fs.readFile(path.join(root, 'README.md'), 'utf8');
const section = readme.match(/<!-- repository-districts:start -->([\s\S]*?)<!-- repository-districts:end -->/)[1];
const out = path.join(root, 'assets/previews/activity');
await fs.mkdir(out, {recursive:true});
await fs.writeFile(path.join(out, 'index.html'), `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Repository Districts · local preview</title><style>body{margin:0;background:#0d1117;color:#edf0f4;font:16px/1.6 system-ui}main{max-width:1000px;margin:32px auto;padding:16px}img{display:block;max-width:100%;height:auto}p{margin:16px 0}a{color:#82a9d5}h2{font-size:24px;border-bottom:1px solid #292c32}sub{font-size:12px;vertical-align:baseline}picture{display:block}</style></head><body><main>${section.replaceAll('="assets/', '="../../../assets/').replace('href="docs/', 'href="../../../docs/')}</main></body></html>`);
const browser = await launch();
const server = await serve();
const report = {status:'pending', viewports:[], svg:[]};
try {
  const page = await browser.newPage({colorScheme:'dark'});
  for (const width of [320, 390, 768, 1100]) {
    await page.setViewportSize({width, height:1000});
    await page.emulateMedia({reducedMotion:'no-preference'});
    await page.goto(`${server.origin}/assets/previews/activity/index.html`);
    await page.waitForFunction(() => [...document.images].every(i => i.complete && i.naturalWidth > 0));
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Overflow at ${width}`);
    const images = page.locator('a picture img');
    assert.equal(await images.count(), snapshot.projects.length);
    for (const project of snapshot.projects) {
      const linkedImage = page.locator(`a[href="https://github.com/${project.repo}"] img`);
      const source = await linkedImage.evaluate(i => i.currentSrc);
      assert(source.endsWith(width <= 600 ? '-mobile.svg' : '.svg'));
      assert(!source.endsWith('-static.svg'));
    }
    await page.screenshot({path:path.join(out, `preview-${width}.png`), fullPage:true});
    if (width === 1100 && snapshot.projects.length) {
      const image = images.first();
      await image.screenshot({path:path.join(out,'district-desktop.png')});
      const start = await image.screenshot();
      await page.waitForTimeout(2000);
      assert(!start.equals(await image.screenshot()), 'SMIL must animate inside a README image');
    }
    if (width === 390 && snapshot.projects.length) {
      await images.first().screenshot({path:path.join(out,'district-mobile.png')});
    }
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(() => [...document.querySelectorAll('a picture img')].every(i => i.currentSrc.endsWith('-static.svg')));
    report.viewports.push({width, responsiveImages:true, staticFallback:true, overflow:false});
  }
  for (const project of snapshot.projects) {
    const stem = `activity-${project.repo.replace('/', '--').toLowerCase()}`;
    for (const mobile of [false, true]) {
      const file = `${stem}${mobile ? '-mobile' : ''}.svg`;
      await page.goto(`${server.origin}/assets/profile/generated/${file}`);
      const state = await page.evaluate(() => {
        const svg = document.documentElement;
        const {width, height} = svg.viewBox.baseVal;
        const outOfBounds = [...svg.querySelectorAll('text,polygon,polyline')].filter(el => {
          const box = el.getBBox();
          const transform = el.getCTM();
          return [[box.x,box.y],[box.x+box.width,box.y+box.height]].some(([x,y]) => {
            const p = new DOMPoint(x,y).matrixTransform(transform);
            // getCTM includes browser viewport scaling for standalone SVGs.
            const inverse = svg.getCTM().inverse();
            const q = p.matrixTransform(inverse);
            return q.x < -1 || q.y < -1 || q.x > width+1 || q.y > height+1;
          });
        }).map(el => el.textContent || el.tagName);
        return {tiles:svg.querySelectorAll('[data-date]').length,
                commits:[...svg.querySelectorAll('[data-commits]')].reduce((n,e)=>n+Number(e.dataset.commits),0),
                outOfBounds};
      });
      assert.deepEqual(state.outOfBounds, [], `${file} clips content`);
      assert.equal(state.tiles, config.periodDays);
      assert.equal(state.commits, project.statistics.totalCommits);
      await page.evaluate(() => {document.documentElement.pauseAnimations();document.documentElement.setCurrentTime(0);});
      const beginning = await page.locator('svg').screenshot();
      await page.evaluate(() => document.documentElement.setCurrentTime(9));
      assert(beginning.equals(await page.locator('svg').screenshot()), 'The nine-second loop must return to its first frame');
      report.svg.push({file, ...state, seamlessLoop:true});
    }
  }
  report.status = 'passed';
  console.log('Passed responsive README images at four widths, reduced motion, live image animation, exact loop, bounds, and tile/commit totals.');
} finally {
  await fs.writeFile(path.join(out,'validation.json'), JSON.stringify(report,null,2));
  await browser.close();
  await server.close();
}
