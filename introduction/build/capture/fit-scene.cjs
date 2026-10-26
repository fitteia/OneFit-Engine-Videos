// Captures shots/10-fit-compact.png: the real fit in the dark Compact layout,
// with Plots under the Terminal in the centre column.
//   GUI      a running OFE-GUI (default http://127.0.0.1:19143/), its work
//            folder holding nothing else
//   DATA     the data file to upload (ffc-relaxation.dat)
//   PROFILE  a Chromium profile folder to use (kept between captures)
//   CHROME   a Chromium binary, if Playwright has none of its own
const { chromium } = require('playwright-core');
const path = require('path');
const GUI = process.env.GUI || 'http://127.0.0.1:19143/';
const OUT = path.join(__dirname, '..', 'shots', '10-fit-compact.png');

// Options | Terminal over Plots | Parameters over Output
const LAYOUT = { version: 1, cols: [
  { w: 0.25, panes: [{ id: 'settings', h: 1, hidden: true }] },
  { w: 0.30, panes: [{ id: 'form', h: 1 }] },
  { w: 0.38, panes: [{ id: 'terminal', h: 1 }, { id: 'selected', auto: true }, { id: 'plots', h: 1.35 }] },
  { w: 0.32, panes: [{ id: 'fits', auto: true }, { id: 'parameters', auto: true }, { id: 'output', h: 1 }] },
] };

(async () => {
  const ctx = await chromium.launchPersistentContext(process.env.PROFILE || path.join(__dirname, 'profile'), {
    ...(process.env.CHROME ? { executablePath: process.env.CHROME } : {}),
    viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2, colorScheme: 'dark',
  });
  await ctx.addInitScript((layout) => {
    try { localStorage.setItem('onefite-gui-theme', 'dark'); localStorage.setItem('onefite-gui-panes-v1', JSON.stringify(layout)); } catch (e) {}
  }, LAYOUT);
  const page = ctx.pages()[0] || await ctx.newPage();
  page.on('dialog', d => d.accept().catch(() => {}));
  await page.goto(GUI); await page.waitForTimeout(2000);
  await page.keyboard.press('Escape');
  if (!(await page.isVisible('#terminalToggleBtn'))) {
    await page.click('text=Compact layout...'); await page.waitForTimeout(1200); await page.keyboard.press('Escape');
  }

  await page.fill('#function', 'Mz(t,M0:1,Minf:0.05,T1:2[0.01<100])=Minf+(M0-Minf)*exp(-t/T1)');
  await page.dispatchEvent('#function', 'input');
  if (process.env.DATA) { await page.setInputFiles('#dataFilesPicker', process.env.DATA); await page.waitForTimeout(1500); }
  for (const id of ['#logX', '#reducedChi2']) if (!(await page.isChecked(id))) await page.check(id, { force: true });
  const autoY = await page.$('xpath=//label[normalize-space(.)="auto Y"]/input');
  if (autoY && !(await autoY.isChecked())) await autoY.check({ force: true });
  await page.fill('#fitMethods', 'simp scan min');
  await page.click('#runBtn');
  await page.waitForFunction(() => /done|error|fail/i.test(document.getElementById('status').textContent), null, { timeout: 120000 });
  await page.waitForTimeout(3000);
  console.log('status:', await page.textContent('#status'));

  await page.click('#terminalToggleBtn'); await page.waitForTimeout(2500);
  const term = await page.$('.xterm-helper-textarea');
  await term.focus();
  await page.keyboard.type('export PATH=/opt/onefite-go/bin:$PATH; clear\n'); await page.waitForTimeout(800);
  await page.keyboard.type('onefite --version\n'); await page.waitForTimeout(1500);
  await page.keyboard.type('ls ofe-tmp/*.pdf ofe-tmp/*.json\n'); await page.waitForTimeout(1200);
  await page.keyboard.press('Alt+KeyH'); await page.waitForTimeout(300);
  // the fit made an MP4 too: show the plot, not the video player
  await page.evaluate(() => { const b = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === 'Plots'); b?.click(); });
  await page.waitForTimeout(2500);
  await page.mouse.move(5, 1075);
  await page.screenshot({ path: OUT });
  console.log('wrote', OUT);
  await ctx.close();
})();
