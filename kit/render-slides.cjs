// Renders each slide (<section class="slide" id=...>) of slides/slides.html in
// the current folder to slides/<id>.png at 3840x2160, and writes the boxes of
// its elements marked data-hl="name" to slides/boxes.json as "id:name", in
// picture pixels, for narration.py to highlight by name.
// CHROME may point at a Chromium binary; otherwise Playwright's own is used.
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const dir = path.join(process.cwd(), 'slides');
const ids = [...fs.readFileSync(path.join(dir, 'slides.html'), 'utf8').matchAll(/<section class="slide" id="([^"]+)"/g)].map(m => m[1]);
(async () => {
  const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  const p = await (await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 })).newPage();
  const boxes = {};
  for (const s of ids) {
    await p.goto(`file://${dir}/slides.html?s=${s}`); await p.waitForTimeout(400);
    await p.screenshot({ path: `${dir}/${s}.png` });
    for (const [k, b] of await p.evaluate(() => [...document.querySelectorAll('.slide.on [data-hl]')].map(e => {
      const r = e.getBoundingClientRect(); return [e.dataset.hl, [r.left, r.top, r.right, r.bottom]];
    }))) boxes[`${s}:${k}`] = b.map((v, i) => Math.round(v * 2) + (i < 2 ? -16 : 16));
  }
  fs.writeFileSync(path.join(dir, 'boxes.json'), JSON.stringify(boxes, null, 1));
  await b.close();
})();
