import { launch } from './lib.mjs';
const browser = await launch();
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
  await page.goto('https://github.com/slavisa-simic/vigil', { waitUntil: 'domcontentloaded' });
  const result = await page.locator('article.markdown-body').evaluate(article => {
    const image = (width, height, percent) => `<img align="top" width="${percent}%" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}'%3E%3Crect width='100%25' height='100%25' fill='%23101113'/%3E%3C/svg%3E">`;
    article.innerHTML = `<p align="center">${image(1120,100,100)}<br>${image(432,430,38.57142)}${image(256,430,22.85713)}${image(432,430,38.57142)}<br>${image(1120,100,100)}</p>`;
    return new Promise(resolve => setTimeout(() => {
      const rects = [...article.querySelectorAll('img')].map(img => { const r = img.getBoundingClientRect(); return { x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right,verticalAlign:getComputedStyle(img).verticalAlign }; });
      resolve({ rects, gap_after_header:rects[1].y-rects[0].bottom, gap_before_footer:rects[4].y-rects[1].bottom });
    }, 500));
  });
  console.log(JSON.stringify(result, null, 2));
  if (Math.abs(result.gap_after_header) > .1 || Math.abs(result.gap_before_footer) > .1) throw new Error('Image row gaps: use a documented fallback');
} finally { await browser.close(); }
