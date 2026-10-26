// Renders each slide of slides/slides.html to slides/<id>.png at 3840x2160.
// CHROME may point at a Chromium binary; otherwise Playwright's own is used.
const { chromium } = require('playwright-core');
const path = require('path');
const dir = path.join(__dirname, 'slides');
(async () => {
  const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  const p = await (await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 })).newPage();
  for (const s of ['title', 'cli1', 'cli2', 'start', 'modes', 'close']) {
    await p.goto(`file://${dir}/slides.html?s=${s}`); await p.waitForTimeout(400);
    await p.screenshot({ path: `${dir}/${s}.png` });
  }
  await b.close();
})();
